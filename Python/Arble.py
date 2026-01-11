import sys, os, json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget,
    QVBoxLayout, QLineEdit, QToolBar, QFileDialog, QCompleter
)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
from PyQt6.QtCore import QUrl, QStringListModel

HOME_URL = "https://vahint.github.io/arble/"
GAME_URL = "https://vahint.github.io/pong56/"
APP_ICON = "arble_logo.png"
SAVE_FILE = "tabs.json"


class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Arble Browser 🌐")
        self.setWindowIcon(QIcon(APP_ICON))

        self.visited_urls = set()
        self.dark_mode = False

        profile = QWebEngineProfile.defaultProfile()
        profile.setCachePath("browser_cache")
        profile.setPersistentStoragePath("browser_storage")
        profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
        profile.setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36"
        )

        self.tabs = QTabWidget(movable=True, tabsClosable=True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.tabBarDoubleClicked.connect(lambda _: self.add_new_tab())
        self.setCentralWidget(self.tabs)

        navbar = QToolBar()
        self.addToolBar(navbar)

        # Navigation Actions
        for label, callback in [
            ("◀", lambda: self.current_browser().back()),
            ("▶", lambda: self.current_browser().forward()),
            ("🔄", lambda: self.current_browser().reload())
        ]:
            btn = QAction(label, self)
            btn.triggered.connect(callback)
            navbar.addAction(btn)

        # Home, Game, New Tab
        home_btn = QAction("Home", self)
        home_btn.triggered.connect(self.go_home)
        navbar.addAction(home_btn)

        new_tab_btn = QAction("New Tab", self)
        new_tab_btn.setShortcut("Ctrl+T")
        new_tab_btn.triggered.connect(self.add_new_tab)
        navbar.addAction(new_tab_btn)

        game_btn = QAction("Game", self)
        game_btn.setShortcut("Ctrl+G")
        game_btn.triggered.connect(self.go_game)
        navbar.addAction(game_btn)

        # Dark mode toggle
        dark_btn = QAction("🌙 Dark Mode", self)
        dark_btn.triggered.connect(self.toggle_dark_mode)
        navbar.addAction(dark_btn)

        # Screenshot
        shot_btn = QAction("📸 Screenshot", self)
        shot_btn.triggered.connect(self.save_screenshot)
        navbar.addAction(shot_btn)

        self.completer_model = QStringListModel()
        self.completer = QCompleter(self.completer_model)

        self.restore_tabs()

    def add_new_tab(self, url: str = "about:blank", title: str | None = None):
        title = title or "New Tab"
        page = QWebEngineView()

        settings = page.settings()
        wa = QWebEngineSettings.WebAttribute
        settings.setAttribute(wa.JavascriptEnabled, True)
        settings.setAttribute(wa.LocalStorageEnabled, True)
        settings.setAttribute(wa.PluginsEnabled, True)

        def handle_load(ok: bool):
            if not ok:
                page.setHtml("""
                    <!DOCTYPE html><html><head><title>No Internet</title></head>
                    <body style='display:flex;justify-content:center;align-items:center;height:100vh;background:#f0f0f0;font-family:sans-serif;'>
                        <div style='text-align:center;'><h1>No Internet Connection</h1><p>Please check your network and try again.</p></div>
                    </body></html>
                """)

        page.loadFinished.connect(handle_load)
        page.setUrl(QUrl(url))

        address = QLineEdit()
        address.setCompleter(self.completer)
        if url not in ("about:blank", ""):
            address.setText(url)

        def update_url_bar(qurl):
            address.setText(qurl.toString())

        def load_url():
            typed_url = address.text()
            page.setUrl(QUrl(typed_url))
            if typed_url not in self.visited_urls:
                self.visited_urls.add(typed_url)
                self.completer_model.setStringList(list(self.visited_urls))

        address.returnPressed.connect(load_url)
        page.urlChanged.connect(update_url_bar)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(address)
        layout.addWidget(page)

        index = self.tabs.addTab(container, title)
        self.tabs.setCurrentIndex(index)

    def current_browser(self):
        w = self.tabs.currentWidget()
        return w.layout().itemAt(1).widget() if w else None

    def current_url(self):
        browser = self.current_browser()
        return browser.url().toString() if browser else ""

    def go_home(self):
        if (browser := self.current_browser()):
            browser.setUrl(QUrl(HOME_URL))

    def go_game(self):
        if (browser := self.current_browser()):
            browser.setUrl(QUrl(GAME_URL))

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        js = """
            document.documentElement.style.filter = 
              (document.documentElement.style.filter === "invert(1) hue-rotate(180deg)") 
              ? "none" 
              : "invert(1) hue-rotate(180deg)";
        """
        if (browser := self.current_browser()):
            browser.page().runJavaScript(js)

    def save_screenshot(self):
        browser = self.current_browser()
        if browser:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Screenshot", "screenshot.png", "PNG Files (*.png)")
            if file_path:
                browser.grab().save(file_path)

    def closeEvent(self, event):
        self.save_tabs()
        super().closeEvent(event)

    def save_tabs(self):
        urls = []
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            page = widget.layout().itemAt(1).widget()
            urls.append(page.url().toString())
        with open(SAVE_FILE, "w") as f:
            json.dump(urls, f)

    def restore_tabs(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r") as f:
                    urls = json.load(f)
                for url in urls:
                    self.add_new_tab(url)
                return
            except Exception as e:
                print(f"Error loading tabs: {e}")
        self.add_new_tab(HOME_URL, "Home")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Browser()
    window.resize(1200, 800)
    window.show()
    sys.exit(app.exec())
