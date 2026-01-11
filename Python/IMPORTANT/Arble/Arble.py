import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget,
    QVBoxLayout, QLineEdit, QToolBar
)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
from PyQt6.QtCore import QUrl

HOME_URL = "https://vahint.github.io/arble/"
GAME_URL = "https://vahint.github.io/pong56/"
APP_ICON = "arble_logo.png"


class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Arble Browser 🌐")
        self.setWindowIcon(QIcon(APP_ICON))

        # — Shared WebEngine Profile with cache, storage, UA, cookies —
        profile = QWebEngineProfile.defaultProfile()
        profile.setCachePath("browser_cache")
        profile.setPersistentStoragePath("browser_storage")
        profile.setPersistentCookiesPolicy(
            QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies
        )
        profile.setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36"
        )

        # ---------- Tabs ----------
        self.tabs = QTabWidget(movable=True, tabsClosable=True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.tabBarDoubleClicked.connect(lambda _: self.add_new_tab())
        self.setCentralWidget(self.tabs)

        # ---------- Toolbar ----------
        navbar = QToolBar()
        self.addToolBar(navbar)

        home_btn = QAction("Home", self)
        home_btn.triggered.connect(self.go_home)
        navbar.addAction(home_btn)

        new_tab_btn = QAction("New Tab", self)
        new_tab_btn.setShortcut("Ctrl+T")
        new_tab_btn.triggered.connect(lambda: self.add_new_tab())
        navbar.addAction(new_tab_btn)

        game_btn = QAction("Game", self)
        game_btn.setShortcut("Ctrl+G")
        game_btn.triggered.connect(self.go_game)
        navbar.addAction(game_btn)

        # First tab = Home
        self.add_new_tab(HOME_URL, "Home")

    def add_new_tab(self, url: str = "about:blank", title: str | None = None):
        title = title or "New Tab"
        page = QWebEngineView()

        # Enable JS and storage via the WebAttribute enum
        settings = page.settings()
        wa = QWebEngineSettings.WebAttribute
        settings.setAttribute(wa.JavascriptEnabled, True)
        settings.setAttribute(wa.LocalStorageEnabled, True)
        settings.setAttribute(wa.PluginsEnabled, True)

        # Handle load failures
        def handle_load(ok: bool):
            if not ok:
                page.setHtml(
                    "<!DOCTYPE html>"
                    "<html><head><title>No Internet</title></head>"
                    "<body style='"
                      "display:flex;"
                      "justify-content:center;"
                      "align-items:center;"
                      "height:100vh;"
                      "background:#f0f0f0;"
                      "font-family:sans-serif;"
                    "'>"
                      "<div style='text-align:center;'>"
                        "<h1>No Internet Connection</h1>"
                        "<p>Please check your network and try again.</p>"
                      "</div>"
                    "</body></html>"
                )

        page.loadFinished.connect(handle_load)
        page.setUrl(QUrl(url))

        address = QLineEdit()
        if url not in ("about:blank", ""):
            address.setText(url)
        address.returnPressed.connect(lambda: page.setUrl(QUrl(address.text())))
        page.urlChanged.connect(lambda q: address.setText(q.toString()))

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(address)
        layout.addWidget(page)

        index = self.tabs.addTab(container, title)
        self.tabs.setCurrentIndex(index)

    def current_browser(self):
        w = self.tabs.currentWidget()
        return w.layout().itemAt(1).widget() if w else None

    def go_home(self):
        if (browser := self.current_browser()):
            browser.setUrl(QUrl(HOME_URL))

    def go_game(self):
        if (browser := self.current_browser()):
            browser.setUrl(QUrl(GAME_URL))

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Browser()
    window.resize(1200, 800)
    window.show()
    sys.exit(app.exec())
