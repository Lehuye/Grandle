#!/usr/bin/env python3
import os
import sys
import uuid
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                             QHBoxLayout, QListWidget, QFileDialog, QLabel, 
                             QWidget, QMessageBox, QComboBox, QTabWidget, QProgressBar)  # 添加这一行
from PyQt5.QtCore import Qt
from PyQt5 import QtGui  # 之前添加的导入
import PyPDF2 
from PIL import Image  # 保留PIL作为基础图像处理库
from utils import allowed_file, convert_image


class ImageConverter(QWidget):
    """图片转换功能面板"""
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()

        # 转换格式选择
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("选择转换格式:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["png", "jpg", "webp", "icns","ico"])
        format_layout.addWidget(self.format_combo)
        layout.addLayout(format_layout)

        # 转换按钮
        convert_btn = QPushButton("选择文件并转换")
        convert_btn.clicked.connect(self.select_and_convert)
        layout.addWidget(convert_btn)

        # GIF合成选项
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("GIF 每帧间隔 (秒):"))
        self.duration_combo = QComboBox()
        self.duration_combo.addItems(["0.1", "0.2", "0.5", "1.0"])
        duration_layout.addWidget(self.duration_combo)
        layout.addLayout(duration_layout)

        # GIF合成按钮
        gif_btn = QPushButton("选择多张图片合成GIF")
        gif_btn.clicked.connect(self.select_and_merge_gif)
        layout.addWidget(gif_btn)

        self.setLayout(layout)

    def select_and_convert(self):
        """选择并转换图片"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "选择多个图片文件", "", "图像文件 (*.jpg *.jpeg *.png *.gif)"
        )
        if not file_paths:
            return
    
        convert_type = self.format_combo.currentText()
        success_count = 0
        failed_files = []
    
        for file_path in file_paths:
            if not allowed_file(file_path, {'jpg', 'jpeg', 'png', 'gif'}):
                failed_files.append(file_path)
                continue
            
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            output_path = os.path.join(os.path.dirname(file_path), f"{base_name}.{convert_type}")
    
            if convert_image(file_path, output_path, convert_type):
                success_count += 1
            else:
                failed_files.append(file_path)
    
        message = f"成功转换 {success_count} 个文件。"
        if failed_files:
            message += f"\n失败文件:\n" + "\n".join(failed_files)
            QMessageBox.warning(self, "部分失败", message)
        else:
            QMessageBox.information(self, "成功", message)

    def select_and_merge_gif(self):
        """选择多张图片合成GIF"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "选择多张图片合成GIF", "", "图像文件 (*.jpg *.jpeg *.png *.gif)"
        )
        if not file_paths or len(file_paths) < 2:
            QMessageBox.critical(self, "错误", "请至少选择两张图片")
            return

        try:
            images = []
            for fp in file_paths:
                img = Image.open(fp).convert("RGBA")
                images.append(img)
            
            duration = float(self.duration_combo.currentText()) * 1000  # 转换为毫秒
            output_path = os.path.join(os.path.dirname(file_paths[0]), f"combo_{uuid.uuid4().hex}.gif")
            
            # 使用PIL的save方法创建GIF
            images[0].save(
                output_path,
                format="GIF",
                append_images=images[1:],
                save_all=True,
                duration=duration,
                loop=0  # 0表示无限循环
            )
            
            QMessageBox.information(self, "成功", f"GIF 合成成功！\n输出文件: {output_path}")
        except Exception as e:
            QMessageBox.critical(self, "合成失败", str(e))
