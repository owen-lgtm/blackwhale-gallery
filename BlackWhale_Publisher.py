import os, subprocess, sys, random
from datetime import datetime
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextEdit
from PySide6.QtCore import QThread, Signal

class DeployThread(QThread):
    log_signal = Signal(str)

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def run(self):
        self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 启动 v2.6 实时同步版引擎...")
        self.parent.build_index(self.log_signal)
        self.parent.git_sync(self.log_signal)

class PublisherFullStack(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BlackWhale Titan FullStack v2.6")
        self.resize(900, 700)
        self.setStyleSheet("background-color: #0c0c0e; color: #fff;")
        
        main = QWidget(); self.setCentralWidget(main); lay = QVBoxLayout(main)
        self.btn_go = QPushButton("🔥 部署 v2.6 (含实时上传进度监控)")
        self.btn_go.setFixedHeight(80)
        self.btn_go.setStyleSheet("background: linear-gradient(90deg, #0057ff, #00c6ff); color: white; font-size: 22px; font-weight: bold; border-radius: 20px; border: none;")
        
        self.log = QTextEdit(); self.log.setReadOnly(True)
        self.log.setStyleSheet("background: #1a1a1c; color: #00ff00; font-family: 'Consolas'; font-size: 14px; padding: 10px; border-radius: 10px;")
        
        lay.addWidget(self.btn_go); lay.addWidget(self.log)
        self.btn_go.clicked.connect(self.start_deploy)
        
        self.thread = DeployThread(self)
        self.thread.log_signal.connect(self.update_log)

    def update_log(self, text):
        self.log.append(text)
        self.log.verticalScrollBar().setValue(self.log.verticalScrollBar().maximum())

    def start_deploy(self):
        self.btn_go.setEnabled(False)
        self.thread.start()

    def build_index(self, logger):
        SORA_DIR, UGC_DIR, COURSE_DIR, HEADER_DIR = "sora2", "ugc", "课程图", "头图"
        logger.emit("[1/3] 正在扫描素材与渲染苹果级排版...")
        
        for d in [SORA_DIR, UGC_DIR, COURSE_DIR, HEADER_DIR]:
            if not os.path.exists(d): os.makedirs(d)

        hero_imgs = [f"头图/{f}" for f in os.listdir(HEADER_DIR) if f.lower().endswith(('.png','.jpg','.jpeg','.webp'))]
        course_imgs = [f"课程图/{f}" for f in os.listdir(COURSE_DIR) if f.lower().endswith(('.png','.jpg','.jpeg','.webp'))]
        
        hero_wall_html = "".join([f'<img src="{img}" class="float-img" style="top:{random.randint(15, 80)}%; {"left" if i%2==0 else "right"}:{random.randint(2, 18)}%; animation-delay:{i*0.6}s;">' for i, img in enumerate(hero_imgs)])

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
        .hero h1 {{ font-size: 64px; font-weight: 800; margin: 0; letter-spacing: -2px; }}
        .hero-list {{ text-align: left; display: inline-block; background: rgba(245,245,247,0.7); padding: 40px; border-radius: 28px; backdrop-filter: blur(15px); margin-top: 30px; }}
        .nav-bar {{ position: sticky; top: 0; background: rgba(255,255,255,0.85); backdrop-filter: blur(20px); display: flex; width: 100%; height: 90px; border-bottom: 1px solid #f2f2f2; z-index: 1000; }}
        .nav-item {{ flex: 1; display: flex; align-items: center; justify-content: center; font-size: 21px; font-weight: 700; cursor: pointer; color: #86868b; transition: 0.3s; }}
        .nav-item.active {{ color: var(--blue); background: #f5f8ff; box-shadow: inset 0 -4px 0 var(--blue); }}
        .tab-content {{ display: none; padding: 60px 4%; animation: fadeIn 0.4s; }}
        .tab-content.active {{ display: block; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 40px; }}
        .video-card {{ position: relative; background: #000; border-radius: 25px; overflow: hidden; aspect-ratio: 9/16; cursor: pointer; box-shadow: 0 20px 40px rgba(0,0,0,0.1); }}
        .video-card video {{ width: 100%; height: 100%; object-fit: cover; opacity: 0.9; }}
        .play-btn {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 70px; height: 70px; background: var(--blue); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #fff; font-size: 24px; pointer-events: none; }}
        .modal {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.92); z-index: 9999; align-items: center; justify-content: center; }}
        .modal-body {{ width: 90%; max-width: 1300px; height: 85vh; background: #fff; border-radius: 35px; display: flex; overflow: hidden; }}
        .modal-left {{ flex: 1.5; background: #000; display: flex; align-items: center; justify-content: center; }}
        .modal-left video {{ max-width: 100%; height: 100%; }}
        .modal-right {{ flex: 1; padding: 50px; display: flex; flex-direction: column; }}
        .prompt-box {{ background: #f5f5f7; padding: 25px; border-radius: 20px; font-family: monospace; flex: 1; overflow-y: auto; white-space: pre-wrap; }}
        .btn-copy {{ margin-top: 20px; padding: 18px; background: var(--blue); color: #fff; border: none; border-radius: 12px; font-weight: 700; cursor: pointer; }}
        .qr-side {{ position: fixed; right: 30px; bottom: 30px; z-index: 500; text-align: center; cursor: zoom-in; transition: 0.3s; }}
        .qr-side:hover {{ transform: scale(1.05); }}
        .qr-side img {{ width: 110px; border-radius: 15px; border: 4px solid #fff; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
        .qr-side p {{ font-size: 12px; font-weight: 800; color: var(--blue); margin-top: 8px; background: rgba(255,255,255,0.8); padding: 4px 8px; border-radius: 20px; }}
        #qrFull {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(255,255,255,0.9); backdrop-filter: blur(10px); z-index: 10000; align-items: center; justify-content: center; cursor: zoom-out; }}
        #qrFull img {{ width: 400px; border-radius: 30px; box-shadow: 0 30px 60px rgba(0,0,0,0.2); }}
    </style>
</head>
<body>
    <div class="hero">
        {hero_wall_html}
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
    <div id="ugc" class="tab-content"><div class="grid">{self.gen_cards(UGC_DIR, "详见课程说明", logger)}</div></div>
    <div id="sora" class="tab-content active"><div class="grid">{self.gen_cards(SORA_DIR, None, logger)}</div></div>
    <div id="course" class="tab-content">
        <div style="max-width:1000px; margin:0 auto;">
            {"".join([f'<img src="{img}" style="width:100%; margin-bottom:40px; border-radius:25px;">' for img in course_imgs])}
        </div>
    </div>
    <div class="qr-side" onclick="toggleQR(true)"><img src="wechat_qr.png" alt="QR"><p>扫码咨询/进群</p></div>
    <div id="qrFull" onclick="toggleQR(false)"><img src="wechat_qr.png"></div>
    <div id="videoModal" class="modal" onclick="closeModal()">
        <div class="modal-body" onclick="event.stopPropagation()">
            <div class="modal-left"><video id="mVideo" controls autoplay></video></div>
            <div class="modal-right">
                <h2 id="mTitle" style="margin-top:0;"></h2>
                <div style="font-weight:700; color:var(--blue); margin-bottom:10px;">详情解析:</div>
                <div class="prompt-box" id="mPrompt"></div>
                <button class="btn-copy" onclick="copyText()">复制当前信息</button>
            </div>
        </div>
    </div>
    <script>
        function showTab(id, el) {{
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            document.getElementById(id).classList.add('active'); el.classList.add('active');
        }}
        function openModal(vUrl, title, prompt) {{
            document.getElementById('mVideo').src = vUrl;
            document.getElementById('mTitle').innerText = title;
            document.getElementById('mPrompt').innerText = prompt;
            document.getElementById('videoModal').style.display = 'flex';
        }}
        function closeModal() {{ document.getElementById('videoModal').style.display = 'none'; document.getElementById('mVideo').pause(); }}
        function toggleQR(show) {{ document.getElementById('qrFull').style.display = show ? 'flex' : 'none'; }}
        function copyText() {{ navigator.clipboard.writeText(document.getElementById('mPrompt').innerText).then(() => alert('已复制内容')); }}
    </script>
</body>
</html>"""
        with open("index.html", "w", encoding="utf-8") as f: f.write(html_content)
        logger.emit("[2/3] 网页 index.html 写入完成。")

    def gen_cards(self, folder, fixed_prompt, logger):
        cards = ""
        if not os.path.exists(folder): return ""
        tasks = sorted([d for d in os.listdir(folder) if d.startswith("Task_")])
        total = len(tasks)
        for i, t in enumerate(tasks):
            if (i + 1) % 5 == 0 or i == 0 or i == total - 1:
                logger.emit(f"   [进度] 正在加载 {folder} 任务: {i+1}/{total}...")
            v_rel = f"{folder}/{t}/video.mp4"
            info_p = f"{folder}/{t}/info.txt"
            title, prompt = t, fixed_prompt if fixed_prompt else "提示词读取中..."
            if not fixed_prompt and os.path.exists(info_p):
                with open(info_p, "r", encoding="utf-8", errors="ignore") as f:
                    c = f.read()
                    if "标题:" in c: title = c.split("标题:")[1].split("提示词:")[0].strip()
                    if "提示词:" in c: prompt = c.split("提示词:")[1].strip().replace('"', '&quot;')
            cards += f'''<div class="video-card" onclick="openModal('{v_rel}', '{title}', `{prompt}`)"><video muted loop onmouseover="this.play()" onmouseout="this.pause()"><source src="{v_rel}" type="video/mp4"></video><div class="play-btn">▶</div><div style="position:absolute; bottom:15px; left:15px; color:#fff; font-weight:700; font-size:12px;">{title}</div></div>'''
        return cards

    def git_sync(self, logger):
        try:
            logger.emit("[3/3] 正在启动 GitHub 实时流同步...")
            # 自动清理 index.lock
            lock_path = os.path.join(".git", "index.lock")
            if os.path.exists(lock_path):
                os.remove(lock_path)
                logger.emit("   ⚡ 系统提示: 已自动清理残留的 Git 锁定文件。")

            def run_live(args):
                process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')
                while True:
                    line = process.stdout.readline()
                    if not line and process.poll() is not None: break
                    if line.strip(): logger.emit(f"   ⚡ {line.strip()}")
                return process.returncode

            run_live(["git", "add", "--all"])
            run_live(["git", "commit", "-m", f"Titan_v2.6_Sync_{datetime.now().strftime('%H%M')}"])
            logger.emit("   ☁️ 正在推送云端 (观察下方进度数值)...")
            res = run_live(["git", "push", "origin", "main", "--progress"])
            
            if res == 0: logger.emit("🎉 部署完成！同步已成功。")
            else: logger.emit("❌ 同步中断，请检查代理端口 10809 是否开启。")
        except Exception as e: logger.emit(f"❌ 系统错误: {str(e)}")
        finally: self.btn_go.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv); win = PublisherFullStack(); win.show(); sys.exit(app.exec())