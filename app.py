import sys
from PyQt5.QtWidgets import QGroupBox, QSpinBox, QComboBox, QDialogButtonBox, QVBoxLayout, QFormLayout, QPushButton, QLineEdit, QFileDialog, QApplication, QDialog

# creating a class
# that inherits the QDialog class


class Window(QDialog):

    # constructor
    def __init__(self):
        super().__init__()

        # setting window title
        self.setWindowTitle("Last Mile Food Rescue")

        # setting geometry to the window
        self.setGeometry(100, 100, 300, 400)

        # creating a dialog button for ok and cancel
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        # adding action when form is accepted
        self.button_box.accepted.connect(self.close)

        # adding action when form is rejected
        self.button_box.rejected.connect(self.reject)

        # creating a vertical layout
        main_layout = QVBoxLayout()

        # adding form group box to the layout
        main_layout.addWidget(self.create_file_picker_form())

        # adding button box to the layout
        main_layout.addWidget(self.button_box)

        # setting lay out
        self.setLayout(main_layout)

    def create_file_picker_form(self):
        """Creates and retuns the Box for the File Picker
        """
        # Creates one QGroupBox
        file_picker_group = QGroupBox("File Picker")

        # creating a form layout
        layout = QFormLayout()

        # Create Puttons
        file_button_1 = QPushButton("Choose File")
        self.file1_path = QLineEdit()
        file_button_1.clicked.connect(
            lambda: self.file_picker(self.file1_path)
        )

        file_button_2 = QPushButton("Choose File")
        self.file2_path = QLineEdit()
        file_button_2.clicked.connect(
            lambda: self.file_picker(self.file2_path)
        )

        file_button_3 = QPushButton("Choose File")
        self.file3_path = QLineEdit()
        file_button_3.clicked.connect(
            lambda: self.file_picker(self.file3_path)
        )

        # adding rows
        layout.addRow(self.file1_path, file_button_1)

        layout.addRow(self.file2_path, file_button_2)

        layout.addRow(self.file3_path, file_button_3)

        # setting layout
        file_picker_group.setLayout(layout)

        return file_picker_group

    def file_picker(self, q_line_edit: QLineEdit = None):
        """Prompts the user for a file input, and
        sets the QLineEdit's text to the file, if it is not none"""
        file, check = QFileDialog.getOpenFileName(None, "Choose a file",
                                                  "", "CSV File (*.csv)")
        if check:
            print(file)

            if q_line_edit is not None:
                q_line_edit.setText(file)


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
