from PyQt5.QtWidgets import *
from PyQt5 import QtCore
import functions
import salesforce
from pandas import set_option
import sys
import requests

# creating a class that inherits the QDialog class


class Window(QDialog):
    # constructor
    def __init__(self):
        super().__init__()

        self.uri = "https://lastmilefood.my.salesforce.com/services/data/v52.0/jobs/"

        self.whatToDoStr = ""
        self.rescuesFileStr = ""
        self.donorsFileStr = ""
        self.nonprofitsFileStr = ""
        self.volunteersFileStr = ""

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
        self.rescuesButton = QPushButton(self.fileLabel)
        self.rescuesButton.clicked.connect(
            lambda: self.filePicker(self.rescuesButton))
        self.rescuesButton.hide()

        self.donorsButton = QPushButton(self.fileLabel)
        self.donorsButton.clicked.connect(
            lambda: self.filePicker(self.donorsButton))
        self.donorsButton.hide()

        self.nonprofitsButton = QPushButton(self.fileLabel)
        self.nonprofitsButton.clicked.connect(
            lambda: self.filePicker(self.nonprofitsButton))
        self.nonprofitsButton.hide()

        self.volunteersButton = QPushButton(self.fileLabel)
        self.volunteersButton.clicked.connect(
            lambda: self.filePicker(self.volunteersButton))
        self.volunteersButton.hide()

        # adding rows
        self.filePickerLayout.addRow(self.rescuesButton)
        self.filePickerLayout.addRow(self.donorsButton)
        self.filePickerLayout.addRow(self.nonprofitsButton)
        self.filePickerLayout.addRow(self.volunteersButton)

        # setting layout
        self.filePickerGroup.setLayout(self.filePickerLayout)

    def filePicker(self, button: QPushButton = None):
        file, check = QFileDialog.getOpenFileName(None, "Choose a file",
                                                  "", "CSV File (*.csv)")
        if check:
            if button is not None:
                button.setText(self.getFileNameFromPath(file))
            if button == self.rescuesButton:
                self.rescuesFileStr = file
            elif button == self.donorsButton:
                self.donorsFileStr = file
            elif button == self.nonprofitsButton:
                self.nonprofitsFileStr = file
            elif button == self.volunteersButton:
                self.volunteersFileStr = file
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
        self.emailTextBox.setMinimumWidth(200)
        self.passwordTextBox.setMinimumWidth(200)
        self.tokenTextBox.setMinimumWidth(200)

        layout.addRow(self.tr("&Email:"), self.emailTextBox)
        layout.addRow(self.tr("&Password:"), self.passwordTextBox)
        layout.addRow(self.tr("&Token:"), self.tokenTextBox)

        self.credentialsGroup.setLayout(layout)

    def createWhatToDoForm(self):
        self.whatToDoGroup = QGroupBox("What would you like to do?")

        layout = QFormLayout()

        dataUploadButton = QRadioButton("Salesforce data upload")
        salesforceDupesButton = QRadioButton(
            "Find Salesforce duplicates")
        incompleteDataButton = QRadioButton(
            "Find incomplete rescue data")
        rescueDiscrepanciesButton = QRadioButton(
            "Find rescue discrepancies")
        newSalesforceButton = QRadioButton(
            "Create new Salesforce accounts and contacts")

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
            # filename on button box persists
            if buttonName == "Salesforce data upload":
                self.whatToDoStr = "Salesforce data upload"
                self.updateButtonText(
                    [self.donorsButton, self.nonprofitsButton, self.volunteersButton, self.rescuesButton])
                self.donorsButton.show()
                self.nonprofitsButton.show()
                self.volunteersButton.show()
                self.rescuesButton.show()
            elif buttonName == "Find Salesforce duplicates":
                self.whatToDoStr = "Find Salesforce duplicates"
                self.rescuesButton.hide()
                self.donorsButton.hide()
                self.nonprofitsButton.hide()
                self.volunteersButton.hide()
            elif buttonName == "Find incomplete rescue data":
                self.whatToDoStr = "Find incomplete rescue data"
                self.updateButtonText([self.rescuesButton])
                self.rescuesButton.show()
                self.donorsButton.hide()
                self.nonprofitsButton.hide()
                self.volunteersButton.hide()
            elif buttonName == "Find rescue discrepancies":
                self.whatToDoStr = "Find rescue discrepancies"
                self.updateButtonText([self.rescuesButton])
                self.rescuesButton.show()
                self.donorsButton.hide()
                self.nonprofitsButton.hide()
                self.volunteersButton.hide()
            elif buttonName == "Create new Salesforce accounts and contacts":
                self.whatToDoStr = "Create new Salesforce accounts and contacts"
                self.updateButtonText(
                    [self.donorsButton, self.nonprofitsButton, self.volunteersButton])
                self.rescuesButton.hide()
                self.donorsButton.show()
                self.nonprofitsButton.show()
                self.volunteersButton.show()

    def updateButtonText(self, buttons):
        for button in buttons:
            if button == self.rescuesButton:
                if self.rescuesFileStr == "":
                    self.rescuesButton.setText("Rescues report")
                else:
                    self.rescuesButton.setText(
                        self.getFileNameFromPath(self.rescuesFileStr))
            elif button == self.donorsButton:
                if self.donorsFileStr == "":
                    self.donorsButton.setText("Donors report")
                else:
                    self.donorsButton.setText(
                        self.getFileNameFromPath(self.rescuesFileStr))
            elif button == self.nonprofitsButton:
                if self.nonprofitsFileStr == "":
                    self.nonprofitsButton.setText("Nonprofits report")
                else:
                    self.nonprofitsButton.setText(
                        self.getFileNameFromPath(self.rescuesFileStr))
            elif button == self.volunteersButton:
                if self.volunteersFileStr == "":
                    self.volunteersButton.setText("Volunteers report")
                else:
                    self.volunteersButton.setText(
                        self.getFileNameFromPath(self.rescuesFileStr))

    def createButtonBox(self):
        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.endStuff)
        self.buttonBox.rejected.connect(self.reject)

    # checks that all filepickers have the appropriate files loaded
    def checkFilePickersLoaded(self):
        if self.whatToDoStr == "Salesforce data upload":  # 4
            if self.rescuesFileStr or self.donorsFileStr or self.nonprofitsFileStr or self.volunteersFileStr == "":
                return False
            else:
                return True
        elif self.whatToDoStr == "Find Salesforce duplicates":  # 0
            return True
        elif self.whatToDoStr == "Find incomplete rescue data" or "Find rescue discrepancies":  # 1
            if self.rescuesFileStr == "":
                return False
            else:
                return True
        elif self.whatToDoStr == "Create new Salesforce accounts and contacts":  # 3
            if self.rescuesFileStr or self.donorsFileStr or self.nonprofitsFileStr == "":
                return False
            else:
                return True

    def checkCredentials(self):
        try:
            session = salesforce.loginToSalesforce(self.emailTextBox.text(
            ), self.passwordTextBox.text(), self.tokenTextBox.text())
            return True, session
        except:
            self.createDialogBox(
                "ERROR: Credentials invalid. Please check your credentials.")
            return False, requests.Session()

    def getDataframes(self, session):
        accountsDF = salesforce.getDataframeFromSalesforce(
            'SELECT Id, Name, RecordTypeId FROM Account', session, self.uri)
        contactsDF = salesforce.getDataframeFromSalesforce(
            'SELECT Id, Name, AccountId FROM Contact', session, self.uri)
        return accountsDF, contactsDF

    def endStuff(self):
        if not self.checkFilePickersLoaded():
            self.createDialogBox(
                "ERROR: Files are not loaded. Please load files.")
            return
        # run functions
        # only checks credentials if the function selected uses them
        if self.whatToDoStr == "Salesforce data upload":
            credentialsValidated, session = self.checkCredentials()
            if credentialsValidated:
                accountsDF, contactsDF = self.getDataframes(session)
                functions.uploadDataToSalesforce(
                    accountsDF,
                    contactsDF,
                    session,
                    self.uri,
                    self.donorsFileStr,
                    self.nonprofitsFileStr,
                    self.volunteersFileStr,
                    self.rescuesFileStr
                )
        elif self.whatToDoStr == "Find Salesforce duplicates":
            credentialsValidated, session = self.checkCredentials()
            if credentialsValidated:
                accountsDF, contactsDF = self.getDataframes(session)
                functions.findDuplicateFoodDonors(accountsDF)
                functions.findDuplicateNonprofitPartners(accountsDF)
                functions.findDuplicateVolunteers(contactsDF)
        elif self.whatToDoStr == "Find incomplete rescue data":
            set_option('display.max_colwidth', None)
            functions.findIncompleteRescues(self.rescuesFileStr)
        elif self.whatToDoStr == "Find rescue discrepancies":
            credentialsValidated, session = self.checkCredentials()
            if credentialsValidated:
                # TODO: need to figure out how to display the print messages
                functions.findRescueDiscrepancies(
                    session, self.uri, 1, self.rescuesFileStr)
                functions.findRescueDiscrepancies(
                    session, self.uri, 2, self.rescuesFileStr)
        elif self.whatToDoStr == "Create new Salesforce accounts and contacts":
            credentialsValidated, session = self.checkCredentials()
            if credentialsValidated:
                accountsDF, contactsDF = self.getDataframes(session)
                functions.uploadFoodDonors(
                    accountsDF, session, self.uri, self.donorsFileStr)
                functions.uploadNonprofitPartners(
                    accountsDF, session, self.uri, self.nonprofitsFileStr)
                functions.uploadVolunteers(
                    contactsDF, session, self.uri, self.volunteersFileStr)
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
