from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QLineEdit, QLabel, QFileDialog, QMessageBox, QMenu
)
from PyQt5.QtCore import Qt, QSettings
import os


class PathManagerPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.settings = QSettings("MyCompany", "ImageConverter")
        self.load_paths()

    def initUI(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("常用路径管理"))

        self.path_list = QListWidget()
        self.path_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.path_list.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.path_list)

        add_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("手动输入路径...")
        self.add_btn = QPushButton("添加路径")
        self.add_btn.clicked.connect(self.add_path)
        add_layout.addWidget(self.path_input)
        add_layout.addWidget(self.add_btn)
        layout.addLayout(add_layout)

        self.select_btn = QPushButton("浏览文件夹")
        self.select_btn.clicked.connect(self.select_folder)
        layout.addWidget(self.select_btn)

        self.setLayout(layout)

    def show_context_menu(self, position):
        menu = QMenu()
        remove_action = menu.addAction("移除路径")
        default_action = menu.addAction("设为默认路径")

        item = self.path_list.itemAt(position)
        if item:
            action = menu.exec_(self.path_list.mapToGlobal(position))
            if action == remove_action:
                self.remove_selected_path()
            elif action == default_action:
                self.set_default_path(item.text())

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder:
            self.path_input.setText(folder)

    def add_path(self):
        path = self.path_input.text().strip()
        if not path or not os.path.isdir(path):
            QMessageBox.warning(self, "错误", "请输入有效的文件夹路径")
            return

        existing_paths = [self.path_list.item(i).text() for i in range(self.path_list.count())]
        if path in existing_paths:
            QMessageBox.information(self, "提示", "该路径已存在")
            return

        self.path_list.addItem(path)
        self.save_paths()

    def remove_selected_path(self):
        current_row = self.path_list.currentRow()
        if current_row >= 0:
            self.path_list.takeItem(current_row)
            self.save_paths()

    def set_default_path(self, path):
        print("设为默认路径:", path)
        self.settings.setValue("default_path", path)
        QMessageBox.information(self, "成功", f"已设为默认路径：{path}")

    def get_default_path(self):
        return self.settings.value("default_path", "")

    def load_paths(self):
        paths = self.settings.value("saved_paths", [])
        if isinstance(paths, str):
            paths = [paths]
        for path in paths:
            if os.path.isdir(path):
                self.path_list.addItem(path)

    def save_paths(self):
        paths = [self.path_list.item(i).text() for i in range(self.path_list.count())]
        self.settings.setValue("saved_paths", paths)