#!/bin/bash


## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


## add udev rule
AUTOSTART_FILE=~/.local/share/applications/menulibre-rsscast.desktop


cat > $AUTOSTART_FILE << EOL
[Desktop Entry]
Name=RSSCast
GenericName=RSSCast
Comment=Convert Youtube feed to podcast RSS.
Version=1.1
Type=Application
Exec=$SCRIPT_DIR/startrsscast
Path=$SCRIPT_DIR
Icon=$SCRIPT_DIR/rsscast/gui/img/rss-icon-black.png
Actions=
Categories=Office;
StartupNotify=true
Terminal=false

EOL


echo "File created in: $AUTOSTART_FILE"
