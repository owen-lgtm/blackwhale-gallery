import os, subprocess, sys, random
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                             QHBoxLayout, QWidget, QTextEdit, QLabel, QFrame, QMessageBox)
from PySide6.QtCore import QThread, Signal, Qt, QEventLoop
from PySide6.QtGui import QFont, QColor

# 版本号：v20.0.20260121.Aura_Sora_Pro
# 更新内容：深度参考 creatok 风格设计工具页，加入鼠标边框跟随与悬停动效

class DeployThread(QThread):
    log_signal = Signal(str)
    status_signal = Signal(dict)
    request_confirm_signal = Signal()

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self._confirm_result = False
        self._wait_loop = None

    def handle_confirmation(self, result):
        self._confirm_result = result
        if self._wait_loop:
            self._wait_loop.quit()

    def run(self):
        self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 启动：构建数字化内容库与 SoraX 深度工具页...")
        counts = self.parent.build_index(self.log_signal)
        self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 高级静态页面构建完成。")
        
        self._wait_loop = QEventLoop()
        self.request_confirm_signal.emit()
        self._wait_loop.exec()

        if self._confirm_result:
            self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 执行远程同步同步至 GitHub...")
            self.status_signal.emit({
                "ugc": counts['ugc'], "sora": counts['sora'],
                "time": datetime.now().strftime('%H:%M:%S')
            })
            self.parent.git_sync(self.log_signal)
        else:
            self.log_signal.emit("❌ 发布已取消。")
            self.parent.finalize_deploy()

