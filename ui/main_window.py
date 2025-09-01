from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout
from .path_manager import PathManagerPanel
from .panel.image_converter_panel import ImageConverter
from .panel.video_converter_panel import VideoConverter  # 我们等下会创建 video_converter.py
# from .panel.pdf_merger_panel import PathManagerPanel  # 我们等下会创建 path_manager.py


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("图片转换工具")
        self.setGeometry(100, 100, 800, 600)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # 初始化路径管理器和功能面板
        self.pdf_merger_panel = PathManagerPanel()
        self.image_converter_panel = ImageConverter()
        self.video_converter_panel = VideoConverter()

        # 水平布局，左边是路径列表，右边是功能面板
        layout = QHBoxLayout()
        layout.addWidget(self.pdf_merger_panel, 1)   # 左边占 1 份
        layout.addWidget(self.image_converter_panel, 3)  # 右边占 3 份
        layout.addWidget(self.video_converter_panel, 3)  # 右边占 3 份

        main_widget.setLayout(layout)