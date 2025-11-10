#!/bin/bash

# Get the absolute path of the project directory
PROJECT_DIR=$(cd "$(dirname "$0")" && pwd)

# Create the .desktop file
cat > "$PROJECT_DIR/pyauncher.desktop" << EOL
[Desktop Entry]
Name=Pyauncher
Exec=$PROJECT_DIR/launch.sh
Icon=pyauncher
Type=Application
Categories=Utility;
EOL

# Create the icon directory
mkdir -p ~/.local/share/icons/hicolor/48x48/apps/

# Copy the icon
cp "$PROJECT_DIR/pics/interface.png" ~/.local/share/icons/hicolor/48x48/apps/pyauncher.png

# Move the .desktop file
mv "$PROJECT_DIR/pyauncher.desktop" ~/.local/share/applications/

# Make launch.sh executable
chmod +x "$PROJECT_DIR/launch.sh"

echo "Pyauncher has been installed successfully!"
echo "You can now launch it from your application menu."
