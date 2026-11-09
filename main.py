#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ramord Store - Official Desktop Hub for Linux
Allows one-click installation, launching, updating, and direct email support for Ramord applications.
Built with GTK4 & Libadwaita (Apple-like modern unified window and header bar), 6 Languages.
Official Contact: ramordhelp@gmail.com
"""

import os
import sys
import shutil
import signal
import subprocess
import threading
import urllib.parse
import html
from dataclasses import dataclass
from pathlib import Path

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Gio, Gdk

from i18n import LANGUAGES, get_lang, set_lang, t

OFFICIAL_EMAIL = "ramordhelp@gmail.com"
APP_DIR = Path(__file__).resolve().parent
ICON_PATH = APP_DIR / "assets/ramord-store.svg"


def detect_system_language():
    raw = os.environ.get('LC_ALL') or os.environ.get('LC_MESSAGES') or os.environ.get('LANG') or 'en'
    code = raw.split('.')[0].split('_')[0].lower()
    return code if code in LANGUAGES else 'en'


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


class RamordStoreWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Ramord Store")
        self.set_default_size(780, 840)
        self.set_icon_name("ramord-store")

        self.current_lang = detect_system_language()
        set_lang(self.current_lang)

        self.theme_mode = "auto"
        self.css_provider = None
        self._app_rows = {}
        self._installing_apps = set()

        self._build_ui()
        self._apply_theme()
        self._refresh_texts()

    def _detect_system_theme(self) -> str:
        try:
            sm = Adw.StyleManager.get_default()
            return "night" if sm.get_dark() else "day"
        except Exception:
            return "night"

    def _resolve_theme_key(self) -> str:
        if self.theme_mode in ("day", "night"):
            return self.theme_mode
        return self._detect_system_theme()

    def _apply_theme(self):
        """Applies solid Day (#F4F1EA/#EFECE6/#2B2A27/#1A3328) or Night (#080C0A/#101613/#E8E4DA/#589E7B) theme."""
        active_key = self._resolve_theme_key()
        is_day = (active_key == "day")

        if is_day:
            bg = "#F4F1EA"
            card = "#EFECE6"
            card_border = "rgba(26, 51, 40, 0.15)"
            text = "#2B2A27"
            dim = "#6B6862"
            accent = "#1A3328"
            accent_hover = "#284e3e"
            accent_text = "#F4F1EA"
            header_bg = "#EAE5DC"
        else:
            bg = "#080C0A"
            card = "#101613"
            card_border = "rgba(88, 158, 123, 0.20)"
            text = "#E8E4DA"
            dim = "#8A948E"
            accent = "#589E7B"
            accent_hover = "#6db893"
            accent_text = "#080C0A"
            header_bg = "#0d1310"

        css_text = f"""
        window, window.background {{
            border-radius: 16px;
            background: {bg};
            color: {text};
        }}

        headerbar {{
            background: {header_bg};
            border-bottom: 1px solid {card_border};
            color: {text};
            border-top-left-radius: 16px;
            border-top-right-radius: 16px;
        }}

        preferencesgroup > box {{
            background: {card};
            border: 1px solid {card_border};
            border-radius: 14px;
            padding: 4px;
            color: {text};
        }}

        .boxed-list {{
            background: {card};
            border: 1px solid {card_border};
            border-radius: 14px;
            color: {text};
        }}

        .boxed-list row {{
            border-bottom: 1px solid {card_border};
            color: {text};
        }}

        .suggested-action {{
            background: {accent};
            color: {accent_text};
            font-weight: 700;
            border: none;
        }}

        .suggested-action:hover {{
            background: {accent_hover};
        }}

        .destructive-action {{
            background: #ef4444;
            color: #ffffff;
            font-weight: 700;
            border: none;
        }}

        popover contents, popover .view, popover listview {{
            background-color: {card};
            color: {text};
            border-radius: 12px;
            border: 1px solid {card_border};
            padding: 6px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }}

        popover listview row {{
            padding: 10px 14px;
            border-radius: 8px;
            margin: 2px 0;
            min-height: 38px;
            color: {text};
        }}

        popover listview row:selected, popover listview row:hover {{
            background: {card_border};
            color: {accent};
        }}
        """

        if self.css_provider is not None:
            Gtk.StyleContext.remove_provider_for_display(
                Gdk.Display.get_default(),
                self.css_provider
            )

        self.css_provider = Gtk.CssProvider()
        self.css_provider.load_from_data(css_text.encode('utf-8'))
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            self.css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def _build_ui(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_content(main_box)

        # Header Bar
        self.header_bar = Adw.HeaderBar()
        main_box.append(self.header_bar)

        # Language Selector
        self.lang_btn = Gtk.MenuButton()
        self.lang_btn.add_css_class("flat")
        self.lang_btn.set_tooltip_text("Language / Dil")

        lang_btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        lang_icon = Gtk.Image.new_from_icon_name("preferences-desktop-locale-symbolic")
        self.lang_btn_label = Gtk.Label(label=LANGUAGES.get(self.current_lang, "English"))
        self.lang_btn_label.add_css_class("heading")
        lang_btn_box.append(lang_icon)
        lang_btn_box.append(self.lang_btn_label)
        self.lang_btn.set_child(lang_btn_box)

        lang_popover = Gtk.Popover()
        lang_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        lang_box.set_margin_top(8)
        lang_box.set_margin_bottom(8)
        lang_box.set_margin_start(8)
        lang_box.set_margin_end(8)

        for code, label in LANGUAGES.items():
            btn = Gtk.Button(label=label)
            btn.add_css_class("flat")
            btn.connect("clicked", self._on_change_language, code, lang_popover)
            lang_box.append(btn)

        lang_popover.set_child(lang_box)
        self.lang_btn.set_popover(lang_popover)
        self.header_bar.pack_start(self.lang_btn)

        # Theme Switcher
        self.theme_btn = Gtk.MenuButton()
        self.theme_btn.add_css_class("flat")
        self.theme_btn.set_tooltip_text("Theme / Tema")
        theme_btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        theme_icon = Gtk.Image.new_from_icon_name("display-brightness-symbolic")
        self.theme_btn_label = Gtk.Label(label=t(f"theme_{self.theme_mode}", self.current_lang))
        self.theme_btn_label.add_css_class("heading")
        theme_btn_box.append(theme_icon)
        theme_btn_box.append(self.theme_btn_label)
        self.theme_btn.set_child(theme_btn_box)

        theme_popover = Gtk.Popover()
        theme_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        theme_box.set_margin_top(8)
        theme_box.set_margin_bottom(8)
        theme_box.set_margin_start(8)
        theme_box.set_margin_end(8)

        for m_key in ("auto", "day", "night"):
            m_btn = Gtk.Button(label=t(f"theme_{m_key}", self.current_lang))
            m_btn.add_css_class("flat")
            m_btn.connect("clicked", self._on_change_theme, m_key, theme_popover)
            theme_box.append(m_btn)

        theme_popover.set_child(theme_box)
        self.theme_btn.set_popover(theme_popover)
        self.header_bar.pack_start(self.theme_btn)

        # Scrolled Window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)
        main_box.append(scrolled)

        # Clamp Container
        clamp = Adw.Clamp()
        clamp.set_maximum_size(720)
        clamp.set_tightening_threshold(560)
        scrolled.set_child(clamp)

        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        content_box.set_margin_top(24)
        content_box.set_margin_bottom(32)
        content_box.set_margin_start(16)
        content_box.set_margin_end(16)
        clamp.set_child(content_box)

        # 1. Header Banner
        self.banner_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.banner_box.set_halign(Gtk.Align.CENTER)
        self.banner_box.set_margin_top(12)
        self.banner_box.set_margin_bottom(12)
        content_box.append(self.banner_box)

        if ICON_PATH.exists():
            self.banner_icon = Gtk.Image.new_from_file(str(ICON_PATH))
            self.banner_icon.set_pixel_size(96)
        else:
            self.banner_icon = Gtk.Image.new_from_icon_name("software-properties-symbolic")
            self.banner_icon.set_pixel_size(84)
        self.banner_box.append(self.banner_icon)

        self.banner_title = Gtk.Label(label="Ramord Store")
        self.banner_title.add_css_class("title-1")
        self.banner_box.append(self.banner_title)

        self.banner_desc = Gtk.Label()
        self.banner_desc.add_css_class("body")
        self.banner_desc.add_css_class("dim-label")
        self.banner_desc.set_wrap(True)
        self.banner_desc.set_justify(Gtk.Justification.CENTER)
        self.banner_desc.set_max_width_chars(54)
        self.banner_box.append(self.banner_desc)

        # 2. Applications PreferencesGroup
        self.apps_group = Adw.PreferencesGroup()
        content_box.append(self.apps_group)

        for meta in APPS:
            row = Adw.ActionRow()
            row.set_title(meta.name)
            row.set_subtitle(t(meta.desc_key, self.current_lang))
            row.set_subtitle_lines(0)

            # Icon Prefix
            if Path(meta.icon_rel_path).exists():
                icon_img = Gtk.Image.new_from_file(meta.icon_rel_path)
                icon_img.set_pixel_size(44)
            else:
                icon_img = Gtk.Image.new_from_icon_name("application-x-executable-symbolic")
                icon_img.set_pixel_size(40)
            row.add_prefix(icon_img)

            # Suffix buttons
            btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            btn_box.set_valign(Gtk.Align.CENTER)

            btn_launch = Gtk.Button(label=t("btn_launch", self.current_lang))
            btn_launch.connect("clicked", lambda b, m=meta: self._launch_app(m))
            btn_box.append(btn_launch)

            btn_action = Gtk.Button()
            btn_action.add_css_class("suggested-action")
            btn_action.connect("clicked", lambda b, m=meta: self._install_app(m))
            btn_box.append(btn_action)

            btn_mail = Gtk.Button.new_from_icon_name("mail-send-symbolic")
            btn_mail.set_tooltip_text(t("btn_support_app", self.current_lang))
            btn_mail.connect("clicked", lambda b, m=meta: self._open_email_for_app(m))
            btn_box.append(btn_mail)

            row.add_suffix(btn_box)
            self.apps_group.add(row)

            self._app_rows[meta.id] = {
                "meta": meta,
                "row": row,
                "btn_launch": btn_launch,
                "btn_action": btn_action,
                "btn_mail": btn_mail,
            }

        # 3. Support & Feedback Card
        self.support_group = Adw.PreferencesGroup()
        content_box.append(self.support_group)

        self.support_row = Adw.ActionRow()
        self.support_row.set_subtitle_lines(0)

        mail_icon = Gtk.Image.new_from_icon_name("mail-message-new-symbolic")
        mail_icon.set_pixel_size(36)
        self.support_row.add_prefix(mail_icon)

        sup_btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        sup_btn_box.set_valign(Gtk.Align.CENTER)

        self.btn_copy_mail = Gtk.Button(label=t("btn_copy_email", self.current_lang))
        self.btn_copy_mail.connect("clicked", self._copy_email)
        sup_btn_box.append(self.btn_copy_mail)

        self.btn_open_mail = Gtk.Button(label=t("btn_send_email", self.current_lang))
        self.btn_open_mail.add_css_class("suggested-action")
        self.btn_open_mail.connect("clicked", lambda b: self._open_email_for_app(None))
        sup_btn_box.append(self.btn_open_mail)

        self.support_row.add_suffix(sup_btn_box)
        self.support_group.add(self.support_row)

    def _is_app_installed(self, meta: AppMeta) -> bool:
        if shutil.which(meta.bin_name):
            return True
        desktop_dest = Path.home() / f".local/share/applications/{meta.desktop_file}"
        return desktop_dest.exists()

    def _update_card_state(self, app_id: str):
        c = self._app_rows.get(app_id)
        if not c:
            return
        meta = c["meta"]
        installed = self._is_app_installed(meta)
        is_installing = (meta.id in self._installing_apps)

        if is_installing:
            c["btn_action"].set_label(t("installing", self.current_lang))
            c["btn_action"].set_sensitive(False)
            c["btn_launch"].set_visible(False)
        elif installed:
            c["btn_action"].set_label(t("btn_update", self.current_lang))
            c["btn_action"].set_sensitive(True)
            c["btn_launch"].set_visible(True)
        else:
            c["btn_action"].set_label(t("btn_install", self.current_lang))
            c["btn_action"].set_sensitive(True)
            c["btn_launch"].set_visible(False)

    def _install_app(self, meta: AppMeta):
        self._installing_apps.add(meta.id)
        self._update_card_state(meta.id)

        def worker():
            proj_dir = Path.home() / f"Projeler/{meta.name.replace(' ', '')}"
            success = True
            msg = ""
            try:
                if not proj_dir.exists():
                    r = subprocess.run(["git", "clone", "--depth", "1", meta.repo_url, str(proj_dir)],
                                       capture_output=True, text=True, timeout=120)
                    if r.returncode != 0:
                        success = False
                        msg = r.stderr or r.stdout
                else:
                    subprocess.run(["git", "pull"], cwd=str(proj_dir), capture_output=True, timeout=60)

                if success:
                    install_sh = proj_dir / "install.sh"
                    if install_sh.exists():
                        r2 = subprocess.run(["bash", str(install_sh)], cwd=str(proj_dir),
                                            capture_output=True, text=True, timeout=120)
                        if r2.returncode != 0:
                            success = False
                            msg = r2.stderr or r2.stdout
                    else:
                        success = False
                        msg = "install.sh not found"
            except Exception as e:
                success = False
                msg = str(e)

            def on_done():
                self._installing_apps.discard(meta.id)
                self._update_card_state(meta.id)
                dialog = Adw.MessageDialog(
                    transient_for=self,
                    heading=t("app_title", self.current_lang),
                    body=t("op_success", self.current_lang) if success else (t("op_failed", self.current_lang) + "\n" + msg)
                )
                dialog.add_response("ok", "Tamam" if self.current_lang == "tr" else "OK")
                dialog.present()
                return False

            GLib.idle_add(on_done)

        threading.Thread(target=worker, daemon=True).start()

    def _launch_app(self, meta: AppMeta):
        try:
            subprocess.Popen([meta.bin_name], start_new_session=True)
        except Exception:
            proj_dir = Path.home() / f"Projeler/{meta.name.replace(' ', '')}"
            if (proj_dir / "main.py").exists():
                subprocess.Popen(["python3", str(proj_dir / "main.py")], start_new_session=True)

    def _open_email_for_app(self, meta: AppMeta | None):
        subject = f"Support: {meta.name}" if meta else "Support Request - Ramord Ecosystem"
        app_name = meta.name if meta else 'an application'
        body = f'Hello Ramord Support Team,\n\nI need assistance with {app_name}:\n'
        mailto = f"mailto:{OFFICIAL_EMAIL}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
        Gio.AppInfo.launch_default_for_uri(mailto, None)

    def _copy_email(self, button):
        clipboard = Gdk.Display.get_default().get_clipboard()
        clipboard.set(OFFICIAL_EMAIL)
        self.btn_copy_mail.set_label(t("copied", self.current_lang))
        GLib.timeout_add(2000, lambda: self.btn_copy_mail.set_label(t("btn_copy_email", self.current_lang)) or False)

    def _on_change_language(self, button, code, popover):
        self.current_lang = code
        set_lang(code)
        popover.popdown()
        self._refresh_texts()

    def _on_change_theme(self, button, mode, popover):
        self.theme_mode = mode
        popover.popdown()
        self._apply_theme()
        self._refresh_texts()

    def _refresh_texts(self):
        lang = self.current_lang
        self.set_title(t("app_title", lang))
        self.banner_title.set_label(t("app_title", lang))
        self.banner_desc.set_label(t("app_subtitle", lang))
        self.lang_btn_label.set_label(LANGUAGES.get(lang, "English"))
        self.theme_btn_label.set_label(t(f"theme_{self.theme_mode}", lang))

        self.apps_group.set_title(html.escape(t("tab_apps", lang)))
        for meta in APPS:
            c = self._app_rows.get(meta.id)
            if c:
                c["row"].set_subtitle(t(meta.desc_key, lang))
                c["btn_launch"].set_label(t("btn_launch", lang))
                c["btn_mail"].set_tooltip_text(t("btn_support_app", lang))
                self._update_card_state(meta.id)

        self.support_group.set_title(html.escape(t("tab_support", lang)))
        self.support_row.set_title(t("support_title", lang))
        self.support_row.set_subtitle(f"{t('support_desc', lang)}\n{OFFICIAL_EMAIL}")
        self.btn_copy_mail.set_label(t("btn_copy_email", lang))
        self.btn_open_mail.set_label(t("btn_send_email", lang))


class RamordStoreApp(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id="com.ramord.store",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS
        )

    def do_activate(self):
        windows = self.get_windows()
        if not windows:
            win = RamordStoreWindow(self)
            win.present()
        else:
            for w in list(windows):
                w.close()
            self.quit()


def main():
    app = RamordStoreApp()

    def handle_sig(sig, frame):
        for w in list(app.get_windows()):
            try:
                w.close()
            except Exception:
                pass
        app.quit()

    try:
        signal.signal(signal.SIGINT, handle_sig)
        signal.signal(signal.SIGTERM, handle_sig)
    except Exception:
        pass

    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
