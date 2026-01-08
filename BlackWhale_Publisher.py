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
        self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 启动 v2.1 Premium 视觉版引擎...")
        counts = self.parent.build_index(self.log_signal)
        self.status_signal.emit({
            "ugc": counts['ugc'], "sora": counts['sora'],
            "time": datetime.now().strftime('%H:%M:%S')
        })
        self.parent.git_sync(self.log_signal)

class PublisherTitanV21(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BlackWhale Titan Evolved v2.1 Premium")
        self.resize(1000, 850)
        self.setStyleSheet("background-color: #050505; color: #e0e0e0;")
        
        main_widget = QWidget(); self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget); layout.setContentsMargins(25, 25, 25, 25); layout.setSpacing(20)

        self.init_top_panel(layout)

        self.log = QTextEdit(); self.log.setReadOnly(True)
        self.log.setStyleSheet("background: #0d0d0f; color: #00ffcc; border: 1px solid #1a1a1a; border-radius: 15px; padding: 15px; font-family: 'Consolas';")
        layout.addWidget(self.log)

        self.btn_go = QPushButton("✨ 部署 v2.1 Premium (流光视觉 & 增量同步)")
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
        self.lay_sora, self.stat_sora = self.create_stat_widget("Sora2 创作案例", "0", "#ff007c")
        self.lay_time, self.stat_time = self.create_stat_widget("云端同步状态", "待命", "#ffffff")
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
        self.stat_time["val"].setText(f"同步于 {data['time']}")

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
    <title>BlackWhale | 60节TIKTOK UGC AI创作系统课</title>
    <style>
        :root {{ --blue: #0057ff; --aurora: linear-gradient(120deg, #fdfbfb 0%, #ebedee 100%); }}
        body {{ background: #fff; color: #1d1d1f; font-family: "SF Pro Display", sans-serif; margin: 0; overflow-x: hidden; }}
        
        /* 流光背景与进入动效 */
        .hero {{ height: 95vh; display: flex; align-items: center; justify-content: center; position: relative; background: #fff; overflow: hidden; }}
        .hero::before {{ content: ""; position: absolute; width: 200%; height: 200%; background: radial-gradient(circle at 50% 50%, rgba(0,87,255,0.05) 0%, rgba(255,255,255,0) 50%); animation: auroraFlow 20s infinite alternate; }}
        @keyframes auroraFlow {{ from {{ transform: translate(-10%, -10%) rotate(0deg); }} to {{ transform: translate(10%, 10%) rotate(5deg); }} }}
        
        .float-img {{ position: absolute; width: 160px; height: 160px; object-fit: cover; border-radius: 24px; box-shadow: 0 15px 35px rgba(0,0,0,0.08); transition: 0.8s cubic-bezier(0.2, 1, 0.3, 1); animation: enterUp 1.2s ease-out backwards, breathe 8s infinite ease-in-out; }}
        .float-img:hover {{ transform: scale(1.1) rotate(2deg) !important; z-index: 100; }}
        
        .hero-content {{ z-index: 10; text-align: center; animation: enterUp 1s ease-out; }}
        .hero h1 {{ font-size: 68px; font-weight: 800; margin-bottom: 25px; letter-spacing: -2.5px; line-height: 1.1; }}
        
        /* 文字排版优化：玻璃拟态 */
        .hero-list {{ text-align: left; display: inline-block; background: rgba(255,255,255,0.4); padding: 40px; border-radius: 32px; backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.6); margin-bottom: 30px; }}
        .hero-list p {{ font-size: 18px; color: #424245; margin: 12px 0; font-weight: 500; }}
        
        /* 联系按钮 */
        .contact-btn {{ display: inline-flex; align-items: center; padding: 18px 45px; background: #1d1d1f; color: #fff; border-radius: 50px; font-weight: 600; font-size: 18px; cursor: pointer; transition: 0.3s; text-decoration: none; border: none; }}
        .contact-btn:hover {{ transform: scale(1.05); background: var(--blue); box-shadow: 0 15px 30px rgba(0,87,255,0.3); }}

        .nav-bar {{ position: sticky; top: 0; background: rgba(255,255,255,0.8); backdrop-filter: blur(20px); display: flex; width: 100%; height: 90px; border-bottom: 1px solid #f2f2f2; z-index: 1000; }}
        .nav-item {{ flex: 1; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 700; cursor: pointer; color: #86868b; transition: 0.3s; }}
        .nav-item.active {{ color: var(--blue); box-shadow: inset 0 -4px 0 var(--blue); }}
        
        .tab-content {{ display: none; padding: 60px 5%; animation: fadeIn 0.5s; }}
        .tab-content.active {{ display: block; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 40px; }}
        .video-card {{ position: relative; background: #000; border-radius: 28px; overflow: hidden; aspect-ratio: 9/16; cursor: pointer; transition: 0.5s cubic-bezier(0.2, 1, 0.3, 1); box-shadow: 0 20px 40px rgba(0,0,0,0.1); }}
        .video-card:hover {{ transform: scale(1.06); }}
        .video-card video {{ width: 100%; height: 100%; object-fit: cover; }}
        
        /* 二维码样式 */
        .qr-side {{ position: fixed; right: 40px; bottom: 40px; z-index: 500; text-align: center; cursor: zoom-in; animation: enterUp 1.5s ease-out backwards; }}
        .qr-side img {{ width: 120px; border-radius: 20px; border: 5px solid #fff; box-shadow: 0 15px 40px rgba(0,0,0,0.12); }}
        #qrFull {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(255,255,255,0.95); backdrop-filter: blur(15px); z-index: 10000; align-items: center; justify-content: center; cursor: zoom-out; }}
        #qrFull img {{ width: 450px; border-radius: 40px; box-shadow: 0 40px 80px rgba(0,0,0,0.15); }}

        @keyframes enterUp {{ from {{ opacity: 0; transform: translateY(40px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        @keyframes breathe {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-20px); }} }}
        @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}

        /* 弹窗样式 */
        .modal {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.95); z-index: 9999; align-items: center; justify-content: center; }}
        .modal-body {{ width: 92%; max-width: 1350px; height: 85vh; background: #fff; border-radius: 40px; display: flex; overflow: hidden; }}
        .modal-left {{ flex: 1.6; background: #000; }}
        .modal-left video {{ width: 100%; height: 100%; object-fit: contain; }}
        .modal-right {{ flex: 1; padding: 60px; display: flex; flex-direction: column; }}
        .prompt-box {{ background: #f5f5f7; padding: 30px; border-radius: 24px; font-family: 'SF Mono', monospace; flex: 1; overflow-y: auto; line-height: 1.6; color: #1d1d1f; }}
    </style>
</head>
<body>
    <div class="hero">
        {hero_wall}
        <div class="hero-content">
            <h1>60节TIKTOK UGC带货<br>视频创作系统课</h1>
            <div class="hero-list">
                <p>🚀 60节系统化UGC带货内容生成与AI创作（持续更新）</p>
                <p>🎨 系统化AI生文/图/视频/音频全流程实操</p>
                <p>🛠 原生感TIKTOK UGC视频一键批量生成工具</p>
                <p>📈 批量自产自然流橱窗矩阵与原生感素材创作</p>
            </div><br>
            <button class="contact-btn" onclick="toggleQR(true)">立即咨询加入 BlackWhale</button>
        </div>
    </div>
    
    <div class="nav-bar">
        <div class="nav-item" onclick="showTab('ugc', this)">UGC实战案例</div>
        <div class="nav-item active" onclick="showTab('sora', this)">Sora2创作案例 (100+)</div>
        <div class="nav-item" onclick="showTab('course', this)">课程大纲详情</div>
    </div>

    <div id="ugc" class="tab-content"><div class="grid">{self.gen_cards(UGC_DIR, "详见课程内部策略库", logger)}</div></div>
    <div id="sora" class="tab-content active"><div class="grid">{self.gen_cards(SORA_DIR, None, logger)}</div></div>
    <div id="course" class="tab-content"><div style="max-width:1100px; margin:0 auto;">{course_html}</div></div>

    <div class="qr-side" onclick="toggleQR(true)"><img src="wechat_qr.png"><p style="font-weight:700; color:#888; margin-top:10px;">扫码咨询详情</p></div>
    <div id="qrFull" onclick="toggleQR(false)"><img src="wechat_qr.png"></div>

    <div id="videoModal" class="modal" onclick="closeModal()">
        <div class="modal-body" onclick="event.stopPropagation()">
            <div class="modal-left"><video id="mVideo" controls autoplay></video></div>
            <div class="modal-right">
                <h2 id="mTitle" style="font-size:32px; margin-top:0;"></h2>
                <p style="color:var(--blue); font-weight:700;">💡 创作提示词与解析:</p>
                <div class="prompt-box" id="mPrompt"></div>
                <button style="margin-top:25px; padding:20px; background:var(--blue); color:#fff; border:none; border-radius:15px; font-weight:700; cursor:pointer;" onclick="copyText()">复制提示词内容</button>
            </div>
        </div>
    </div>

    <script>
        function showTab(id, el) {{
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            document.getElementById(id).classList.add('active');
            el.classList.add('active');
        }}
        function openModal(vUrl, title, prompt) {{
            document.getElementById('mVideo').src = vUrl;
            document.getElementById('mTitle').innerText = title;
            document.getElementById('mPrompt').innerText = prompt;
            document.getElementById('videoModal').style.display = 'flex';
        }}
        function closeModal() {{ document.getElementById('videoModal').style.display = 'none'; document.getElementById('mVideo').pause(); }}
        function toggleQR(show) {{ document.getElementById('qrFull').style.display = show ? 'flex' : 'none'; }}
        function copyText() {{ navigator.clipboard.writeText(document.getElementById('mPrompt').innerText).then(() => alert('✅ 内容已复制')); }}
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
            info_p = f"{folder}/{t}/info.txt"
            title, prompt = t, fixed_prompt if fixed_prompt else "解析中..."
            if not fixed_prompt and os.path.exists(info_p):
                with open(info_p, "r", encoding="utf-8", errors="ignore") as f:
                    c = f.read()
                    if "标题:" in c: title = c.split("标题:")[1].split("提示词:")[0].strip()
                    if "提示词:" in c: prompt = c.split("提示词:")[1].strip().replace('"', '&quot;')
            cards += f'<div class="video-card" onclick="openModal(\'{v_rel}\', \'{title}\', `{prompt}`)"><video muted loop onmouseover="this.play()" onmouseout="this.pause()"><source src="{v_rel}" type="video/mp4"></video><div style="position:absolute; bottom:20px; left:20px; color:#fff; font-weight:700; text-shadow:0 2px 10px rgba(0,0,0,0.5);">{title}</div></div>'
        return cards

    def git_sync(self, logger):
        try:
            logger.emit("[3/3] 执行 Git v2.1 增量静默推送...")
            def run_git(args): return subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            run_git(["git", "config", "--global", "credential.helper", "store"])
            run_git(["git", "add", "."])
            run_git(["git", "commit", "-m", f"Titan_v2.1_Premium_{datetime.now().strftime('%H%M')}"])
            res = run_git(["git", "push", "origin", "main"])
            if res.returncode == 0: logger.emit("🎉 部署成功！v2.1 Premium 已上线。")
            else: logger.emit(f"❌ Git 提示: {res.stderr}")
        except Exception as e: logger.emit(f"❌ 异常: {str(e)}")
        finally: self.btn_go.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv); win = PublisherTitanV21(); win.show(); sys.exit(app.exec())