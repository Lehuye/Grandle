#!/usr/bin/env python3
import os
import sys
import uuid
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                             QHBoxLayout, QListWidget, QFileDialog, QLabel, 
                             QWidget, QMessageBox, QComboBox, QTabWidget, QProgressBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5 import QtGui
from utils import allowed_file  # 复用已有的文件检查工具函数


class ConvertWorker(QThread):
    """后台转换线程，避免UI卡顿"""
    progress_updated = pyqtSignal(int)
    conversion_finished = pyqtSignal(int, list)  # 成功数量, 失败文件列表

    def __init__(self, file_paths, convert_type, output_dir=None):
        super().__init__()
        self.file_paths = file_paths
        self.convert_type = convert_type
        self.output_dir = output_dir
        self.total_files = len(file_paths)

    def run(self):
        success_count = 0
        failed_files = []
        
        for i, file_path in enumerate(self.file_paths):
            # 更新进度
            progress = int((i + 1) / self.total_files * 100)
            self.progress_updated.emit(progress)
            
            # 检查文件是否合法
            if not allowed_file(file_path, {'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv'}):
                failed_files.append(file_path)
                continue
            
            try:
                # 确定输出路径
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                if self.output_dir:
                    output_path = os.path.join(self.output_dir, f"{base_name}.{self.convert_type}")
                else:
                    output_path = os.path.join(os.path.dirname(file_path), f"{base_name}.{self.convert_type}")
                
                # 使用ffmpeg进行转换
                # 基本转换命令，根据目标格式设置不同参数
                if self.convert_type == 'webp':
                    # WebP是动图格式，使用特定参数
                    cmd = [
                        'ffmpeg', '-y', '-i', file_path,
                        '-vcodec', 'libwebp',
                        '-filter:v', 'fps=10',  # WebP通常帧率较低
                        '-lossless', '0',       # 非无损模式
                        '-compression_level', '6',
                        '-loop', '0',           # 无限循环
                        output_path
                    ]
                else:
                    # 通用视频格式转换
                    cmd = [
                        'ffmpeg', '-y', '-i', file_path,
                        '-c:v', 'libx264' if self.convert_type == 'mp4' else 'libvpx-vp9',
                        '-crf', '23', '-preset', 'medium',
                        '-c:a', 'aac' if self.convert_type == 'mp4' else 'opus',
                        '-b:a', '128k',
                        output_path
                    ]
                
                # 执行转换命令
                result = subprocess.run(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                if result.returncode != 0:
                    raise Exception(f"转换失败: {result.stderr}")
                
                success_count += 1
            except Exception as e:
                print(f"处理 {file_path} 时出错: {str(e)}")
                failed_files.append(file_path)
        
        self.conversion_finished.emit(success_count, failed_files)


class VideoConverter(QWidget):
    """视频转换功能面板"""
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()

        # 转换格式选择
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("选择转换格式:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["mp4", "webm", "webp", "mkv", "avi"])
        format_layout.addWidget(self.format_combo)
        layout.addLayout(format_layout)

        # 输出目录选择
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("输出目录:"))
        self.output_dir_label = QLabel("使用源文件目录")
        self.output_dir_label.setStyleSheet("color: #666; font-style: italic;")
        select_output_btn = QPushButton("选择目录")
        select_output_btn.setMaximumWidth(100)
        select_output_btn.clicked.connect(self.select_output_dir)
        
        output_layout.addWidget(self.output_dir_label)
        output_layout.addWidget(select_output_btn)
        output_layout.setStretch(0, 1)  # 让标签占满剩余空间
        layout.addLayout(output_layout)

        # 转换按钮
        convert_btn = QPushButton("选择文件并转换")
        convert_btn.clicked.connect(self.select_and_convert)
        layout.addWidget(convert_btn)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)
        self.output_dir = None  # 存储用户选择的输出目录

    def select_output_dir(self):
        """选择输出目录"""
        dir_path = QFileDialog.getExistingDirectory(
            self, "选择输出目录", os.path.expanduser("~")
        )
        if dir_path:
            self.output_dir = dir_path
            self.output_dir_label.setText(dir_path)
            self.output_dir_label.setToolTip(dir_path)
            self.output_dir_label.setStyleSheet("")  # 重置样式

    def select_and_convert(self):
        """选择并转换视频文件"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "选择多个视频文件", "", 
            "视频文件 (*.mp4 *.avi *.mov *.mkv *.flv *.wmv *.webm)"
        )
        if not file_paths:
            return
    
        convert_type = self.format_combo.currentText()
        
        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # 创建并启动转换线程
        self.worker = ConvertWorker(file_paths, convert_type, self.output_dir)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.conversion_finished.connect(self.on_conversion_finished)
        self.worker.start()

    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)

    def on_conversion_finished(self, success_count, failed_files):
        """转换完成处理"""
        self.progress_bar.setVisible(False)
        
        message = f"成功转换 {success_count} 个文件。"
        if failed_files:
            message += f"\n失败文件 ({len(failed_files)}):\n" + "\n".join(failed_files[:5])
            if len(failed_files) > 5:
                message += f"\n... 还有 {len(failed_files) - 5} 个文件"
            QMessageBox.warning(self, "部分失败", message)
        else:
            QMessageBox.information(self, "成功", message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("视频转换器")
    window.setGeometry(100, 100, 600, 300)
    window.setCentralWidget(VideoConverter())
    window.show()
    sys.exit(app.exec_())
