import datetime
import configparser
import pandas as pd
import salesforce

### WRAPPER FUNCTIONS
def uploadAccounts(salesforceAccountsDF, adminAccountsDF, accountType, session):
    """generic function to upload Account (both donor and nonprofit) data to Salesforce"""
    adminAccountsDF.columns = ['Parent Name', 'Name', 'Phone', 'Line1', 'Line2', 'ShippingCity', 'ShippingState', 'ShippingPostalCode']

    # clean Accounts data
    salesforceAccountsDF = salesforceAccountsDF[salesforceAccountsDF['RecordTypeId'] == accountType]
    salesforceAccountsDF = salesforceAccountsDF[['Id', 'Name']]
    salesforceAccountsDF = salesforceAccountsDF.reset_index().drop(axis='columns', columns=['index'])

    # cleanup whitespace from names and parent names
    salesforceAccountsDF = cleanupNameWhitespace(salesforceAccountsDF, 'Name')
    adminAccountsDF = cleanupNameWhitespace(adminAccountsDF, 'Parent Name')
    adminAccountsDF = cleanupNameWhitespace(adminAccountsDF, 'Name')

    # find all accounts in the admin tool not in salesforce
    # If the name does not exist in salesforce, then it will be added
    accountsNotInSalesforceDF = pd.merge(adminAccountsDF, salesforceAccountsDF, on='Name', how='left')
    accountsNotInSalesforceDF = accountsNotInSalesforceDF[accountsNotInSalesforceDF['Id'].isnull()]
    accountsNotInSalesforceDF = accountsNotInSalesforceDF.reset_index().drop(axis='columns', columns=['index', 'Id'])

    # convert shipping addresses to Salesforce format
    accountsNotInSalesforceDF['ShippingStreet'] = accountsNotInSalesforceDF['Line1'] + (' ' + accountsNotInSalesforceDF['Line2']).fillna('')
    accountsNotInSalesforceDF.drop(axis='columns', columns=['Line1', 'Line2'], inplace=True)

    # add columns for ParentId and RecordTypeId
    accountsNotInSalesforceDF['ParentId'] = None
    accountsNotInSalesforceDF['RecordTypeId'] = accountType

    # create empty dataframes for first and second upload jobs
    uploadDFRows = []
    uploadDF2Rows = []

    # iterate through accounts to determine parent-child relationships
    for index, row in accountsNotInSalesforceDF.iterrows():
        childName = row['Name']
        parentName = row['Parent Name']

        if childName == parentName:
            uploadDFRows.append(row.values)
        elif parentName in salesforceAccountsDF['Name'].values:
            parentId = salesforceAccountsDF[salesforceAccountsDF['Name'] == parentName]['Id'].item()
            row['ParentId'] = parentId
            uploadDFRows.append(row.values)
        else:
            # create generic record for the new parent account
            parentRow = [parentName, parentName, None, None, None, None, None, None, accountType]
            uploadDFRows.append(parentRow)
            # add child account to the second job
            uploadDF2Rows.append(row.values)

    # prepare dataframe for first upload
    uploadDF = pd.DataFrame(uploadDFRows, columns=accountsNotInSalesforceDF.columns)
    uploadDF.drop_duplicates(inplace=True)
    uploadDF = uploadDF.reset_index().drop(axis='columns', columns=['Parent Name', 'index'])

    # fix phone number formatting
    if not uploadDF['Phone'].dtype == 'object':
        uploadDF['Phone'] = uploadDF['Phone'].astype('Int64')

    # fix zip code formatting
    if not uploadDF['ShippingPostalCode'].dtype == 'object':
        uploadDF['ShippingPostalCode'] = uploadDF['ShippingPostalCode'].astype('Int64')

    # upload first job to Salesforce
    salesforce.executeSalesforceIngestJob('insert', uploadDF.to_csv(index=False), 'Account', session)

    # pull down new list of Accounts
    salesforceAccountsDF = salesforce.getDataframeFromSalesforce('SELECT Id, Name, RecordTypeId FROM Account', session)

    # clean new Accounts data
    salesforceAccountsDF = salesforceAccountsDF[salesforceAccountsDF['RecordTypeId'] == accountType]
    salesforceAccountsDF = salesforceAccountsDF[['Id', 'Name']]
    salesforceAccountsDF = salesforceAccountsDF.reset_index().drop(axis='columns', columns=['index'])

    # attach ID of parent to each record
    uploadDF2 = pd.DataFrame(uploadDF2Rows, columns=accountsNotInSalesforceDF.columns)
    for index, row in uploadDF2.iterrows():
        parentName = row['Parent Name']
        parentId = salesforceAccountsDF[salesforceAccountsDF['Name'] == parentName]['Id'].item()
        uploadDF2.at[index, 'ParentId'] = parentId

    # fix phone number formatting
    if not uploadDF2['Phone'].dtype == 'object':
        uploadDF2['Phone'] = uploadDF2['Phone'].astype('Int64')

    # fix zip code formatting
    if not uploadDF2['ShippingPostalCode'].dtype == 'object':
        uploadDF2['ShippingPostalCode'] = uploadDF2['ShippingPostalCode'].astype('Int64')

    # drop parent name column and upload the new child accounts to salesforce
    uploadDF2.drop(axis='columns', columns=['Parent Name'], inplace=True)
    salesforce.executeSalesforceIngestJob('insert', uploadDF2.to_csv(index=False), 'Account', session)

