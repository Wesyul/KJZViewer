"""
KJZ 红外图像查看器
主程序入口
"""
import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("KJZ 红外图像查看器")
    app.setOrganizationName("KJZ")
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
