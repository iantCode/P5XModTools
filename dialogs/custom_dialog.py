import webbrowser
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel

class CustomDialog(QDialog): 
    def __init__(self, parent=None, title: str = "", content: str = "", url: str = ""):
        super().__init__(parent)
        self.url = url

        self.setWindowTitle(title)

        buttons = QDialogButtonBox.StandardButton.Ok
        self.button_box = QDialogButtonBox(buttons)
        if url != "":
            buttons = QDialogButtonBox.StandardButton.Open | QDialogButtonBox.StandardButton.Ok
            self.button_box = QDialogButtonBox(buttons)
            self.button_box.button(QDialogButtonBox.StandardButton.Open).clicked.connect(self.open_link)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel(content)
        self.layout.addWidget(message)
        self.layout.addWidget(self.button_box) 
        self.setLayout(self.layout)
    
    def open_link(self):
        webbrowser.open(self.url, new=0, autoraise=True)