def uploadFoodRescues(rescuesDF, session):
    """generic function to upload Food Rescue data to Salesforce"""
    # load in Accounts from Salesforce
    salesforceAccountsDF = salesforce.getDataframeFromSalesforce('SELECT Id, Name, RecordTypeId FROM Account', session)

    # load in Contacts from Salesforce
    salesforceContactsDF = salesforce.getDataframeFromSalesforce('SELECT Id, Name, AccountId FROM Contact', session)

    # cleanup rescuesDF
    rescuesDF.drop(axis='columns', columns=['Donor Name', 'Recipient Name'], inplace=True)
    rescuesDF = rescuesDF[(rescuesDF['Rescue State'] == 'canceled') | (rescuesDF['Rescue State'] == 'completed')] # Keeps Only 'canceled' or 'completed' Rescues
    rescuesDF = rescuesDF.reset_index().drop(axis='columns', columns='index')

    # get list of Food Donors
    salesforceDonorsDF = salesforceAccountsDF[salesforceAccountsDF['RecordTypeId'] == getConfigValue('RecordTypeId', 'foodDonor')]
    salesforceDonorsDF = salesforceDonorsDF[['Id', 'Name']]
    salesforceDonorsDF = salesforceDonorsDF.reset_index().drop(axis='columns', columns=['index'])
    salesforceDonorsDF.columns = ['Food_Donor_Account_Name__c', 'Donor Location Name']

    # get list of Nonprofit Partners
    salesforcePartnersDF = salesforceAccountsDF[salesforceAccountsDF['RecordTypeId'] == getConfigValue('RecordTypeId', 'nonProfitPartner')]
    salesforcePartnersDF = salesforcePartnersDF[['Id', 'Name']]
    salesforcePartnersDF = salesforcePartnersDF.reset_index().drop(axis='columns', columns=['index'])
    salesforcePartnersDF.columns = ['Agency_Name__c', 'Recipient Location Name']

    # get list of Volunteers
    salesforceVolunteersDF = salesforceContactsDF[salesforceContactsDF['AccountId'] == getConfigValue('AccountId','volunteers')]
    salesforceVolunteersDF = salesforceVolunteersDF[['Id', 'Name']]
    salesforceVolunteersDF = salesforceVolunteersDF.reset_index().drop(axis='columns', columns=['index'])
    salesforceVolunteersDF.columns = ['Volunteer_Name__c', 'Volunteer Name']

    # cleanup whitespace in name fields before performing vlookups
    salesforceDonorsDF = cleanupNameWhitespace(salesforceDonorsDF, 'Donor Location Name')
    salesforcePartnersDF = cleanupNameWhitespace(salesforcePartnersDF, 'Recipient Location Name')
    salesforceVolunteersDF = cleanupNameWhitespace(salesforceVolunteersDF, 'Volunteer Name')
    rescuesDF = cleanupNameWhitespace(rescuesDF, 'Donor Location Name')
    rescuesDF = cleanupNameWhitespace(rescuesDF, 'Recipient Location Name')
    rescuesDF['Volunteer Name'] = rescuesDF['Volunteer Name'].astype(str)
    rescuesDF = cleanupNameWhitespace(rescuesDF, 'Volunteer Name')

    # Dataframe merges (vlookups) to add links to rescuesDF
    mergedDF = pd.merge(rescuesDF, salesforceDonorsDF, on='Donor Location Name', how='left')
    mergedDF = pd.merge(mergedDF, salesforcePartnersDF, on='Recipient Location Name', how='left')
    mergedDF = pd.merge(mergedDF, salesforceVolunteersDF, on='Volunteer Name', how='left')

    # Drops unneeded columns for upload
    mergedDF.drop(axis='columns', columns=['Donor Location Name', 'Recipient Location Name', 'Volunteer Name'], inplace=True)

    # Renames columns for upload
    mergedDF.columns=['Rescue_Id__c', 'Day_of_Pickup__c', 'State__c', 'Description__c', 'Food_Type__c', 'Weight__c', 'Rescue_Detail_URL__c', 'Food_Donor_Account_Name__c', 'Agency_Name__c', 'Volunteer_Name__c']

    # upload rescues to Salesforce
    salesforce.executeSalesforceIngestJob('insert', mergedDF.to_csv(index=False), 'Food_Rescue__c', session)

