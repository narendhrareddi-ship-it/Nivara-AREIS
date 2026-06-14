#!/usr/bin/env bash
# Double-click or run: bash Install-NIVARA-Desktop-Shortcut.sh
URL="https://nivara-areis-etzshrs4dtzuyqmsnv8bds.streamlit.app/"
DESK="$HOME/Desktop"
mkdir -p "$DESK"
FILE="$DESK/NIVARA-AREIS.desktop"
cat > "$FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=NIVARA AREIS
Comment=Bangalore Real Estate AI Dashboard
Exec=xdg-open $URL
Icon=applications-internet
Terminal=false
Categories=Office;
EOF
chmod +x "$FILE"
echo "Shortcut created: $FILE"
xdg-open "$URL" 2>/dev/null || open "$URL" 2>/dev/null || echo "Open: $URL"