class PublisherTitanV23Liquid(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BlackWhale Titan v20.0.20260121.Aura_Sora_Pro")
        self.resize(1000, 850)
        self.setStyleSheet("background-color: #050505; color: #e0e0e0;")
        
        main_widget = QWidget(); self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget); layout.setContentsMargins(25, 25, 25, 25); layout.setSpacing(20)

        self.init_top_panel(layout)

        self.log = QTextEdit(); self.log.setReadOnly(True)
        self.log.setStyleSheet("background: #0d0d0f; color: #00ffcc; border: 1px solid #1a1a1a; border-radius: 15px; padding: 15px; font-family: 'Consolas';")
        layout.addWidget(self.log)

        self.btn_go = QPushButton("✨ 构建并预览 (完成后手动确认推送)")
        self.btn_go.setFixedHeight(85)
        self.btn_go.setStyleSheet("QPushButton { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7928CA, stop:1 #FF0080); color: white; font-size: 22px; font-weight: bold; border-radius: 20px; border: none; } QPushButton:hover { opacity: 0.9; }")
        self.btn_go.clicked.connect(self.start_deploy)
        layout.addWidget(self.btn_go)

        self.thread = DeployThread(self)
        self.thread.log_signal.connect(self.update_log)
        self.thread.status_signal.connect(self.update_status)
        self.thread.request_confirm_signal.connect(self.show_confirm_dialog)

    def show_confirm_dialog(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Titan 部署确认")
        msg_box.setText("Creaktok 风格页面已就绪！")
        msg_box.setInformativeText("请检查 toolweb 目录下的跟随特效与悬停动效。\n是否立即推送到 GitHub？")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.button(QMessageBox.Yes).setText("确认无误，开始发布")
        msg_box.button(QMessageBox.No).setText("取消")
        res = msg_box.exec()
        self.thread.handle_confirmation(res == QMessageBox.Yes)

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

    def finalize_deploy(self):
        self.btn_go.setEnabled(True)

    def build_tool_page(self, logger):
        TOOL_DIR = "toolweb"
        if not os.path.exists(TOOL_DIR): os.makedirs(TOOL_DIR)
        
        tool_html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SoraX | 一键无限生成工具</title>
    <style>
        :root {{ --primary: #7928CA; --accent: #FF0080; --bg: #030303; }}
        body {{ margin:0; padding:0; font-family: "SF Pro Display", sans-serif; background: var(--bg); color: #fff; overflow-x: hidden; }}
        
        /* 边框跟踪特效背景 */
        #glow-bg {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; background: radial-gradient(circle at var(--x) var(--y), rgba(121, 40, 202, 0.15) 0%, transparent 40%); z-index: 0; }}

        .nav {{ height: 80px; display: flex; align-items: center; padding: 0 5%; background: rgba(0,0,0,0.8); backdrop-filter: blur(20px); border-bottom: 1px solid #1a1a1a; position: sticky; top:0; z-index:100; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 100px 20px; position: relative; z-index: 1; }}

        .hero-title {{ text-align: center; margin-bottom: 80px; }}
        .hero-title h1 {{ font-size: 72px; font-weight: 800; background: linear-gradient(135deg, #fff 0%, #888 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -3px; }}
        .hero-title p {{ font-size: 20px; color: #888; max-width: 700px; margin: 20px auto; }}

        .feature-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 30px; }}
        .card {{ background: #0d0d0d; border: 1px solid #1a1a1a; padding: 40px; border-radius: 32px; transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); position: relative; overflow: hidden; }}
        .card:hover {{ transform: translateY(-10px); border-color: var(--primary); box-shadow: 0 20px 40px rgba(121, 40, 202, 0.2); }}
        .card h3 {{ font-size: 28px; margin-bottom: 15px; color: #fff; }}
        .card p {{ color: #888; font-size: 16px; line-height: 1.6; white-space: pre-line; }}
        .card-icon {{ width: 50px; height: 50px; background: linear-gradient(135deg, var(--primary), var(--accent)); border-radius: 12px; margin-bottom: 25px; display: flex; align-items: center; justify-content: center; font-weight: bold; }}

        .img-section {{ margin-top: 80px; border-radius: 40px; overflow: hidden; border: 1px solid #1a1a1a; background: #000; box-shadow: 0 50px 100px rgba(0,0,0,0.5); }}
        .img-section img {{ width: 100%; display: block; filter: brightness(0.9); transition: 0.5s; }}
        .img-section img:hover {{ filter: brightness(1.1); transform: scale(1.02); }}

        .cta-box {{ text-align: center; padding: 100px 0; }}
        .btn-back {{ display: inline-block; padding: 20px 60px; background: #fff; color: #000; border-radius: 100px; text-decoration: none; font-weight: 700; transition: 0.3s; }}
        .btn-back:hover {{ transform: scale(1.1); background: var(--primary); color: #fff; }}
    </style>
</head>
<body>
    <div id="glow-bg"></div>
    <div class="nav"><strong style="font-size: 24px; letter-spacing: -1px;">BlackWhale <span style="color:var(--accent)">SoraX</span></strong></div>
    
    <div class="container">
        <div class="hero-title">
            <h1>无限创作，极致高清</h1>
            <p>基于下一代生成式 AI 引擎，专为 TIKTOK UGC 批量带货设计的视频工业化生产系统。</p>
        </div>

        <div class="feature-grid">
            <div class="card">
                <div class="card-icon">01</div>
                <h3>全网最低更高清</h3>
                <p>更高清，全网最低\\n15秒高清最低0.07/条\\n极致画质与成本控制的完美平衡</p>
            </div>
            <div class="card">
                <div class="card-icon">02</div>
                <h3>无限并发</h3>
                <p>一键批量提交，无限并发无上限\\n无需排队，多任务集群同步处理</p>
            </div>
            <div class="card">
                <div class="card-icon">03</div>
                <h3>一键批量管理</h3>
                <p>批量下载，文件自动命名归档\\n专为批量设计，一键根目录上传多批次任务\\n图生视频任务自动裁剪首2帧</p>
            </div>
            <div class="card">
                <div class="card-icon">04</div>
                <h3>AI元数据抹除</h3>
                <p>一键元数据抹除，告别AI强制标注\\n让您的视频更具原生感，安全绕过平台算法检测</p>
            </div>
        </div>

        <div class="img-section"><img src="tool1.png" alt="Tool Interface 1"></div>
        <div class="img-section" style="margin-top:40px;"><img src="tool2.png" alt="Tool Interface 2"></div>

        <div class="cta-box">
            <a href="../index.html" class="btn-back">返回数字化内容库</a>
        </div>
    </div>

    <script>
        const bg = document.getElementById('glow-bg');
        window.addEventListener('mousemove', (e) => {{
            bg.style.setProperty('--x', e.clientX + 'px');
            bg.style.setProperty('--y', e.clientY + 'px');
        }});
    </script>
</body>
</html>"""
        with open(os.path.join(TOOL_DIR, "index.html"), "w", encoding="utf-8") as f: f.write(tool_html)

    def build_index(self, logger):
        SORA_DIR, UGC_DIR, HEADER_DIR, COURSE_DIR = "sora2", "ugc", "头图", "课程图"
        for d in [SORA_DIR, UGC_DIR, HEADER_DIR, COURSE_DIR, "toolweb"]:
            if not os.path.exists(d): os.makedirs(d)
        
        self.build_tool_page(logger)

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
        body, html {{ background: #fff; color: #1d1d1f; font-family: "SF Pro Display", sans-serif; margin: 0; padding: 0; overflow-x: hidden; scroll-behavior: smooth; }}
        
        .hero {{ height: 100vh; display: flex; align-items: center; justify-content: center; position: relative; background: #fff; overflow: hidden; }}
        .liquid-container {{ position: absolute; width: 100%; height: 100%; top: 0; left: 0; z-index: 1; opacity: 0.4; filter: url(#liquid-filter); }}
        .blob {{ position: absolute; width: 600px; height: 600px; border-radius: 50%; filter: blur(60px); animation: move 25s infinite alternate ease-in-out; }}
        .blob-1 {{ background: #e0e7ff; top: -10%; left: 10%; }}
        .blob-2 {{ background: #fce7f3; bottom: -10%; right: 10%; }}
        @keyframes move {{ 0% {{ transform: translate(0,0) scale(1); }} 100% {{ transform: translate(50px, 50px) scale(1.1); }} }}

        .hero-content {{ z-index: 10; text-align: center; }}
        .hero h1 {{ font-size: 72px; font-weight: 800; margin: 0 0 25px 0; letter-spacing: -3.5px; line-height: 1.05; color: #000; }}
        .hero-list p {{ font-size: 18px; color: #86868b; margin: 10px 0; font-weight: 400; }}
        
        .contact-btn {{ display: inline-block; padding: 22px 55px; background: #000; color: #fff; border-radius: 100px; font-weight: 600; font-size: 18px; cursor: pointer; transition: 0.4s; border: none; margin-top: 30px; text-decoration: none; }}
        .contact-btn:hover {{ background: var(--blue); transform: scale(1.05); }}
        .tool-btn {{ background: transparent; color: #000; border: 2px solid #000; margin-left: 15px; }}
        .tool-btn:hover {{ background: #000; color: #fff; }}

        .float-img-container {{ position: absolute; z-index: 2; transition: 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275); }}
        .float-img {{ width: 150px; height: 150px; object-fit: cover; border-radius: 25px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); display: block; }}
        .float-img-container:hover {{ z-index: 100; }}
        .ai-tag {{ font-size: 8px; color: rgba(0,0,0,0.2); display: block; text-align: center; margin-top: 5px; opacity: 0; }}
        .float-img-container:hover .ai-tag {{ opacity: 1; }}

        .nav-bar {{ position: sticky; top: 0; background: rgba(255,255,255,0.75); backdrop-filter: blur(30px); display: flex; width: 100%; height: 95px; border-bottom: 1px solid rgba(0,0,0,0.05); z-index: 1000; }}
        .nav-item {{ flex: 1; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 700; cursor: pointer; color: #86868b; }}
        .nav-item.active {{ color: #000; box-shadow: inset 0 -4px 0 #000; }}

        .tab-content {{ display: none; opacity: 0; padding: 60px 5%; transition: 0.5s; }}
        .tab-content.active {{ display: block; opacity: 1; }}

        .grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 20px; }}
        .video-card {{ background: #fbfbfd; border-radius: 22px; overflow: hidden; aspect-ratio: 9/16; cursor: pointer; transition: 0.3s; }}
        .video-card video, .video-card img {{ width: 100%; height: 100%; object-fit: cover; }}
        
        .qr-modal {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(255,255,255,0.85); backdrop-filter: blur(20px); z-index: 10000; align-items: center; justify-content: center; opacity: 0; transition: 0.3s; }}
        .qr-container {{ background: #fff; padding: 30px; border-radius: 40px; box-shadow: 0 40px 100px rgba(0,0,0,0.1); text-align: center; }}
        .qr-container img {{ width: 260px; height: 260px; }}

        .modal {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.92); z-index: 9999; align-items: center; justify-content: center; }}
        .modal-body {{ width: 94%; max-width: 1200px; height: 85vh; background: #fff; border-radius: 40px; display: flex; overflow: hidden; }}
        .modal-left {{ flex: 1.4; background: #000; display: flex; align-items: center; justify-content: center; }}
        .modal-right {{ flex: 1; padding: 50px; overflow-y: auto; }}
        .more-trigger {{ grid-column: 1 / -1; text-align: center; padding: 40px; color: #86868b; font-weight: 600; cursor: pointer; }}
    </style>
</head>
<body>
    <svg style="display:none;"><filter id="liquid-filter"><feGaussianBlur in="SourceGraphic" stdDeviation="10" result="blur" /><feColorMatrix in="blur" mode="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 19 -9" result="liquid" /></filter></svg>

    <div class="hero" id="home">
        <div class="liquid-container"><div class="blob blob-1"></div><div class="blob blob-2"></div></div>
        {hero_wall}
        <div class="hero-content">
            <h1>60节TikTok UGC带货<br>视频创作系统课</h1>
            <div class="hero-list">
                <p>60节系统化UGC带货内容生成与AI创作（持续更新中）</p>
                <p>系统化AI生文/图/视频/音频从基础、实操到进阶</p>
                <p>原生感TIKTOK UGC带货视频一键批量生成工具</p>
                <p>批量自产自然流橱窗矩阵与原生感UGC带货视频创作</p>
            </div>
            <a class="contact-btn" href="javascript:void(0)" onclick="toggleQR(true)">立即咨询加入 BlackWhale</a>
            <a class="contact-btn tool-btn" href="toolweb/index.html">sora2一键无限生成工具</a>
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
        function openModal(url, title, prompt, isVideo) {{
            const container = document.getElementById('modalMedia');
            if(isVideo) {{ container.innerHTML = `<video src="${{url}}" style="max-width:100%; max-height:100%;" controls autoplay></video>`; }}
            else {{ container.innerHTML = `<img src="${{url}}" style="max-width:100%; max-height:100%;">`; }}
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
            poster_arg = ""
            if video_file:
                poster_path = os.path.join(t_path, "poster.jpg")
                if not os.path.exists(poster_path):
                    try: subprocess.run(["ffmpeg", "-y", "-i", os.path.join(t_path, video_file), "-ss", "00:00:00.5", "-vframes", "1", poster_path], capture_output=True)
                    except: pass
                if os.path.exists(poster_path): poster_arg = f'poster="{folder}/{t}/poster.jpg"'
            file_url = f"{folder}/{t}/{video_file if video_file else img_file}"
            is_video = "true" if video_file else "false"
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
            logger.emit("[同步] 正在上传至 GitHub...")
            def run_git(args): return subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            run_git(["git", "add", "."])
            run_git(["git", "commit", "-m", f"Aura_SoraPro_Update_{datetime.now().strftime('%m%d%H%M')}"])
            res = run_git(["git", "push", "origin", "main"])
            if res.returncode == 0: logger.emit("🎉 部署成功！高级工具页及特效已上线。")
            else: logger.emit(f"❌ 推送失败: {res.stderr}")
        except Exception as e: logger.emit(f"❌ 异常: {str(e)}")
        finally: self.finalize_deploy()

if __name__ == "__main__":
    app = QApplication(sys.argv); win = PublisherTitanV23Liquid(); win.show(); sys.exit(app.exec())