def uploadFoodDonors(accountsDF, session, donorFile):
    """wrapper function to upload Food Donors to Salesforce"""
    # load in donor data from admin tool
    donorsDF = pd.read_csv(donorFile)

    # filter out inactive accounts and unnecessary data columns
    donorsDF = donorsDF[donorsDF['Status'] == 'Active']
    donorsDF = donorsDF[['Donor name', 'Location name', 'Phone', 'Line1', 'Line2', 'City', 'State', 'Zip']]

    # upload Food Donors to Salesforce
    uploadAccounts(accountsDF, donorsDF, getConfigValue('RecordTypeId', 'foodDonor'), session)

def uploadNonprofitPartners(accountsDF, session, nonprofitPartner):
    """wrapper function to upload Nonprofit Partners"""
    # load in partner data from admin tool
    partnersDF = pd.read_csv(nonprofitPartner)

    # filter out inactive accounts and unnecessary data columns
    partnersDF = partnersDF[partnersDF['Status'] == 'Active']
    partnersDF = partnersDF[['Recipient name', 'Location name', 'Phone', 'Line1', 'Line2', 'City', 'State', 'Zip']]

    # upload Nonprofit Partners to Salesforce
    uploadAccounts(accountsDF, partnersDF, getConfigValue('RecordTypeId', 'nonProfitPartner'), session)

