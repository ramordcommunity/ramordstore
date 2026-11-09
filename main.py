# -*- coding: utf-8 -*-
"""
Ramord Store - Official Desktop Hub for Linux
Allows one-click installation, launching, updating, and direct email support for Ramord applications.
Compliant with Obsidian Luxury & Dark Turquoise Design and Ramord System Rules.
Official Contact: ramordhelp@gmail.com
"""

from __future__ import annotations
import os
import shutil
import subprocess
import sys
import urllib.parse
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap, QDesktopServices, QPen
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from i18n import LANGUAGES, get_lang, set_lang, t

OFFICIAL_EMAIL = "ramordhelp@gmail.com"
APP_DIR = Path(__file__).resolve().parent
ICON_PATH = APP_DIR / "assets/ramord-store.svg"

# Theme Palettes: Solid Day & Night Modes (User-Specified)
THEMES = {
    "day": {
        "bg": "#F4F1EA",
        "card": "#EFECE6",
        "card_border": "rgba(26, 51, 40, 0.15)",
        "text": "#2B2A27",
        "dim": "#6B6862",
        "accent": "#1A3328",
        "accent_hover": "#284e3e",
        "accent_text": "#F4F1EA",
        "btn_ghost_bg": "rgba(26, 51, 40, 0.08)",
        "btn_ghost_border": "rgba(26, 51, 40, 0.22)",
        "menu_bg": "#EFECE6",
        "menu_sel": "rgba(26, 51, 40, 0.15)",
    },
    "night": {
        "bg": "#080C0A",
        "card": "#101613",
        "card_border": "rgba(88, 158, 123, 0.20)",
        "text": "#E8E4DA",
        "dim": "#8A948E",
        "accent": "#589E7B",
        "accent_hover": "#6db893",
        "accent_text": "#080C0A",
        "btn_ghost_bg": "rgba(88, 158, 123, 0.10)",
        "btn_ghost_border": "rgba(88, 158, 123, 0.25)",
        "menu_bg": "#101613",
        "menu_sel": "rgba(88, 158, 123, 0.20)",
    }
}

ACTIVE_THEME_KEY = "night"
PRIMARY = THEMES["night"]["accent"]
PRIMARY_HOVER = THEMES["night"]["accent_hover"]
PRIMARY_DARK = THEMES["night"]["accent"]
TEXT = THEMES["night"]["text"]
DIM = THEMES["night"]["dim"]
AMBER = "#f59e0b"
GREEN = "#10b981"

