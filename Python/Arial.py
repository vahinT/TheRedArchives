import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLineEdit, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl

class LightweightBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Arble")
        self.setGeometry(100, 100, 900, 600)

        self.browser = QWebEngineView()
        from PyQt6.QtCore import QUrl  # Add this import if not already there

        self.browser.setUrl(QUrl("https://www.google.com"))


        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.returnPressed.connect(self.search)

        layout = QVBoxLayout()
        layout.addWidget(self.search_bar)
        layout.addWidget(self.browser)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def search(self):
        query = self.search_bar.text()
        if query:
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            self.browser.setUrl(QUrl(url))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LightweightBrowser()
    window.show()
    sys.exit(app.exec())
