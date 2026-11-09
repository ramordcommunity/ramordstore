#!/usr/bin/env bash
# Ramord Store - Local Installation & System Integration Script
# Official Contact: ramordhelp@gmail.com

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${HOME}/.local/bin"
DESKTOP_DIR="${HOME}/.local/share/applications"
ICON_DIR="${HOME}/.local/share/icons"
TARGET_BIN="${BIN_DIR}/ramord-store"

echo "==> Installing Ramord Store..."

mkdir -p "${BIN_DIR}" "${DESKTOP_DIR}" "${ICON_DIR}/hicolor/scalable/apps"

# 1. Executable runner
cat << EOF > "${TARGET_BIN}"
#!/usr/bin/env bash
exec python3 "${SCRIPT_DIR}/main.py" "\$@"
EOF
chmod +x "${TARGET_BIN}"

# 2. Universal Icon Deployment across all themes and resolutions
RESOLUTIONS=(16 22 24 32 48 64 128 256 512)

if [ -d "${ICON_DIR}" ]; then
    for tdir in "${ICON_DIR}"/*; do
        if [ -d "${tdir}" ]; then
            for app_dir in $(find "${tdir}" -type d -name "apps" 2>/dev/null); do
                cp -f "${SCRIPT_DIR}/assets/ramord-store.svg" "${app_dir}/ramord-store.svg" 2>/dev/null || true
                
                pname="$(basename "$(dirname "${app_dir}")")"
                res=""
                if [[ "${pname}" =~ ^[0-9]+$ ]]; then
                    res="${pname}"
                elif [[ "${pname}" =~ ^([0-9]+)x[0-9]+$ ]]; then
                    res="${BASH_REMATCH[1]}"
                fi
                
                if [ -n "${res}" ] && command -v rsvg-convert >/dev/null 2>&1; then
                    rsvg-convert -w "${res}" -h "${res}" "${SCRIPT_DIR}/assets/ramord-store.svg" -o "${app_dir}/ramord-store.png" 2>/dev/null || true
                elif command -v rsvg-convert >/dev/null 2>&1; then
                    rsvg-convert -w 128 -h 128 "${SCRIPT_DIR}/assets/ramord-store.svg" -o "${app_dir}/ramord-store.png" 2>/dev/null || true
                fi
            done
            
            if command -v gtk-update-icon-cache >/dev/null 2>&1; then
                gtk-update-icon-cache -f -t "${tdir}" >/dev/null 2>&1 || true
            fi
        fi
    done
fi

mkdir -p "${HOME}/.local/share/pixmaps"
cp -f "${SCRIPT_DIR}/assets/ramord-store.svg" "${HOME}/.local/share/pixmaps/ramord-store.svg"
if command -v rsvg-convert >/dev/null 2>&1; then
    rsvg-convert -w 256 -h 256 "${SCRIPT_DIR}/assets/ramord-store.svg" -o "${HOME}/.local/share/pixmaps/ramord-store.png" 2>/dev/null || true
fi

# 3. Desktop Application Shortcut
cat << EOF > "${DESKTOP_DIR}/ramord-store.desktop"
[Desktop Entry]
Type=Application
Version=1.0
Name=Ramord Store
GenericName=App Store & Support Hub
GenericName[tr]=Uygulama Mağazası ve Destek Merkezi
Comment=Open source application hub and support center for Linux
Comment[tr]=Linux için açık kaynak uygulama merkezi ve destek merkezi
Exec=ramord-store
Icon=/home/ramordser/Projeler/RamordStore/assets/ramord-store.svg
Terminal=false
Categories=System;PackageManager;Utility;
Keywords=store;app;install;ramord;support;
Keywords[tr]=mağaza;uygulama;kur;destek;ramord;
StartupNotify=true
StartupWMClass=ramord-store
EOF

chmod +x "${DESKTOP_DIR}/ramord-store.desktop"
cp -f "${DESKTOP_DIR}/ramord-store.desktop" "${HOME}/Masaüstü/RamordStore.desktop" 2>/dev/null || true

# 4. Cache updates
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "${DESKTOP_DIR}" >/dev/null 2>&1 || true
fi

if command -v kbuildsycoca6 >/dev/null 2>&1; then
    kbuildsycoca6 --noincremental >/dev/null 2>&1 || true
fi

echo "==> Ramord Store installed successfully!"
echo "    Binary:  ${TARGET_BIN}"
echo "    Desktop: ${DESKTOP_DIR}/ramord-store.desktop"
