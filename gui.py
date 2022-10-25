from PyQt5.QtWidgets import *
from PyQt5 import QtCore
import functions
import salesforce
from pandas import set_option
import sys

# creating a class that inherits the QDialog class


class Window(QDialog):
    # constructor
    def __init__(self):
        super().__init__()

        self.uri = "https://lastmilefood.my.salesforce.com/services/data/v52.0/jobs/"

        self.whatToDoStr = ""
        self.file1Str = ""
        self.file2Str = ""
        self.file3Str = ""
        self.file4Str = ""

        # set window title
        self.setWindowTitle("Last Mile Food Rescue")

        # add maximize and minimize buttons
        self.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, True)

        # set geometry for the window
        self.setGeometry(500, 500, 500, 500)

        # create forms
        self.createFilePickerForm()

        self.createButtonBox()

        self.createCredentialsForm()

        self.createWhatToDoForm()

        # layout
        mainLayout = QHBoxLayout()

        buttonsAndFilePickerLayout = QVBoxLayout()
        credentialsLayout = QHBoxLayout()

        credentialsLayout.addWidget(self.credentialsGroup)
        buttonsAndFilePickerLayout.addWidget(self.filePickerGroup)
        buttonsAndFilePickerLayout.addWidget(self.whatToDoGroup)
        buttonsAndFilePickerLayout.addWidget(self.buttonBox)

        mainLayout.addLayout(credentialsLayout)
        mainLayout.addLayout(buttonsAndFilePickerLayout)

        self.setLayout(mainLayout)

    def createFilePickerForm(self):
        self.filePickerGroup = QGroupBox("File Picker")

        # creating a form layout
        self.filePickerLayout = QFormLayout()

        self.fileLabel = ""

        # Create Buttons
        self.fileButton1 = QPushButton(self.fileLabel)
        self.fileButton1.clicked.connect(
            lambda: self.filePicker(self.fileButton1))
        self.fileButton1.hide()

        self.fileButton2 = QPushButton(self.fileLabel)
        self.fileButton2.clicked.connect(
            lambda: self.filePicker(self.fileButton2))
        self.fileButton2.hide()

        self.fileButton3 = QPushButton(self.fileLabel)
        self.fileButton3.clicked.connect(
            lambda: self.filePicker(self.fileButton3))
        self.fileButton3.hide()

        self.fileButton4 = QPushButton(self.fileLabel)
        self.fileButton4.clicked.connect(
            lambda: self.filePicker(self.fileButton4))
        self.fileButton4.hide()

        # adding rows
        self.filePickerLayout.addRow(self.fileButton1)
        self.filePickerLayout.addRow(self.fileButton2)
        self.filePickerLayout.addRow(self.fileButton3)
        self.filePickerLayout.addRow(self.fileButton4)

        # setting layout
        self.filePickerGroup.setLayout(self.filePickerLayout)

    def filePicker(self, button: QPushButton = None):
        file, check = QFileDialog.getOpenFileName(None, "Choose a file",
                                                  "", "CSV File (*.csv)")
        if check:
            if button is not None:
                button.setText(self.getFileNameFromPath(file))
            if button == self.fileButton1:
                self.file1Str = file
            elif button == self.fileButton2:
                self.file2Str = file
            elif button == self.fileButton3:
                self.file3Str = file
            elif button == self.fileButton4:
                self.file4Str = file
            return file
        else:
            return ""

    def getFileNameFromPath(self, path):
        # reverse string
        path = path[::-1]
        # substring from last occurrance of / and reverse string again
        return path[0:path.index("/")][::-1]

    def createCredentialsForm(self):
        self.credentialsGroup = QGroupBox("Credentials")

        layout = QFormLayout()

        # add text boxes
        self.emailTextBox = QLineEdit(self)
        self.passwordTextBox = QLineEdit(self)
        self.tokenTextBox = QLineEdit(self)

        self.passwordTextBox.setEchoMode(QLineEdit.Password)
        self.tokenTextBox.setEchoMode(QLineEdit.Password)

        # set minimum widths
        self.emailTextBox.setMinimumWidth(175)
        self.passwordTextBox.setMinimumWidth(175)
        self.tokenTextBox.setMinimumWidth(175)

        layout.addRow(self.tr("&Email:"), self.emailTextBox)
        layout.addRow(self.tr("&Password:"), self.passwordTextBox)
        layout.addRow(self.tr("&Token:"), self.tokenTextBox)

        self.credentialsGroup.setLayout(layout)

    def createWhatToDoForm(self):
        self.whatToDoGroup = QGroupBox("What would you like to do?")

        layout = QFormLayout()

        dataUploadButton = QRadioButton("Salesforce data upload")  # 4 files
        salesforceDupesButton = QRadioButton(
            "Find Salesforce duplicates")  # 0 files
        incompleteDataButton = QRadioButton(
            "Find incomplete rescue data")  # 1 file
        rescueDiscrepanciesButton = QRadioButton(
            "Find rescue discrepancies")  # 1 file
        newSalesforceButton = QRadioButton(
            "Create new Salesforce accounts and contacts")  # 3 files

        layout.addRow(dataUploadButton)
        layout.addRow(salesforceDupesButton)
        layout.addRow(incompleteDataButton)
        layout.addRow(rescueDiscrepanciesButton)
        layout.addRow(newSalesforceButton)

        dataUploadButton.toggled.connect(self.onRadioButtonClick)
        salesforceDupesButton.toggled.connect(self.onRadioButtonClick)
        incompleteDataButton.toggled.connect(self.onRadioButtonClick)
        rescueDiscrepanciesButton.toggled.connect(self.onRadioButtonClick)
        newSalesforceButton.toggled.connect(self.onRadioButtonClick)

        self.whatToDoGroup.setLayout(layout)

    def onRadioButtonClick(self):
        button = self.sender()
        buttonName = button.text()
        
        # update button displays
        if button.isChecked:
            self.file1Str, self.file2Str, self.file3Str, self.file4Str = "", "", "", ""
            if buttonName == "Salesforce data upload":
                self.whatToDoStr = "Salesforce data upload"
                self.fileButton1.show()
                self.fileButton1.setText("Donors report")
                self.fileButton2.show()
                self.fileButton2.setText("Nonprofits report")
                self.fileButton3.show()
                self.fileButton3.setText("Volunteers report")
                self.fileButton4.show()
                self.fileButton4.setText("Rescues report")
            elif buttonName == "Find Salesforce duplicates":
                self.whatToDoStr = "Find Salesforce duplicates"
                self.fileButton1.hide()
                self.fileButton2.hide()
                self.fileButton3.hide()
                self.fileButton4.hide()
            elif buttonName == "Find incomplete rescue data":
                self.whatToDoStr = "Find incomplete rescue data"
                self.fileButton1.show()
                self.fileButton1.setText("Rescues report")
                self.fileButton2.hide()
                self.fileButton3.hide()
                self.fileButton4.hide()
            elif buttonName == "Find rescue discrepancies":
                self.whatToDoStr = "Find rescue discrepancies"
                self.fileButton1.show()
                self.fileButton1.setText("Rescues report")
                self.fileButton2.hide()
                self.fileButton3.hide()
                self.fileButton4.hide()
            elif buttonName == "Create new Salesforce accounts and contacts":
                self.whatToDoStr = "Create new Salesforce accounts and contacts"
                self.fileButton1.show()
                self.fileButton1.setText("Donors report")
                self.fileButton2.show()
                self.fileButton2.setText("Nonprofits report")
                self.fileButton3.show()
                self.fileButton3.setText("Volunteers report")
                self.fileButton4.hide()

    def createButtonBox(self):
        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.endStuff)
        self.buttonBox.rejected.connect(self.reject)

    def checkFilePickersLoaded(self):
        # check that all filepickers have files loaded
        # TODO: maybe check the actual files (ex rescue data) as opposed to the buttons?
        if self.whatToDoStr == "Salesforce data upload":  # 4
            if self.file1Str or self.file2Str or self.file3Str or self.file4Str == "":
                return False
            else:
                return True
        elif self.whatToDoStr == "Find Salesforce duplicates":  # 0
            return True
        elif self.whatToDoStr == "Find incomplete rescue data" or "Find rescue discrepancies":  # 1
            if self.file1Str == "":
                return False
            else:
                return True
        elif self.whatToDoStr == "Create new Salesforce accounts and contacts":  # 3
            if self.file1Str or self.file2Str or self.file3Str == "":
                return False
            else:
                return True

    # TODO: implement
    def checkCredentials(self):
        session = salesforce.loginToSalesforce(self.emailTextBox.text(), self.passwordTextBox.text(), self.tokenTextBox.text())
        return True, session

    def getDataframes(self, session):
        salesforceAccountsDF = functions.getDataframeFromSalesforce('SELECT Id, Name, RecordTypeId FROM Account', session, self.uri) 
        salesforceContactsDF = functions.getDataframeFromSalesforce('SELECT Id, Name, AccountId FROM Contact', session, self.uri)
        return salesforceAccountsDF, salesforceContactsDF

    def endStuff(self):
        if not self.checkFilePickersLoaded():
            self.createDialogBox(
                "ERROR: Files are not loaded. Please load files.")
            return
        validCredentials, session = self.checkCredentials()
        if not validCredentials:
            self.createDialogBox(
                "ERROR: Credentials invalid. Please check your credentials.")
            return
        # run functions
        # TODO: maybe add the dataframes and session as instance variables so we don't have to get them every time?
        # TODO: check order of file strs in args
        if self.whatToDoStr == "Salesforce data upload":  # 4       
            accountsDF, contactsDF = self.getDataframes(session)   
            functions.uploadDataToSalesforce(
                accountsDF,                
                contactsDF,
                session, 
                self.uri,
                self.file1Str,
                self.file2Str,
                self.file3Str,
                self.file4Str
            )
        elif self.whatToDoStr == "Find Salesforce duplicates":  # 0
            accountsDF, contactsDF = self.getDataframes(session)   
            functions.findDuplicateFoodDonors(accountsDF)
            functions.findDuplicateNonprofitPartners(accountsDF)
            functions.findDuplicateVolunteers(contactsDF)
        elif self.whatToDoStr == "Find incomplete rescue data": # 1
            set_option('display.max_colwidth', None)
            functions.findIncompleteRescues(self.file1Str)
        elif self.whatToDoStr == "Find rescue discrepancies":  # 1
            # TODO: need to figure out how to display the print messages
           functions.findRescueDiscrepancies(session, self.uri, 1, self.file1Str)
           functions.findRescueDiscrepancies(session, self.uri, 2, self.file1Str)
        elif self.whatToDoStr == "Create new Salesforce accounts and contacts":  # 3
            accountsDF, contactsDF = self.getDataframes(session)   
            functions.uploadFoodDonors(accountsDF, session, self.uri, self.file1Str)
            functions.uploadNonprofitPartners(accountsDF, session, self.uri, self.file2Str)
            functions.uploadVolunteers(contactsDF, session, self.uri, self.file3Str)
        # TODO: return errors in dialog box (?) use try catch

    def createDialogBox(self, message):
        dialog = QMessageBox.about(self, "Alert", message)
        return dialog


# main method
if __name__ == '__main__':

    # create pyqt5 app
    app = QApplication(sys.argv)

    # create the instance of our Window
    window = Window()

    # showing the window
    window.show()

    # start the app
    sys.exit(app.exec())
