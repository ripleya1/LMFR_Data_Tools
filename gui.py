from PyQt5.QtWidgets import *
from PyQt5 import QtCore
import sys

# creating a class that inherits the QDialog class
class Window(QDialog):
    # constructor
    def __init__(self):
        super().__init__()

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

        #Create Buttons
        self.fileButton1 = QPushButton(self.fileLabel)
        self.fileButton1.clicked.connect(lambda: self.filePicker(self.fileButton1))
        self.fileButton1.hide()

        self.fileButton2 = QPushButton(self.fileLabel)
        self.fileButton2.clicked.connect(lambda: self.filePicker(self.fileButton2))
        self.fileButton2.hide()

        self.fileButton3 = QPushButton(self.fileLabel)
        self.fileButton3.clicked.connect(lambda: self.filePicker(self.fileButton3))
        self.fileButton3.hide()

        self.fileButton4 = QPushButton(self.fileLabel)
        self.fileButton4.clicked.connect(lambda: self.filePicker(self.fileButton4))
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
            print(file)
            if button is not None:
                button.setText(self.getFileNameFromPath(file))
            return file

    def getFileNameFromPath(self, path):
        path = path[::-1] # reverse string
        return path[0:path.index("/")][::-1] # substring from last occurrance of / and reverse string again

    def createCredentialsForm(self):
        self.credentialsGroup = QGroupBox("Credentials")

        layout = QFormLayout()
        
        emailTextBox = QLineEdit(self)
        passwordTextBox = QLineEdit(self)
        tokenTextBox = QLineEdit(self)

        passwordTextBox.setEchoMode(QLineEdit.Password)
        tokenTextBox.setEchoMode(QLineEdit.Password)

        emailTextBox.setMinimumWidth(175)
        passwordTextBox.setMinimumWidth(175)
        tokenTextBox.setMinimumWidth(175)

        layout.addRow(self.tr("&Email:"), emailTextBox)
        layout.addRow(self.tr("&Password:"), passwordTextBox)
        layout.addRow(self.tr("&Token:"), tokenTextBox)

        self.credentialsGroup.setLayout(layout)

    def createWhatToDoForm(self):
        self.whatToDoGroup = QGroupBox("What would you like to do?")

        layout = QFormLayout()

        dataUploadButton = QRadioButton("Salesforce data upload") # 4 files
        salesforceDupesButton = QRadioButton("Find Salesforce duplicates") # 0 files
        incompleteDataButton = QRadioButton("Find incomplete rescue data") # 1 file
        rescueDiscrepanciesButton = QRadioButton("Find rescue discrepancies") # 1 file
        newSalesforceButton = QRadioButton("Create new Salesforce accounts and contacts") # 3 files

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
        if button.isChecked:
            if buttonName == "Salesforce data upload":
                self.fileButton1.show()
                self.fileButton1.setText("Donors report")
                self.fileButton2.show()
                self.fileButton2.setText("Nonprofits report")
                self.fileButton3.show()
                self.fileButton3.setText("Volunteers report")
                self.fileButton4.show()
                self.fileButton4.setText("Rescues report")
            elif buttonName == "Find Salesforce duplicates":
                self.fileButton1.hide()
                self.fileButton2.hide()
                self.fileButton3.hide()
                self.fileButton4.hide()
            elif buttonName == "Find incomplete rescue data":
                self.fileButton1.show()
                self.fileButton1.setText("Rescues report")
                self.fileButton2.hide()
                self.fileButton3.hide()
                self.fileButton4.hide()
            elif buttonName == "Find rescue discrepancies":
                self.fileButton1.show()
                self.fileButton1.setText("Rescues report")
                self.fileButton2.hide()
                self.fileButton3.hide()
                self.fileButton4.hide()
            elif buttonName == "Create new Salesforce accounts and contacts":
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
        self.buttonBox.accepted.connect(self.close)
        self.buttonBox.rejected.connect(self.reject)

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
