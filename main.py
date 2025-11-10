import sys
import os
import subprocess
import shlex
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QIcon

import json
from xdg.BaseDirectory import xdg_data_dirs, xdg_cache_home
from xdg.DesktopEntry import DesktopEntry
from xdg.IconTheme import getIconPath

def get_applications_data():
    """
    Retrieves application data (name, exec, icon) from a cache file if it
    exists, otherwise it scans for .desktop files, creates the cache, and
    returns the data.
    """
    cache_file = os.path.join(xdg_cache_home, 'pyauncher_cache.json')
    
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                pass # Cache is corrupt, rebuild it

    applications = {}
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
            if entry.getNoDisplay():
                continue
            
            app_name = entry.getName()
            icon_name = entry.getIcon()
            exec_command = entry.getExec()

            icon_path = None
            if icon_name:
                icon_path = getIconPath(icon_name, size=48)
                if not icon_path or not os.path.exists(icon_path):
                    if os.path.exists(icon_name):
                        icon_path = icon_name
                    else:
                        icon_path = None
            
            applications[app_name] = {
                'exec': exec_command,
                'icon': icon_path
            }
        except Exception:
            continue
            
    # Sort applications by name
    sorted_apps = dict(sorted(applications.items()))

    with open(cache_file, 'w') as f:
        json.dump(sorted_apps, f)

    return sorted_apps


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
            QListWidget::item:selected {
                background-color: #44475a;
            }
        """)

        self.apps = get_applications_data()
        self.populate_apps()
        self.search_bar.setFocus()

    def populate_apps(self):
        self.app_list.clear()
        for app_name, app_data in self.apps.items():
            item = QListWidgetItem(app_name)
            icon_path = app_data.get('icon')
            if icon_path:
                item.setIcon(QIcon(icon_path))
            self.app_list.addItem(item)

    def filter_apps(self, text):
        for i in range(self.app_list.count()):
            item = self.app_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())

        # Select the first visible item
        for i in range(self.app_list.count()):
            if not self.app_list.item(i).isHidden():
                self.app_list.setCurrentRow(i)
                return

    def launch_app(self, item):
        app_name = item.text()
        app_data = self.apps.get(app_name)
        
        if app_data:
            exec_command = app_data.get('exec')
            # Remove field codes like %U, %F, etc.
            cleaned_command = ' '.join([part for part in exec_command.split() if not part.startswith('%')])
            command = shlex.split(cleaned_command)
        else:
            command = [app_name]

        try:
            subprocess.Popen(command, start_new_session=True)
            QApplication.quit()
        except (FileNotFoundError, OSError) as e:
            print(f"Error launching '{' '.join(command)}': {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            QApplication.quit()
        elif event.key() == Qt.Key_Up:
            current_row = self.app_list.currentRow()
            # find previous visible item
            for i in range(current_row - 1, -1, -1):
                if not self.app_list.item(i).isHidden():
                    self.app_list.setCurrentRow(i)
                    break
        elif event.key() == Qt.Key_Down:
            current_row = self.app_list.currentRow()
            # find next visible item
            for i in range(current_row + 1, self.app_list.count()):
                if not self.app_list.item(i).isHidden():
                    self.app_list.setCurrentRow(i)
                    break
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
            self.search_bar.setFocus()
            QApplication.sendEvent(self.search_bar, event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    launcher = Launcher()
    launcher.show()
    sys.exit(app.exec())
