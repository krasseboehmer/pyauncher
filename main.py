import sys
import os
import subprocess
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QIcon

from xdg.BaseDirectory import xdg_data_dirs
from xdg.DesktopEntry import DesktopEntry
from xdg.IconTheme import getIconPath

def get_linux_distribution():
    """
    Determines the Linux distribution using /etc/os-release.
    Returns a dictionary with 'ID' and 'ID_LIKE' if found, otherwise empty.
    """
    distro_info = {}
    if os.path.exists('/etc/os-release'):
        with open('/etc/os-release', 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('ID='):
                    distro_info['ID'] = line.split('=')[1].strip('"')
                elif line.startswith('ID_LIKE='):
                    distro_info['ID_LIKE'] = line.split('=')[1].strip('"')
    return distro_info

def run_command(command_args):
    """
    Runs a shell command and returns its stdout if successful, None otherwise.
    """
    try:
        result = subprocess.run(
            command_args,
            capture_output=True,
            text=True,
            check=False, # Don't raise an exception for non-zero exit codes
            encoding='utf-8', # Explicitly set encoding
            errors='replace' # Replace unencodable characters
        )
        if result.returncode == 0:
            return result.stdout
        else:
            return None
    except FileNotFoundError:
        return None
    except Exception as e:
        return None

def get_installed_applications():
    """
    Attempts to list installed applications on a Linux system using various
    package managers.
    """
    applications = set()
    desktop_files = []
    for data_dir in xdg_data_dirs:
        applications_dir = os.path.join(data_dir, 'applications')
        if os.path.isdir(applications_dir):
            for filename in os.listdir(applications_dir):
                if filename.endswith('.desktop'):
                    try:
                        entry = DesktopEntry(os.path.join(applications_dir, filename))
                        applications.add(entry.getName())
                    except Exception:
                        continue
    return sorted(list(applications))

def get_application_icon_path(application_name: str, size: int = 48) -> str | None:
    """
    Retrieves the full path to an application's icon on a Linux desktop.
    """
    desktop_files = []
    for data_dir in xdg_data_dirs:
        applications_dir = os.path.join(data_dir, 'applications')
        if os.path.isdir(applications_dir):
            for filename in os.listdir(applications_dir):
                if filename.endswith('.desktop'):
                    desktop_files.append(os.path.join(applications_dir, filename))

    icon_name = None
    for d_file in desktop_files:
        try:
            entry = DesktopEntry(d_file)
            if application_name.lower() == entry.getName().lower() or \
               application_name.lower() == os.path.basename(d_file).replace('.desktop', '').lower():
                icon_name = entry.getIcon()
                if icon_name:
                    break
        except Exception:
            continue

    if icon_name:
        icon_path = getIconPath(icon_name, size=size)
        if icon_path and os.path.exists(icon_path):
            return icon_path
        
        if os.path.exists(icon_name):
            return icon_name

    return None

def get_application_exec(application_name: str) -> str | None:
    """
    Retrieves the executable command for an application from its .desktop file.
    """
    desktop_files = []
    for data_dir in xdg_data_dirs:
        applications_dir = os.path.join(data_dir, 'applications')
        if os.path.isdir(applications_dir):
            for filename in os.listdir(applications_dir):
                if filename.endswith('.desktop'):
                    desktop_files.append(os.path.join(applications_dir, filename))

    for d_file in desktop_files:
        try:
            entry = DesktopEntry(d_file)
            if application_name.lower() == entry.getName().lower() or \
               application_name.lower() == os.path.basename(d_file).replace('.desktop', '').lower():
                return entry.getExec()
        except Exception:
            continue

    return None


class Launcher(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Pyauncher')
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.resize(800, 400)

        # Move window to top center
        screen_geometry = QApplication.primaryScreen().geometry()
        self.move(int((screen_geometry.width() - self.width()) / 2), 0)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText('Search for applications...')
        self.search_bar.textChanged.connect(self.filter_apps)
        self.layout.addWidget(self.search_bar)

        self.app_list = QListWidget()
        self.app_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.app_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.app_list.itemClicked.connect(self.launch_app)
        self.layout.addWidget(self.app_list)

        self.setStyleSheet("""
            QWidget {
                background-color: #282a36;
                color: #f8f8f2;
                border-radius: 10px;
            }
            QLineEdit {
                border: 2px solid #44475a;
                border-radius: 10px;
                padding: 5px;
                font-size: 16px;
            }
            QListWidget {
                border: none;
                font-size: 14px;
            }
        """)

        self.populate_apps()
        self.search_bar.setFocus()
        self.search_bar.installEventFilter(self)
        self.app_list.installEventFilter(self)

    def populate_apps(self):
        self.app_list.clear()
        apps = get_installed_applications()
        for app_name in apps:
            icon_path = get_application_icon_path(app_name)
            item = QListWidgetItem(app_name)
            if icon_path:
                item.setIcon(QIcon(icon_path))
            self.app_list.addItem(item)

    def filter_apps(self, text):
        for i in range(self.app_list.count()):
            item = self.app_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def launch_app(self, item):
        app_name = item.text()
        exec_command = get_application_exec(app_name)
        
        if exec_command:
            # The exec command may contain placeholders like %U, %F, etc.
            # For simplicity, we'll remove them.
            command = exec_command.split('%')[0].strip()
        else:
            command = app_name

        try:
            subprocess.Popen(command, shell=True, start_new_session=True)
            QApplication.quit()
        except (FileNotFoundError, OSError):
            print(f"Error: Could not find application '{command}'")

    def eventFilter(self, watched, event):
        if event.type() == QEvent.KeyPress:
            if watched == self.search_bar:
                if event.key() == Qt.Key_Down:
                    if self.app_list.count() > 0:
                        # find first visible item and select it
                        for i in range(self.app_list.count()):
                            if not self.app_list.item(i).isHidden():
                                self.app_list.setCurrentRow(i)
                                self.app_list.setFocus()
                                break
                        return True
            elif watched == self.app_list:
                if event.key() == Qt.Key_Up and self.app_list.currentRow() == 0:
                    self.search_bar.setFocus()
                    return True
        return super().eventFilter(watched, event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            QApplication.quit()
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            selected_item = self.app_list.currentItem()
            if selected_item:
                self.launch_app(selected_item)
            else:
                # If no item is explicitly selected, launch the first visible item
                for i in range(self.app_list.count()):
                    item = self.app_list.item(i)
                    if not item.isHidden():
                        self.launch_app(item)
                        break
        else:
            super().keyPressEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    launcher = Launcher()
    launcher.show()
    sys.exit(app.exec())