def uploadVolunteers(contactsDF, session, volunteerFile):
    """wrapper function to upload Volunteers"""
    # load volunteer data from admin tool
    volunteersDF = pd.read_csv(volunteerFile)

    # filter all Contacts to just get Food Rescue Heroes
    salesforceVolunteersDF = contactsDF[contactsDF['AccountId'] == getConfigValue('AccountId', 'volunteers')]
    salesforceVolunteersDF = salesforceVolunteersDF[['Id', 'Name']]

    # clean up columns
    volunteersDF = volunteersDF[['Name', 'Email', 'Phone', 'Line1', 'Line2', 'City', 'State', 'Zip']]

    #Converts Mailing Address to Salesforce format
    volunteersDF['MailingStreet'] = volunteersDF['Line1'] + (' ' + volunteersDF['Line2'].fillna(''))
    volunteersDF.drop(axis='columns', columns=['Line1','Line2'], inplace=True)
    volunteersDF.columns = ['Name', 'Email', 'Phone', 'MailingStreet', 'MailingCity', 'MailingState', 'MailingPostalCode']

    # cleanup whitespace in the Name fields to increase matches
    volunteersDF = cleanupNameWhitespace(volunteersDF, 'Name')
    salesforceVolunteersDF = cleanupNameWhitespace(salesforceVolunteersDF, 'Name')

    # find all volunteers in the admin tool not in Salesforce
    volunteersNotInSalesforceDF = pd.merge(volunteersDF, salesforceVolunteersDF, on='Name', how='left')
    volunteersNotInSalesforceDF = volunteersNotInSalesforceDF[volunteersNotInSalesforceDF['Id'].isnull()]
    volunteersNotInSalesforceDF = volunteersNotInSalesforceDF.reset_index().drop(axis='columns', columns=['index', 'Id'])

    # add a column to register these Contacts as Volunteers
    volunteersNotInSalesforceDF['AccountId'] = getConfigValue('AccountId', 'volunteers')

    # Formats Phone Datatype
    volunteersNotInSalesforceDF['Phone'] = volunteersNotInSalesforceDF['Phone'].astype('Int64')

    # split Name column into FirstName and LastName columns
    volunteersNotInSalesforceDF['FirstName'] = volunteersNotInSalesforceDF['Name'].apply(lambda x: (' '.join(x.split()[0:-1])))
    volunteersNotInSalesforceDF['LastName'] = volunteersNotInSalesforceDF['Name'].apply(lambda x: (x.split()[-1]))

    # Get rid of unneeded columns
    volunteersNotInSalesforceDF.drop(axis='columns', columns=['Name'], inplace=True)
    volunteersNotInSalesforceDF = volunteersNotInSalesforceDF[['FirstName', 'LastName', 'Email', 'Phone', 'MailingStreet', 'MailingCity', 'MailingState', 'MailingPostalCode', 'AccountId']]

    # upload Volunteers to Salesforce
    salesforce.executeSalesforceIngestJob('insert', volunteersNotInSalesforceDF.to_csv(index=False), 'Contact', session)

def uploadNewFoodRescues(session, rescueFile):
    """wrapper function that finds all new Food Rescues and uploads them to Salesforce"""
    # read in all rescues from admin tool
    rescuesDF = pd.read_csv(rescueFile)

    # read in all rescues currently in Salesforce
    salesforceRescuesDF = salesforce.getDataframeFromSalesforce('SELECT Id, Rescue_Id__c, Food_Type__c, Weight__c FROM Food_Rescue__c', session).drop_duplicates()
    salesforceRescuesDF.columns = ['Id', 'Rescue ID', 'Food Type', 'Weight']

    # find list of rescues not yet in Salesforce
    mergedDF = pd.merge(rescuesDF, salesforceRescuesDF, on=['Rescue ID', 'Food Type', 'Weight'], how='left')
    mergedDF = mergedDF[mergedDF['Id'].isnull()]
    mergedDF = mergedDF.reset_index().drop(axis='columns', columns=['index', 'Id'])

    # upload these new rescues to Salesforce
    uploadFoodRescues(mergedDF, session)

def uploadDataToSalesforce(accountsDF: pd.DataFrame, contactsDF, session, uri, donorFile=None, nonprofitPartner=None, volunteerFile=None, rescueFile=None):
    """master function to upload new data to Salesforce (Accounts, Contacts, Rescues)
    Files are optional
    """
    # first make sure all new Donors, Nonprofits, and Volunteers are uploaded to Salesforce

    # Upload Food Donors
    if donorFile != "" and donorFile is not None:
        print('-----------------------------')
        print('Checking for new Food Donors:')
        print('-----------------------------')
        uploadFoodDonors(accountsDF, session, donorFile)

    # Upload NonProfit Partners
    if nonprofitPartner != "" and nonprofitPartner is not None:
        print('------------------------------------')
        print('Checking for new Nonprofit Partners:')
        print('------------------------------------')
        uploadNonprofitPartners(accountsDF, session, nonprofitPartner)

    # Upload Volunteers
    if volunteerFile != "" and volunteerFile is not None:
        print('----------------------------')
        print('Checking for new Volunteers:')
        print('----------------------------')
        uploadVolunteers(contactsDF, session, volunteerFile)

    # upload new rescue data
    if rescueFile != "" and rescueFile is not None:
        print('-------------------------------')
        print('Uploading all new Food Rescues:')
        print('-------------------------------')
        uploadNewFoodRescues(session, rescueFile)

    print('\nDone!')

