import os, subprocess, sys, random
from datetime import datetime
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QTextEdit, QLabel, QFrame, QLayout
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QFont, QColor

class DeployThread(QThread):
    log_signal = Signal(str)
    status_signal = Signal(dict)

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def run(self):
        start_time = datetime.now()
        self.log_signal.emit(f"[{start_time.strftime('%H:%M:%S')}] 🚀 启动 Titan Evolved 实时同步引擎...")
        
        # 1. 扫描与渲染
        counts = self.parent.build_index(self.log_signal)
        
        # 2. 更新面板状态
        self.status_signal.emit({
            "ugc": counts['ugc'],
            "sora": counts['sora'],
            "time": datetime.now().strftime('%H:%M:%S')
        })
        
        # 3. Git 同步
        self.parent.git_sync(self.log_signal)

class PublisherTitan(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Titan Evolved v20.0.20260108")
        self.resize(1000, 800)
        self.setStyleSheet("background-color: #050505; color: #e0e0e0;")
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 顶部面板 (Top Panel)
        self.init_top_panel(layout)

        # 日志区域
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet("""
            background: #0a0a0c; 
            color: #00ffcc; 
            font-family: 'Cascadia Code', 'Consolas'; 
            font-size: 13px; 
            border: 1px solid #222; 
            border-radius: 12px; 
            padding: 15px;
        """)
        layout.addWidget(self.log)

        # 部署按钮
        self.btn_go = QPushButton("🚀 执 行 全 局 跨 境 同 步")
        self.btn_go.setFixedHeight(70)
        self.btn_go.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1a73e8, stop:1 #00e5ff);
                color: white;
                font-size: 20px;
                font-weight: bold;
                border-radius: 15px;
                border: none;
            }
            QPushButton:hover { background: #1557b0; }
            QPushButton:disabled { background: #333; color: #777; }
        """)
        self.btn_go.clicked.connect(self.start_deploy)
        layout.addWidget(self.btn_go)

        self.thread = DeployThread(self)
        self.thread.log_signal.connect(self.update_log)
        self.thread.status_signal.connect(self.update_status)

    def init_top_panel(self, parent_layout):
        panel = QFrame()
        panel.setFixedHeight(110)
        panel.setStyleSheet("background: #111; border-radius: 15px; border: 1px solid #222;")
        panel_lay = QHBoxLayout(panel)

        # 修正：将返回的布局和用于更新的字典分开
        self.lay_ugc, self.stat_ugc = self.create_stat_widget("UGC 案例", "0", "#00ffcc")
        self.lay_sora, self.stat_sora = self.create_stat_widget("Sora 案例", "0", "#ff007c")
        self.lay_time, self.stat_time = self.create_stat_widget("最后同步", "--:--", "#ffffff")

        panel_lay.addLayout(self.lay_ugc)
        panel_lay.addLayout(self.lay_sora)
        panel_lay.addLayout(self.lay_time)
        parent_layout.addWidget(panel)

    def create_stat_widget(self, title, value, color):
        lay = QVBoxLayout()
        t_label = QLabel(title)
        t_label.setStyleSheet("color: #888; font-size: 14px; border: none;")
        v_label = QLabel(value)
        v_label.setStyleSheet(f"color: {color}; font-size: 28px; font-weight: bold; border: none;")
        lay.addWidget(t_label, alignment=Qt.AlignCenter)
        lay.addWidget(v_label, alignment=Qt.AlignCenter)
        return lay, {"val": v_label}

    def update_log(self, text):
        self.log.append(text)
        self.log.verticalScrollBar().setValue(self.log.verticalScrollBar().maximum())

    def update_status(self, data):
        self.stat_ugc["val"].setText(str(data['ugc']))
        self.stat_sora["val"].setText(str(data['sora']))
        self.stat_time["val"].setText(data['time'])

    def start_deploy(self):
        self.btn_go.setEnabled(False)
        self.thread.start()

    def build_index(self, logger):
        SORA_DIR, UGC_DIR = "sora2", "ugc"
        HEADER_DIR, COURSE_DIR = "头图", "课程图"
        for d in [SORA_DIR, UGC_DIR, HEADER_DIR, COURSE_DIR]:
            if not os.path.exists(d): os.makedirs(d)

        ugc_count = len([d for d in os.listdir(UGC_DIR) if os.path.isdir(os.path.join(UGC_DIR, d))])
        sora_count = len([d for d in os.listdir(SORA_DIR) if os.path.isdir(os.path.join(SORA_DIR, d))])
        
        # 保持 v2.5 的核心渲染逻辑（生成 index.html）
        self.generate_html(SORA_DIR, UGC_DIR, HEADER_DIR, COURSE_DIR, logger)
        
        logger.emit(f"[1/3] 扫描完成: UGC({ugc_count}) | Sora({sora_count})")
        return {'ugc': ugc_count, 'sora': sora_count}

    def generate_html(self, SORA_DIR, UGC_DIR, HEADER_DIR, COURSE_DIR, logger):
        # 复制之前版本中 build_index 里的 HTML 拼接代码
        hero_imgs = [f"头图/{f}" for f in os.listdir(HEADER_DIR) if f.lower().endswith(('.png','.jpg','.jpeg','.webp'))]
        course_imgs = [f"课程图/{f}" for f in os.listdir(COURSE_DIR) if f.lower().endswith(('.png','.jpg','.jpeg','.webp'))]
        hero_wall_html = "".join([f'<img src="{img}" class="float-img" style="top:{random.randint(15, 80)}%; {"left" if i%2==0 else "right"}:{random.randint(2, 18)}%; animation-delay:{i*0.6}s;">' for i, img in enumerate(hero_imgs)])

        html_content = f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <title>BlackWhale | 展示页</title>
    <style>
        body {{ background: #fff; font-family: sans-serif; margin: 0; }}
        /* 此处省略部分冗长的 CSS 以保持代码简洁，建议在本地保留原有的样式代码 */
        .hero {{ height: 50vh; background: #f5f5f7; display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden; }}
        .float-img {{ position: absolute; width: 120px; border-radius: 15px; box-shadow: 0 10px 20px rgba(0,0,0,0.1); }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; padding: 20px; }}
        .video-card {{ background: #000; border-radius: 20px; aspect-ratio: 9/16; overflow: hidden; position: relative; }}
        video {{ width: 100%; height: 100%; object-fit: cover; }}
    </style>
</head>
<body>
    <div class="hero">{hero_wall_html}<h1>BlackWhale 数字化内容库</h1></div>
    <div class="grid">
        {self.gen_cards(UGC_DIR, "UGC 案例", logger)}
        {self.gen_cards(SORA_DIR, None, logger)}
    </div>
</body>
</html>"""
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        logger.emit("[2/3] index.html 已生成。")

    def gen_cards(self, folder, fixed_prompt, logger):
        cards = ""
        if not os.path.exists(folder): return ""
        tasks = sorted([d for d in os.listdir(folder) if d.startswith("Task_")])
        for t in tasks:
            v_rel = f"{folder}/{t}/video.mp4"
            cards += f'<div class="video-card"><video muted loop onmouseover="this.play()" onmouseout="this.pause()"><source src="{v_rel}" type="video/mp4"></video></div>'
        return cards

    def git_sync(self, logger):
        try:
            logger.emit("[3/3] 启动同步流...")
            def run_git(args): return subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            run_git(["git", "add", "."])
            run_git(["git", "commit", "-m", f"Titan_Update_{datetime.now().strftime('%H%M')}"])
            logger.emit("⚡ 正在推送至云端...")
            res = run_git(["git", "push", "origin", "main"])
            if res.returncode == 0: logger.emit("🎉 部署成功！")
            else: logger.emit(f"❌ Git 错误: {res.stderr}")
        except Exception as e: logger.emit(f"❌ 系统异常: {str(e)}")
        finally: self.btn_go.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PublisherTitan()
    win.show()
    sys.exit(app.exec())