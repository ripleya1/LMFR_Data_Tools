from PyQt5.QtWidgets import *
import sys

# creating a class
# that inherits the QDialog class


class Window(QDialog):

    file_1 = "File 1"
    file_2 = "File 2"
    file_3 = "File 3"

    # constructor
    def __init__(self):
        super().__init__()

        # setting window title
        self.setWindowTitle("Last Mile Food Rescue")

        # setting geometry to the window
        self.setGeometry(100, 100, 300, 400)

        # creating a group box
        self.file_picker_group = QGroupBox("File Picker")

        # creating spin box to select age
        self.ageSpinBar = QSpinBox()

        # creating combo box to select degree
        self.degreeComboBox = QComboBox()

        # adding items to the combo box
        self.degreeComboBox.addItems(["BTech", "MTech", "PhD"])

        # calling the method that create the form
        self.create_file_picker_form()

        # creating a dialog button for ok and cancel
        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        # adding action when form is accepted
        self.buttonBox.accepted.connect(self.getInfo)

        # adding action when form is rejected
        self.buttonBox.rejected.connect(self.reject)

        # creating a vertical layout
        mainLayout = QVBoxLayout()

        # adding form group box to the layout
        mainLayout.addWidget(self.file_picker_group)

        # adding button box to the layout
        mainLayout.addWidget(self.buttonBox)

        # setting lay out
        self.setLayout(mainLayout)

    # get info method called when form is accepted
    def getInfo(self):

        # printing the form information
        print("Person Name : {0}".format(self.nameLineEdit.text()))
        print("Degree : {0}".format(self.degreeComboBox.currentText()))
        print("Age : {0}".format(self.ageSpinBar.text()))

        # closing the window
        self.close()

    # creat form method
    def create_file_picker_form(self):

        # creating a form layout
        layout = QFormLayout()

        #Create Puttons
        file_button_1 = QPushButton(self.file_1)
        file_button_1.clicked.connect(self.file_picker)
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
