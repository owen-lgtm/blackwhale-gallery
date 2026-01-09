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
        self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] 🧪 启动 v2.3-测试2：注入液态高光引擎...")
        counts = self.parent.build_index(self.log_signal)
        self.status_signal.emit({
            "ugc": counts['ugc'], "sora": counts['sora'],
            "time": datetime.now().strftime('%H:%M:%S')
        })
        self.parent.git_sync(self.log_signal)

class PublisherTitanV23Liquid(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BlackWhale Titan Evolved v2.3-测试2 (Liquid Aura)")
        self.resize(1000, 850)
        self.setStyleSheet("background-color: #050505; color: #e0e0e0;")
        
        main_widget = QWidget(); self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget); layout.setContentsMargins(25, 25, 25, 25); layout.setSpacing(20)

        self.init_top_panel(layout)

        self.log = QTextEdit(); self.log.setReadOnly(True)
        self.log.setStyleSheet("background: #0d0d0f; color: #00ffcc; border: 1px solid #1a1a1a; border-radius: 15px; padding: 15px; font-family: 'Consolas';")
        layout.addWidget(self.log)

        self.btn_go = QPushButton("✨ 执行 v2.3-测试2 (液态高光部署)")
        self.btn_go.setFixedHeight(85)
        self.btn_go.setStyleSheet("QPushButton { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff007c, stop:1 #0057ff); color: white; font-size: 22px; font-weight: bold; border-radius: 20px; border: none; } QPushButton:hover { transform: scale(1.01); }")
        self.btn_go.clicked.connect(self.start_deploy)
        layout.addWidget(self.btn_go)

        self.thread = DeployThread(self)
        self.thread.log_signal.connect(self.update_log)
        self.thread.status_signal.connect(self.update_status)

    def init_top_panel(self, parent_layout):
        panel = QFrame(); panel.setFixedHeight(120); panel.setStyleSheet("background: #111; border-radius: 20px; border: 1px solid #222;")
        panel_lay = QHBoxLayout(panel)
        self.lay_ugc, self.stat_ugc = self.create_stat_widget("UGC 案例库", "0", "#00ffcc")
        self.lay_sora, self.stat_sora = self.create_stat_widget("Sora2 案例 (100+)", "0", "#ff007c")
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
        body, html {{ background: #fff; color: #1d1d1f; font-family: "SF Pro Display", sans-serif; margin: 0; padding: 0; overflow-x: hidden; scroll-behavior: smooth; }}
        
        /* 1. 液态高光波动背景 - 针对测试2优化 */
        .hero {{ height: 100vh; display: flex; align-items: center; justify-content: center; position: relative; background: #fff; overflow: hidden; }}
        
        .liquid-container {{ position: absolute; width: 100%; height: 100%; top: 0; left: 0; z-index: 1; opacity: 0.4; filter: url(#liquid-filter); }}
        .blob {{ position: absolute; width: 600px; height: 600px; border-radius: 50%; filter: blur(60px); animation: move 25s infinite alternate ease-in-out; }}
        .blob-1 {{ background: #e0e7ff; top: -10%; left: 10%; animation-delay: 0s; }}
        .blob-2 {{ background: #fce7f3; bottom: -10%; right: 10%; animation-delay: -5s; }}
        .blob-3 {{ background: #dcfce7; top: 40%; left: 50%; width: 500px; animation-delay: -10s; }}
        .blob-4 {{ background: #fef9c3; top: 10%; right: 20%; width: 400px; animation-delay: -15s; }}

        @keyframes move {{ 
            0% {{ transform: translate(0,0) scale(1) rotate(0); }}
            50% {{ transform: translate(100px, 50px) scale(1.1) rotate(90deg); }}
            100% {{ transform: translate(-50px, 100px) scale(0.9) rotate(180deg); }}
        }}

        /* 2. 核心文本排版 */
        .hero-content {{ z-index: 10; text-align: center; animation: slideUpFade 1.2s cubic-bezier(0.2, 1, 0.3, 1); }}
        .hero h1 {{ font-size: 72px; font-weight: 800; margin: 0 0 25px 0; letter-spacing: -3.5px; line-height: 1.05; color: #000; text-shadow: 0 10px 30px rgba(0,0,0,0.02); }}
        .hero-list {{ display: flex; flex-direction: column; gap: 12px; margin-bottom: 45px; }}
        .hero-list p {{ font-size: 20px; color: #6e6e73; margin: 0; font-weight: 400; letter-spacing: -0.2px; }}
        
        .contact-btn {{ display: inline-block; padding: 22px 65px; background: #000; color: #fff; border-radius: 100px; font-weight: 600; font-size: 18px; cursor: pointer; transition: 0.4s; text-decoration: none; border: none; }}
        .contact-btn:hover {{ background: var(--blue); transform: scale(1.05); box-shadow: 0 25px 50px rgba(0,87,255,0.2); }}

        .float-img {{ position: absolute; width: 160px; height: 160px; object-fit: cover; border-radius: 32px; box-shadow: 0 10px 40px rgba(0,0,0,0.06); transition: 0.8s; z-index: 2; animation: breathe 10s infinite ease-in-out; }}
        
        /* 3. 页面流畅性优化 (100+ 视频支持) */
        .nav-bar {{ position: sticky; top: 0; background: rgba(255,255,255,0.75); backdrop-filter: blur(30px); display: flex; width: 100%; height: 95px; border-bottom: 1px solid rgba(0,0,0,0.05); z-index: 1000; }}
        .nav-item {{ flex: 1; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 700; cursor: pointer; color: #86868b; transition: 0.3s; }}
        .nav-item.active {{ color: #000; box-shadow: inset 0 -4px 0 #000; }}

        .tab-content {{ display: none; opacity: 0; padding: 80px 5%; transition: opacity 0.6s ease; }}
        .tab-content.active {{ display: block; opacity: 1; }}

        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 45px; }}
        .video-card {{ position: relative; background: #000; border-radius: 40px; overflow: hidden; aspect-ratio: 9/16; cursor: pointer; transition: 0.6s cubic-bezier(0.2, 1, 0.3, 1); box-shadow: 0 30px 60px rgba(0,0,0,0.12); }}
        .video-card:hover {{ transform: scale(1.04) translateY(-10px); z-index: 5; }}
        .video-card video {{ width: 100%; height: 100%; object-fit: cover; }}

        /* 弹窗系统保持 v2.0 */
        .modal {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.97); z-index: 9999; align-items: center; justify-content: center; }}
        .modal-body {{ width: 95%; max-width: 1450px; height: 86vh; background: #fff; border-radius: 50px; display: flex; overflow: hidden; }}
        .modal-left {{ flex: 1.6; background: #000; }}
        .modal-left video {{ width: 100%; height: 100%; object-fit: contain; }}
        .modal-right {{ flex: 1; padding: 65px; display: flex; flex-direction: column; overflow-y: auto; }}
        .prompt-box {{ background: #f5f5f7; padding: 35px; border-radius: 30px; font-family: "SF Mono", monospace; line-height: 1.8; color: #1d1d1f; font-size: 16px; flex-grow: 1; }}

        @keyframes slideUpFade {{ from {{ opacity: 0; transform: translateY(60px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        @keyframes breathe {{ 0%, 100% {{ transform: translateY(0) rotate(0deg); }} 50% {{ transform: translateY(-35px) rotate(1deg); }} }}
    </style>
</head>
<body>
    <svg style="display:none;">
        <filter id="liquid-filter">
            <feTurbulence type="fractalNoise" baseFrequency="0.012" numOctaves="3" seed="1">
                <animate attributeName="baseFrequency" dur="30s" values="0.012;0.008;0.012" repeatCount="indefinite" />
            </feTurbulence>
            <feDisplacementMap in="SourceGraphic" scale="80" />
        </filter>
    </svg>

    <div class="hero" id="home">
        <div class="liquid-container">
            <div class="blob blob-1"></div>
            <div class="blob blob-2"></div>
            <div class="blob blob-3"></div>
            <div class="blob blob-4"></div>
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
        <div class="nav-item active" onclick="showTab('sora', this)">Sora2 案例 (100+)</div>
        <div class="nav-item" onclick="showTab('course', this)">课程大纲详情</div>
    </div>

    <div id="ugc" class="tab-content"><div class="grid">{self.gen_cards(UGC_DIR, "详见课程内部策略库", logger)}</div></div>
    <div id="sora" class="tab-content active" style="display:block; opacity:1;"><div class="grid">{self.gen_cards(SORA_DIR, None, logger)}</div></div>
    <div id="course" class="tab-content"><div style="max-width:1150px; margin:0 auto;">{course_html}</div></div>

    <div id="videoModal" class="modal" onclick="closeModal()">
        <div class="modal-body" onclick="event.stopPropagation()">
            <div class="modal-left"><video id="mVideo" controls autoplay></video></div>
            <div class="modal-right">
                <h2 id="mTitle" style="font-size:35px; margin:0 0 25px 0;"></h2>
                <div style="font-weight:700; color:var(--blue); margin-bottom:15px;">🔍 技术解析与提示词:</div>
                <div class="prompt-box" id="mPrompt"></div>
                <button style="margin-top:30px; padding:22px; background:#000; color:#fff; border:none; border-radius:20px; font-weight:700; cursor:pointer;" onclick="copyText()">📋 复制解析内容</button>
            </div>
        </div>
    </div>

    <script>
        function showTab(id, el) {{
            document.querySelectorAll('.tab-content').forEach(t => {{ t.style.display='none'; t.style.opacity='0'; }});
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            const target = document.getElementById(id);
            target.style.display = 'block';
            setTimeout(() => target.style.opacity = '1', 50);
            el.classList.add('active');
            // 解决突兀感：如果已滚动，则平稳锚定在导航栏
            if(window.scrollY > 200) window.scrollTo({{top: window.innerHeight - 95, behavior: 'smooth'}});
        }}
        function openModal(vUrl, title, prompt) {{
            document.getElementById('mVideo').src = vUrl;
            document.getElementById('mTitle').innerText = title;
            document.getElementById('mPrompt').innerText = prompt;
            document.getElementById('videoModal').style.display = 'flex';
        }}
        function closeModal() {{ document.getElementById('videoModal').style.display = 'none'; document.getElementById('mVideo').pause(); }}
        function copyText() {{ navigator.clipboard.writeText(document.getElementById('mPrompt').innerText).then(() => alert('已成功复制')); }}
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
        tasks = sorted([d for d in os.listdir(folder) if d.startswith("Task_")], reverse=True)
        for t in tasks:
            v_rel = f"{folder}/{t}/video.mp4"
            info_p = f"{folder}/{t}/info.txt"
            title, prompt = t, fixed_prompt if fixed_prompt else "内容库深度解析中..."
            if not fixed_prompt and os.path.exists(info_p):
                with open(info_p, "r", encoding="utf-8", errors="ignore") as f:
                    c = f.read()
                    if "标题:" in c: title = c.split("标题:")[1].split("提示词:")[0].strip()
                    if "提示词:" in c: prompt = c.split("提示词:")[1].strip().replace('"', '&quot;')
            # 百级扩展核心：使用 loading="lazy" 确保 100+ 视频不消耗冗余内存
            cards += f'<div class="video-card" onclick="openModal(\'{v_rel}\', \'{title}\', `{prompt}`)"><video muted loop loading="lazy" onmouseover="this.play()" onmouseout="this.pause()"><source src="{v_rel}" type="video/mp4"></video></div>'
        return cards

    def git_sync(self, logger):
        try:
            logger.emit("[3/3] 正在通过 Titan 引擎执行液态部署推送...")
            def run_git(args): return subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            run_git(["git", "config", "--global", "credential.helper", "store"])
            run_git(["git", "add", "."])
            run_git(["git", "commit", "-m", f"Titan_v2.3_Liquid_Beta2_{datetime.now().strftime('%H%M')}"])
            res = run_git(["git", "push", "origin", "main"])
            if res.returncode == 0: logger.emit("🎉 测试2部署成功！液态高光视觉已上线。")
            else: logger.emit(f"❌ 推送失败: {res.stderr}")
        except Exception as e: logger.emit(f"❌ 异常: {str(e)}")
        finally: self.btn_go.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv); win = PublisherTitanV23Liquid(); win.show(); sys.exit(app.exec())