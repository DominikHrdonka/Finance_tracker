import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QRadioButton, QPushButton, QLineEdit, QLabel

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        # Radio Buttony
        self.radio1 = QRadioButton("Možnost 1")
        self.radio2 = QRadioButton("Možnost 2")
        layout.addWidget(self.radio1)
        layout.addWidget(self.radio2)
        
        # Textové pole
        self.textbox = QLineEdit(self)
        layout.addWidget(self.textbox)
        
        # Tlačítko
        self.button = QPushButton("Submit", self)
        self.button.clicked.connect(self.onSubmit)
        layout.addWidget(self.button)
        
        # Štítek na výstup
        self.label = QLabel("Výstup se zobrazí zde.")
        layout.addWidget(self.label)
        
        self.setLayout(layout)
        self.setWindowTitle("RadioButton a Submit")
        self.show()

    def onSubmit(self):
        selected_option = ""
        if self.radio1.isChecked():
            selected_option = "Možnost 1"
        elif self.radio2.isChecked():
            selected_option = "Možnost 2"
        
        text = self.textbox.text()
        self.label.setText(f"Vybráno: {selected_option}, Zapsaný text: {text}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())