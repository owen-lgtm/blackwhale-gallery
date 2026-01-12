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
        self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 启动商用极致优化引擎：视频预处理 & 首页对齐...")
        counts = self.parent.build_index(self.log_signal)
        self.status_signal.emit({
            "ugc": counts['ugc'], "sora": counts['sora'],
            "time": datetime.now().strftime('%H:%M:%S')
        })
        self.parent.git_sync(self.log_signal)

class PublisherTitanV23Liquid(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BlackWhale Titan Evolved v2.3-商用加速版")
        self.resize(1000, 850)
        self.setStyleSheet("background-color: #050505; color: #e0e0e0;")
        
        main_widget = QWidget(); self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget); layout.setContentsMargins(25, 25, 25, 25); layout.setSpacing(20)

        self.init_top_panel(layout)

        self.log = QTextEdit(); self.log.setReadOnly(True)
        self.log.setStyleSheet("background: #0d0d0f; color: #00ffcc; border: 1px solid #1a1a1a; border-radius: 15px; padding: 15px; font-family: 'Consolas';")
        layout.addWidget(self.log)

        self.btn_go = QPushButton("✨ 执行 v2.3-加速部署 (含视频流优化)")
        self.btn_go.setFixedHeight(85)
        self.btn_go.setStyleSheet("QPushButton { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7928CA, stop:1 #FF0080); color: white; font-size: 22px; font-weight: bold; border-radius: 20px; border: none; } QPushButton:hover { opacity: 0.9; }")
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

        # 优化1：首页小图1:1比例显示与原地悬停放大效果
        hero_imgs = [f"头图/{f}" for f in os.listdir(HEADER_DIR) if f.lower().endswith(('.png','.jpg','.jpeg','.webp'))]
        hero_wall = "".join([f'''
            <div class="float-img-container" style="top:{random.randint(15, 80)}%; {"left" if i%2==0 else "right"}:{random.randint(2, 18)}%; animation-delay:{i*0.6}s;">
                <img src="{img}" class="float-img">
                <span class="ai-tag">AI UGC CASE</span>
            </div>''' for i, img in enumerate(hero_imgs)])

        course_imgs = sorted([f"课程图/{f}" for f in os.listdir(COURSE_DIR) if f.lower().endswith(('.png','.jpg','.jpeg','.webp'))])
        course_html = "".join([f'<img src="{img}" style="width:100%; margin-bottom:40px; border-radius:25px; box-shadow:0 20px 50px rgba(0,0,0,0.05);">' for img in course_imgs])

        html_content = f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BlackWhale | 数字化内容库</title>
    <style>
        :root {{ --blue: #0057ff; }}
        body, html {{ background: #fff; color: #1d1d1f; font-family: "SF Pro Display", -apple-system, sans-serif; margin: 0; padding: 0; overflow-x: hidden; scroll-behavior: smooth; }}
        
        @media (max-width: 768px) {{
            .hero h1 {{ font-size: 38px !important; padding: 0 20px; }}
            .float-img-container {{ display: none; }}
            .grid {{ grid-template-columns: repeat(2, 1fr) !important; gap: 15px !important; padding: 15px !important; }}
            .modal-body {{ flex-direction: column !important; height: 95vh !important; }}
        }}

        .hero {{ height: 100vh; display: flex; align-items: center; justify-content: center; position: relative; background: #fff; overflow: hidden; }}
        .hero-content {{ z-index: 10; text-align: center; }}
        .hero h1 {{ font-size: 72px; font-weight: 800; margin: 0 0 25px 0; letter-spacing: -3.5px; line-height: 1.05; color: #000; }}
        
        /* 首页文字对齐要求 */
        .hero-list p {{ font-size: 18px; color: #86868b; margin: 10px 0; font-weight: 400; }}
        
        .contact-btn {{ display: inline-block; padding: 22px 65px; background: #000; color: #fff; border-radius: 100px; font-weight: 600; font-size: 18px; cursor: pointer; transition: 0.4s; border: none; margin-top: 30px; }}
        .contact-btn:hover {{ background: var(--blue); transform: scale(1.05); }}

        /* 首页小图优化：1:1容器，悬停原地放大显示全图 */
        .float-img-container {{ position: absolute; z-index: 2; transition: 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275); }}
        .float-img {{ width: 150px; height: 150px; object-fit: cover; border-radius: 25px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); display: block; }}
        .float-img-container:hover {{ z-index: 100; }}
        .float-img-container:hover .float-img {{ transform: scale(1.3); object-fit: contain; background: #fff; }}
        .ai-tag {{ font-size: 8px; color: rgba(0,0,0,0.2); display: block; text-align: center; margin-top: 5px; font-family: monospace; opacity: 0; }}
        .float-img-container:hover .ai-tag {{ opacity: 1; }}

        .nav-bar {{ position: sticky; top: 0; background: rgba(255,255,255,0.75); backdrop-filter: blur(30px); display: flex; width: 100%; height: 95px; border-bottom: 1px solid rgba(0,0,0,0.05); z-index: 1000; }}
        .nav-item {{ flex: 1; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 700; cursor: pointer; color: #86868b; }}
        .nav-item.active {{ color: #000; box-shadow: inset 0 -4px 0 #000; }}

        .tab-content {{ display: none; opacity: 0; padding: 60px 5%; transition: 0.5s; }}
        .tab-content.active {{ display: block; opacity: 1; }}

        .grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 20px; }}
        .video-card {{ position: relative; background: #fbfbfd; border-radius: 22px; overflow: hidden; aspect-ratio: 9/16; cursor: pointer; transition: 0.3s; }}
        .video-card:hover {{ transform: translateY(-5px); box-shadow: 0 15px 30px rgba(0,0,0,0.1); }}
        .video-card video, .video-card img {{ width: 100%; height: 100%; object-fit: cover; background: #000; }}

        .qr-modal {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(255,255,255,0.85); backdrop-filter: blur(20px); z-index: 10000; align-items: center; justify-content: center; opacity: 0; transition: 0.3s; }}
        .qr-container {{ background: #fff; padding: 30px; border-radius: 40px; box-shadow: 0 40px 100px rgba(0,0,0,0.1); text-align: center; }}
        .qr-container img {{ width: 260px; height: 260px; object-fit: contain; }}

        .modal {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.92); z-index: 9999; align-items: center; justify-content: center; }}
        .modal-body {{ width: 94%; max-width: 1200px; height: 85vh; background: #fff; border-radius: 40px; display: flex; overflow: hidden; }}
        .modal-left {{ flex: 1.4; background: #000; display: flex; align-items: center; justify-content: center; }}
        .modal-right {{ flex: 1; padding: 50px; overflow-y: auto; }}

        .more-trigger {{ grid-column: 1 / -1; text-align: center; padding: 40px; color: #86868b; font-weight: 600; cursor: pointer; }}
    </style>
</head>
<body>
    <div class="hero" id="home">
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
    
    <div id="qrModal" class="qr-modal" onclick="toggleQR(false)">
        <div class="qr-container" onclick="event.stopPropagation()">
            <img src="qr.png" alt="QR">
            <p style="font-weight:700; margin-top:15px;">扫码咨询 BlackWhale 导师</p>
        </div>
    </div>

    <div class="nav-bar">
        <div class="nav-item active" onclick="showTab('ugc', this)">UGC实战案例</div>
        <div class="nav-item" onclick="showTab('sora', this)">Sora2 案例 (100+)</div>
        <div class="nav-item" onclick="showTab('course', this)">课程大纲详情</div>
    </div>

    <div id="ugc" class="tab-content active" style="display:block; opacity:1;"><div class="grid">{self.gen_cards(UGC_DIR, "课程原创案例，详见视频课程讲解", logger)}</div></div>
    <div id="sora" class="tab-content"><div class="grid">{self.gen_cards(SORA_DIR, None, logger)}<div class="more-trigger" onclick="toggleQR(true)">—— 点击获取更多案例 ——</div></div></div>
    <div id="course" class="tab-content"><div style="max-width:1000px; margin:0 auto;">{course_html}</div></div>

    <div id="videoModal" class="modal" onclick="closeModal()">
        <div class="modal-body" onclick="event.stopPropagation()">
            <div class="modal-left" id="modalMedia"></div>
            <div class="modal-right">
                <h2 id="mTitle" style="font-size:28px;"></h2>
                <div style="color:var(--blue); font-weight:700; margin:25px 0 10px 0;">解析与提示词:</div>
                <div id="mPrompt" style="background:#f5f5f7; padding:25px; border-radius:20px; white-space:pre-wrap; line-height:1.6;"></div>
            </div>
        </div>
    </div>

    <script>
        function toggleQR(show) {{
            const m = document.getElementById('qrModal');
            if(show) {{ m.style.display='flex'; setTimeout(()=>m.style.opacity='1',10); }}
            else {{ m.style.opacity='0'; setTimeout(()=>m.style.display='none',300); }}
        }}
        function showTab(id, el) {{
            document.querySelectorAll('.tab-content').forEach(t => {{ t.style.display='none'; t.style.opacity='0'; }});
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            const target = document.getElementById(id);
            target.style.display = 'block'; setTimeout(() => target.style.opacity = '1', 50);
            el.classList.add('active');
        }}
        // 商用级：点击后按需加载流
        function openModal(url, title, prompt, isVideo) {{
            const container = document.getElementById('modalMedia');
            if(isVideo) {{
                container.innerHTML = `<video src="${{url}}" style="max-width:100%; max-height:100%;" controls autoplay></video>`;
            }} else {{
                container.innerHTML = `<img src="${{url}}" style="max-width:100%; max-height:100%;">`;
            }}
            document.getElementById('mTitle').innerText = title;
            document.getElementById('mPrompt').innerText = prompt;
            document.getElementById('videoModal').style.display = 'flex';
        }}
        function closeModal() {{ document.getElementById('videoModal').style.display='none'; document.getElementById('modalMedia').innerHTML=''; }}
    </script>
</body>
</html>"""
        with open("index.html", "w", encoding="utf-8") as f: f.write(html_content)
        return {'ugc': len(os.listdir(UGC_DIR)), 'sora': len(os.listdir(SORA_DIR))}

    def gen_cards(self, folder, fixed_prompt, logger):
        cards = ""
        if not os.path.exists(folder): return ""
        tasks = sorted([d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))], reverse=True)
        for t in tasks:
            t_path = os.path.join(folder, t)
            video_file = next((f for f in os.listdir(t_path) if f.lower().endswith('.mp4')), None)
            img_file = next((f for f in os.listdir(t_path) if f.lower().endswith(('.png','.jpg','.jpeg','.webp'))), None)
            
            # 优化3：视频预处理（生成 poster 封面图）
            poster_arg = ""
            if video_file:
                poster_path = os.path.join(t_path, "poster.jpg")
                if not os.path.exists(poster_path):
                    # 尝试使用 ffmpeg 静默生成首帧缩略图，不改变视频
                    try: subprocess.run(["ffmpeg", "-y", "-i", os.path.join(t_path, video_file), "-ss", "00:00:00.5", "-vframes", "1", poster_path], capture_output=True)
                    except: pass
                if os.path.exists(poster_path): poster_arg = f'poster="{folder}/{t}/poster.jpg"'

            file_url = f"{folder}/{t}/{video_file if video_file else img_file}"
            is_video = "true" if video_file else "false"
            
            # 优化4：极致加速，设置 preload="none"
            display_html = f'<video {poster_arg} preload="none" muted loop onmouseover="this.play()" onmouseout="this.pause()"><source src="{file_url}"></video>' if video_file else f'<img src="{file_url}" loading="lazy">'
            
            title, prompt = t, fixed_prompt if fixed_prompt else "解析加载中..."
            info_p = os.path.join(t_path, "info.txt")
            if not fixed_prompt and os.path.exists(info_p):
                with open(info_p, "r", encoding="utf-8", errors="ignore") as f:
                    c = f.read()
                    if "标题:" in c: title = c.split("标题:")[1].split("提示词:")[0].strip()
                    if "提示词:" in c: prompt = c.split("提示词:")[1].strip().replace('"', '&quot;')

            cards += f'<div class="video-card" onclick="openModal(\'{file_url}\', \'{title}\', `{prompt}`, {is_video})">{display_html}</div>'
        return cards

    def git_sync(self, logger):
        try:
            logger.emit("[同步] 正在推送商用极致加速版...")
            def run_git(args): return subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            run_git(["git", "add", "."])
            run_git(["git", "commit", "-m", f"Ultra_Fast_V2.3_{datetime.now().strftime('%m%d%H%M')}"])
            res = run_git(["git", "push", "origin", "main"])
            if res.returncode == 0: logger.emit("🎉 部署成功！网页已支持 poster 缩略图加速模式。")
            else: logger.emit(f"❌ 推送失败: {res.stderr}")
        except Exception as e: logger.emit(f"❌ 异常: {str(e)}")
        finally: self.btn_go.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv); win = PublisherTitanV23Liquid(); win.show(); sys.exit(app.exec())