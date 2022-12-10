import time
import json
import sys
from io import StringIO
import requests
import pandas as pd
from zeep import Client
import functions


def loginToSalesforce(username: str, password: str, securityToken: str):
    """login function that returns a Salesforce API session"""
    wsdl = './basic_wsdl.xml'

    # Creates the session in order to be able to pull out the Session ID
    SOAPclient = Client(wsdl)
    data = {'username': username, 'password': password+securityToken}
    response = SOAPclient.service.login(**data)
    sessionId = response.sessionId

    # create session for Bulk 2.0 API calls
    session = requests.Session()
    session.headers.update({'Authorization': 'Bearer ' + sessionId})

    return session

def loginToSalesforceSANDBOX(username: str, password: str, securityToken: str, clientId: str, clientSecret: str):
    """
    DEVELOPMENT MODE -- FOR TESTING ONLY

    login function for Salesforce sandbox, returns a dev session for testing
    need to pull client ID and client secret from a sandbox in Salesforce and
        plug them into this function below
    """
    data = {'grant_type': 'password', 'client_id': clientId, 'client_secret': clientSecret,
            'username': username, 'password': password+securityToken}
    response = requests.post('https://test.salesforce.com/services/oauth2/token', data=data)
    sessionId = response.json()['access_token']

    # create session for Bulk 2.0 API calls
    session = requests.Session()
    session.headers.update({'Authorization': 'Bearer ' + sessionId})

    return session

def getDataframeFromSalesforce(query: str, session: requests.Session):
    """
    SALESFORCE BULK 2.0 API FUNCTIONS: QUERY AND INGEST
    function to query Salesforce and return a Pandas Dataframe
    """
    uri = functions.getConfigValue('GeneralConfiguration', 'uri')
    session.headers.update({'Content-Type': 'application/json;charset=utf-8'})

    # create a job to query all Account records
    data = json.dumps({
        "operation": "query",
        "query": query,
    })
    response = session.post(uri + 'query', data=data)

    # Makes sure that the query job was created successfully
    if response.status_code == 200:
        print('Query job created.')
    else:
        print('Query job creation failed:\n' + str(response.json()))
        sys.exit()

    # pull out job ID to use for future requests
    jobId = response.json().get('id')

    # wait for job to complete before getting results
    print('Waiting for query job to complete...')
    jobComplete = False

    # Checks to see if the query job has been completed
    while not jobComplete:
        response = session.get(uri+'query/'+jobId)
        jsonRes = response.json()
        if str(jsonRes['state']) == 'JobComplete':
            jobComplete = True
        time.sleep(0.5)

    # get job results
    response = session.get(uri+'query/'+jobId+'/results')
    s = str(response.content, 'utf-8')
    data = StringIO(s)

    df = pd.read_csv(data)
    return df

def executeSalesforceIngestJob(operation: str, importData: pd.DataFrame, objectType: str, session: requests.Session):
    """
    function to create and execute a Salesforce bulk upload or delete job
    """
    uri = functions.getConfigValue('GeneralConfiguration', 'uri')

    # create data import job
    data = json.dumps({
        "operation": operation,
        "object": objectType,
        "contentType": "CSV",
        "lineEnding": "LF"
    })
    response = session.post(uri+'ingest/', data=data)

    # Makes sure that the data batch job was created successfully
    if response.status_code == 200:
        if operation == 'insert':
            print('Upload job created.')
        elif operation == 'delete':
            print('Delete job created.')
        elif operation == 'update':
            print('Update job created.')
    else:
        if operation == 'insert':
            print('Upload job creation failed.')
        elif operation == 'delete':
            print('Delete job creation failed.')
        elif operation == 'update':
            print('Update job creation failed.')
        print(response.json())
        sys.exit()

    jobId = response.json().get('id')

    # add data to job
    session.headers.update({'Content-Type': 'text/csv;charset=UTF-8'})
    response = session.put(uri+'ingest/'+jobId+'/batches',
                           data=importData.encode('utf-8'))

    # Makes sure that the job was created successfully
    if response.status_code == 201:
        print('Data added to job.')
    else:
        print('Data add failed.')
        print(response.json())
        sys.exit()

    # close the job => Salesforce begins processing the job
    session.headers.update({'Content-Type': 'application/json;charset=utf-8'})
    data = json.dumps({'state': 'UploadComplete'})
    response = session.patch(uri+'ingest/'+jobId, data=data)

    # wait for job to complete before getting results
    print('Waiting for job to complete...')
    jobComplete = False

    # Checks to see if Job is complete
    while not jobComplete:
        response = session.get(uri+'ingest/'+jobId)
        jsonRes = response.json()
        if str(jsonRes['state']) == 'JobComplete':
            jobComplete = True
        elif str(jsonRes['state']) == 'Failed':
            print('Job Failed. Please check Bulk Data Load Jobs in Salesforce Setup')
            print(jsonRes['errorMessage'])
            sys.exit()
        time.sleep(0.25)

    if operation == 'insert':
        print('Upload complete!\n')
    if operation == 'update':
        print('Update complete!\n')
    elif operation == 'delete':
        print('Deletion complete.\n')

    # get job results to display to user
    print('Job results:')
    response = session.get(uri+'ingest/'+jobId)
    jsonRes = response.json()
    print('Records processed: ' + str(jsonRes['numberRecordsProcessed']))
    print('Records failed: ' + str(jsonRes['numberRecordsFailed']) + '\n')
    if jsonRes['numberRecordsFailed'] > 0:
        response = session.get(uri+'ingest/'+jobId+'/failedResults')
        print('---ERROR MESSAGE---')
        print(response.text)
        print('-------------------')
        print('Please check Salesforce for further explanation: Setup > Bulk Data Load Jobs\n')
