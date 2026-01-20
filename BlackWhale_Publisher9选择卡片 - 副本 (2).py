import os, subprocess, sys, random, webbrowser
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                             QHBoxLayout, QWidget, QTextEdit, QLabel, QFrame, QMessageBox)
from PySide6.QtCore import QThread, Signal, Qt, QEventLoop
from PySide6.QtGui import QFont, QColor

# 版本号：v20.0.20260121.Aura_Sora_Pro_Titan_V2_SplitMode_Optimized_Pricing
# 更新内容：优化二维码弹窗尺寸，Sora页增加领取按钮，UGC末尾增加引导卡片。新增Toolweb定价动态卡片系统。

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

        self.btn_home = QPushButton("🌐 访问黑鲸数字化内容主页")
        self.btn_home.setFixedHeight(50)
        self.btn_home.setStyleSheet("QPushButton { background: #1a1a1a; color: #00ffcc; font-size: 16px; border-radius: 15px; border: 1px solid #333; } QPushButton:hover { background: #222; border-color: #00ffcc; }")
        self.btn_home.clicked.connect(lambda: webbrowser.open("https://owen-lgtm.github.io/blackwhale-gallery/"))
        layout.addWidget(self.btn_home)

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
        msg_box.setText("分层加速架构页面已就绪！")
        msg_box.setInformativeText("主页已切换为图片预览模式，并生成了独立视频详情页。\n是否立即推送到 GitHub？")
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
    <title>BlackWhale | 黑鲸千帆一键无限生成</title>
    <style>
        :root {{ --primary: #7928CA; --accent: #FF0080; --bg: #030303; }}
        body {{ margin:0; padding:0; font-family: "SF Pro Display", sans-serif; background: var(--bg); color: #fff; overflow-x: hidden; }}
        
        #glow-bg {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; background: radial-gradient(circle at var(--x) var(--y), rgba(121, 40, 202, 0.15) 0%, transparent 40%); z-index: 0; }}

        .nav {{ height: 80px; display: flex; align-items: center; padding: 0 5%; background: rgba(0,0,0,0.8); backdrop-filter: blur(20px); border-bottom: 1px solid #1a1a1a; position: sticky; top:0; z-index:100; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 60px 20px; position: relative; z-index: 1; }}

        .hero-title {{ text-align: center; margin-bottom: 80px; }}
        .hero-title h1 {{ font-size: 72px; font-weight: 800; background: linear-gradient(135deg, #fff 0%, #888 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -3px; }}
        .hero-title p {{ font-size: 20px; color: #888; max-width: 700px; margin: 20px auto; }}

        .feature-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 30px; margin-bottom: 100px; }}
        .card {{ background: rgba(13, 13, 13, 0.6); backdrop-filter: blur(10px); border: 1px solid #1a1a1a; padding: 40px; border-radius: 32px; transition: all 0.5s cubic-bezier(0.19, 1, 0.22, 1); position: relative; overflow: hidden; }}
        .card:hover {{ transform: translateY(-12px) scale(1.03); border-color: var(--primary); box-shadow: 0 25px 50px rgba(121, 40, 202, 0.25); }}
        .card h3 {{ font-size: 28px; margin-bottom: 15px; color: #fff; }}
        .card p {{ color: #888; font-size: 16px; line-height: 1.6; }}
        .card-icon {{ width: 50px; height: 50px; background: linear-gradient(135deg, var(--primary), var(--accent)); border-radius: 12px; margin-bottom: 25px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 20px; }}

        .split-section {{ display: flex; align-items: center; gap: 60px; margin-bottom: 100px; }}
        .split-text {{ flex: 1; }}
        .split-text h2 {{ font-size: 48px; margin-bottom: 25px; background: linear-gradient(to right, #fff, #888); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .split-text ul {{ list-style: none; padding: 0; }}
        .split-text li {{ color: #aaa; font-size: 18px; margin-bottom: 12px; display: flex; align-items: center; }}
        .split-text li::before {{ content: "✦"; color: var(--accent); margin-right: 15px; font-size: 20px; }}
        .split-img {{ flex: 1.2; border-radius: 32px; border: 1px solid #222; overflow: hidden; box-shadow: 0 40px 80px rgba(0,0,0,0.5); transition: transform 0.6s cubic-bezier(0.165, 0.84, 0.44, 1); }}
        .split-img:hover {{ transform: scale(1.02); }}
        .split-img img {{ width: 100%; display: block; }}

        .section-title {{ text-align: center; margin-bottom: 60px; }}
        .section-title .badge {{ background: #222; padding: 6px 16px; border-radius: 100px; font-size: 14px; color: #888; margin-bottom: 20px; display: inline-block; }}
        .section-title h2 {{ font-size: 56px; letter-spacing: -2px; margin: 0; }}
        .section-title p {{ color: #888; margin-top: 15px; font-size: 18px; }}

        .capability-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 25px; margin-bottom: 80px; }}
        .mini-card {{ background: rgba(13, 13, 13, 0.6); backdrop-filter: blur(10px); border: 1px solid #1a1a1a; padding: 35px; border-radius: 28px; transition: all 0.5s cubic-bezier(0.19, 1, 0.22, 1); }}
        .mini-card:hover {{ border-color: #00ffcc; transform: scale(1.05) translateY(-5px); box-shadow: 0 15px 30px rgba(0, 255, 204, 0.1); }}
        .mini-card .icon {{ font-size: 32px; margin-bottom: 20px; display: block; filter: hue-rotate(280deg); transition: transform 0.4s ease; }}
        .mini-card:hover .icon {{ transform: scale(1.2) rotate(5deg); }}
        .mini-card h4 {{ font-size: 22px; margin: 0 0 12px 0; color: #fff; }}
        .mini-card p {{ font-size: 15px; color: #666; line-height: 1.6; margin: 0; }}

        /* --- Pricing Card System Start --- */
        .pricing-section {{ padding: 100px 0; text-align: center; }}
        .toggle-container {{ display: inline-flex; background: #111; padding: 6px; border-radius: 100px; margin-bottom: 60px; border: 1px solid #222; position: relative; }}
        .toggle-btn {{ padding: 12px 35px; border-radius: 100px; cursor: pointer; font-weight: 600; font-size: 15px; color: #666; transition: 0.3s; z-index: 1; border:none; background:none; }}
        .toggle-btn.active {{ color: #fff; }}
        .toggle-slider {{ position: absolute; height: calc(100% - 12px); width: calc(50% - 6px); background: linear-gradient(135deg, var(--primary), var(--accent)); border-radius: 100px; transition: transform 0.4s cubic-bezier(0.19, 1, 0.22, 1); left: 6px; z-index: 0; }}
        .flagship-mode .toggle-slider {{ transform: translateX(100%); }}

        .price-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 30px; perspective: 1000px; }}
        .price-card {{ background: rgba(20, 20, 20, 0.5); border: 1px solid #222; border-radius: 35px; padding: 45px 30px; backdrop-filter: blur(20px); transition: all 0.6s cubic-bezier(0.165, 0.84, 0.44, 1); position: relative; overflow: hidden; display: flex; flex-direction: column; align-items: center; }}
        .price-card:hover {{ transform: translateY(-15px) rotateX(5deg); border-color: var(--primary); box-shadow: 0 40px 80px rgba(0,0,0,0.4); }}
        
        .price-card .p-title {{ font-size: 18px; color: #888; margin-bottom: 10px; }}
        .price-card .p-main {{ font-size: 52px; font-weight: 800; margin: 15px 0; color: #fff; letter-spacing: -2px; }}
        .price-card .p-sub {{ font-size: 14px; color: var(--accent); margin-bottom: 30px; font-weight: 600; }}
        
        .p-btn {{ width: 80%; padding: 16px; border-radius: 15px; background: #222; color: #fff; border: 1px solid #333; font-weight: 700; cursor: pointer; transition: 0.3s; margin-bottom: 35px; letter-spacing: 1px; }}
        .price-card:hover .p-btn {{ background: linear-gradient(135deg, var(--primary), var(--accent)); border:none; transform: scale(1.05); box-shadow: 0 10px 20px rgba(121, 40, 202, 0.3); }}
        
        .p-features {{ width: 100%; text-align: left; list-style: none; padding: 0; margin: 0; }}
        .p-features li {{ font-size: 14px; color: #aaa; margin-bottom: 15px; display: flex; align-items: center; }}
        .p-features li::before {{ content: "✓"; color: #00ffcc; margin-right: 12px; font-weight: bold; }}
        
        .price-content {{ display: none; width: 100%; }}
        .price-content.active {{ display: contents; }}
        /* --- Pricing Card System End --- */

        .cta-box {{ text-align: center; padding: 60px 0; }}
        .btn-action {{ display: inline-block; padding: 22px 65px; background: linear-gradient(135deg, var(--primary), var(--accent)); color: #fff; border-radius: 100px; text-decoration: none; font-weight: 700; font-size: 20px; transition: 0.4s; box-shadow: 0 20px 40px rgba(121,40,202,0.3); border:none; cursor:pointer; }}
        .btn-action:hover {{ transform: scale(1.1) translateY(-5px); box-shadow: 0 30px 60px rgba(121,40,202,0.5); }}

        .qr-overlay {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); backdrop-filter: blur(15px); z-index: 2000; align-items: center; justify-content: center; }}
        .qr-card {{ background: #fff; padding: 40px; border-radius: 40px; text-align: center; color: #000; }}
        .qr-card img {{ width: 280px; height: 280px; border-radius: 20px; }}
    </style>
</head>
<body>
    <div id="glow-bg"></div>
    <div class="nav"><strong style="font-size: 24px; letter-spacing: -1px;">BlackWhale <span style="color:var(--accent)">SoraX</span></strong></div>
    
    <div class="container">
        <div class="hero-title">
            <h1>黑鲸千帆 重塑你的AI生产力</h1>
            <p>专注AI UGC，无限并发一键生成管理工具</p>
        </div>

        <div class="feature-grid">
            <div class="card">
                <div class="card-icon">01</div>
                <h3>全网最低 更高清</h3>
                <p>生成更高清，15秒高清最低仅0.07/条，全网最低。</p>
            </div>
            <div class="card">
                <div class="card-icon">02</div>
                <h3>无限并发 批量无水印</h3>
                <p>一键批量提交，无限并发无上限，无水印直出。</p>
            </div>
            <div class="card">
                <div class="card-icon">03</div>
                <h3>一键批量管理</h3>
                <p>专为批量设计自动批量下载，多批次一次提交，自动裁剪首帧更省力。</p>
            </div>
            <div class="card">
                <div class="card-icon">04</div>
                <h3>AI元数据一键抹除直出</h3>
                <p>告别AI强制标注，注入模拟iPhone手机拍摄元数据，彻底告别AI标记和限流。</p>
            </div>
        </div>

        <div class="split-section">
            <div class="split-text">
                <h2>黑鲸千帆高级版</h2>
                <ul>
                    <li>无限并发，一键无水印直出</li>
                    <li>永久有效，随时补充</li>
                    <li>专为批量而生，支持手动模板批量和手动批量提交，自动归档多批次任务</li>
                    <li>横竖屏时长自主选择</li>
                    <li>超低价格，多档可选</li>
                    <li>AI元数据一键抹除直出，告别AI强制标注</li>
                </ul>
            </div>
            <div class="split-img">
                <img src="tool1.png" alt="Advanced Version">
            </div>
        </div>

        <div class="split-section" style="flex-direction: row-reverse;">
            <div class="split-text">
                <h2>黑鲸千帆旗舰版</h2>
                <ul>
                    <li>全网最低价，15秒高清0.07/条起</li>
                    <li>无限并发，一键无水印直出</li>
                    <li>专为批量而生，支持手动模板批量和手动批量提交，自动归档多批次任务</li>
                    <li>横竖屏时长自主选择</li>
                    <li>AI元数据一键抹除直出，告别AI强制标注</li>
                </ul>
            </div>
            <div class="split-img">
                <img src="tool2.png" alt="Flagship Version">
            </div>
        </div>

        <div class="section-title">
            <div class="badge">Sora 2 的突破</div>
            <h2>前所未有的 AI 视频模型能力</h2>
            <p>Sora 2 带来了最强大的 AI 视频生成能力，黑鲸千帆则负责把这些能力落地为稳定可靠的制作流程。</p>
        </div>

        <div class="capability-grid">
            <div class="mini-card">
                <span class="icon">📷</span>
                <h4>真实感</h4>
                <p>Sora 2 生成的人物、环境、动作、光影，都比以前更加逼真，毫无油腻感。</p>
            </div>
            <div class="mini-card">
                <span class="icon">🔄</span>
                <h4>动态物理世界</h4>
                <p>Sora 2 在物体的动态物理规律表现上大幅提升。</p>
            </div>
            <div class="mini-card">
                <span class="icon">🧠</span>
                <h4>语义理解</h4>
                <p>Sora 2 对视频意图理解更加准确，从而生成更符合预期的视频。</p>
            </div>
            <div class="mini-card">
                <span class="icon">🎞️</span>
                <h4>自主分镜</h4>
                <p>Sora 2 支持分镜的生成，黑鲸千帆可以自动匹配分镜与视频内容。</p>
            </div>
            <div class="mini-card">
                <span class="icon">🎧</span>
                <h4>音乐与音效</h4>
                <p>Sora 2 支持音乐与音效的生成，黑鲸千帆可以自动匹配音乐与视频内容。</p>
            </div>
            <div class="mini-card">
                <span class="icon">💬</span>
                <h4>角色调用</h4>
                <p>Sora 2 支持对生成角色调用，黑鲸千帆可以自动调用角色生成一致性视频内容。</p>
            </div>
        </div>

        <div class="pricing-section">
            <div class="toggle-container" id="pricingToggle">
                <div class="toggle-slider" id="slider"></div>
                <button class="toggle-btn active" onclick="switchPricing('adv')">高级版 Advanced</button>
                <button class="toggle-btn" onclick="switchPricing('fla')">旗舰版 Flagship</button>
            </div>

            <div class="price-grid">
                <div class="price-content active" id="advGroup">
                    <div class="price-card">
                        <div class="p-title">初航版</div>
                        <div class="p-main">0.4元/条</div>
                        <button class="p-btn" onclick="toggleQR(true)">SELECT</button>
                        <div class="p-sub">3000条+额外赠送100条</div>
                        <ul class="p-features">
                            <li>永久有效，不限有效期</li>
                            <li>无限并发，一键批量提交</li>
                            <li>一键元数据抹除，告别AI强制标注</li>
                            <li>一键批量去水印</li>
                            <li>批量下载，文件自动命名归档</li>
                            <li>专为批量设计，一键根目录上传多批次任务</li>
                            <li>（图生）自动裁剪首2帧</li>
                        </ul>
                    </div>
                    <div class="price-card">
                        <div class="p-title">领航版</div>
                        <div class="p-main">0.24元/条</div>
                        <button class="p-btn" onclick="toggleQR(true)">SELECT</button>
                        <div class="p-sub">8000条+额外赠送200条</div>
                        <ul class="p-features">
                            <li>永久有效，不限有效期</li>
                            <li>无限并发，一键批量提交</li>
                            <li>一键元数据抹除，告别AI强制标注</li>
                            <li>一键批量去水印</li>
                            <li>批量下载，文件自动命名归档</li>
                            <li>专为批量设计，一键根目录上传多批次任务</li>
                            <li>（图生）自动裁剪首2帧</li>
                        </ul>
                    </div>
                    <div class="price-card">
                        <div class="p-title">巅峰版</div>
                        <div class="p-main">0.19元/条</div>
                        <button class="p-btn" onclick="toggleQR(true)">SELECT</button>
                        <div class="p-sub">15000条+额外赠送500条</div>
                        <ul class="p-features">
                            <li>永久有效，不限有效期</li>
                            <li>无限并发，一键批量提交</li>
                            <li>一键元数据抹除，告别AI强制标注</li>
                            <li>一键批量去水印</li>
                            <li>批量下载，文件自动命名归档</li>
                            <li>专为批量设计，一键根目录上传多批次任务</li>
                            <li>（图生）自动裁剪首2帧</li>
                        </ul>
                    </div>
                </div>

                <div class="price-content" id="flaGroup">
                    <div class="price-card">
                        <div class="p-title">初航版</div>
                        <div class="p-main">2.3元/条</div>
                        <button class="p-btn" onclick="toggleQR(true)">SELECT</button>
                        <div class="p-sub">500条+额外赠送50条</div>
                        <ul class="p-features">
                            <li>15s更高清</li>
                            <li>无限并发，一键批量提交</li>
                            <li>一键元数据抹除，告别AI强制标注</li>
                            <li>一键批量去水印</li>
                            <li>批量下载，文件自动命名归档</li>
                            <li>专为批量设计，一键根目录上传多批次任务</li>
                            <li>（图生）自动裁剪首2帧</li>
                        </ul>
                    </div>
                    <div class="price-card">
                        <div class="p-title">领航版</div>
                        <div class="p-main">1.8元/条</div>
                        <button class="p-btn" onclick="toggleQR(true)">SELECT</button>
                        <div class="p-sub">1000条+额外赠送100条</div>
                        <ul class="p-features">
                            <li>15s更高清</li>
                            <li>无限并发，一键批量提交</li>
                            <li>一键元数据抹除，告别AI强制标注</li>
                            <li>一键批量去水印</li>
                            <li>批量下载，文件自动命名归档</li>
                            <li>专为批量设计，一键根目录上传多批次任务</li>
                            <li>（图生）自动裁剪首2帧</li>
                        </ul>
                    </div>
                    <div class="price-card">
                        <div class="p-title">巅峰版</div>
                        <div class="p-main">0.5元/条</div>
                        <button class="p-btn" onclick="toggleQR(true)">SELECT</button>
                        <div class="p-sub">5000条+额外赠送200条</div>
                        <ul class="p-features">
                            <li>15s更高清</li>
                            <li>无限并发，一键批量提交</li>
                            <li>一键元数据抹除，告别AI强制标注</li>
                            <li>一键批量去水印</li>
                            <li>批量下载，文件自动命名归档</li>
                            <li>专为批量设计，一键根目录上传多批次任务</li>
                            <li>（图生）自动裁剪首2帧</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
        <div class="cta-box">
            <button class="btn-action" onclick="toggleQR(true)">联系试用</button>
            <br><br>
            <a href="../index.html" style="color:#666; text-decoration:none;">返回数字化内容库</a>
        </div>
    </div>

    <div id="qrOverlay" class="qr-overlay" onclick="toggleQR(false)">
        <div class="qr-card" onclick="event.stopPropagation()">
            <img src="../qr.png" alt="QR Code">
            <h3 style="margin-top:20px;">扫码联系我们</h3>
            <p style="color:#666;">获取试用名额</p>
        </div>
    </div>

    <script>
        const bg = document.getElementById('glow-bg');
        window.addEventListener('mousemove', (e) => {{
            bg.style.setProperty('--x', e.clientX + 'px');
            bg.style.setProperty('--y', e.clientY + 'px');
        }});

        function toggleQR(show) {{
            const el = document.getElementById('qrOverlay');
            el.style.display = show ? 'flex' : 'none';
        }}

        function switchPricing(mode) {{
            const toggle = document.getElementById('pricingToggle');
            const btns = document.querySelectorAll('.toggle-btn');
            const adv = document.getElementById('advGroup');
            const fla = document.getElementById('flaGroup');

            if(mode === 'adv') {{
                toggle.classList.remove('flagship-mode');
                btns[0].classList.add('active');
                btns[1].classList.remove('active');
                adv.classList.add('active');
                fla.classList.remove('active');
            }} else {{
                toggle.classList.add('flagship-mode');
                btns[0].classList.remove('active');
                btns[1].classList.add('active');
                adv.classList.remove('active');
                fla.classList.add('active');
            }}
        }}
    </script>
</body>
</html>"""
        with open(os.path.join(TOOL_DIR, "index.html"), "w", encoding="utf-8") as f: f.write(tool_html)

    def build_index(self, logger):
        SORA_DIR, UGC_DIR, HEADER_DIR, COURSE_DIR = "sora2", "ugc", "头图", "课程图"
        for d in [SORA_DIR, UGC_DIR, HEADER_DIR, COURSE_DIR, "toolweb"]:
            if not os.path.exists(d): os.makedirs(d)
        
        self.build_tool_page(logger)
        self.build_video_detail_page(SORA_DIR, logger)

        hero_imgs = [f"头图/{f}" for f in os.listdir(HEADER_DIR) if f.lower().endswith(('.png','.jpg','.jpeg','.webp'))]
        hero_wall = "".join([f'''
            <div class="float-img-container" style="top:{random.randint(15, 80)}%; {"left" if i%2==0 else "right"}:{random.randint(2, 18)}%; animation-delay:{i*0.6}s;">
                <img src="{img}" class="float-img">
                <span class="ai-tag">AI UGC CASE</span>
            </div>''' for i, img in enumerate(hero_imgs)])

        course_imgs = sorted([f"课程图/{f}" for f in os.listdir(COURSE_DIR) if f.lower().endswith(('.png','.jpg','.jpeg','.webp'))])
        course_html = "".join([f'<img src="{img}" style="width:100%; margin-bottom:40px; border-radius:25px; box-shadow:0 20px 50px rgba(0,0,0,0.05);">' for img in course_imgs])

        # 获取UGC卡片并追加引导卡片
        ugc_cards = self.gen_cards(UGC_DIR, "课程原创案例，详见视频课程讲解", logger, mode="full")
        ugc_cards += '<div class="video-card" onclick="toggleQR(true)" style="display:flex; flex-direction:column; align-items:center; justify-content:center; background:#f5f5f7; border:2px dashed #ddd;"><span style="font-size:40px; margin-bottom:15px;">🔍</span><span style="font-weight:700; color:#000;">查看更多课程实战案例</span><span style="font-size:12px; color:#888; margin-top:10px;">扫码咨询</span></div>'

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
        .qr-container img {{ width: auto; height: auto; max-width: 80vw; max-height: 80vh; border-radius: 20px; }}

        .modal {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.92); z-index: 9999; align-items: center; justify-content: center; }}
        .modal-body {{ width: 94%; max-width: 1200px; height: 85vh; background: #fff; border-radius: 40px; display: flex; overflow: hidden; }}
        .modal-left {{ flex: 1.4; background: #000; display: flex; align-items: center; justify-content: center; }}
        .modal-right {{ flex: 1; padding: 50px; overflow-y: auto; }}
        .more-trigger {{ grid-column: 1 / -1; text-align: center; padding: 40px; color: #86868b; font-weight: 600; cursor: pointer; }}
        .preview-alert {{ color: #FF0080; font-weight: bold; margin-top: 15px; display: block; }}
        .goto-btn {{ display: inline-block; margin-top: 20px; padding: 12px 25px; background: #000; color: #fff; border-radius: 12px; text-decoration: none; font-weight: 600; }}
        
        .sora-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }}
        .free-btn {{ padding: 12px 25px; background: #000; color: #fff; border-radius: 100px; font-weight: 600; text-decoration: none; transition: 0.3s; border: none; cursor: pointer; }}
        .free-btn:hover {{ background: var(--blue); }}
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
            <a class="contact-btn tool-btn" href="toolweb/index.html">黑鲸千帆一键无限生成工具</a>
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

    <div id="ugc" class="tab-content active" style="display:block; opacity:1;"><div class="grid">{ugc_cards}</div></div>
    <div id="sora" class="tab-content">
        <div class="sora-header">
            <h2 style="font-size:32px; margin:0;">Sora 2.0 深度创作库</h2>
            <button class="free-btn" onclick="toggleQR(true)">✨ 免费领取更多Sora 100+带货案例</button>
        </div>
        <div class="grid">{self.gen_cards(SORA_DIR, None, logger, mode="preview")}<div class="more-trigger" onclick="toggleQR(true)">—— 点击获取更多案例 ——</div></div>
    </div>
    <div id="course" class="tab-content"><div style="max-width:1000px; margin:0 auto;">{course_html}</div></div>

    <div id="videoModal" class="modal" onclick="closeModal()">
        <div class="modal-body" onclick="event.stopPropagation()">
            <div class="modal-left" id="modalMedia"></div>
            <div class="modal-right">
                <h2 id="mTitle" style="font-size:28px;"></h2>
                <div id="previewNotice" style="display:none;">
                    <span class="preview-alert">⚠️ 当前仅预览，前往观看完整视频</span>
                    <a href="videos.html" class="goto-btn">🎥 查看更多视频</a>
                </div>
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
        function openModal(url, title, prompt, isVideo, isPreview) {{
            const container = document.getElementById('modalMedia');
            const notice = document.getElementById('previewNotice');
            if(isPreview && isVideo) {{
                const poster = url.substring(0, url.lastIndexOf("/")) + "/poster.jpg";
                container.innerHTML = `<img src="${{poster}}" style="max-width:100%; max-height:100%;">`;
                notice.style.display = 'block';
            }} else {{
                if(isVideo) {{ container.innerHTML = `<video src="${{url}}" style="max-width:100%; max-height:100%;" controls autoplay></video>`; }}
                else {{ container.innerHTML = `<img src="${{url}}" style="max-width:100%; max-height:100%;">`; }}
                notice.style.display = 'none';
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

    def build_video_detail_page(self, folder, logger):
        html_content = f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BlackWhale | Sora2 视频空间</title>
    <style>
        :root {{ --blue: #0057ff; }}
        body, html {{ background: #050505; color: #fff; font-family: "SF Pro Display", sans-serif; margin: 0; padding: 0; }}
        .header {{ padding: 40px 5%; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #1a1a1a; }}
        .back-link {{ color: #888; text-decoration: none; font-size: 16px; transition: 0.3s; }}
        .back-link:hover {{ color: #fff; }}
        .grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 20px; padding: 40px 5%; }}
        .video-card {{ background: #111; border-radius: 22px; overflow: hidden; aspect-ratio: 9/16; cursor: pointer; transition: 0.3s; border: 1px solid #222; }}
        .video-card:hover {{ border-color: var(--blue); transform: scale(1.02); }}
        .video-card video {{ width: 100%; height: 100%; object-fit: cover; }}
        .modal {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.95); z-index: 9999; align-items: center; justify-content: center; }}
        .modal-body {{ width: 94%; max-width: 1200px; height: 85vh; background: #111; border-radius: 40px; display: flex; overflow: hidden; border: 1px solid #333; }}
        .modal-left {{ flex: 1.4; background: #000; display: flex; align-items: center; justify-content: center; }}
        .modal-right {{ flex: 1; padding: 50px; overflow-y: auto; color: #eee; }}
        #mPrompt {{ background:#1a1a1a; padding:25px; border-radius:20px; white-space:pre-wrap; line-height:1.6; border: 1px solid #333; }}
    </style>
</head>
<body>
    <div class="header">
        <h1 style="margin:0; font-size:32px;">Sora2 高清视频全集</h1>
        <a href="index.html" class="back-link">← 返回主页</a>
    </div>
    <div class="grid">{self.gen_cards(folder, None, logger, mode="full")}</div>
    
    <div id="videoModal" class="modal" onclick="closeModal()">
        <div class="modal-body" onclick="event.stopPropagation()">
            <div class="modal-left" id="modalMedia"></div>
            <div class="modal-right">
                <h2 id="mTitle" style="font-size:28px;"></h2>
                <div style="color:var(--blue); font-weight:700; margin:25px 0 10px 0;">解析与提示词:</div>
                <div id="mPrompt"></div>
                <button onclick="copyPrompt()" style="margin-top:20px; padding:10px 20px; border-radius:10px; border:none; background:var(--blue); color:white; cursor:pointer;">复制提示词</button>
            </div>
        </div>
    </div>

    <script>
        function openModal(url, title, prompt, isVideo) {{
            const container = document.getElementById('modalMedia');
            container.innerHTML = `<video src="${{url}}" style="max-width:100%; max-height:100%;" controls autoplay></video>`;
            document.getElementById('mTitle').innerText = title;
            document.getElementById('mPrompt').innerText = prompt;
            document.getElementById('videoModal').style.display = 'flex';
        }}
        function closeModal() {{ document.getElementById('videoModal').style.display='none'; document.getElementById('modalMedia').innerHTML=''; }}
        function copyPrompt() {{
            const text = document.getElementById('mPrompt').innerText;
            navigator.clipboard.writeText(text).then(() => alert('提示词已复制'));
        }}
    </script>
</body>
</html>"""
        with open("videos.html", "w", encoding="utf-8") as f: f.write(html_content)

    def gen_cards(self, folder, fixed_prompt, logger, mode="full"):
        cards = ""
        if not os.path.exists(folder): return ""
        tasks = sorted([d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))], reverse=True)
        for t in tasks:
            t_path = os.path.join(folder, t)
            video_file = next((f for f in os.listdir(t_path) if f.lower().endswith('.mp4')), None)
            img_file = next((f for f in os.listdir(t_path) if f.lower().endswith(('.png','.jpg','.jpeg','.webp'))), None)
            poster_arg = ""
            poster_path = os.path.join(t_path, "poster.jpg")
            
            if video_file and not os.path.exists(poster_path):
                try: subprocess.run(["ffmpeg", "-y", "-i", os.path.join(t_path, video_file), "-ss", "00:00:00.5", "-vframes", "1", poster_path], capture_output=True)
                except: pass
            
            if os.path.exists(poster_path): poster_arg = f'poster="{folder}/{t}/poster.jpg"'
            
            file_url = f"{folder}/{t}/{video_file if video_file else img_file}"
            is_video = "true" if video_file else "false"
            is_preview = "true" if mode == "preview" else "false"
            
            if mode == "preview" and video_file:
                display_html = f'<img src="{folder}/{t}/poster.jpg" loading="lazy">'
            else:
                display_html = f'<video {poster_arg} preload="none" muted loop onmouseover="this.play()" onmouseout="this.pause()"><source src="{file_url}"></video>' if video_file else f'<img src="{file_url}" loading="lazy">'
            
            title, prompt = t, fixed_prompt if fixed_prompt else "解析加载中..."
            info_p = os.path.join(t_path, "info.txt")
            if not fixed_prompt and os.path.exists(info_p):
                with open(info_p, "r", encoding="utf-8", errors="ignore") as f:
                    c = f.read()
                    if "标题:" in c: title = c.split("标题:")[1].split("提示词:")[0].strip()
                    if "提示词:" in c: prompt = c.split("提示词:")[1].strip().replace('"', '&quot;').replace('`', '\\`')
            
            cards += f'<div class="video-card" onclick="openModal(\'{file_url}\', \'{title}\', `{prompt}`, {is_video}, {is_preview})">{display_html}</div>'
        return cards

    def git_sync(self, logger):
        try:
            logger.emit("[同步] 正在上传至 GitHub...")
            def run_git(args): return subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            run_git(["git", "add", "."])
            run_git(["git", "commit", "-m", f"Aura_SoraPro_SplitUpdate_{datetime.now().strftime('%m%d%H%M')}"])
            res = run_git(["git", "push", "origin", "main"])
            if res.returncode == 0: logger.emit("🎉 部署成功！主页已优化预览，独立视频空间已上线。")
            else: logger.emit(f"❌ 推送失败: {res.stderr}")
        except Exception as e: logger.emit(f"❌ 异常: {str(e)}")
        finally: self.finalize_deploy()

if __name__ == "__main__":
    app = QApplication(sys.argv); win = PublisherTitanV23Liquid(); win.show(); sys.exit(app.exec())