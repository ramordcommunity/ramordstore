# -*- coding: utf-8 -*-
"""
Ramord Store - Localization Module (6 Languages: tr, en, de, es, fr, it)
Compliant with Ramord System Rules.
Official Contact: ramordhelp@gmail.com
"""

from __future__ import annotations
import locale
import os

LANGUAGES = {
    "tr": "Türkçe",
    "en": "English",
    "de": "Deutsch",
    "es": "Español",
    "fr": "Français",
    "it": "Italiano",
}

TRANSLATIONS: dict[str, dict[str, str]] = {
    "app_title": {
        "tr": "Ramord Store",
        "en": "Ramord Store",
        "de": "Ramord Store",
        "es": "Ramord Store",
        "fr": "Ramord Store",
        "it": "Ramord Store",
    },
    "app_subtitle": {
        "tr": "Ramord Açık Kaynak Uygulama Merkezi",
        "en": "Ramord Open Source Application Hub",
        "de": "Ramord Open-Source-Anwendungszentrum",
        "es": "Centro de Aplicaciones de Código Abierto Ramord",
        "fr": "Centre d'Applications Open Source Ramord",
        "it": "Centro Applicazioni Open Source Ramord",
    },
    "tab_apps": {
        "tr": "Uygulamalar",
        "en": "Applications",
        "de": "Anwendungen",
        "es": "Aplicaciones",
        "fr": "Applications",
        "it": "Applicazioni",
    },
    "tab_support": {
        "tr": "Resmi Destek & İletişim",
        "en": "Official Support & Contact",
        "de": "Offizieller Support & Kontakt",
        "es": "Soporte Oficial y Contacto",
        "fr": "Support Officiel & Contact",
        "it": "Supporto Ufficiale e Contatto",
    },
    "status_installed": {
        "tr": "Kurulu",
        "en": "Installed",
        "de": "Installiert",
        "es": "Instalado",
        "fr": "Installé",
        "it": "Installato",
    },
    "status_not_installed": {
        "tr": "Kurulu Değil",
        "en": "Not Installed",
        "de": "Nicht installiert",
        "es": "No instalado",
        "fr": "Non installé",
        "it": "Non installato",
    },
    "btn_install": {
        "tr": "Kur",
        "en": "Install",
        "de": "Installieren",
        "es": "Instalar",
        "fr": "Installer",
        "it": "Installa",
    },
    "btn_update": {
        "tr": "Güncelle",
        "en": "Update",
        "de": "Aktualisieren",
        "es": "Actualizar",
        "fr": "Mettre à jour",
        "it": "Aggiorna",
    },
    "btn_launch": {
        "tr": "Başlat",
        "en": "Launch",
        "de": "Starten",
        "es": "Iniciar",
        "fr": "Lancer",
        "it": "Avvia",
    },
    "btn_support_app": {
        "tr": "Destek Al (E-Posta)",
        "en": "Get Support (Email)",
        "de": "Support anfordern (E-Mail)",
        "es": "Obtener Soporte (Correo)",
        "fr": "Obtenir de l'Aide (E-mail)",
        "it": "Ricevi Assistenza (Email)",
    },
    "btn_github": {
        "tr": "GitHub Kaynağı",
        "en": "GitHub Repository",
        "de": "GitHub-Repository",
        "es": "Repositorio GitHub",
        "fr": "Dépôt GitHub",
        "it": "Repository GitHub",
    },
    "support_title": {
        "tr": "Doğrudan Destek ve Geri Bildirim",
        "en": "Direct Support & Feedback",
        "de": "Direkter Support & Feedback",
        "es": "Soporte Directo y Comentarios",
        "fr": "Support Direct et Commentaires",
        "it": "Supporto Diretto e Feedback",
    },
    "support_desc": {
        "tr": "Uygulamalarla ilgili bir hata, öneri veya destek talebiniz olduğunda resmi e-posta adresimiz üzerinden doğrudan geliştirici ekibine ulaşabilirsiniz:",
        "en": "For bug reports, feature suggestions, or support inquiries regarding any Ramord application, you can reach the core developer team directly via our official email address:",
        "de": "Bei Fehlermeldungen, Vorschlägen oder Supportanfragen zu Ramord-Anwendungen können Sie das Entwicklerteam direkt über unsere offizielle E-Mail-Adresse erreichen:",
        "es": "Para informes de errores, sugerencias o consultas de soporte sobre las aplicaciones de Ramord, puede comunicarse directamente con el equipo de desarrollo a través de nuestro correo oficial:",
        "fr": "Pour tout rapport de bug, suggestion ou demande d'assistance concernant les applications Ramord, vous pouvez contacter directement l'équipe via notre adresse e-mail officielle :",
        "it": "Per segnalazioni di bug, suggerimenti o richieste di assistenza riguardanti le applicazioni Ramord, puoi contattare direttamente il team di sviluppo tramite la nostra email ufficiale:",
    },
    "support_email_label": {
        "tr": "Resmi Destek Adresi:",
        "en": "Official Support Address:",
        "de": "Offizielle Support-Adresse:",
        "es": "Dirección Oficial de Soporte:",
        "fr": "Adresse Officielle de Support :",
        "it": "Indirizzo Ufficiale di Supporto:",
    },
    "btn_send_email": {
        "tr": "E-Posta İstemcisini Aç",
        "en": "Open Email Client",
        "de": "E-Mail-Programm öffnen",
        "es": "Abrir Cliente de Correo",
        "fr": "Ouvrir le Client E-mail",
        "it": "Apri Client Email",
    },
    "btn_copy_email": {
        "tr": "E-Postayı Kopyala",
        "en": "Copy Email",
        "de": "E-Mail kopieren",
        "es": "Copiar Correo",
        "fr": "Copier l'E-mail",
        "it": "Copia Email",
    },
    "copied": {
        "tr": "Kopyalandı!",
        "en": "Copied!",
        "de": "Kopiert!",
        "es": "¡Copiado!",
        "fr": "Copié !",
        "it": "Copiato!",
    },
    "op_success": {
        "tr": "İşlem başarıyla tamamlandı.",
        "en": "Operation completed successfully.",
        "de": "Vorgang erfolgreich abgeschlossen.",
        "es": "Operación completada con éxito.",
        "fr": "Opération terminée avec succès.",
        "it": "Operazione completata con successo.",
    },
    "op_failed": {
        "tr": "İşlem başarısız oldu.",
        "en": "Operation failed.",
        "de": "Vorgang fehlgeschlagen.",
        "es": "Operación fallida.",
        "fr": "Opération échouée.",
        "it": "Operazione non riuscita.",
    },
    "installing": {
        "tr": "Yükleniyor...",
        "en": "Installing...",
        "de": "Wird installiert...",
        "es": "Instalando...",
        "fr": "Installation en cours...",
        "it": "Installazione in corso...",
    },
    # App-specific descriptions
    "desc_ramord_link": {
        "tr": "Linux ile Windows/Mac bilgisayarlar arasında internet, KVM (fare/klavye/ortak pano) ve web dosya paylaşımı köprüsü.",
        "en": "Network, KVM (mouse/keyboard/clipboard), and web file sharing bridge between Linux and Windows/Mac computers.",
        "de": "Netzwerk-, KVM- (Maus/Tastatur/Zwischenablage) und Web-Dateifreigabe-Bridge zwischen Linux und Windows/Mac-Computern.",
        "es": "Puente de red, KVM (ratón/teclado/portapapeles) y archivos web entre computadoras Linux y Windows/Mac.",
        "fr": "Passerelle réseau, KVM (souris/clavier/presse-papiers) et fichiers web entre Linux et ordinateurs Windows/Mac.",
        "it": "Bridge di rete, KVM (mouse/tastiera/appunti) e file web tra computer Linux e Windows/Mac.",
    },
    "desc_ramord_cast": {
        "tr": "Linux masaüstünüzü Smart TV ve monitörlere düşük gecikmeyle yansıtma ve bağımsız sanal 2. ekran aracı.",
        "en": "Low-latency wireless screen mirroring and independent virtual second-display tool for Smart TVs and monitors.",
        "de": "Kabellose Bildschirmspiegelung mit geringer Latenz und virtueller Zweitmonitor für Smart-TVs und Monitore.",
        "es": "Transmisión inalámbrica de pantalla de baja latencia y segundo monitor virtual para televisores inteligentes y monitores.",
        "fr": "Mise en miroir sans fil à faible latence et deuxième écran virtuel pour Smart TV et moniteurs sous Linux.",
        "it": "Duplicazione schermo wireless a bassa latenza e secondo display virtuale per Smart TV e monitor.",
    },
    "desc_ramord_cad": {
        "tr": "Masaüstü ve mobil platformlar için yüksek performanslı 3D SLDPRT, STEP ve DWG mühendislik görüntüleme ve inceleme aracı.",
        "en": "High-performance 3D SLDPRT, STEP, and DWG engineering viewer and inspection tool for desktop and mobile platforms.",
        "de": "Hochleistungs-3D-SLDPRT-, STEP- und DWG-Engineering-Viewer und Prüfwerkzeug für Desktop und Mobilgeräte.",
        "es": "Visor y herramienta de inspección de ingeniería 3D SLDPRT, STEP y DWG de alto rendimiento para escritorio y móvil.",
        "fr": "Visualiseur et outil d'inspection 3D SLDPRT, STEP et DWG haute performance pour bureau et mobile.",
        "it": "Visualizzatore e strumento di ispezione 3D SLDPRT, STEP e DWG ad alte prestazioni per desktop e dispositivi mobili.",
    },
    "theme_auto": {
        "tr": "Sistem Teması",
        "en": "System Theme",
        "de": "Systemthema",
        "es": "Tema del Sistema",
        "fr": "Thème du Système",
        "it": "Tema di Sistema",
    },
    "theme_day": {
        "tr": "Gündüz Modu",
        "en": "Day Mode",
        "de": "Tagmodus",
        "es": "Modo Día",
        "fr": "Mode Jour",
        "it": "Modalità Giorno",
    },
    "theme_night": {
        "tr": "Gece Modu",
        "en": "Night Mode",
        "de": "Nachtmodus",
        "es": "Modo Noche",
        "fr": "Mode Nuit",
        "it": "Modalità Notte",
    },
}

_CURRENT_LANG: str = "tr"


def detect_system_language() -> str:
    for env in ("LC_ALL", "LC_MESSAGES", "LANG"):
        val = os.environ.get(env, "")
        if val:
            prefix = val.split("_")[0].lower()
            if prefix in LANGUAGES:
                return prefix
    try:
        loc = locale.getdefaultlocale()[0]
        if loc:
            prefix = loc.split("_")[0].lower()
            if prefix in LANGUAGES:
                return prefix
    except Exception:
        pass
    return "tr"


def get_lang() -> str:
    return _CURRENT_LANG


def set_lang(code: str) -> None:
    global _CURRENT_LANG
    if code in LANGUAGES:
        _CURRENT_LANG = code


def t(key: str, lang: str | None = None) -> str:
    use_lang = lang or _CURRENT_LANG
    mapping = TRANSLATIONS.get(key)
    if not mapping:
        return key
    return mapping.get(use_lang, mapping.get("en", key))


_CURRENT_LANG = detect_system_language()