def resolveRescueDiscrepancies(session, rescueFile):
    """DOES NOT WORK.

    Intention: Finds the Discrepancies between Salesforce and Admin Tool and then uploads them to SalesForce
    """
    # TODO Parse Discrepancy Dataframe for what needs to update and format it in a nice way
    # TODO Update Records in Salesforce to match what is in the admin site. This will probably require some parsing and string comparison to match up Contacts & Accounts with their SalesforceIDs
    #       It might not, but there is a chance.

    # DiscrepenciesDF is a multi-index dataframe by columns, with Level 0 being the Column Name, and Level 1 being 'Admin' or 'Salesforce' depending on which Datasource the value came from
    discrepanciesDF = compareAdminAndSalesforceRescues(session, rescueFile,1,1)


### WRAPPER FUNCTIONS FOR HELPER TOOLS
def findDuplicateRecords(df, colName):
    """generic function to find duplicate records"""
    duplicatesDF = None
    try:
        duplicatesDF = pd.concat(g for _, g in df.groupby(colName) if len(g) > 1)
    except ValueError:
        duplicatesDF = 'No duplicates were found!'

    return duplicatesDF

def findDuplicateFoodDonors(accountsDF):
    """wrapper function that returns duplicate Food Donor Accounts in Salesforce"""
    # filter all Accounts to just get Food Donors (id: '0123t000000YYv2AAG')
    foodDonorsDF = accountsDF[accountsDF['RecordTypeId'] == getConfigValue('RecordTypeId', 'foodDonor')]

    return findDuplicateRecords(foodDonorsDF, 'Name')

def findDuplicateNonprofitPartners(accountsDF,):
    """wrapper function that returns duplicate Nonprofit Partner Accounts in Salesforce"""
    # filter all Accounts to just get Nonprofit Partners (id: '0123t000000YYv3AAG')
    nonprofitPartnersDF = accountsDF[accountsDF['RecordTypeId'] == getConfigValue('RecordTypeId', 'nonProfitPartner')]

    return findDuplicateRecords(nonprofitPartnersDF, 'Name')

def findDuplicateVolunteers(contactsDF):
    """wrapper function that returns duplicate Volunteer Contacts in Salesforce"""
    # filter all Contacts to just get Food Rescue Heroes (id: '0013t00001teMBwAAM')
    volunteersDF = contactsDF[contactsDF['AccountId'] == getConfigValue('AccountId', 'volunteers')]

    return findDuplicateRecords(volunteersDF, 'Name')

def findIncompleteRescues(rescueFile):
    """function to find old rescues that haven't been marked as completed or canceled"""
    # filter out completed and canceled rescues
    rescuesDF = pd.read_csv(rescueFile)
    rescuesDF = rescuesDF[(rescuesDF['Rescue State'] != 'completed') & (rescuesDF['Rescue State'] != 'canceled')]
    rescuesDF = rescuesDF.reset_index().drop(axis='columns', columns=['index'])

    # convert date strings to date objects for comparison
    for index, _ in rescuesDF.iterrows():
        rescuesDF.at[index, 'Day of Pickup Start'] = datetime.datetime.strptime(rescuesDF.at[index, 'Day of Pickup Start'], '%Y-%m-%d').date()

    # return rescues before today that haven't been completed or canceled
    today = datetime.date.today()
    rescuesDF = rescuesDF[rescuesDF['Day of Pickup Start'] < today]
    return rescuesDF[['Rescue ID', 'Day of Pickup Start', 'Rescue State', 'Rescue Detail URL']].drop_duplicates().reset_index().drop(axis='columns', columns=['index'])

