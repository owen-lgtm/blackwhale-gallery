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
        self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 正在注入流光视觉系统 v2.1...")
        counts = self.parent.build_index(self.log_signal)
        self.status_signal.emit({
            "ugc": counts['ugc'], "sora": counts['sora'],
            "time": datetime.now().strftime('%H:%M:%S')
        })
        self.parent.git_sync(self.log_signal)

class PublisherTitanV21(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BlackWhale Titan Evolved v2.1 | Premium Vision")
        self.resize(1000, 850)
        self.setStyleSheet("background-color: #050505; color: #e0e0e0;")
        
        main_widget = QWidget(); self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget); layout.setContentsMargins(25, 25, 25, 25); layout.setSpacing(20)

        self.init_top_panel(layout)

        self.log = QTextEdit(); self.log.setReadOnly(True)
        self.log.setStyleSheet("background: #0d0d0f; color: #00ffcc; border: 1px solid #1a1a1a; border-radius: 15px; padding: 15px; font-family: 'Consolas';")
        layout.addWidget(self.log)

        self.btn_go = QPushButton("✨ 执行流光视觉部署 (v2.1 Premium)")
        self.btn_go.setFixedHeight(85)
        self.btn_go.setStyleSheet("QPushButton { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0057ff, stop:1 #00c6ff); color: white; font-size: 22px; font-weight: bold; border-radius: 20px; border: none; } QPushButton:hover { transform: scale(1.01); }")
        self.btn_go.clicked.connect(self.start_deploy)
        layout.addWidget(self.btn_go)

        self.thread = DeployThread(self)
        self.thread.log_signal.connect(self.update_log)
        self.thread.status_signal.connect(self.update_status)

    def init_top_panel(self, parent_layout):
        panel = QFrame(); panel.setFixedHeight(120); panel.setStyleSheet("background: #111; border-radius: 20px; border: 1px solid #222;")
        panel_lay = QHBoxLayout(panel)
        self.lay_ugc, self.stat_ugc = self.create_stat_widget("UGC 案例库", "0", "#00ffcc")
        self.lay_sora, self.stat_sora = self.create_stat_widget("Sora2 创作案例 (100+)", "0", "#ff007c")
        self.lay_time, self.stat_time = self.create_stat_widget("最后同步", "--:--", "#ffffff")
        panel_lay.addLayout(self.lay_ugc); panel_lay.addLayout(self.lay_sora); panel_lay.addLayout(self.lay_time)
        parent_layout.addWidget(panel)

    def create_stat_widget(self, title, value, color):
        lay = QVBoxLayout()
        t_label = QLabel(title); t_label.setStyleSheet("color: #888; font-size: 14px; border:none;")
        v_label = QLabel(value); v_label.setStyleSheet(f"color: {color}; font-size: 30px; font-weight: bold; border:none;")
        lay.addWidget(t_label, alignment=Qt.AlignCenter); lay.addWidget(v_label, alignment=Qt.AlignCenter)
        return lay, {"val": v_label}

    def update_log(self, text):
        self.log.append(text)
        self.log.verticalScrollBar().setValue(self.log.verticalScrollBar().maximum())

    def update_status(self, data):
        self.stat_ugc["val"].setText(str(data['ugc']))
        self.stat_sora["val"].setText(str(data['sora']))
        self.stat_time["val"].setText(data['time'])

    def start_deploy(self):
        self.btn_go.setEnabled(False); self.thread.start()

    def build_index(self, logger):
        SORA_DIR, UGC_DIR, HEADER_DIR, COURSE_DIR = "sora2", "ugc", "头图", "课程图"
        for d in [SORA_DIR, UGC_DIR, HEADER_DIR, COURSE_DIR]:
            if not os.path.exists(d): os.makedirs(d)

        hero_imgs = [f"头图/{f}" for f in os.listdir(HEADER_DIR) if f.lower().endswith(('.png','.jpg','.jpeg','.webp'))]
        hero_wall = "".join([f'<img src="{img}" class="float-img" style="top:{random.randint(15, 80)}%; {"left" if i%2==0 else "right"}:{random.randint(2, 18)}%; animation-delay:{i*0.6}s;">' for i, img in enumerate(hero_imgs)])
        course_imgs = [f"课程图/{f}" for f in os.listdir(COURSE_DIR) if f.lower().endswith(('.png','.jpg','.jpeg','.webp'))]
        course_html = "".join([f'<img src="{img}" style="width:100%; margin-bottom:40px; border-radius:25px; box-shadow:0 20px 50px rgba(0,0,0,0.05);">' for img in course_imgs])

        html_content = f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <title>BlackWhale | 数字化内容库</title>
    <style>
        :root {{ --blue: #0057ff; }}
        body {{ background: #fff; color: #1d1d1f; font-family: "SF Pro Display", "Helvetica Neue", sans-serif; margin: 0; overflow-x: hidden; }}
        
        /* 流光线条背景系统 */
        .hero {{ height: 100vh; display: flex; align-items: center; justify-content: center; position: relative; background: #fff; overflow: hidden; }}
        .bg-lines {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; pointer-events: none; }}
        .line {{ position: absolute; background: linear-gradient(90deg, transparent, rgba(0,87,255,0.1), transparent); height: 1px; width: 100%; animation: flow 8s infinite linear; }}
        @keyframes flow {{ 0% {{ transform: translateX(-100%); }} 100% {{ transform: translateX(100%); }} }}
        
        /* 进入动效 */
        .hero-content {{ z-index: 10; text-align: center; animation: fadeInUp 1s cubic-bezier(0.2, 1, 0.3, 1); }}
        @keyframes fadeInUp {{ from {{ opacity: 0; transform: translateY(30px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        
        .hero h1 {{ font-size: 72px; font-weight: 800; margin-bottom: 30px; letter-spacing: -3px; line-height: 1.05; color: #000; }}
        
        /* 极简排版小字部分 - 去除图标，对标 Behance */
        .hero-list {{ display: flex; flex-direction: column; gap: 10px; margin-bottom: 40px; }}
        .hero-list p {{ font-size: 19px; color: #86868b; margin: 0; font-weight: 400; letter-spacing: -0.2px; }}
        
        /* 高端联系按钮 */
        .contact-btn {{ display: inline-block; padding: 20px 50px; background: #000; color: #fff; border-radius: 60px; font-weight: 600; font-size: 18px; cursor: pointer; transition: all 0.4s; text-decoration: none; border: none; }}
        .contact-btn:hover {{ background: var(--blue); transform: scale(1.05); box-shadow: 0 20px 40px rgba(0,87,255,0.2); }}

        .float-img {{ position: absolute; width: 150px; height: 150px; object-fit: cover; border-radius: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); transition: 0.8s cubic-bezier(0.2, 1, 0.3, 1); z-index: 2; animation: breathe 6s infinite ease-in-out; }}
        .float-img:hover {{ transform: scale(1.15) !important; z-index: 100; box-shadow: 0 30px 60px rgba(0,0,0,0.12); }}
        @keyframes breathe {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-20px); }} }}

        .nav-bar {{ position: sticky; top: 0; background: rgba(255,255,255,0.7); backdrop-filter: blur(30px); display: flex; width: 100%; height: 90px; border-bottom: 1px solid #f2f2f2; z-index: 1000; }}
        .nav-item {{ flex: 1; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 700; cursor: pointer; color: #86868b; transition: 0.3s; }}
        .nav-item.active {{ color: #000; box-shadow: inset 0 -3px 0 #000; }}

        /* 二维码交互 */
        .qr-side {{ position: fixed; right: 40px; bottom: 40px; z-index: 500; cursor: zoom-in; animation: fadeInUp 1.5s ease-out; }}
        .qr-side img {{ width: 110px; border-radius: 18px; border: 4px solid #fff; box-shadow: 0 10px 30px rgba(0,0,0,0.08); }}
        #qrFull {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(255,255,255,0.98); z-index: 10000; align-items: center; justify-content: center; cursor: zoom-out; animation: fadeIn 0.3s; }}
        #qrFull img {{ width: 420px; border-radius: 40px; box-shadow: 0 40px 100px rgba(0,0,0,0.1); }}
        
        .tab-content {{ display: none; padding: 60px 5%; animation: fadeIn 0.6s; }}
        .tab-content.active {{ display: block; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 40px; }}
        .video-card {{ position: relative; background: #f5f5f7; border-radius: 30px; overflow: hidden; aspect-ratio: 9/16; cursor: pointer; transition: 0.5s cubic-bezier(0.2, 1, 0.3, 1); }}
        .video-card:hover {{ transform: scale(1.04); box-shadow: 0 30px 60px rgba(0,0,0,0.1); }}
        .video-card video {{ width: 100%; height: 100%; object-fit: cover; }}
        
        @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
    </style>
</head>
<body>
    <div class="hero">
        <div class="bg-lines">
            <div class="line" style="top:20%; animation-duration:12s;"></div>
            <div class="line" style="top:40%; animation-duration:15s; animation-delay:-2s;"></div>
            <div class="line" style="top:60%; animation-duration:10s; animation-delay:-5s;"></div>
            <div class="line" style="top:80%; animation-duration:18s;"></div>
        </div>
        {hero_wall}
        <div class="hero-content">
            <h1>60节TikTok UGC带货<br>视频创作系统课</h1>
            <div class="hero-list">
                <p>60节系统化UGC带货内容生成与AI创作（持续更新中）</p>
                <p>系统化AI生文/图/视频/音频从基础、实操到进阶</p>
                <p>原生感TIKTOK UGC带货视频一键批量生成工具</p>
                <p>批量自产自然流橱窗矩阵与原生感UGC带货视频创作</p>
            </div>
            <button class="contact-btn" onclick="toggleQR(true)">立即咨询加入 BlackWhale</button>
        </div>
    </div>
    
    <div class="nav-bar">
        <div class="nav-item" onclick="showTab('ugc', this)">UGC实战案例</div>
        <div class="nav-item active" onclick="showTab('sora', this)">Sora2 创作案例 (100+)</div>
        <div class="nav-item" onclick="showTab('course', this)">课程大纲详情</div>
    </div>

    <div id="ugc" class="tab-content"><div class="grid">{self.gen_cards(UGC_DIR, "详见课程内部策略库", logger)}</div></div>
    <div id="sora" class="tab-content active"><div class="grid">{self.gen_cards(SORA_DIR, None, logger)}</div></div>
    <div id="course" class="tab-content"><div style="max-width:1100px; margin:0 auto;">{course_html}</div></div>

    <div class="qr-side" onclick="toggleQR(true)"><img src="wechat_qr.png"></div>
    <div id="qrFull" onclick="toggleQR(false)"><img src="wechat_qr.png"></div>

    <script>
        function showTab(id, el) {{
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            document.getElementById(id).classList.add('active');
            el.classList.add('active');
        }}
        function toggleQR(show) {{ document.getElementById('qrFull').style.display = show ? 'flex' : 'none'; }}
    </script>
</body>
</html>"""
        with open("index.html", "w", encoding="utf-8") as f: f.write(html_content)
        ugc_count = len([d for d in os.listdir(UGC_DIR) if os.path.isdir(os.path.join(UGC_DIR, d))])
        sora_count = len([d for d in os.listdir(SORA_DIR) if os.path.isdir(os.path.join(SORA_DIR, d))])
        return {'ugc': ugc_count, 'sora': sora_count}

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
            logger.emit("[3/3] 正在启动静默推送系统...")
            def run_git(args): return subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            run_git(["git", "config", "--global", "credential.helper", "store"])
            run_git(["git", "add", "."])
            run_git(["git", "commit", "-m", f"Titan_v2.1_Premium_{datetime.now().strftime('%H%M')}"])
            res = run_git(["git", "push", "origin", "main"])
            if res.returncode == 0: logger.emit("🎉 部署成功！v2.1 Premium 视觉版已上线。")
            else: logger.emit(f"❌ Git 提示: {res.stderr}")
        except Exception as e: logger.emit(f"❌ 异常: {str(e)}")
        finally: self.btn_go.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv); win = PublisherTitanV21(); win.show(); sys.exit(app.exec())