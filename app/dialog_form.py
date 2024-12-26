from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLineEdit,
    QCheckBox,
    QComboBox,
    QPushButton,
    QLabel,
)


class CustomDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Custom Input Dialog")

        # Layout
        layout = QVBoxLayout()

        # Input Field
        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("Enter some dependencies")
        layout.addWidget(QLabel("Input dependencies:"))
        layout.addWidget(self.input_field)

        # Checkbox
        self.checkbox = QCheckBox("upgrade", self)
        layout.addWidget(self.checkbox)
        self.verbose = QCheckBox("verbose", self)
        layout.addWidget(self.verbose)

        # ComboBox (Select Box)
        self.select_box = QComboBox(self)
        index_url1 = "https://pypi.tuna.tsinghua.edu.cn/simple"
        index_url2 = "https://pypi.mirrors.ustc.edu.cn/simple"
        index_url3 = "https://pypi.douban.com/simple/"
        index_url4 = "https://mirrors.aliyun.com/pypi/simple/"
        index_url5 = "https://download.pytorch.org/whl/cpu"
        index_url6 = "https://download.pytorch.org/whl/cu118"
        index_url7 = "https://download.pytorch.org/whl/cu121"
        self.select_box.addItems(
            [
                "",
                index_url1,
                index_url2,
                index_url3,
                index_url4,
                index_url5,
                index_url6,
                index_url7,
            ]
        )
        layout.addWidget(QLabel("Select a index-url:"))
        layout.addWidget(self.select_box)

        # OK and Cancel Buttons
        self.ok_button = QPushButton("OK", self)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.reject)

        layout.addWidget(self.ok_button)
        layout.addWidget(self.cancel_button)

        # Set the layout
        self.setLayout(layout)

    def get_values(self):
        """Retrieve values from the dialog."""
        input_text = self.input_field.text()
        is_checked = self.checkbox.isChecked()
        is_verbose = self.verbose.isChecked()
        selected_option = self.select_box.currentText()
        return input_text, is_checked, is_verbose, selected_option
