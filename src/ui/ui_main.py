import os
import tkinter as tk
from tkinter import ttk

from src.ui.basic_ui import BasicUI
from src.ui.tab_kingscada import TabKingSCDAD

import logging
logger = logging.getLogger(__name__)

class MainUI(BasicUI):
    def __init__(self, root, base_dir):
        self.root = root
        #窗口标题
        self.root.title("SCADA Tools")
        #窗口大小
        self.root.geometry("1000x500")
        #窗口缩放禁用
        root.resizable(False, False)
        # 图标路径
        icon_path = os.path.join(base_dir, "Image", "icon.png")
        # 使用 PNG 图标
        if os.path.exists(icon_path):
            self.icon_image = tk.PhotoImage(file=icon_path)
            root.iconphoto(True, self.icon_image)
        else:
            logger.warning(f"未找到图标路径: {icon_path}")
        # Notebook
        self.tab_control = ttk.Notebook(root)
        self.tab_control.pack(expand=1, fill="both")

        # Tabs
        self.tabs = {
            "KingSCADA点表生成": TabKingSCDAD(self.tab_control, base_dir),
        }

        for name, tab in self.tabs.items():
            self.tab_control.add(tab, text=name)