def detect_system_theme() -> str:
    try:
        res = subprocess.run(["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
                             capture_output=True, text=True, timeout=1)
        out = res.stdout.lower()
        if "dark" in out:
            return "night"
        if "light" in out or "default" in out:
            return "day"
    except Exception:
        pass
    return "night"

def build_qss(theme_name: str) -> str:
    t_cfg = THEMES.get(theme_name, THEMES["night"])
    bg = t_cfg["bg"]
    card = t_cfg["card"]
    card_border = t_cfg["card_border"]
    text = t_cfg["text"]
    dim = t_cfg["dim"]
    accent = t_cfg["accent"]
    accent_hover = t_cfg["accent_hover"]
    accent_text = t_cfg["accent_text"]
    btn_ghost_bg = t_cfg["btn_ghost_bg"]
    btn_ghost_border = t_cfg["btn_ghost_border"]
    menu_bg = t_cfg["menu_bg"]
    menu_sel = t_cfg["menu_sel"]

    return f"""
QMainWindow {{
    background: {bg};
    color: {text};
}}
QWidget {{
    color: {text};
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
    font-size: 13px;
}}
QScrollArea {{
    background: transparent;
    border: none;
}}
#card {{
    background-color: {card};
    border: 1px solid {card_border};
    border-radius: 16px;
}}
#card:hover {{
    border: 1px solid {accent};
}}
#title {{
    font-size: 24px;
    font-weight: 700;
    color: {text};
    letter-spacing: -0.5px;
}}
#subtitle {{
    font-size: 13px;
    color: {dim};
}}
#appName {{
    font-size: 17px;
    font-weight: 700;
    color: {text};
}}
#appDesc {{
    font-size: 13px;
    color: {dim};
    line-height: 1.4;
}}
#statusInstalled {{
    color: {accent};
    font-weight: 600;
    font-size: 12px;
}}
#statusNotInstalled {{
    color: {dim};
    font-weight: 600;
    font-size: 12px;
}}
QPushButton {{
    background-color: {btn_ghost_bg};
    border: 1px solid {btn_ghost_border};
    border-radius: 10px;
    padding: 8px 16px;
    font-weight: 600;
    color: {text};
}}
QPushButton:hover {{
    background-color: {accent};
    color: {accent_text};
    border-color: {accent};
}}
QPushButton#btnPrimary {{
    background-color: {accent};
    border: 1px solid {accent};
    color: {accent_text};
    font-weight: 700;
}}
QPushButton#btnPrimary:hover {{
    background-color: {accent_hover};
    border-color: {accent_hover};
}}
QPushButton#btnSupport {{
    background-color: transparent;
    border: 1px solid {card_border};
    color: {dim};
}}
QPushButton#btnSupport:hover {{
    border-color: {accent};
    color: {accent};
    background-color: {btn_ghost_bg};
}}
QComboBox {{
    background-color: {card};
    border: 1px solid {card_border};
    border-radius: 8px;
    padding: 5px 12px;
    color: {text};
}}
QComboBox:hover {{
    border-color: {accent};
}}
QComboBox QAbstractItemView {{
    background-color: {menu_bg};
    border: 1px solid {card_border};
    selection-background-color: {menu_sel};
    selection-color: {accent};
}}
"""



@dataclass
class AppMeta:
    id: str
    name: str
    desc_key: str
    repo_url: str
    bin_name: str
    icon_rel_path: str
    desktop_file: str


APPS: list[AppMeta] = [
    AppMeta(
        id="ramord-link",
        name="Ramord Link",
        desc_key="desc_ramord_link",
        repo_url="https://github.com/ramordcommunity/ramordlink.git",
        bin_name="ramord-link",
        icon_rel_path="/home/ramordser/Projeler/RamordLink/assets/ramord-link.svg",
        desktop_file="ramord-link.desktop",
    ),
    AppMeta(
        id="ramord-cast",
        name="Ramord Cast",
        desc_key="desc_ramord_cast",
        repo_url="https://github.com/ramordcommunity/ramordcast.git",
        bin_name="ramordcast",
        icon_rel_path="/home/ramordser/Projeler/RamordCast/assets/ramordcast.png",
        desktop_file="com.ramord.cast.desktop",
    ),
    AppMeta(
        id="ramord-cad",
        name="Ramord CAD",
        desc_key="desc_ramord_cad",
        repo_url="https://github.com/ramordcommunity/ramordcad.git",
        bin_name="ramordcad",
        icon_rel_path="/home/ramordser/Masaüstü/RamordCAD_AnaSayfa_Logo_512.png",
        desktop_file="ramordcad.desktop",
    ),
]

STYLE = build_qss(ACTIVE_THEME_KEY)


class InstallWorker(QThread):
    finished_signal = Signal(bool, str)

    def __init__(self, app_meta: AppMeta) -> None:
        super().__init__()
        self.meta = app_meta

    def run(self) -> None:
        target_dir = Path.home() / f"Projeler/{self.meta.name.replace(' ', '')}"
        try:
            if not target_dir.exists():
                subprocess.run(
                    ["git", "clone", self.meta.repo_url, str(target_dir)],
                    check=True,
                    capture_output=True,
                )
            else:
                subprocess.run(
                    ["git", "-C", str(target_dir), "pull", "origin", "main"],
                    check=False,
                    capture_output=True,
                )

            install_sh = target_dir / "install.sh"
            if install_sh.exists():
                subprocess.run(["bash", str(install_sh)], check=True, capture_output=True)

            self.finished_signal.emit(True, self.meta.id)
        except Exception as e:
            self.finished_signal.emit(False, str(e))


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(t("app_title"))
        self.setMinimumSize(820, 680)
        self.resize(880, 780)
        if ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(ICON_PATH)))

        self._workers: list[InstallWorker] = []
        self.theme_mode = "auto"
        self._apply_active_theme(self._resolve_theme_key(self.theme_mode))
        self._build_ui()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(28, 24, 28, 28)
        main_layout.setSpacing(18)

        # Header
        header = QHBoxLayout()
        header.setSpacing(14)

        logo_lbl = QLabel()
        if ICON_PATH.exists():
            pm = QPixmap(str(ICON_PATH))
            if not pm.isNull():
                logo_lbl.setPixmap(pm.scaled(52, 52, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_lbl.setFixedSize(52, 52)
        header.addWidget(logo_lbl)

        h_text = QVBoxLayout()
        h_text.setSpacing(2)
        self.title_lbl = QLabel(t("app_title"))
        self.title_lbl.setObjectName("title")
        self.subtitle_lbl = QLabel(t("app_subtitle"))
        self.subtitle_lbl.setObjectName("subtitle")
        h_text.addWidget(self.title_lbl)
        h_text.addWidget(self.subtitle_lbl)
        header.addLayout(h_text)
        header.addStretch()

        # Theme dropdown
        self.theme_combo = QComboBox()
        self.theme_combo.setCursor(Qt.PointingHandCursor)
        self._rebuild_theme_combo()
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        header.addWidget(self.theme_combo)

        # Language dropdown
        self.lang_combo = QComboBox()
        self.lang_combo.setCursor(Qt.PointingHandCursor)
        for code, label in LANGUAGES.items():
            self.lang_combo.addItem(f"{code.upper()} - {label}", code)
        cur_idx = list(LANGUAGES.keys()).index(get_lang())
        self.lang_combo.setCurrentIndex(cur_idx)
        self.lang_combo.currentIndexChanged.connect(self._on_lang_changed)
        header.addWidget(self.lang_combo)

        main_layout.addLayout(header)

        # Scrollable App List
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.apps_layout = QVBoxLayout(scroll_content)
        self.apps_layout.setSpacing(14)
        self.apps_layout.setContentsMargins(0, 0, 0, 0)

        self._app_cards: dict[str, dict] = {}

        for meta in APPS:
            card = self._create_app_card(meta)
            self.apps_layout.addWidget(card)

        # Direct Support & Feedback Card at the bottom
        support_card = self._create_support_card()
        self.apps_layout.addWidget(support_card)
        self.apps_layout.addStretch()

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

    def _create_app_card(self, meta: AppMeta) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        top_row = QHBoxLayout()
        top_row.setSpacing(14)

        icon_lbl = QLabel()
        if Path(meta.icon_rel_path).exists():
            pm = QPixmap(meta.icon_rel_path)
            if not pm.isNull():
                icon_lbl.setPixmap(pm.scaled(46, 46, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon_lbl.setFixedSize(46, 46)
        top_row.addWidget(icon_lbl)

        info_col = QVBoxLayout()
        info_col.setSpacing(3)
        name_lbl = QLabel(meta.name)
        name_lbl.setObjectName("appName")
        status_lbl = QLabel()
        info_col.addWidget(name_lbl)
        info_col.addWidget(status_lbl)
        top_row.addLayout(info_col)
        top_row.addStretch()

        # Action Buttons
        btn_action = QPushButton()
        btn_action.setObjectName("btnPrimary")
        btn_action.setCursor(Qt.PointingHandCursor)
        top_row.addWidget(btn_action)

        btn_launch = QPushButton(t("btn_launch"))
        btn_launch.setCursor(Qt.PointingHandCursor)
        top_row.addWidget(btn_launch)

        btn_mail = QPushButton(t("btn_support_app"))
        btn_mail.setObjectName("btnSupport")
        btn_mail.setCursor(Qt.PointingHandCursor)
        btn_mail.clicked.connect(lambda _=False, m=meta: self._open_email_for_app(m))
        top_row.addWidget(btn_mail)

        layout.addLayout(top_row)

        desc_lbl = QLabel(t(meta.desc_key))
        desc_lbl.setObjectName("appDesc")
        desc_lbl.setWordWrap(True)
        layout.addWidget(desc_lbl)

        self._app_cards[meta.id] = {
            "meta": meta,
            "status_lbl": status_lbl,
            "desc_lbl": desc_lbl,
            "btn_action": btn_action,
            "btn_launch": btn_launch,
            "btn_mail": btn_mail,
        }

        self._update_card_state(meta.id)
        return card

    def _create_support_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        self.support_title = QLabel(t("support_title"))
        self.support_title.setObjectName("appName")
        self.support_desc = QLabel(t("support_desc"))
        self.support_desc.setObjectName("appDesc")
        self.support_desc.setWordWrap(True)
        layout.addWidget(self.support_title)
        layout.addWidget(self.support_desc)

        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(12)

        self.email_display = QLabel(f"<b>{OFFICIAL_EMAIL}</b>")
        self.email_display.setStyleSheet(f"color: {PRIMARY}; font-size: 15px;")
        bottom_row.addWidget(self.email_display)
        bottom_row.addStretch()

        self.btn_open_mail = QPushButton(t("btn_send_email"))
        self.btn_open_mail.setObjectName("btnPrimary")
        self.btn_open_mail.setCursor(Qt.PointingHandCursor)
        self.btn_open_mail.clicked.connect(lambda: self._open_email_for_app(None))
        bottom_row.addWidget(self.btn_open_mail)

        self.btn_copy_mail = QPushButton(t("btn_copy_email"))
        self.btn_copy_mail.setCursor(Qt.PointingHandCursor)
        self.btn_copy_mail.clicked.connect(self._copy_email)
        bottom_row.addWidget(self.btn_copy_mail)

        layout.addLayout(bottom_row)
        return card

    def _is_app_installed(self, meta: AppMeta) -> bool:
        if shutil.which(meta.bin_name):
            return True
        desktop = Path.home() / f".local/share/applications/{meta.desktop_file}"
        return desktop.exists()

    def _update_card_state(self, app_id: str) -> None:
        c = self._app_cards.get(app_id)
        if not c:
            return
        meta: AppMeta = c["meta"]
        installed = self._is_app_installed(meta)

        if installed:
            c["status_lbl"].setText(f"● {t('status_installed')}")
            c["status_lbl"].setObjectName("statusInstalled")
            c["status_lbl"].setStyleSheet(f"color: {GREEN}; font-weight: 600;")
            c["btn_action"].setText(t("btn_update"))
            c["btn_action"].setObjectName("")
            c["btn_launch"].setVisible(True)
            c["btn_launch"].clicked.disconnect() if c["btn_launch"].receivers(c["btn_launch"].clicked) > 0 else None
            c["btn_launch"].clicked.connect(lambda _=False, m=meta: self._launch_app(m))
        else:
            c["status_lbl"].setText(f"○ {t('status_not_installed')}")
            c["status_lbl"].setObjectName("statusNotInstalled")
            c["status_lbl"].setStyleSheet(f"color: {DIM}; font-weight: 600;")
            c["btn_action"].setText(t("btn_install"))
            c["btn_action"].setObjectName("btnPrimary")
            c["btn_launch"].setVisible(False)

        c["btn_action"].clicked.disconnect() if c["btn_action"].receivers(c["btn_action"].clicked) > 0 else None
        c["btn_action"].clicked.connect(lambda _=False, m=meta: self._install_app(m))

    def _install_app(self, meta: AppMeta) -> None:
        c = self._app_cards.get(meta.id)
        if c:
            c["btn_action"].setEnabled(False)
            c["btn_action"].setText(t("installing"))

        worker = InstallWorker(meta)
        worker.finished_signal.connect(self._on_install_finished)
        self._workers.append(worker)
        worker.start()

    def _on_install_finished(self, success: bool, msg: str) -> None:
        if success:
            self._update_card_state(msg)
            QMessageBox.information(self, t("app_title"), t("op_success"))
        else:
            QMessageBox.warning(self, t("app_title"), f"{t('op_failed')}\n{msg}")
            for meta in APPS:
                self._update_card_state(meta.id)

    def _launch_app(self, meta: AppMeta) -> None:
        try:
            subprocess.Popen([meta.bin_name], start_new_session=True)
        except Exception:
            # Fallback to python runner if in local projects
            proj_dir = Path.home() / f"Projeler/{meta.name.replace(' ', '')}"
            if (proj_dir / "main.py").exists():
                subprocess.Popen(["python3", str(proj_dir / "main.py")], start_new_session=True)

    def _open_email_for_app(self, meta: AppMeta | None) -> None:
        subject = f"Support: {meta.name}" if meta else "Support Request - Ramord Ecosystem"
        body = f"Hello Ramord Support Team,\n\nI need assistance with {meta.name if meta else 'an application'}:\n"
        mailto = f"mailto:{OFFICIAL_EMAIL}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
        QDesktopServices.openUrl(mailto)

    def _copy_email(self) -> None:
        QApplication.clipboard().setText(OFFICIAL_EMAIL)
        self.btn_copy_mail.setText(t("copied"))
        QTimer.singleShot(2000, lambda: self.btn_copy_mail.setText(t("btn_copy_email")))

    def _resolve_theme_key(self, mode: str) -> str:
        if mode in ("day", "night"):
            return mode
        return detect_system_theme()

    def _apply_active_theme(self, theme_key: str) -> None:
        global ACTIVE_THEME_KEY, PRIMARY, PRIMARY_HOVER, PRIMARY_DARK, TEXT, DIM
        ACTIVE_THEME_KEY = theme_key
        t_cfg = THEMES.get(theme_key, THEMES["night"])
        PRIMARY = t_cfg["accent"]
        PRIMARY_HOVER = t_cfg["accent_hover"]
        PRIMARY_DARK = t_cfg["accent"]
        TEXT = t_cfg["text"]
        DIM = t_cfg["dim"]

        app = QApplication.instance()
        if app is not None:
            app.setStyleSheet(build_qss(theme_key))
        if hasattr(self, "email_display"):
            self.email_display.setStyleSheet(f"color: {PRIMARY}; font-size: 15px;")

    def _rebuild_theme_combo(self) -> None:
        if not hasattr(self, "theme_combo"):
            return
        self.theme_combo.blockSignals(True)
        self.theme_combo.clear()
        self.theme_combo.addItem(f"{t('theme_auto')}", "auto")
        self.theme_combo.addItem(f"{t('theme_day')}", "day")
        self.theme_combo.addItem(f"{t('theme_night')}", "night")
        idx = {"auto": 0, "day": 1, "night": 2}.get(self.theme_mode, 0)
        self.theme_combo.setCurrentIndex(idx)
        self.theme_combo.blockSignals(False)

    def _on_theme_changed(self, index: int) -> None:
        mode = self.theme_combo.itemData(index)
        if mode in ("auto", "day", "night"):
            self.theme_mode = mode
            self._apply_active_theme(self._resolve_theme_key(mode))

    def _on_lang_changed(self, index: int) -> None:
        code = self.lang_combo.itemData(index)
        if code in LANGUAGES:
            set_lang(code)
            self._update_all_texts()

    def _update_all_texts(self) -> None:
        self.setWindowTitle(t("app_title"))
        self.title_lbl.setText(t("app_title"))
        self.subtitle_lbl.setText(t("app_subtitle"))
        self.support_title.setText(t("support_title"))
        self.support_desc.setText(t("support_desc"))
        self.btn_open_mail.setText(t("btn_send_email"))
        self.btn_copy_mail.setText(t("btn_copy_email"))
        self._rebuild_theme_combo()

        for app_id, c in self._app_cards.items():
            meta: AppMeta = c["meta"]
            c["desc_lbl"].setText(t(meta.desc_key))
            c["btn_launch"].setText(t("btn_launch"))
            c["btn_mail"].setText(t("btn_support_app"))
            self._update_card_state(app_id)


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("ramord-store")
    app.setDesktopFileName("ramord-store")
    if ICON_PATH.exists():
        app.setWindowIcon(QIcon(str(ICON_PATH)))
    app.setStyleSheet(STYLE)

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
