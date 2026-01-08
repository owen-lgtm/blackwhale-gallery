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
        self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 启动 Titan v20.7 顶配视觉引擎...")
        counts = self.parent.build_index(self.log_signal)
        self.status_signal.emit({
            "ugc": counts['ugc'], "sora": counts['sora'],
            "time": datetime.now().strftime('%H:%M:%S')
        })
        self.parent.git_sync(self.log_signal)

class PublisherTitanFinal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Titan Evolved v20.7 | 视觉巅峰修复版")
        self.resize(1000, 850)
        self.setStyleSheet("background-color: #050505; color: #e0e0e0;")
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        # 顶部面板
        self.init_top_panel(layout)

        # 日志区域
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet("""
            background: #0d0d0f; color: #00ffcc; border: 1px solid #1a1a1a;
            border-radius: 15px; padding: 15px; font-family: 'Consolas'; font-size: 13px;
        """)
        layout.addWidget(self.log)

        # 部署按钮
        self.btn_go = QPushButton("🔥 部署至 GitHub Pages (还原 v2.5 视觉)")
        self.btn_go.setFixedHeight(85)
        self.btn_go.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0057ff, stop:1 #00c6ff);
                color: white; font-size: 22px; font-weight: bold; border-radius: 20px; border: none;
            }
            QPushButton:hover { background: #004ecc; }
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
        self.lay_ugc, self.stat_ugc = self.create_stat_widget("UGC 案例库", "0", "#00ffcc")
        self.lay_sora, self.stat_sora = self.create_stat_widget("Sora2 案例库", "0", "#ff007c")
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
        self.btn_go.setEnabled(False)
        self.thread.start()

    def build_index(self, logger):
        SORA_DIR, UGC_DIR, HEADER_DIR, COURSE_DIR = "sora2", "ugc", "头图", "课程图"
        for d in [SORA_DIR, UGC_DIR, HEADER_DIR, COURSE_DIR]:
            if not os.path.exists(d): os.makedirs(d)

        # 1. 还原 v2.5 首页悬浮图片墙文案与特效
        hero_imgs = [f"头图/{f}" for f in os.listdir(HEADER_DIR) if f.lower().endswith(('.png','.jpg','.jpeg','.webp'))]
        hero_wall = "".join([f'<img src="{img}" class="float-img" style="top:{random.randint(15, 80)}%; {"left" if i%2==0 else "right"}:{random.randint(2, 18)}%; animation-delay:{i*0.6}s;">' for i, img in enumerate(hero_imgs)])
        
        # 2. 还原课程案例图
        course_imgs = [f"课程图/{f}" for f in os.listdir(COURSE_DIR) if f.lower().endswith(('.png','.jpg','.jpeg','.webp'))]
        course_html = "".join([f'<img src="{img}" style="width:100%; margin-bottom:40px; border-radius:25px; box-shadow:0 20px 50px rgba(0,0,0,0.1);">' for img in course_imgs])

        # 3. 核心 HTML 视觉还原 (含文案、预览悬停放大、点击模态框布局)
        html_content = f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <title>BlackWhale | 60节TIKTOK UGC AI创作系统课</title>
    <style>
        :root {{ --blue: #0057ff; --apple-grad: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab); }}
        body {{ background: #fff; color: #1d1d1f; font-family: "SF Pro Display", "PingFang SC", sans-serif; margin: 0; overflow-x: hidden; }}
        .hero {{ height: 95vh; display: flex; align-items: center; justify-content: center; position: relative; background: #fff; overflow: hidden; }}
        .hero::before {{ content: ""; position: absolute; width: 200%; height: 200%; background: var(--apple-grad); background-size: 400% 400%; opacity: 0.06; animation: gradientBG 15s ease infinite; z-index: 1; }}
        @keyframes gradientBG {{ 0% {{background-position: 0% 50%;}} 50% {{background-position: 100% 50%;}} 100% {{background-position: 0% 50%;}} }}
        .float-img {{ position: absolute; width: 155px; height: 155px; object-fit: cover; border-radius: 22px; box-shadow: 0 15px 35px rgba(0,0,0,0.08); transition: 0.8s; z-index: 2; animation: breathe 6s infinite ease-in-out; }}
        .float-img:hover {{ transform: scale(1.15) rotate(2deg) !important; z-index: 100; }}
        @keyframes breathe {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-20px); }} }}
        .hero-content {{ z-index: 10; text-align: center; }}
        .hero h1 {{ font-size: 64px; font-weight: 800; margin: 0; letter-spacing: -2px; line-height: 1.1; }}
        .hero-list {{ text-align: left; display: inline-block; background: rgba(245,245,247,0.7); padding: 40px; border-radius: 28px; backdrop-filter: blur(15px); margin-top: 30px; }}
        .nav-bar {{ position: sticky; top: 0; background: rgba(255,255,255,0.85); backdrop-filter: blur(20px); display: flex; width: 100%; height: 90px; border-bottom: 1px solid #f2f2f2; z-index: 1000; }}
        .nav-item {{ flex: 1; display: flex; align-items: center; justify-content: center; font-size: 21px; font-weight: 700; cursor: pointer; color: #86868b; transition: 0.3s; }}
        .nav-item.active {{ color: var(--blue); background: #f5f8ff; box-shadow: inset 0 -4px 0 var(--blue); }}
        .tab-content {{ display: none; padding: 60px 4%; animation: fadeIn 0.4s; }}
        .tab-content.active {{ display: block; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 40px; }}
        .video-card {{ position: relative; background: #000; border-radius: 25px; overflow: hidden; aspect-ratio: 9/16; cursor: pointer; box-shadow: 0 20px 40px rgba(0,0,0,0.1); transition: 0.4s; }}
        .video-card:hover {{ transform: scale(1.05); z-index: 5; }}
        .video-card video {{ width: 100%; height: 100%; object-fit: cover; opacity: 0.9; }}
        .play-btn {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 70px; height: 70px; background: var(--blue); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #fff; font-size: 24px; pointer-events: none; opacity: 0.8; }}
        /* 还原 v2.5 左右展示弹窗 */
        .modal {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.92); z-index: 9999; align-items: center; justify-content: center; }}
        .modal-body {{ width: 90%; max-width: 1300px; height: 85vh; background: #fff; border-radius: 35px; display: flex; overflow: hidden; }}
        .modal-left {{ flex: 1.5; background: #000; display: flex; align-items: center; justify-content: center; }}
        .modal-left video {{ max-width: 100%; height: 100%; }}
        .modal-right {{ flex: 1; padding: 50px; display: flex; flex-direction: column; }}
        .prompt-box {{ background: #f5f5f7; padding: 25px; border-radius: 20px; font-family: monospace; flex: 1; overflow-y: auto; white-space: pre-wrap; font-size: 15px; line-height: 1.6; color: #333; }}
        .btn-copy {{ margin-top: 20px; padding: 18px; background: var(--blue); color: #fff; border: none; border-radius: 12px; font-weight: 700; cursor: pointer; font-size: 16px; }}
        @keyframes fadeIn {{ from {{opacity:0;}} to {{opacity:1;}} }}
    </style>
</head>
<body>
    <div class="hero">
        {hero_wall}
        <div class="hero-content">
            <h1>60节TIKTOK UGC带货<br>视频创作系统课</h1>
            <div class="hero-list">
                <p>• 1，60节系统化UGC带货内容生成与AI创作（持续更新中）</p>
                <p>• 2，系统化AI生文/图/视频/音频从基础、实操到进阶</p>
                <p>• 3，原生感TIKTOK UGC带货视频一键批量生成工具</p>
                <p>• 4，批量自产自然流橱窗矩阵与原生感UGC带货视频创作</p>
            </div>
        </div>
    </div>
    <div class="nav-bar">
        <div class="nav-item" onclick="showTab('ugc', this)">UGC实战案例</div>
        <div class="nav-item active" onclick="showTab('sora', this)">Sora2创作案例</div>
        <div class="nav-item" onclick="showTab('course', this)">课程大纲详情</div>
    </div>
    <div id="ugc" class="tab-content"><div class="grid">{self.gen_cards(UGC_DIR, "详见课程内部解析", logger)}</div></div>
    <div id="sora" class="tab-content active"><div class="grid">{self.gen_cards(SORA_DIR, None, logger)}</div></div>
    <div id="course" class="tab-content"><div style="max-width:1000px; margin:0 auto;">{course_html}</div></div>
    
    <div id="videoModal" class="modal" onclick="closeModal()">
        <div class="modal-body" onclick="event.stopPropagation()">
            <div class="modal-left"><video id="mVideo" controls autoplay></video></div>
            <div class="modal-right">
                <h2 id="mTitle" style="margin-top:0; font-size:28px;"></h2>
                <div style="font-weight:700; color:var(--blue); margin-bottom:15px; font-size:18px;">💡 提示词与详情解析:</div>
                <div class="prompt-box" id="mPrompt"></div>
                <button class="btn-copy" onclick="copyText()">📋 复制提示词信息</button>
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
        function copyText() {{ 
            const text = document.getElementById('mPrompt').innerText;
            navigator.clipboard.writeText(text).then(() => {{
                const btn = document.querySelector('.btn-copy');
                btn.innerText = '✅ 已成功复制';
                setTimeout(() => btn.innerText = '📋 复制提示词信息', 2000);
            }});
        }}
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
            title, prompt = t, fixed_prompt if fixed_prompt else "正在读取云端提示词..."
            if not fixed_prompt and os.path.exists(info_p):
                try:
                    with open(info_p, "r", encoding="utf-8", errors="ignore") as f:
                        c = f.read()
                        if "标题:" in c: title = c.split("标题:")[1].split("提示词:")[0].strip()
                        if "提示词:" in c: prompt = c.split("提示词:")[1].strip().replace('"', '&quot;')
                except: pass
            
            cards += f'''
            <div class="video-card" onclick="openModal('{v_rel}', '{title}', `{prompt}`)">
                <video muted loop onmouseover="this.play()" onmouseout="this.pause()">
                    <source src="{v_rel}" type="video/mp4">
                </video>
                <div class="play-btn">▶</div>
                <div style="position:absolute; bottom:15px; left:15px; color:#fff; font-weight:700; font-size:14px; text-shadow:0 2px 4px rgba(0,0,0,0.5);">{title}</div>
            </div>'''
        return cards

    def git_sync(self, logger):
        try:
            logger.emit("[3/3] 正在启动 GitHub Pages 静默同步 (已注入凭据保持器)...")
            def run_git(args): return subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            
            # 解决登录验证：强制 Git 记住当前已手动配置的 Token 凭据
            run_git(["git", "config", "--global", "credential.helper", "store"])
            
            run_git(["git", "add", "."])
            run_git(["git", "commit", "-m", f"Titan_Final_Vision_{datetime.now().strftime('%H%M')}"])
            
            logger.emit("⚡ 正在推送增量数据至 blackwhale-gallery...")
            res = run_git(["git", "push", "origin", "main"])
            
            if res.returncode == 0: 
                logger.emit("🎉 部署成功！v2.5 视觉风格已完整找回。")
            else: 
                # 如果依然提示验证，说明 origin 需要重设 Token 地址（仅需执行一次）
                logger.emit(f"❌ Git 同步提示: {res.stderr}")
        except Exception as e: 
            logger.emit(f"❌ 系统异常: {str(e)}")
        finally: 
            self.btn_go.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PublisherTitanFinal()
    win.show()
    sys.exit(app.exec())