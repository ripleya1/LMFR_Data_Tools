from PyQt5.QtWidgets import *
from PyQt5 import QtCore
import functions
import salesforce
import sys
import requests

# to generate exe run: pyinstaller --onefile --windowed gui.py

class Window(QDialog):
    # constructor
    def __init__(self):
        super().__init__()

        self.selectedOption = ""
        self.rescuesFileStr = ""
        self.donorsFileStr = ""
        self.nonprofitsFileStr = ""
        self.volunteersFileStr = ""

        # set window title
        self.setWindowTitle("Last Mile Food Rescue")

        # add maximize and minimize buttons
        self.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, True)

        # set default size for the window
        self.setGeometry(500, 500, 500, 500)

        # create forms
        self.createFilePickerForm()
        self.createButtonBox()
        self.createCredentialsForm()
        self.createWhatToDoForm()

        # layouts
        mainLayout = QHBoxLayout()
        # right and left sides
        buttonsAndFilePickerLayout = QVBoxLayout()
        credentialsLayout = QHBoxLayout()
        # add widgets to layouts
        credentialsLayout.addWidget(self.credentialsGroup)
        buttonsAndFilePickerLayout.addWidget(self.filePickerGroup)
        buttonsAndFilePickerLayout.addWidget(self.whatToDoGroup)
        buttonsAndFilePickerLayout.addWidget(self.buttonBox)
        # add right and left side layouts to main layout
        mainLayout.addLayout(credentialsLayout)
        mainLayout.addLayout(buttonsAndFilePickerLayout)

        self.setLayout(mainLayout)

    # function that creates the file picker form
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

        # adding rows to layout
        self.filePickerLayout.addRow(self.rescuesButton)
        self.filePickerLayout.addRow(self.donorsButton)
        self.filePickerLayout.addRow(self.nonprofitsButton)
        self.filePickerLayout.addRow(self.volunteersButton)

        self.filePickerGroup.setLayout(self.filePickerLayout)

    # helper function that opens a file picker and updates the file path instance variables
    def filePicker(self, button: QPushButton = None):
        file, check = QFileDialog.getOpenFileName(None, "Choose a file",
                                                  "", "CSV File (*.csv)")
        # check if a file was selected
        if check:
            # change button text to the (extracted) file name
            if button is not None:
                button.setText(self.getFileNameFromPath(file))
            # update instance variables
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

    # helper function that extracts the file name from a full file path
    def getFileNameFromPath(self, path):
        # reverse string
        path = path[::-1]
        # substring from last occurrance of / and reverse string again
        return path[0:path.index("/")][::-1]

    # function that creates the credentials form
    def createCredentialsForm(self):
        self.credentialsGroup = QGroupBox("Credentials")

        layout = QFormLayout()

        # create text boxes
        self.emailTextBox = QLineEdit(self)
        self.passwordTextBox = QLineEdit(self)
        self.tokenTextBox = QLineEdit(self)

        # makes the password text boxes have the little dots
        self.passwordTextBox.setEchoMode(QLineEdit.Password)
        self.tokenTextBox.setEchoMode(QLineEdit.Password)

        # set minimum widths
        self.emailTextBox.setMinimumWidth(200)
        self.passwordTextBox.setMinimumWidth(200)
        self.tokenTextBox.setMinimumWidth(200)

        # add each text box
        layout.addRow(self.tr("&Email:"), self.emailTextBox)
        layout.addRow(self.tr("&Password:"), self.passwordTextBox)
        layout.addRow(self.tr("&Token:"), self.tokenTextBox)

        self.credentialsGroup.setLayout(layout)

    # function that creates the what to do form
    def createWhatToDoForm(self):
        self.whatToDoGroup = QGroupBox("What would you like to do?")

        layout = QFormLayout()

        dataUploadButton = QRadioButton("Salesforce data upload (one or many files)")
        salesforceDupesButton = QRadioButton(
            "Find Salesforce duplicates")
        incompleteDataButton = QRadioButton(
            "Find incomplete rescue data")
        rescueDiscrepanciesButton = QRadioButton(
            "Find rescue discrepancies")
        resolveRescueDiscrepanciesButton = QRadioButton(
            "Find Changes between Salesforce Data and Admin Site Data",
        )
        
        # Disables the resolveRescueDiscrepanciesButton as it is not confirmed to work yet
        resolveRescueDiscrepanciesButton.setEnabled(False)

        newSalesforceButton = QRadioButton(
            "Create new Salesforce accounts and contacts")

        # add tooltips
        dataUploadButton.setToolTip("Upload data to Salesforce.")
        salesforceDupesButton.setToolTip("Find duplicates in Salesforce.\nSends the results to multiple text files in the current folder.\nDoes not create text files if no duplicates were found.")
        incompleteDataButton.setToolTip("Find incomplete rescue data.\nSends the results to a text file in the current folder.\nDoes not create a text file if no incomplete data was found.")
        rescueDiscrepanciesButton.setToolTip("Find rescue discrepancies.\nSends the results to multiple text files in the current folder.\nDoes not create text files if no discrepancies were found.")
        resolveRescueDiscrepanciesButton.setToolTip("Function disabled as it has not yet been implemented.")
        newSalesforceButton.setToolTip("Create a new Salesforce account with contacts.")

        # add buttons
        layout.addRow(dataUploadButton)
        layout.addRow(salesforceDupesButton)
        layout.addRow(incompleteDataButton)
        layout.addRow(rescueDiscrepanciesButton)
        layout.addRow(resolveRescueDiscrepanciesButton)
        layout.addRow(newSalesforceButton)

        # set button triggers
        dataUploadButton.toggled.connect(self.onRadioButtonClick)
        salesforceDupesButton.toggled.connect(self.onRadioButtonClick)
        incompleteDataButton.toggled.connect(self.onRadioButtonClick)
        rescueDiscrepanciesButton.toggled.connect(self.onRadioButtonClick)
        resolveRescueDiscrepanciesButton.toggled.connect(self.onRadioButtonClick)
        newSalesforceButton.toggled.connect(self.onRadioButtonClick)

        self.whatToDoGroup.setLayout(layout)

    # helper function that determines what happens when a radio button is clicked
    def onRadioButtonClick(self):
        button = self.sender()
        # text displayed on button
        buttonName = button.text()

        # update button displays
        if button.isChecked:
            # update instance variables based on which button is clicked
            # filename on button box persists
            if buttonName == "Salesforce data upload (one or many files)":
                self.selectedOption = "Salesforce data upload"
                self.updateButtonText(
                    [self.donorsButton, self.nonprofitsButton, self.volunteersButton, self.rescuesButton])
                self.donorsButton.show()
                self.nonprofitsButton.show()
                self.volunteersButton.show()
                self.rescuesButton.show()
            elif buttonName == "Find Salesforce duplicates":
                self.selectedOption = "Find Salesforce duplicates"
                self.rescuesButton.hide()
                self.donorsButton.hide()
                self.nonprofitsButton.hide()
                self.volunteersButton.hide()
            elif buttonName == "Find incomplete rescue data":
                self.selectedOption = "Find incomplete rescue data"
                self.updateButtonText([self.rescuesButton])
                self.rescuesButton.show()
                self.donorsButton.hide()
                self.nonprofitsButton.hide()
                self.volunteersButton.hide()
            elif buttonName == "Find rescue discrepancies":
                self.selectedOption = "Find rescue discrepancies"
                self.updateButtonText([self.rescuesButton])
                self.rescuesButton.show()
                self.donorsButton.hide()
                self.nonprofitsButton.hide()
                self.volunteersButton.hide()
            elif buttonName == "Find Changes between Salesforce Data and Admin Site Data":
                self.selectedOption = "Find Changes between Salesforce Data and Admin Site Data"
                self.updateButtonText([self.rescuesButton])
                self.rescuesButton.show()
                self.donorsButton.hide()
                self.nonprofitsButton.hide()
                self.volunteersButton.hide()
            elif buttonName == "Create new Salesforce accounts and contacts":
                self.selectedOption = "Create new Salesforce accounts and contacts"
                self.updateButtonText(
                    [self.donorsButton, self.nonprofitsButton, self.volunteersButton])
                self.rescuesButton.hide()
                self.donorsButton.show()
                self.nonprofitsButton.show()
                self.volunteersButton.show()

    # helper function that updates the button text based on whether or not it has a file attached to it
    def updateButtonText(self, buttons):
        # update every button that is passed in
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

    # function that creates a button box
    def createButtonBox(self):
        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        # "Ok"
        self.buttonBox.accepted.connect(self.runFunctions)
        # "Cancel"
        self.buttonBox.rejected.connect(self.reject)

    # function that checks that filepickers have all of the appropriate files loaded
    def checkFilePickersLoaded(self):
        if self.selectedOption == "Salesforce data upload":  # 4
            if self.rescuesFileStr == "" and self.donorsFileStr == "" and self.nonprofitsFileStr == "" and self.volunteersFileStr == "":
                return False
            else:
                return True
        elif self.selectedOption == "Find Salesforce duplicates":  # 0 files
            return True
        elif self.selectedOption == "Find incomplete rescue data" or self.selectedOption == "Find rescue discrepancies" or self.selectedOption == "Find Changes between Salesforce Data and Admin Site Data":  # 1
            if self.rescuesFileStr == "":
                return False
            else:
                return True
        elif self.selectedOption == "Create new Salesforce accounts and contacts":  # 3
            if self.rescuesFileStr == "" or self.donorsFileStr == "" or self.nonprofitsFileStr == "":
                return False
            else:
                return True

    # helper function that checks salesforce credentials and returns a requests.Session()
    # creates an informative dialog box and returns false in the case of an error
    def checkCredentials(self):
        try:
            session = salesforce.loginToSalesforce(self.emailTextBox.text(
            ), self.passwordTextBox.text(), self.tokenTextBox.text())
            return True, session
        except:
            self.createErrorDialogBox(
                "Credentials invalid. Please check your credentials.")
            return False, requests.Session()

    # helper function that gets the accounts and contacts dataframes from salesforce
    def getDataframes(self, session):
        accountsDF = salesforce.getDataframeFromSalesforce(
            'SELECT Id, Name, RecordTypeId FROM Account', session)
        contactsDF = salesforce.getDataframeFromSalesforce(
            'SELECT Id, Name, AccountId FROM Contact', session)
        return accountsDF, contactsDF

    # the meat
    # function that does the stuff we're actually trying to do
    def runFunctions(self):
        if not self.checkFilePickersLoaded():
            self.createErrorDialogBox(
                "Files are not loaded. Please load files.")
            return
        # run functions for the selected option
        # only checks credentials if the option selected uses them
        # uses try except to create an error dialog box if an error is encountered
        if self.selectedOption == "Salesforce data upload":
            credentialsValidated, session = self.checkCredentials()
            if credentialsValidated:
                try:
                    accountsDF, contactsDF = self.getDataframes(session)
                    functions.uploadDataToSalesforce(
                        accountsDF,
                        contactsDF,
                        session,
                        self.donorsFileStr,
                        self.nonprofitsFileStr,
                        self.volunteersFileStr,
                        self.rescuesFileStr
                    )
                    # create a success dialog box if an exception is not encountered
                    self.createSuccessDialogBox("Data successfully uploaded!")
                except Exception as err:
                    self.createErrorDialogBox(err)
        elif self.selectedOption == "Find Salesforce duplicates":
            credentialsValidated, session = self.checkCredentials()
            if credentialsValidated:
                try:
                    accountsDF, contactsDF = self.getDataframes(session)
                    foodDonorsDF = functions.findDuplicateFoodDonors(accountsDF)
                    dialogBoxStr = ""
                    # does not create txt files if the dataframe is empty
                    if not self.dfIsEmpty(foodDonorsDF):
                        self.convertDFToTxt(foodDonorsDF, "duplicate_food_donors")
                        dialogBoxStr += "duplicate_food_donors.txt\n"
                    nonprofitDF = functions.findDuplicateNonprofitPartners(accountsDF)
                    if not self.dfIsEmpty(nonprofitDF):
                        self.convertDFToTxt(nonprofitDF, "duplicate_nonprofits")
                        dialogBoxStr += "duplicate_nonprofits.txt\n"
                    volunteersDF = functions.findDuplicateVolunteers(contactsDF)
                    if not self.dfIsEmpty(volunteersDF):
                        self.convertDFToTxt(volunteersDF, "duplicate_volunteers")
                        dialogBoxStr += "duplicate_volunteers.txt\n"
                    self.createSuccessDialogBox("Processing successful! Result is in text files in the current folder (if there were any duplicates). The following files were created:\n" + dialogBoxStr)
                except Exception as err:
                    self.createErrorDialogBox(err)
        elif self.selectedOption == "Find incomplete rescue data":
            try:
                data = functions.findIncompleteRescues(self.rescuesFileStr)
                dialogBoxStr = ""
            except ValueError as err:
                self.createErrorDialogBox("Double check the csv column names.\n" + str(err))
            except Exception as err:
                self.createErrorDialogBox(err)
            except:
                self.createErrorDialogBox("Unspecified error.")
            else:
                if not self.dfIsEmpty(data):
                    self.convertDFToTxt(data, "incomplete_rescue_data")
                    dialogBoxStr += "incomplete_rescue_data.txt"
                self.createSuccessDialogBox("Processing successful! Result is in a text file in the current folder (if there were any incomplete rescues). The following files were created:\n" + dialogBoxStr)
        elif self.selectedOption == "Find rescue discrepancies":
            credentialsValidated, session = self.checkCredentials()
            if credentialsValidated:
                try:
                    dialogBoxStr = ""
                    choice1DF = functions.findRescueDiscrepancies(
                        session, 1, self.rescuesFileStr)
                    choice2DF = functions.findRescueDiscrepancies(
                        session, 2, self.rescuesFileStr)
                    if not self.dfIsEmpty(choice1DF):
                        self.convertDFToTxt(choice1DF, "rescue_discrepancies_not_in_admin")
                        dialogBoxStr += "rescue_discrepancies_not_in_admin.txt\n"
                    if not self.dfIsEmpty(choice2DF):
                        self.convertDFToTxt(choice2DF, "rescue_discrepancies_not_in_salesforce")
                        dialogBoxStr += "rescue_discrepancies_not_in_salesforce.txt\n"
                    self.createSuccessDialogBox("Processing successful! Result is in multiple text files in the current folder (if there were any rescue discrepancies). The following files were created:\n" + dialogBoxStr)
                except Exception as err:
                    self.createDialogBox("Error:\n" + str(err))
        elif self.selectedOption == "Find Changes between Salesforce Data and Admin Site Data":
            credentialsValidated, session = self.checkCredentials()
            if credentialsValidated:
                try:
                    dialogBoxStr = ""
                    differenceDF = functions.compareAdminAndSalesforceRescues(session, self.rescuesFileStr,onlyCompareRecordsWithPrimaryKey=1 ,howToShowResults=1)

                    if not self.dfIsEmpty(differenceDF):
                        self.convertDFToTxt(differenceDF, "difference_admin_salesforce")
                        dialogBoxStr += "difference_admin_salesforce.txt\n"
                    self.createSuccessDialogBox("Processing successful! Result is in a text file in the current folder (if there were any rescue discrepancies). The following files were created:\n" + dialogBoxStr)

                except Exception as err:
                    self.createDialogBox("Error:\n" + str(err))
        elif self.selectedOption == "Create new Salesforce accounts and contacts":
            credentialsValidated, session = self.checkCredentials()
            if credentialsValidated:
                try:
                    accountsDF, contactsDF = self.getDataframes(session)
                    functions.uploadFoodDonors(
                        accountsDF, session, self.donorsFileStr)
                    functions.uploadNonprofitPartners(
                        accountsDF, session, self.nonprofitsFileStr)
                    functions.uploadVolunteers(
                        contactsDF, session, self.volunteersFileStr)
                    self.createSuccessDialogBox("Successfully uploaded files!")
                except Exception as err:
                    self.createErrorDialogBox(err)

    # helper function that checks if a pandas dataframe is empty
    # https://stackoverflow.com/a/54009974
    def dfIsEmpty(self, df):
        return len(df.columns) == 0

    # helper function that creates a txt file from a pandas dataframe (or part of one)
    # https://stackoverflow.com/questions/41428539/data-frame-to-file-txt-python
    def convertDFToTxt(self, df, fileName):
        fileName += ".txt"
        df.to_csv(fileName, sep = "\t", index = False)

    # helper function that creates a dialog box specifically for errors
    def createErrorDialogBox(self, error):
        dialog = QMessageBox.about(self, "Error", str(error))
        return dialog

    # helper function that creates a dialog box specifically for success messages
    def createSuccessDialogBox(self, successMessage):
        dialog = QMessageBox.about(self, "Success!", str(successMessage))
        return dialog

    # helper function that creates a generic dialog box
    def createDialogBox(self, message):
        dialog = QMessageBox.about(self, "Alert", str(message))
        return dialog

# actually running the GUI
app = QApplication(sys.argv)

window = Window()
window.show()

# start the app
sys.exit(app.exec())