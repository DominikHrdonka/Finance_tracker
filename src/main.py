import sys
import keyboard
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QRadioButton, QPushButton, QLineEdit, QLabel

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        # Radio Buttony
        self.radio1 = QRadioButton("Přijem")
        self.radio2 = QRadioButton("Výdaj")
        layout.addWidget(self.radio1)
        layout.addWidget(self.radio2)
        
        # Textové pole
        self.textbox = QLineEdit(self)
        layout.addWidget(self.textbox)
        keyboard.add_hotkey('enter', self.onSubmit)
        
        # Tlačítko
        self.button = QPushButton("Enter", self)
        self.button.clicked.connect(self.onSubmit)
        layout.addWidget(self.button)
        
        # Štítek na výstup
        self.label = QLabel("Výstup se zobrazí zde.")
        layout.addWidget(self.label)
        
        self.setLayout(layout)
        self.setWindowTitle("Finance Tracker")
        self.show()

    def onSubmit(self):
        selected_option = ""
        if self.radio1.isChecked():
            selected_option = "Příjem"
            text = self.textbox.text()
            self.label.setText(f"Na.vaš učet bylo připsáno: {text}\nNa vašem učtu je zůstatek: ")
        if self.radio2.isChecked():
            selected_option = "Výdaj"
            text = self.textbox.text()
            self.label.setText(f"Z vašeho učtu bylo vydáno: {text}\nNa vašem učtu je zůstatek:")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
