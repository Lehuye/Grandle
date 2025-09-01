import sys
from PyQt5 import QtGui  # 之前添加的导入
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                             QHBoxLayout, QListWidget, QFileDialog, QLabel, 
                             QWidget, QMessageBox, QComboBox, QTabWidget, QProgressBar)  # 添加这一行
from ui.panel.image_converter_panel import ImageConverter
from ui.panel.video_converter_panel import VideoConverter
from ui.panel.pdf_merger_panel import PDFMergerPanel

class MainWindow(QMainWindow):
    """主窗口"""
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("多功能文件处理工具")
        self.setGeometry(300, 300, 600, 400)
        
        # 创建标签页控件
        tab_widget = QTabWidget()
        
        # 添加图片转换标签页
        self.image_converter = ImageConverter()
        tab_widget.addTab(self.image_converter, "图片转换")

        # 添加视频转换标签页
        self.video_converter = VideoConverter()
        tab_widget.addTab(self.video_converter, "视频转换")
        
        # 添加PDF合并标签页
        self.pdf_merger = PDFMergerPanel(self)  # 传递主窗口引用
        tab_widget.addTab(self.pdf_merger, "PDF合并")

        
        self.setCentralWidget(tab_widget)
        
        # 状态栏
        self.statusBar().showMessage('就绪')
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # 改进字体设置，尝试多种中文字体
    font_families = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC", "Arial Unicode MS"]
    for family in font_families:
        font = app.font()
        font.setFamily(family)
        app.setFont(font)
        # 测试字体是否可用
        test_font = QtGui.QFont(family)
        if test_font.exactMatch():
            break
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