def updateSFRescuesWithComments(session, rescueCommentFile):
    """function to update Salesforce rescues with comments from an excel file"""
    # get rescues from Salesforce
    salesforceRescuesDF = salesforce.getDataframeFromSalesforce('SELECT Id, Rescue_Id__c, Comments__c FROM Food_Rescue__c', session)
    salesforceRescuesDF.columns = ['Id', 'Rescue ID', 'Comments']

    # create rescues DF from comments CSV file
    commentsDF = pd.read_csv(rescueCommentFile)
    commentsDF = commentsDF[['Rescue ID', 'Comments']]

    # filter out rescues that already have associated comments
    salesforceRescuesDF = salesforceRescuesDF.loc[salesforceRescuesDF.Comments.isnull()]
    # drop the comments column (which is all NaN after above filter)
    salesforceRescuesDF = salesforceRescuesDF[['Id', 'Rescue ID']]

    # filter out records that have no comments to upload
    commentsDF = commentsDF.loc[commentsDF.Comments.notnull()]

    # merge two dataframes on Rescue IDs
    mergedCommentsDF = pd.merge(salesforceRescuesDF, commentsDF, on='Rescue ID', how='left')

    # filter so only rows that picked up comments to upload remain
    mergedCommentsDF = mergedCommentsDF[mergedCommentsDF['Comments'].notnull()]

    # drop Rescue ID column, rename Comments column, and update Salesforce with new Comments
    mergedCommentsDF.drop(axis='columns', columns=['Rescue ID'], inplace=True)
    mergedCommentsDF.columns = ['Id', 'Comments__c']
    salesforce.executeSalesforceIngestJob('update', mergedCommentsDF.to_csv(index=False), 'Food_Rescue__c', session)

def findRescueDiscrepancies(session, choice, rescueFile):
    """function to find all food rescue discrepancies between Salesforce and the admin tool
    
    Choice can be two options:
        If choice is `1`, then rescue IDs that are marked completed in Salesforce but not in the admin tool are identified
        If choice is `2`, then rescue IDs that are marked completed in the admin tool but not in Salesforce are identified
    """
    salesforceRescuesDF = salesforce.getDataframeFromSalesforce('SELECT State__c, Food_Type__c, Day_of_Pickup__c, Rescue_Detail_URL__c, Rescue_Id__c FROM Food_Rescue__c', session)
    salesforceRescuesDF['Day_of_Pickup__c'] = pd.to_datetime(salesforceRescuesDF['Day_of_Pickup__c'])

    # only completed rescues
    salesforceRescuesDF = salesforceRescuesDF[salesforceRescuesDF['State__c'] == 'completed']

    # sort by Rescue ID
    salesforceRescuesDF = salesforceRescuesDF.sort_values(by='Rescue_Id__c')

    adminRescuesDF = pd.read_csv(rescueFile)
    adminRescuesDF['Day of Pickup Start'] = pd.to_datetime(adminRescuesDF['Day of Pickup Start'])

    # only completed rescues
    adminRescuesDF = adminRescuesDF[adminRescuesDF['Rescue State'] == 'completed']

    # sort by Rescue ID
    adminRescuesDF = adminRescuesDF.sort_values(by='Rescue ID')

    adminRescueID = adminRescuesDF['Rescue ID']
    salesforceRescueID = salesforceRescuesDF['Rescue_Id__c']

    if choice == 1:
        # print all rescue IDs in Salesforce but not in admin
        res = salesforceRescueID[~salesforceRescueID.isin(adminRescueID)]
        print('All rescue IDs that are marked completed in Salesforce but not in the admin tool:')
    elif choice == 2:
        # print all rescue IDs in the admin tool but not in Salesforce
        res = adminRescueID[~adminRescueID.isin(salesforceRescueID)]
        print('All rescue IDs that are marked completed in the admin tool but not in Salesforce:')

    print('Record Count:')
    print(res.count())
    return res

