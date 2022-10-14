from PyQt5.QtWidgets import *
from PyQt5 import QtCore
import sys

# https://doc.qt.io/qtforpython/overviews/layout.html 

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
        self.create_file_picker_form()

        self.create_button_box()

        self.create_credentials_form()

        self.create_what_to_do_form()

        # layout
        mainLayout = QHBoxLayout()

        buttonsAndFilePickerLayout = QVBoxLayout()
        credentialsLayout = QHBoxLayout()

        credentialsLayout.addWidget(self.credentials_group)
        buttonsAndFilePickerLayout.addWidget(self.file_picker_group)
        buttonsAndFilePickerLayout.addWidget(self.what_to_do_group)
        buttonsAndFilePickerLayout.addWidget(self.buttonBox)

        mainLayout.addLayout(credentialsLayout)
        mainLayout.addLayout(buttonsAndFilePickerLayout)

        # mainLayout.addWidget(self.buttonBox)

        self.setLayout(mainLayout)

    def create_file_picker_form(self):
        self.file_picker_group = QGroupBox("File Picker")

        # creating a form layout
        layout = QFormLayout()

        self.file1Path = "Choose a file"
        self.file2Path = "Choose a file"
        self.file3Path = "Choose a file"

        #Create Buttons
        file_button_1 = QPushButton(self.file1Path)
        file_button_1.clicked.connect(
            lambda: self.file_picker(self.file1Path)
        )

        file_button_2 = QPushButton(self.file_2)
        file_button_2.clicked.connect(self.file_picker)
        file_button_3 = QPushButton(self.file_3)
        file_button_3.clicked.connect(self.file_picker)

        # adding rows
        layout.addRow(file_button_1)
        layout.addRow(file_button_2)
        layout.addRow(file_button_3)

        # setting layout
        self.file_picker_group.setLayout(layout)

    def file_picker(self):
        file, check = QFileDialog.getOpenFileName(None, "Choose a file",
                                                "", "CSV File (*.csv)")
        if check:
            print(file)
            return file

    def create_credentials_form(self):
        self.credentials_group = QGroupBox("Credentials")

        layout = QFormLayout()
        
        email_text_box = QLineEdit(self)
        password_text_box = QLineEdit(self)
        token_text_box = QLineEdit(self)

        password_text_box.setEchoMode(QLineEdit.Password)
        token_text_box.setEchoMode(QLineEdit.Password)

        layout.addRow(self.tr("&Email:"), email_text_box)
        layout.addRow(self.tr("&Password:"), password_text_box)
        layout.addRow(self.tr("&Token:"), token_text_box)

        self.credentials_group.setLayout(layout)

    def create_what_to_do_form(self):
        self.what_to_do_group = QGroupBox("What would you like to do?")

        layout = QFormLayout()

        data_upload_button = QRadioButton("Salesforce data upload")
        salesforce_dupes_button = QRadioButton("Find Salesforce duplicates")
        incomplete_data_button = QRadioButton("Find incomplete rescue data")
        new_salesforce_button = QRadioButton("Create new Salesforce accounts and contacts")

        layout.addRow(data_upload_button)
        layout.addRow(salesforce_dupes_button)
        layout.addRow(incomplete_data_button)
        layout.addRow(new_salesforce_button)

        data_upload_button.toggled.connect(self.onRadioButtonClick)
        salesforce_dupes_button.toggled.connect(self.onRadioButtonClick)
        incomplete_data_button.toggled.connect(self.onRadioButtonClick)
        new_salesforce_button.toggled.connect(self.onRadioButtonClick)

        self.what_to_do_group.setLayout(layout)

    def onRadioButtonClick(self):
        button = self.sender()
        if button.isChecked:
            print(button.text())

    def create_button_box(self):
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
