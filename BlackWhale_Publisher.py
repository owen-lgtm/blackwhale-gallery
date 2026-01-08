import os, subprocess, sys, random
from datetime import datetime
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QTextEdit, QLabel, QFrame
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QFont, QColor

class DeployThread(QThread):
    log_signal = Signal(str)
    status_signal = Signal(dict)

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def run(self):
        self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 启动 Titan v20.7 顶配引擎...")
        counts = self.parent.build_index(self.log_signal)
        self.status_signal.emit({
            "ugc": counts['ugc'], "sora": counts['sora'],
            "time": datetime.now().strftime('%H:%M:%S')
        })
        self.parent.git_sync(self.log_signal)

class PublisherTitanFinal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Titan Evolved v20.7 | Final High-End Edition")
        self.resize(1000, 850)
        self.setStyleSheet("background-color: #050505; color: #e0e0e0;")
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        # --- 顶部面板 (保留 v20.7 功能数据) ---
        self.init_top_panel(layout)

        # --- 日志区域 (磨砂质感) ---
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet("""
            background: #0d0d0f; color: #00ffcc; border: 1px solid #1a1a1a;
            border-radius: 15px; padding: 15px; font-family: 'Cascadia Code'; font-size: 13px;
        """)
        layout.addWidget(self.log)

        # --- 部署按钮 (还原 v2.5 视觉高度) ---
        self.btn_go = QPushButton("🔥 执 行 全 局 跨 境 同 步 (Titan v20.7)")
        self.btn_go.setFixedHeight(85)
        self.btn_go.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0057ff, stop:1 #00c6ff);
                color: white; font-size: 22px; font-weight: bold; border-radius: 20px; border: none;
            }
            QPushButton:hover { transform: scale(1.02); }
            QPushButton:disabled { background: #333; color: #777; }
        """)
        self.btn_go.clicked.connect(self.start_deploy)
        layout.addWidget(self.btn_go)

        self.thread = DeployThread(self)
        self.thread.log_signal.connect(self.update_log)
        self.thread.status_signal.connect(self.update_status)

    def init_top_panel(self, parent_layout):
        panel = QFrame()
        panel.setFixedHeight(120)
        panel.setStyleSheet("background: #111; border-radius: 20px; border: 1px solid #222;")
        panel_lay = QHBoxLayout(panel)
        self.stat_ugc_lay, self.stat_ugc = self.create_stat_widget("UGC 案例库", "0", "#00ffcc")
        self.stat_sora_lay, self.stat_sora = self.create_stat_widget("Sora2 案例库", "0", "#ff007c")
        self.stat_time_lay, self.stat_time = self.create_stat_widget("云端同步状态", "待命", "#ffffff")
        panel_lay.addLayout(self.stat_ugc_lay)
        panel_lay.addLayout(self.stat_sora_lay)
        panel_lay.addLayout(self.stat_time_lay)
        parent_layout.addWidget(panel)

    def create_stat_widget(self, title, value, color):
        lay = QVBoxLayout()
        t_label = QLabel(title); t_label.setStyleSheet("color: #888; font-size: 14px; border:none;")
        v_label = QLabel(value); v_label.setStyleSheet(f"color: {color}; font-size: 30px; font-weight: bold; border:none;")
        lay.addWidget(t_label, alignment=Qt.AlignCenter)
        lay.addWidget(v_label, alignment=Qt.AlignCenter)
        return lay, {"val": v_label}

    def update_log(self, text):
        self.log.append(text)
        self.log.verticalScrollBar().setValue(self.log.verticalScrollBar().maximum())

    def update_status(self, data):
        self.stat_ugc["val"].setText(str(data['ugc']))
        self.stat_sora["val"].setText(str(data['sora']))
        self.stat_time["val"].setText(f"同步于 {data['time']}")

    def start_deploy(self):
        self.btn_go.setEnabled(False)
        self.thread.start()

    def build_index(self, logger):
        SORA_DIR, UGC_DIR = "sora2", "ugc"
        HEADER_DIR, COURSE_DIR = "头图", "课程图"
        for d in [SORA_DIR, UGC_DIR, HEADER_DIR, COURSE_DIR]:
            if not os.path.exists(d): os.makedirs(d)

        # 获取 v2.5 的 HTML 模板核心 (完整还原 UI 质感)
        hero_imgs = [f"头图/{f}" for f in os.listdir(HEADER_DIR) if f.lower().endswith(('.png','.jpg','.jpeg','.webp'))]
        hero_wall = "".join([f'<img src="{img}" class="float-img" style="top:{random.randint(15, 80)}%; {"left" if i%2==0 else "right"}:{random.randint(2, 18)}%; animation-delay:{i*0.6}s;">' for i, img in enumerate(hero_imgs)])

        # 生成还原 v2.5 视觉的 HTML (仅保留核心架构)
        html_content = f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <title>BlackWhale | 数字化内容库</title>
    <style>
        :root {{ --blue: #0057ff; --apple-grad: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab); }}
        body {{ background: #fff; color: #1d1d1f; font-family: "SF Pro Display", sans-serif; margin: 0; }}
        .hero {{ height: 80vh; display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden; background: #fff; }}
        .float-img {{ position: absolute; width: 155px; height: 155px; border-radius: 22px; box-shadow: 0 15px 35px rgba(0,0,0,0.08); animation: breathe 6s infinite ease-in-out; object-fit: cover; }}
        @keyframes breathe {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-20px); }} }}
        .nav-bar {{ position: sticky; top: 0; background: rgba(255,255,255,0.85); backdrop-filter: blur(20px); display: flex; height: 80px; border-bottom: 1px solid #f2f2f2; z-index: 1000; }}
        .nav-item {{ flex: 1; display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: 700; cursor: pointer; color: #86868b; }}
        .nav-item.active {{ color: var(--blue); box-shadow: inset 0 -4px 0 var(--blue); }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 30px; padding: 40px; }}
        .video-card {{ background: #000; border-radius: 25px; aspect-ratio: 9/16; overflow: hidden; position: relative; cursor: pointer; box-shadow: 0 20px 40px rgba(0,0,0,0.1); }}
        video {{ width: 100%; height: 100%; object-fit: cover; }}
    </style>
</head>
<body>
    <div class="hero">{hero_wall}<h1 style="font-size:60px; z-index:10;">BlackWhale 数字化内容库</h1></div>
    <div class="nav-bar">
        <div class="nav-item" onclick="location.hash='ugc'">UGC 实战案例</div>
        <div class="nav-item active" onclick="location.hash='sora'">Sora2 创作案例</div>
    </div>
    <div class="grid" id="mainGrid">
        {self.gen_cards(UGC_DIR, "UGC 案例", logger)}
        {self.gen_cards(SORA_DIR, "Sora 案例", logger)}
    </div>
</body>
</html>"""
        with open("index.html", "w", encoding="utf-8") as f: f.write(html_content)
        
        ugc_count = len([d for d in os.listdir(UGC_DIR) if os.path.isdir(os.path.join(UGC_DIR, d))])
        sora_count = len([d for d in os.listdir(SORA_DIR) if os.path.isdir(os.path.join(SORA_DIR, d))])
        return {'ugc': ugc_count, 'sora': sora_count}

    def gen_cards(self, folder, prompt_default, logger):
        cards = ""
        if not os.path.exists(folder): return ""
        tasks = sorted([d for d in os.listdir(folder) if d.startswith("Task_")])
        for t in tasks:
            v_rel = f"{folder}/{t}/video.mp4"
            cards += f'<div class="video-card"><video muted loop onmouseover="this.play()" onmouseout="this.pause()"><source src="{v_rel}" type="video/mp4"></video></div>'
        return cards

    def git_sync(self, logger):
        try:
            logger.emit("[3/3] 正在启动静默云端同步 (强制跳过登录窗)...")
            def run_git(args): return subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            
            # 关键：静默模式设置，防止弹出验证窗口
            run_git(["git", "config", "--local", "credential.helper", "manager"])
            
            run_git(["git", "add", "."])
            run_git(["git", "commit", "-m", f"Final_Titan_Update_{datetime.now().strftime('%H%M')}"])
            
            logger.emit("⚡ 正在通过本地凭据推送至 blackwhale-gallery...")
            res = run_git(["git", "push", "origin", "main"])
            
            if res.returncode == 0: logger.emit("🎉 部署完成！UI 已完美呈现。")
            else: logger.emit(f"❌ Git 提示: {res.stderr}")
        except Exception as e: logger.emit(f"❌ 异常: {str(e)}")
        finally: self.btn_go.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PublisherTitanFinal()
    win.show()
    sys.exit(app.exec())