def compareAdminAndSalesforceRescues(session, rescueFile, onlyCompareRecordsWithPrimaryKey=1,howToShowResults = 1):
    """Function that compares the FoodRescueHero (admin site) rescues that are downloaded
    with the ones already in Salesforce. Results are returned.

    Discrepancies are also returned for the use of other functions.
    It is a multi-index dataframe by columns, with Level 0 being the Column Name, and Level 1 being 'Admin' or 'Salesforce' depending on which Datasource the value came from

    * `onlyCompareRecordsWithPrimaryKey` can be two options:
            * If `onlyCompareRecordsWithPrimaryKey` is `1`, then this will only compare rescues that are in both Admin and Salesforce
            * If `onlyCompareRecordsWithPrimaryKey` is `2`, then this will compare all rescues, regardless of if they are in both Salesforce and Admin Site.
                * Note, this option may have a lot of differences, as a record that is in the Admin site will technically not have anything to compare to,
                and thus will be different than what is in Salesforce

    * `howToShowResults` can be two options:
            * If `howToShowResults` is `1`, then the differences are shown the same line, side by side with eachother
            * If `howToShowResults` is `2`, then the differences are show on different lines, stacked on top of eachother
    """
    # Constants to be used throughout
    # Used Right now as place holders
    ADMIN_SITE_PRIMARY_KEY = 'Food Rescue Primary Key'
    SALESFORCE_SITE_PRIMARY_KEY = 'Food_Rescue_Id__c'

    # Admin Site Rescue File
    adminFoodRescuesDF = pd.read_csv(rescueFile)

    # Salesforce DataFrames
    salesforceRescuesDF = salesforce.getDataframeFromSalesforce(f'SELECT Id, Rescue_Id__c, {SALESFORCE_SITE_PRIMARY_KEY}, State__c, Day_of_Pickup__c, Description__c, Food_Type__c, Weight__c, Rescue_Detail_URL__c, Food_Donor_Account_Name__c, Agency_Name__c, Volunteer_Name__c FROM Food_Rescue__c', session)
    accountsDF = salesforce.getDataframeFromSalesforce('SELECT Id, Name, RecordTypeId FROM Account', session)
    contactDF = salesforce.getDataframeFromSalesforce('SELECT Id, Name, AccountId FROM Contact', session)

    # Filters DataFrames down to only have the correct information
    foodDonorsDF = accountsDF[accountsDF['RecordTypeId'] == getConfigValue('RecordTypeId', 'foodDonor')]
    partnerDF = accountsDF[accountsDF['RecordTypeId'] == getConfigValue('RecordTypeId', 'nonProfitPartner')]
    volunteerDF = contactDF[contactDF['AccountId'] == getConfigValue('AccountId', 'volunteers')]

    # Renames and removes uneeded columns in joined tables
    foodDonorsDF = accountsDF[['Id', 'Name']]
    foodDonorsDF = foodDonorsDF.rename(
        columns={
            'Id': 'Donor_Id',
            'Name': 'Donor_Name'
        }
    )

    partnerDF = accountsDF[['Id', 'Name']]
    partnerDF = partnerDF.rename(
        columns={
            'Id': 'Partner_Id',
            'Name': 'Partner_Name'
        }
    )

    volunteerDF = contactDF[['Id', 'Name']]
    volunteerDF = volunteerDF.rename(
        columns={
            'Id': 'Volunteer_Id',
            'Name': 'Volunteer_Name'
        }
    )

    # Merges additional dataframes from SalesForce to get all data that can be compared
    salesforceRescuesDF = salesforceRescuesDF.merge(
        foodDonorsDF, how='left', left_on='Food_Donor_Account_Name__c', right_on='Donor_Id')
    salesforceRescuesDF = salesforceRescuesDF.merge(
        partnerDF, how='left', left_on='Agency_Name__c', right_on='Partner_Id')
    salesforceRescuesDF = salesforceRescuesDF.merge(
        volunteerDF, how='left', left_on='Volunteer_Name__c', right_on='Volunteer_Id')

    salesforceRescuesDF.drop(['Donor_Id','Partner_Id','Volunteer_Id'], axis=1, inplace=True)

    if onlyCompareRecordsWithPrimaryKey == 1:
        joinType = 'inner'
    elif onlyCompareRecordsWithPrimaryKey == 2:
        joinType = 'outer'
    else:
        print("Incorrect Value for `onlyCompareRecordsWithPrimaryKey`. Assuming option 1: `Iner Join`")
        joinType = 'inner'

    # Full outer joins the Pandas Dataframe
    df = pd.merge(adminFoodRescuesDF, salesforceRescuesDF, how=joinType, left_on=[ADMIN_SITE_PRIMARY_KEY], right_on=[SALESFORCE_SITE_PRIMARY_KEY])

    df.set_index(ADMIN_SITE_PRIMARY_KEY, inplace=True)

    # Converts all blanks to empty strings for comparison
    df['Day of Pickup Start'].fillna('', inplace=True)
    df['Day_of_Pickup__c'].fillna('', inplace=True)
    df['Donor Name'].fillna('', inplace=True)
    df['Food_Donor_Account_Name__c'].fillna('', inplace=True)
    df['Recipient Name'].fillna('', inplace=True)
    df['Agency_Name__c'].fillna('', inplace=True)
    df['Volunteer Name'].fillna('', inplace=True)
    df['Volunteer_Name__c'].fillna('', inplace=True)
    df['Rescue State'].fillna('', inplace=True)
    df['State__c'].fillna('', inplace=True)
    df['Weight'].fillna('', inplace=True)
    df['Weight__c'].fillna('', inplace=True)
    df['Rescue Detail URL'].fillna('', inplace=True)
    df['Rescue_Detail_URL__c'].fillna('', inplace=True)

    # Formats all DateTime Columns the same
    dateColumns = ['Day of Pickup Start','Day_of_Pickup__c']

    for column in dateColumns:
        df[column] = pd.to_datetime(df[column])
        df[column] = df[column].dt.strftime('%m/%d/%Y')

    # Filters Dataframe down to only where there are differences
    filtered = df[
        (df['Day of Pickup Start'] != df['Day_of_Pickup__c']) |
        (df['Donor Name'] != df['Food_Donor_Account_Name__c']) |
        (df['Recipient Name'] != df['Agency_Name__c']) |
        (df['Volunteer Name'] != df['Volunteer_Name__c']) |
        (df['Rescue State'] != df['State__c']) |
        (df['Weight'] != df['Weight__c']) |
        (df['Rescue Detail URL'] != df['Rescue_Detail_URL__c'])
    ]


    # Splits full outer join apart to be able to run a pd.Compare
    adminFoodRescuesDF = filtered[['Rescue ID','Food Type','Description','Day of Pickup Start', 'Donor Name', 'Recipient Name','Volunteer Name', 'Rescue State', 'Weight', 'Rescue Detail URL']]
    salesforceRescuesDF = filtered[['Rescue_Id__c','Food_Type__c','Description__c','Day_of_Pickup__c', 'Donor_Name','Partner_Name', 'Volunteer_Name', 'State__c', 'Weight__c', 'Rescue_Detail_URL__c']]

    # Renames Food Rescue Dataframe columns to match what is in salesforce
    adminFoodRescuesDF = adminFoodRescuesDF.rename(
        columns={
            'Rescue ID': 'Rescue_Id__c',
            'Food Type': 'Food_Type__c',
            'Description': 'Description__c',
            'Day of Pickup Start': 'Day_of_Pickup__c',
            'Donor Name': 'Donor_Name',
            'Recipient Name': 'Partner_Name',
            'Volunteer Name': 'Volunteer_Name',
            'Rescue State': 'State__c',
            'Weight': 'Weight__c',
            'Rescue Detail URL': 'Rescue_Detail_URL__c'
        }
    )

    if howToShowResults == 1:
        # In-line comparison
        comparisonDF = adminFoodRescuesDF.compare(salesforceRescuesDF, align_axis=1, result_names=('Admin', 'Salesforce'))
    elif howToShowResults == 2:
        # Stacked Comparisons
        comparisonDF = adminFoodRescuesDF.compare(salesforceRescuesDF, align_axis=0, result_names=('Admin', 'Salesforce'))
    else:
        print("Choice is not a valid option. Assuming In-line comparison is preferred")
        comparisonDF = adminFoodRescuesDF.compare(salesforceRescuesDF, align_axis=1, result_names=('Admin', 'Salesforce'))

    return comparisonDF

### GENERAL HELPERS
def cleanupNameWhitespace(df, colName):
    """helper function to cleanup whitespace between words in a DF column"""
    for index, _row in df.iterrows():
        df.at[index, colName] = ' '.join(str(df.at[index, colName]).split())
    return df

def getConfigValue(section, key):
    """Gets the value for the section and key within config.ini"""
    configurationFile = "config.ini"
    config = configparser.ConfigParser()
    config.read(configurationFile)
    try:
        configValue = config[section][key]
    except KeyError as exc:
        raise KeyError(f'Unable to find {key} in {section} within {configurationFile}') from exc

    return configValue
