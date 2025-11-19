import sys
import os
import tkinter as tk

from src.core.logger_config import setup_logger
from src.ui.ui_main import MainUI

if __name__ == "__main__":
    # 进行日志配置
    setup_logger()
    # EdgeTTS 打包后 SSL 证书修复 
    try:
        import certifi
        # 强制指定 SSL 证书位置（解决 401 Invalid response）
        os.environ["SSL_CERT_FILE"] = certifi.where()
    except Exception:
        pass
    # 判断是否是打包后的环境
    if getattr(sys, 'frozen', False):
        # 打包后的路径（exe所在的目录）
        base_dir = os.path.dirname(sys.executable)
    else:
        # 普通Python运行时
        base_dir = os.path.dirname(os.path.abspath(__file__))
    # 启动主界面
    root = tk.Tk()
    app = MainUI(root,base_dir)
    root.mainloop()
