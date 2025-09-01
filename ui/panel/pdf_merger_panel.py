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
from utils import allowed_file

class PDFMergerPanel(QWidget):
    """PDF合并功能面板"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent  # 保存对主窗口的引用
        self.initUI()
        
    def initUI(self):
        # 创建主布局
        main_layout = QVBoxLayout()
        
        # 文件列表区域
        file_label = QLabel('待合并的PDF文件:')
        self.file_list = QListWidget()
        self.file_list.setAlternatingRowColors(True)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton('添加文件')
        self.add_button.clicked.connect(self.add_files)
        
        self.remove_button = QPushButton('移除选中')
        self.remove_button.clicked.connect(self.remove_selected)
        
        self.clear_button = QPushButton('清空列表')
        self.clear_button.clicked.connect(self.clear_list)
        
        self.move_up_button = QPushButton('上移')
        self.move_up_button.clicked.connect(self.move_up)
        
        self.move_down_button = QPushButton('下移')
        self.move_down_button.clicked.connect(self.move_down)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.move_up_button)
        button_layout.addWidget(self.move_down_button)
        
        # 输出文件设置
        output_layout = QHBoxLayout()
        output_label = QLabel('输出文件:')
        self.output_path = QLabel('未选择')
        self.output_path.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.output_path.setStyleSheet("border: 1px solid #ccc; padding: 5px;")
        
        self.select_output_button = QPushButton('选择位置')
        self.select_output_button.clicked.connect(self.select_output_file)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(self.select_output_button)
        
        # 合并按钮和进度条
        self.merge_button = QPushButton('开始合并')
        self.merge_button.setStyleSheet("background-color: #4CAF50; color: white; font-size: 14px;")
        self.merge_button.clicked.connect(self.merge_pdfs)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setValue(0)
        
        # 添加所有组件到主布局
        main_layout.addWidget(file_label)
        main_layout.addWidget(self.file_list)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(output_layout)
        main_layout.addWidget(self.merge_button)
        main_layout.addWidget(self.progress_bar)
        
        self.setLayout(main_layout)
        
    def add_files(self):
        """添加PDF文件到列表"""
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择PDF文件", "", "PDF Files (*.pdf);;All Files (*)", options=options
        )
        
        if files:
            for file in files:
                if allowed_file(file, {'pdf'}):
                    self.file_list.addItem(file)
                else:
                    QMessageBox.warning(self, "警告", f"文件 {file} 不是有效的PDF文件")
            # 通过主窗口访问状态栏
            if self.main_window:
                self.main_window.statusBar().showMessage(f"已添加 {len(files)} 个文件")
    
    def remove_selected(self):
        """移除选中的文件"""
        for item in self.file_list.selectedItems():
            self.file_list.takeItem(self.file_list.row(item))
        # 通过主窗口访问状态栏
        if self.main_window:
            self.main_window.statusBar().showMessage("已移除选中文件")
    
    def clear_list(self):
        """清空文件列表"""
        self.file_list.clear()
        # 通过主窗口访问状态栏
        if self.main_window:
            self.main_window.statusBar().showMessage("文件列表已清空")
    
    def move_up(self):
        """将选中项上移"""
        current_row = self.file_list.currentRow()
        if current_row > 0:
            current_item = self.file_list.takeItem(current_row)
            self.file_list.insertItem(current_row - 1, current_item)
            self.file_list.setCurrentRow(current_row - 1)
    
    def move_down(self):
        """将选中项下移"""
        current_row = self.file_list.currentRow()
        if current_row < self.file_list.count() - 1:
            current_item = self.file_list.takeItem(current_row)
            self.file_list.insertItem(current_row + 1, current_item)
            self.file_list.setCurrentRow(current_row + 1)
    
    def select_output_file(self):
        """选择输出文件位置"""
        options = QFileDialog.Options()
        file, _ = QFileDialog.getSaveFileName(
            self, "保存合并后的PDF", "", "PDF Files (*.pdf);;All Files (*)",
            options=options
        )
        
        if file:
            # 确保文件扩展名为.pdf
            if not file.lower().endswith('.pdf'):
                file += '.pdf'
            self.output_path.setText(file)
    
    def merge_pdfs(self):
        if self.file_list.count() == 0:
            QMessageBox.warning(self, "警告", "没有选择要合并的PDF文件")
            return
        
        output_file = self.output_path.text()
        if output_file == '未选择':
            QMessageBox.warning(self, "警告", "请先设置输出文件位置")
            return
        
        input_files = [self.file_list.item(i).text() for i in range(self.file_list.count())]
        
        if os.path.exists(output_file):
            reply = QMessageBox.question(
                self, "确认", f"文件 '{output_file}' 已存在，是否覆盖?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
        
        try:
            pdf_writer = PyPDF2.PdfWriter()
            total_pages = sum(1 for file in input_files for _ in PyPDF2.PdfReader(file).pages)
            current_page = 0
            self.progress_bar.setMaximum(total_pages)
            
            for file_path in input_files:
                try:
                    with open(file_path, 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        
                        # 处理加密PDF（尝试空密码解密）
                        if pdf_reader.is_encrypted:
                            try:
                                pdf_reader.decrypt("")
                            except PyPDF2.errors.PdfStreamError:
                                QMessageBox.warning(self, "警告", f"{file_path} 加密无法合并，已跳过")
                                continue
                        
                        # 添加页面并更新进度
                        for page in pdf_reader.pages:
                            pdf_writer.add_page(page)
                            current_page += 1
                            self.progress_bar.setValue(current_page)
                    
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"处理文件 {file_path} 失败: {str(e)}")
                    continue
            
            # 写入输出文件
            with open(output_file, 'wb') as f:
                pdf_writer.write(f)
            
            QMessageBox.information(self, "成功", f"合并完成！\n输出路径: {output_file}")
            self.progress_bar.reset()
            self.clear_list()
        
        except Exception as e:
            QMessageBox.critical(self, "合并失败", f"错误原因: {str(e)}")
            self.progress_bar.reset()
