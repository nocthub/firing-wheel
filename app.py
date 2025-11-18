from flask import Flask, render_template, render_template_string
from flask_socketio import SocketIO
import os
import psutil
import threading
import time
import math # لإجراء العمليات الحسابية (لاختبار الضغط)

# --- 1. الإعداد الأولي ---
app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')

# --- (نسخة الحوت الآمنة) ---
WHALE_ART_LINES = [
    "                  ##         ##",
    "             ##   ##   ##    ..",
    "          ## ## ## ## ## ##  ===",
    "      /=====================\\\\/ ===",
    "     {                       / ===",
    "      \\\\______ O           __/",
    "        \\\\    \\\\         __/",
    "         \\\\____\\\\_______/"
]
# --- نهاية تعريف الحوت ---


# --- 2. دالة لجلب البيانات الحية ---
def get_system_stats():
    """
    تجلب إحصائيات النظام الحية (CPU, Memory, Disk)
    """
    try:
        cpu_percent = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        mem_percent = mem.percent
        mem_used = mem.used
        mem_total = mem.total
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        disk_used = disk.used
        disk_total = disk.total
        return {
            "cpu": cpu_percent,
            "mem": {"percent": mem_percent, "used": mem_used, "total": mem_total},
            "disk": {"percent": disk_percent, "used": disk_used, "total": disk_total}
        }
    except Exception as e:
        print(f"Error getting stats: {e}")
        return {}

# --- 3. دالة لمساعدتنا في عرض (GB / MB) ---
def format_bytes(b):
    """يحول البايت إلى MB أو GB"""
    gb = b / (1024**3)
    mb = b / (1024**2)
    if gb >= 1: return f"{gb:.1f} GB"
    else: return f"{mb:.1f} MB"

# --- 4. الخيط (Thread) الذي يعمل في الخلفية ---
thread = None
thread_started = False
def background_thread():
    """يرسل الإحصائيات للمستخدم كل ثانية"""
    global thread_started
    thread_started = True
    print("Starting background thread...")
    while True:
        stats = get_system_stats()
        if stats:
            stats["hostname"] = os.uname()[1]
            stats["pid"] = os.getpid()
            stats["mem"]["used_f"] = format_bytes(stats["mem"]["used"])
            stats["mem"]["total_f"] = format_bytes(stats["mem"]["total"])
            stats["disk"]["used_f"] = format_bytes(stats["disk"]["used"])
            stats["disk"]["total_f"] = format_bytes(stats["disk"]["total"])
            socketio.emit('system_stats', stats)
        socketio.sleep(1)

# --- 5. التعامل مع اتصال المستخدم ---
@socketio.on('connect')
def handle_connect():
    global thread
    if not thread_started:
        thread = socketio.start_background_task(target=background_thread)
    print("Client connected!")

# --- 6. متغيرات البيئة للروابط ---
YOUTUBE_CHANNEL_URL = os.environ.get('YT_CHANNEL_URL', 'https://www.youtube.com/@vandire7')
YOUTUBE_SUBSCRIBE_URL = os.environ.get('YT_SUBSCRIBE_URL', 'https://www.youtube.com/@vandire7?sub_confirmation=1')
YOUTUBE_SHARE_URL = os.environ.get('YT_SHARE_URL', 'https://www.youtube.com/@vandire7')

# --- (كود اختبار الضغط القوي) ---
def stress_worker(duration_sec):
    """
    هذه هي الدالة التي ستعمل على كل نواة (core)
    """
    start_time = time.time()
    while (time.time() - start_time) < duration_sec:
        _ = math.sqrt(64*64*64*64*64) # عملية حسابية عشوائية لاختبار الضغط

@app.route('/stress')
def stress_cpu():
    """
    نقطة النهاية (endpoint) التي تشغل الاختبار على كل الأنوية
    """
    try:
        cpu_count = psutil.cpu_count()
        print(f"Starting CPU stress test on {cpu_count} cores for 5 seconds...")
        for _ in range(cpu_count):
            # ابدأ خيط (thread) جديد لكل نواة
            threading.Thread(target=stress_worker, args=[5]).start()
        return {"status": f"CPU stress test started on {cpu_count} cores for 5 seconds!"}
    except Exception as e:
        print(f"Error starting stress test: {e}")
        return {"status": "Error starting stress test"}, 500
# --- نهاية كود اختبار الضغط ---


# --- 7. كود الـ HTML / CSS / JS (مع كل التحديثات) ---
HTML_CONTENT = """
<html>
<head>
    <title> Docker Showcase by vandire (Live!)</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@700&family=Montserrat:wght@400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>

    <style>
        /* ... (كل أكواد CSS تبقى كما هي - لا تغيير هنا) ... */
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@700&family=Montserrat:wght@400;700&display=swap');

        html, body {
            margin: 0;
            padding: 0;
            overflow: hidden;
            font-family: 'Cairo', sans-serif;
            background: #1d2b64;
        }
        .app-wrapper {
            width: 100%;
            height: 100vh;
            transition: transform 0.8s cubic-bezier(0.4, 0, 0.2, 1);
            transform: translateY(0);
        }
        .section-main, .section-whale {
            width: 100%;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            position: relative;
            box-sizing: border-box;
            color: #ffffff;
            transition: filter 0.5s ease, transform 0.5s ease;
        }
        .section-main {
            background: linear-gradient(135deg, #1d2b64 0%, #f8cdda 100%);
        }
        .section-whale {
            justify-content: center;
            background-color: #1a2035;
            background-image: radial-gradient(
                circle at center,
                rgba(220, 38, 38, 0.4) 0%,
                rgba(26, 32, 53, 0) 60%
            );
            background-size: 200% 200%;
            animation: danger-glow 4s ease-in-out infinite;
        }
        @keyframes danger-glow {
            0% {
                background-position: 50% 50%;
                background-size: 150% 150%;
                opacity: 0.7;
            }
            50% {
                background-position: 50% 50%;
                background-size: 250% 250%;
                opacity: 1;
            }
            100% {
                background-position: 50% 50%;
                background-size: 150% 150%;
                opacity: 0.7;
            }
        }
        .side-panel {
            position: fixed;
            top: 0;
            right: -380px;
            width: 380px;
            height: 100%;
            background: rgba(26, 32, 53, 0.98);
            box-shadow: -10px 0 30px rgba(0,0,0,0.7);
            transition: right 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            z-index: 1000;
            padding: 25px;
            box-sizing: border-box;
            text-align: left;
            font-family: 'Montserrat', sans-serif;
            overflow-y: auto;
        }
        .side-panel.open { right: 0; }
        .side-panel h2 {
            color: #ffcc00; text-align: center; border-bottom: 2px solid #ffcc00;
            padding-bottom: 15px; margin-bottom: 30px; font-size: 1.8em;
            text-shadow: 0 0 10px rgba(255,204,0,0.5);
        }
        .stat-group {
            margin-bottom: 25px; background: rgba(255, 255, 255, 0.05);
            padding: 15px; border-radius: 10px; border-left: 5px solid #17a2b8;
        }
        .stat-item {
            margin-bottom: 15px; font-size: 1.1em; display: flex; align-items: center;
            color: #e0e0e0;
        }
        .stat-item i {
            font-size: 1.3em; margin-right: 15px; color: #17a2b8;
            width: 25px; text-align: center;
        }
        .stat-item strong {
            color: #ffffff;
            margin-right: 10px;
        }
        .stat-item span {
            color: #e0e0e0;
        }
        .stat-item .copyable-id {
            display: inline-block;
            margin-left: 10px;
            padding: 2px 5px;
            background: #222;
            color: #00ff00;
            border-radius: 4px;
            cursor: pointer;
            font-family: 'Courier New', Courier, monospace;
            font-size: 0.9em;
            transition: background-color 0.3s ease, color 0.3s ease;
            white-space: pre;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .stat-item .copyable-id:hover {
            background-color: #333;
        }
        .progress-bar-container {
            width: 100%; background-color: #333; border-radius: 5px;
            overflow: hidden; margin-top: 5px;
        }
        .progress-bar {
            height: 15px; background-color: #28a745; width: 0%;
            border-radius: 5px; transition: width 0.3s ease-out;
        }
        .progress-bar.cpu { background-color: #007bff; }
        .progress-bar.mem { background-color: #28a745; }
        .progress-bar.disk { background-color: #dc3545; }
        .panel-toggle {
            position: fixed; top: 50%; right: 0px; transform: translateY(-50%);
            width: 50px; height: 50px; background: #ffcc00; color: #1d2b64;
            display: flex; justify-content: center; align-items: center;
            font-size: 1.5em; border-radius: 10px 0 0 10px; cursor: pointer;
            z-index: 1001; transition: right 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        }
        .panel-toggle.open { right: 380px; }
        body.panel-open .wheel-app-content {
            filter: blur(8px) brightness(0.7);
            transform: scale(0.98);
            pointer-events: none;
        }
        body.panel-open .section-whale h2,
        body.panel-open .section-whale pre,
        body.panel-open .section-whale p,
        body.panel-open .whale-bubble-danger,
        body.panel-open .buttons-group {
            filter: blur(8px) brightness(0.7);
            pointer-events: none;
        }
        body.panel-open .scroll-toggle {
            filter: blur(8px);
            pointer-events: none;
        }
        .wheel-app-content {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 20px;
            background: rgba(0, 0, 0, 0.85);
            border-radius: 25px;
            box-shadow: 0 15px 40px rgba(0,0,0,0.8);
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: filter 0.5s ease, transform 0.5s ease;
            text-align: center;
        }
        .wheel-app-content h1 {
            color: #ffffff;
            font-size: 2.5em;
            margin-top: 0;
            margin-bottom: 10px;
            text-shadow: 0 0 10px rgba(255,255,255,0.7);
        }
         .wheel-app-content h1 i {
            color: #ffcc00;
            margin: 0 10px;
        }
        .wheel-container {
            position: relative;
            width: 350px;
            height: 350px;
            margin-bottom: 20px;
        }
        .wheel-pointer {
            position: absolute;
            top: -10px;
            left: 50%;
            transform: translateX(-50%);
            width: 0;
            height: 0;
            border-left: 20px solid transparent;
            border-right: 20px solid transparent;
            border-top: 30px solid #ffcc00; /* مؤشر أصفر */
            z-index: 10;
        }
        #wheelCanvas {
            width: 100%;
            height: 100%;
            transition: transform 5s cubic-bezier(0.25, 0.1, 0.25, 1);
        }
        .wheel-controls {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 300px;
        }
        #nameInput {
            width: 100%;
            height: 100px;
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            color: white;
            font-family: 'Cairo', sans-serif;
            font-size: 1em;
            padding: 10px;
            box-sizing: border-box;
            margin-bottom: 15px;
            resize: none;
        }
        #spinButton {
            width: 100%;
            padding: 15px;
            background-color: #dc3545; /* أحمر */
            border: none;
            border-radius: 8px;
            color: white;
            font-family: 'Cairo', sans-serif;
            font-size: 1.2em;
            font-weight: 700;
            cursor: pointer;
            transition: background-color 0.3s ease, transform 0.2s ease;
        }
        #spinButton:hover:not(:disabled) {
            background-color: #c82333;
            transform: translateY(-2px);
        }
        #spinButton:disabled {
            background-color: #555;
            cursor: not-allowed;
            opacity: 0.7;
        }
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(5px);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 2000;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
        }
        .modal-overlay.visible {
            opacity: 1;
            pointer-events: auto;
        }
        .modal-box {
            background: #1a2035;
            padding: 30px;
            border-radius: 15px;
            border: 1px solid #ffcc00;
            box-shadow: 0 0 30px rgba(255, 204, 0, 0.5);
            text-align: center;
            transform: scale(0.9);
            transition: transform 0.3s ease;
        }
        .modal-overlay.visible .modal-box {
            transform: scale(1);
        }
        .modal-box h2 {
            font-family: 'Cairo', sans-serif;
            color: #ffcc00;
            font-size: 2em;
            margin-top: 0;
        }
        .modal-box h2 i {
            color: #dc3545;
            margin-right: 10px;
            animation: gavel-hit 0.5s ease;
        }
        @keyframes gavel-hit {
            0% { transform: rotate(0deg); }
            50% { transform: rotate(-25deg); }
            100% { transform: rotate(0deg); }
        }
        .modal-box p {
            font-family: 'Montserrat', sans-serif;
            font-size: 1.2em;
            color: white;
            margin-bottom: 25px;
        }
        .modal-box button {
            padding: 10px 20px;
            background-color: #ffcc00;
            border: none;
            border-radius: 8px;
            color: #1a2035;
            font-family: 'Cairo', sans-serif;
            font-size: 1em;
            font-weight: 700;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        .modal-box button:hover {
            background-color: #ffffff;
        }
        #splashOverlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(10px);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            opacity: 1;
            transition: opacity 0.5s ease;
        }
        #splashOverlay.hidden {
            opacity: 0;
            pointer-events: none;
        }
        .splash-content {
            text-align: center;
            color: white;
        }
        .splash-content h1 {
            font-size: 2.5em;
            color: #ffcc00;
        }
        .splash-content p {
            font-size: 1.2em;
            font-family: 'Montserrat', sans-serif;
            margin-bottom: 30px;
        }
        #startAppBtn {
            padding: 15px 30px;
            background-color: #28a745;
            border: none;
            border-radius: 10px;
            color: white;
            font-family: 'Cairo', sans-serif;
            font-size: 1.2em;
            font-weight: 700;
            cursor: pointer;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        #startAppBtn:hover {
            transform: scale(1.05);
            box-shadow: 0 0 20px #28a745;
        }
        .section-whale h2 {
            color: #ffcc00;
            font-family: 'Cairo', sans-serif;
            font-size: 1.8em;
            margin-top: 10px;
            margin-bottom: 20px;
            text-shadow: 0 0 10px rgba(255,204,0,0.7);
            transition: filter 0.5s ease, transform 0.5s ease;
            position: absolute;
            top: 70px;
        }
        .section-whale h2 i {
            color: #ef4444;
            text-shadow: 0 0 10px #ef4444;
            margin-right: 10px;
            animation: float 2s ease-in-out infinite;
        }
        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-5px); }
            100% { transform: translateY(0px); }
        }
        .ascii-whale {
            font-family: 'Courier New', Courier, monospace;
            white-space: pre;
            font-size: 1.1em;
            color: #ff8a8a;
            text-shadow: 0 0 10px #dc2626, 0 0 20px #dc2626;
            animation: text-flicker 3s infinite;
            margin: 0;
            line-height: 1.2;
            text-align: center;
            transition: filter 0.5s ease, transform 0.5s ease;
            margin-bottom: 40px;
        }
        @keyframes text-flicker {
            0% { opacity: 1; }
            50% { opacity: 0.8; }
            100% { opacity: 1; }
        }
        .whale-bubble-danger {
            background: rgba(0, 0, 0, 0.2);
            backdrop-filter: blur(5px) brightness(0.9);
            border: 2px solid #ef4444;
            box-shadow: 0 0 20px #ef4444, inset 0 0 10px rgba(239, 68, 68, 0.5);
            padding: 20px 30px;
            border-radius: 15px;
            position: relative;
            max-width: 400px;
            transition: filter 0.5s ease, transform 0.5s ease;
            animation: pulse-border 2s infinite ease-in-out;
        }
        .whale-bubble-danger::before {
            content: '';
            position: absolute;
            top: -12px;
            left: 50%;
            transform: translateX(-50%);
            width: 0;
            height: 0;
            border-left: 10px solid transparent;
            border-right: 10px solid transparent;
            border-bottom: 10px solid #ef4444;
        }
        @keyframes pulse-border {
            0% {
                border-color: #ef4444;
                box-shadow: 0 0 20px #ef4444, inset 0 0 10px rgba(239, 68, 68, 0.5);
            }
            50% {
                border-color: #ff8a8a;
                box-shadow: 0 0 35px #ff8a8a, inset 0 0 15px rgba(239, 68, 68, 0.7);
            }
            100% {
                border-color: #ef4444;
                box-shadow: 0 0 20px #ef4444, inset 0 0 10px rgba(239, 68, 68, 0.5);
            }
        }
        #whale-text {
            font-family: 'Cairo', sans-serif;
            font-weight: 700;
            font-size: 1.6em;
            color: #ffffff;
            margin: 0;
            text-shadow: 0 0 5px rgba(255, 255, 255, 0.7);
            transition: filter 0.5s ease, transform 0.5s ease;
        }
        #whale-text::after {
            content: '_';
            display: inline-block;
            animation: blink-caret 0.75s infinite;
            color: #ef4444;
        }
        @keyframes blink-caret {
            from, to { opacity: 1; }
            50% { opacity: 0; }
        }
        .buttons-group {
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
            position: absolute;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            width: 100%;
            opacity: 0.7;
            transition: opacity 0.3s ease, filter 0.5s ease;
        }
        .buttons-group:hover {
            opacity: 1.0;
        }
        .action-button {
            width: 70px;
            height: 70px;
            border-radius: 20px;
            display: flex;
            justify-content: center; align-items: center;
            color: white; cursor: pointer; text-decoration: none;
            box-shadow: 0 8px 20px rgba(0,0,0,0.4);
            transition: transform 0.3s ease, box-shadow 0.3s ease, background-color 0.3s ease;
        }
        .action-button i {
            font-size: 2.2em;
        }
        .like-btn { background: #28a745; }
        .like-btn:hover { transform: translateY(-5px) scale(1.05); box-shadow: 0 0 30px 5px #28a745; }
        .share-btn { background: #17a2b8; }
        .share-btn:hover { transform: translateY(-5px) scale(1.05); box-shadow: 0 0 30px 5px #17a2b8; }
        .subscribe-btn { background: #dc3545; }
        .subscribe-btn:hover { transform: translateY(-5px) scale(1.05); box-shadow: 0 0 30px 5px #dc3545; }
        .side-panel-button {
            display: block;
            width: 100%;
            padding: 12px;
            background-color: #ff8c00;
            border: none;
            border-radius: 8px;
            color: white;
            font-family: 'Cairo', sans-serif;
            font-size: 1.1em;
            font-weight: 700;
            cursor: pointer;
            transition: background-color 0.3s ease, transform 0.2s ease;
            text-align: center;
        }
        .side-panel-button:hover:not(:disabled) {
            background-color: #ffad42;
            transform: translateY(-2px);
        }
        .side-panel-button:disabled {
            background-color: #555;
            cursor: not-allowed;
            opacity: 0.7;
        }
        .side-panel-button i {
            margin-right: 8px;
        }
        .scroll-toggle {
            position: absolute;
            left: 50%;
            transform: translateX(-50%);
            width: 60px;
            height: 30px;
            background: #ffcc00;
            color: #1d2b64;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 1.5em;
            cursor: pointer;
            z-index: 1001;
            transition: background-color 0.3s ease, filter 0.5s ease;
        }
        .scroll-toggle:hover {
            background-color: #fff;
        }
        #scrollDownBtn {
            bottom: 20px;
            border-radius: 10px 10px 0 0;
            animation: bounce 2s infinite;
        }
        #scrollUpBtn {
            top: 20px;
            border-radius: 0 0 10px 10px;
        }
        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% { transform: translate(-50%, 0); }
            40% { transform: translate(-50%, -10px); }
            60% { transform: translate(-50%, -5px); }
        }
    </style>
</head>
<body>

    <div id="splashOverlay">
        <div class="splash-content">
            <h1><i class="fas fa-volume-up"></i> تطبيق المدير</h1>
            <p>هذه التجربة تتضمن أصواتاً. الرجاء الضغط للبدء.</p>
            <button id="startAppBtn">ابدأ التجربة (مع الصوت)</button>
        </div>
    </div>

    <div class="app-wrapper" id="appWrapper">

        <div class="section-main">
            <div class="wheel-app-content">
                <h1> أحمد يقدم لكم تطبيق المدير </h1>

                <div class="wheel-container">
                    <div class="wheel-pointer"></div>
                    <canvas id="wheelCanvas" width="400" height="400"></canvas>
                </div>

                <div class="wheel-controls">
                    <textarea id="nameInput" rows="5" placeholder="أدخل أسماء الموظفين هنا (كل اسم في سطر)..."></textarea>
                    <button id="spinButton">
                        <i class="fas fa-play"></i> ابدأ الدوران!
                    </button>
                </div>
            </div>

            <div class="scroll-toggle" id="scrollDownBtn">
                <i class="fas fa-chevron-down"></i>
            </div>
        </div>

        <div class="section-whale">
            <div class="scroll-toggle" id="scrollUpBtn">
                <i class="fas fa-chevron-up"></i>
            </div>

            <h2><i class="fas fa-ghost"></i> لقد تم غزوكم من طرف الحوت!</h2>

            <pre id="ascii-whale" class="ascii-whale"></pre>

            <div class="whale-bubble-danger">
                <p id="whale-text"></p>
            </div>

            <div class="buttons-group">
                <a href="{{YOUTUBE_CHANNEL_URL}}" target="blank" rel="noopener noreferrer" class="action-button like-btn" title="إعجاب!">
                    <i class="fas fa-thumbs-up"></i>
                </a>
                <a href="{{YOUTUBE_SHARE_URL}}" target="blank" rel="noopener noreferrer" class="action-button share-btn" title="مشاركة!">
                    <i class="fas fa-share-alt"></i>
                </a>
                <a href="{{YOUTUBE_SUBSCRIBE_URL}}" target="blank" rel="noopener noreferrer" class="action-button subscribe-btn" title="اشتراك!">
                    <i class="fab fa-youtube"></i>
                </a>
            </div>
        </div>

    </div>
    <div class="panel-toggle" id="panelToggle">
        <i class="fas fa-chevron-left"></i>
    </div>
    <div class="side-panel" id="sidePanel">
        <h2><i class="fas fa-server"></i> Live Container Stats</h2>
        <div class="stat-group">
            <div class="stat-item"><i class="fas fa-microchip"></i> <strong>CPU Usage:</strong> <span id="cpuPercent">--</span>%</div>
            <div class="progress-bar-container"><div class="progress-bar cpu" id="cpuProgressBar"></div></div>
        </div>
        <div class="stat-group">
            <div class="stat-item"><i class="fas fa-memory"></i> <strong>Memory Usage:</strong> <span id="memPercent">--</span>%</div>
            <div class="progress-bar-container"><div class="progress-bar mem" id="memProgressBar"></div></div>
            <p style="font-size:0.9em; color:#bbb; margin-top:5px; margin-bottom:0;">
                <i class="fas fa-chart-pie" style="font-size:0.9em; margin-right:5px;"></i> Used: <span id="memUsed">--</span> / Total: <span id="memTotal">--</span>
            </p>
        </div>
        <div class="stat-group">
            <div class="stat-item"><i class="fas fa-hdd"></i> <strong>Disk Usage:</strong> <span id="diskPercent">--</span>%</div>
            <div class="progress-bar-container"><div class="progress-bar disk" id="diskProgressBar"></div></div>
            <p style="font-size:0.9em; color:#bbb; margin-top:5px; margin-bottom:0;">
                <i class="fas fa-chart-area" style="font-size:0.9em; margin-right:5px;"></i> Used: <span id="diskUsed">--</span> / Total: <span id="diskTotal">--</span>
            </p>
        </div>
        <div class="stat-group">
            <div class="stat-item"><i class="fas fa-cogs"></i> <strong>Application PID:</strong> <span id="pid">--</span></div>

            <div class="stat-item" style="margin-bottom:0; align-items: baseline;">
                <i class="fas fa-fingerprint"></i>
                <strong>Container ID:</strong>
                <pre id="hostname" class="copyable-id" title="Click to copy ID">Loading...</pre>
            </div>

        </div>
        <div class="stat-group">
            <div class="stat-item" style="margin-bottom: 10px;">
                <i class="fas fa-bolt" style="color: #ff8c00;"></i>
                <strong>Multi-Core Stress Test</strong>
            </div>
            <button id="stressBtn" class="side-panel-button">
                <i class="fas fa-bolt"></i>
                <span>Test All Cores (5s)</span>
            </button>
        </div>
    </div>

    <div id="modalOverlay" class="modal-overlay">
        <div class="modal-box">
            <h2><i class="fas fa-gavel"></i> قرار المدير</h2>
            <p id="modalMessage"></p>
            <button id="closeModalBtn">مفهوم</button>
        </div>
    </div>

    <audio id="spinningSound" src="/static/sounds/spinning.mp3" preload="auto" loop></audio>
    <audio id="winnerSound" src="/static/sounds/win.mp3" preload="auto"></audio>
    <audio id="dangerSound" src="/static/sounds/danger.mp3" preload="auto" loop muted></audio>


    <script>
        // --- (!!! جديد: تمرير بيانات الحوت إلى جافاسكريبت) ---
        const whaleAsciiLines = {{ WHALE_ART_LINES|tojson }};
        let isAsciiAnimating = false;

        // --- (!!! جديد: جلب عناصر شاشة البداية) ---
        const splashOverlay = document.getElementById('splashOverlay');
        const startAppBtn = document.getElementById('startAppBtn');
        const spinSound = document.getElementById('spinningSound'); // (!!! تعديل)
        const winnerSound = document.getElementById('winnerSound');
        const dangerSound = document.getElementById('dangerSound');

        startAppBtn.addEventListener('click', () => {
            // (!!! جديد: "فتح" جميع الأصوات)
            spinSound.play();
            spinSound.pause();
            spinSound.currentTime = 0;

            winnerSound.play();
            winnerSound.pause();
            winnerSound.currentTime = 0;

            dangerSound.play(); // سيبدأ مكتوماً

            // إخفاء شاشة البداية
            splashOverlay.classList.add('hidden');
        });


        // --- (كود التمرير بين الأقسام) ---
        const appWrapper = document.getElementById('appWrapper');
        const scrollDownBtn = document.getElementById('scrollDownBtn');
        const scrollUpBtn = document.getElementById('scrollUpBtn');

        scrollDownBtn.addEventListener('click', () => {
            appWrapper.style.transform = 'translateY(-100vh)';

            // (!!! تعديل: "إلغاء كتم" الصوت)
            dangerSound.muted = false;
            dangerSound.volume = 0.5;

            if (!isAsciiAnimating) {
                animateAsciiWhale();
            }
        });

        // (!!! تعديل: إرجاع الكتم عند العودة)
        scrollUpBtn.addEventListener('click', () => {
            appWrapper.style.transform = 'translateY(0)';
            dangerSound.muted = true; // <--- إرجاع الكتم
        });

        // --- كود اللوحة الجانبية (مع إرجاع الضبابية) ---
        const panelToggle = document.getElementById('panelToggle');
        const sidePanel = document.getElementById('sidePanel');
        const body = document.body;

        panelToggle.addEventListener('click', () => {
            sidePanel.classList.toggle('open');
            panelToggle.classList.toggle('open');
            body.classList.toggle('panel-open');

            const icon = panelToggle.querySelector('i');
            if (sidePanel.classList.contains('open')) {
                icon.classList.remove('fa-chevron-left');
                icon.classList.add('fa-chevron-right');
            } else {
                icon.classList.remove('fa-chevron-right');
                icon.classList.add('fa-chevron-left');
            }
        });

        var socket = io();

        function updateText(id, value) {
            const el = document.getElementById(id);
            if (el) { el.innerText = value; }
        }
        function updateProgressBar(id, percent) {
            const bar = document.getElementById(id);
            if (bar) { bar.style.width = percent + '%'; }
        }

        // (متغير لحالة النسخ)
        let isCopying = false;
        let originalHostname = 'Loading...';

        socket.on('system_stats', function(data) {
            updateText('cpuPercent', data.cpu.toFixed(1));
            updateText('memPercent', data.mem.percent.toFixed(1));
            updateText('memUsed', data.mem.used_f);
            updateText('memTotal', data.mem.total_f);
            updateText('diskPercent', data.disk.percent.toFixed(1));
            updateText('diskUsed', data.disk.used_f);
            updateText('diskTotal', data.disk.total_f);
            updateText('pid', data.pid);

            originalHostname = data.hostname;
            if (!isCopying) {
                updateText('hostname', data.hostname);
            }

            updateProgressBar('cpuProgressBar', data.cpu);
            updateProgressBar('memProgressBar', data.mem.percent);
            updateProgressBar('diskProgressBar', data.disk.percent);
        });

        // --- (كود النسخ عند النقر) ---
        const hostnameEl = document.getElementById('hostname');
        hostnameEl.addEventListener('click', () => {
            if (isCopying || originalHostname === 'Loading...') return;

            navigator.clipboard.writeText(originalHostname).then(() => {
                isCopying = true;
                hostnameEl.innerText = 'Copied!';
                hostnameEl.style.color = '#ffcc00'; // Yellow
                hostnameEl.style.backgroundColor = '#444';

                setTimeout(() => {
                    hostnameEl.innerText = originalHostname;
                    hostnameEl.style.color = '#00ff00'; // Back to green
                    hostnameEl.style.backgroundColor = '#222';
                    isCopying = false;
                }, 1000);
            }).catch(err => {
                console.error('Failed to copy text: ', err);
            });
        });

        // --- كود زر اختبار الضغط (كما هو) ---
        document.getElementById('stressBtn').addEventListener('click', () => {
            const btn = document.getElementById('stressBtn');
            const icon = btn.querySelector('i');
            const btnText = btn.querySelector('span');

            btn.disabled = true;
            icon.className = 'fas fa-cog fa-spin';
            if (btnText) { btnText.textContent = 'Testing...'; }

            fetch('/stress')
                .then(res => res.json())
                .then(data => {
                    console.log(data.status);
                });

            setTimeout(() => {
                btn.disabled = false;
                icon.className = 'fas fa-bolt';
                if (btnText) { btnText.textContent = 'Test All Cores (5s)'; }
            }, 5000);
        });

        // --- (!!! جديد: كود أنيميشن الحوت ASCII) ---
        function animateAsciiWhale() {
            isAsciiAnimating = true;
            const whaleEl = document.getElementById('ascii-whale');
            const fullText = whaleAsciiLines.join('\\n');
            let charIndex = 0;
            whaleEl.innerText = ''; // ابدأ فارغاً

            function typeChar() {
                if (charIndex < fullText.length) {
                    whaleEl.innerText = fullText.substring(0, charIndex + 1);
                    charIndex++;
                    setTimeout(typeChar, 10); // سرعة 10ms
                }
            }
            typeChar(); // ابدأ الأنيميشن
        }

        // --- (!!! تعديل: كود عجلة الطرد مع صوت spinning.mp3) ---
        const canvas = document.getElementById('wheelCanvas');
        const ctx = canvas.getContext('2d');
        const nameInput = document.getElementById('nameInput');
        const spinButton = document.getElementById('spinButton');
        const modalOverlay = document.getElementById('modalOverlay');
        const modalMessage = document.getElementById('modalMessage');
        const closeModalBtn = document.getElementById('closeModalBtn');

        const colors = ["#DC3545", "#FFC107", "#28A745", "#007BFF", "#6F42C1", "#FD7E14", "#17A2B8", "#E83E8C"];
        let names = [];
        let currentRotation = 0;
        let isSpinning = false;

        function getNames() {
            return nameInput.value.split('\\n').filter(name => name.trim() !== '');
        }

        function drawWheel() {
            names = getNames();
            if (names.length === 0) {
                 // ارسم عجلة افتراضية إذا كانت فارغة
                names = ['أدخل', 'أسماء', 'هنا'];
            }

            const numSegments = names.length;
            const arcSize = (2 * Math.PI) / numSegments;
            const radius = canvas.width / 2;

            ctx.clearRect(0, 0, canvas.width, canvas.height);

            for (let i = 0; i < numSegments; i++) {
                const angle = i * arcSize;

                // رسم الشريحة
                ctx.beginPath();
                ctx.fillStyle = colors[i % colors.length];
                ctx.moveTo(radius, radius);
                ctx.arc(radius, radius, radius - 10, angle, angle + arcSize);
                ctx.lineTo(radius, radius);
                ctx.fill();

                // (!!! تعديل: رسم النص أفقياً)
                ctx.save();
                ctx.fillStyle = "white";
                ctx.font = "bold 16px Cairo";
                ctx.textAlign = "center";
                ctx.textBaseline = "middle";

                // حساب زاوية منتصف الشريحة
                const textAngle = angle + arcSize / 2;

                // حساب موقع (X, Y) للنص
                const textX = radius + Math.cos(textAngle) * (radius * 0.6);
                const textY = radius + Math.sin(textAngle) * (radius * 0.6);

                // تحديد أقصى عرض للنص (حتى لا يتداخل)
                const maxTextWidth = radius * 0.5;

                // ارسم النص أفقياً
                ctx.fillText(names[i], textX, textY, maxTextWidth);

                ctx.restore();
            }
        }

        function showModal(message) {
            modalMessage.textContent = message;
            modalOverlay.classList.add('visible');
        }

        function closeModal() {
            modalOverlay.classList.remove('visible');
        }

        function startSpin() {
            if (isSpinning) return;

            names = getNames();
            if (names.length === 0) {
                showModal("الرجاء إدخال أسماء الموظفين أولاً!");
                return;
            }

            isSpinning = true;
            spinButton.disabled = true;
            spinButton.innerHTML = '<i class="fas fa-cog fa-spin"></i> ...جاري الدوران';

            // (!!! تعديل: تشغيل صوت الدوران)
            spinSound.currentTime = 0;
            spinSound.play();

            const spinDuration = 5000; // 5 ثواني
            const randomSpins = Math.floor(Math.random() * 5) + 8; // 8-12 دورة كاملة
            const randomTarget = Math.random() * (2 * Math.PI); // زاوية التوقف العشوائية
            const targetRotation = (randomSpins * 2 * Math.PI) + randomTarget;

            canvas.style.transition = 'transform 5s cubic-bezier(0.25, 0.1, 0.25, 1)';
            currentRotation += targetRotation;
            canvas.style.transform = `rotate(${currentRotation}rad)`;

            setTimeout(() => {
                // (!!! تعديل: إيقاف صوت الدوران)
                spinSound.pause();
                spinSound.currentTime = 0;

                isSpinning = false;
                spinButton.disabled = false;
                spinButton.innerHTML = '<i class="fas fa-play"></i> ابدأ الدوران!';

                // حساب الفائز
                const numSegments = names.length;
                const arcSize = (2 * Math.PI) / numSegments;
                const finalAngle = currentRotation % (2 * Math.PI);
                const pointerAngle = 1.5 * Math.PI;
                const normalizedAngle = (2 * Math.PI - finalAngle + pointerAngle) % (2 * Math.PI);
                const winnerIndex = Math.floor(normalizedAngle / arcSize);
                const unluckyWinner = names[winnerIndex];

                // إظهار نافذة الطرد
                showModal(`تم طردك من الشركة يا ${unluckyWinner}  يا كسول يا فاشل  `);

            }, spinDuration);
        }

        nameInput.addEventListener('input', drawWheel);
        spinButton.addEventListener('click', startSpin);
        closeModalBtn.addEventListener('click', closeModal);
        drawWheel(); // ارسم العجلة عند التحميل

        // --- كود الحوت المتكلم (كما هو) ---
        const whaleTextEl = document.getElementById('whale-text');
        const whaleMessages = [
            "انتم تم غزوكم من طرف الحوت!",
            "اشتركو و الا اكلتكم يالذيذين هههه",
            "أنا أراقبك من داخل حاوية!",
            "أنا أكبر من شاشتك، اشترك الآن!",
            "إذا لم تشترك، سأرسل لك أمواجاً من الكود!",
            "الحوت غاضب! أين زر الاشتراك؟",
            "اضغط على الجرس (التنبيهات).. وإلا سأجعلك جزءاً من طعامي!",
            "هل أنت متأكد من أنك لا تريد اللايك؟ فكر في محيطك!",
            "اشترك سريعاً قبل أن يصيبك تقلب الأمزجة الحوتية!",
            "مهمة اليوم: اشترك وادعم Vandire. لا مجال للفشل.",
            "أنا هنا فقط للتأكد من أنك اشتركت. تفضل، لا تخف!",
            "إذا رأيتني، فعليك بالاشتراك. إنها قاعدة المحيط.",
            "لا تدعني أبدأ في نفث الماء على لوحة المفاتيح الخاصة بك. اشترك!",

            "Vandire"

        ];
        let msgIndex = 0;
        let charIndex = 0;
        let isErasing = false;
        const typingSpeed = 100; // سرعة الكتابة
        const erasingSpeed = 50; // سرعة المسح
        const delayBetweenMessages = 2000; // الانتظار قبل المسح

        function typeWhaleMessage() {
            const currentMessage = whaleMessages[msgIndex];

            if (isErasing) {
                // --- وضع المسح ---
                if (charIndex > 0) {
                    whaleTextEl.textContent = currentMessage.substring(0, charIndex - 1);
                    charIndex--;
                    setTimeout(typeWhaleMessage, erasingSpeed);
                } else {
                    isErasing = false;
                    msgIndex = (msgIndex + 1) % whaleMessages.length; // انتقل للرسالة التالية
                    setTimeout(typeWhaleMessage, typingSpeed);
                }
            } else {
                // --- وضع الكتابة ---
                if (charIndex < currentMessage.length) {
                    whaleTextEl.textContent = currentMessage.substring(0, charIndex + 1);
                    charIndex++;
                    setTimeout(typeWhaleMessage, typingSpeed);
                } else {
                    isErasing = true;
                    setTimeout(typeWhaleMessage, delayBetweenMessages); // انتظر قبل المسح
                }
            }
        }

        // ابدأ تشغيل الآلة الكاتبة عند تحميل الصفحة
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(typeWhaleMessage, 1500); // ابدأ بعد 1.5 ثانية
        });

    </script>
</body>
</html>
"""

# --- 8. نقطة نهاية التطبيق (APP ENDPOINT) ---
@app.route('/')
def index():
    # --- هذه هي الطريقة الصحيحة لتمرير المتغيرات إلى القالب ---
    return render_template_string(
        HTML_CONTENT,
        WHALE_ART_LINES=WHALE_ART_LINES, # (!!! تعديل: إرسال القائمة)
        YOUTUBE_CHANNEL_URL=YOUTUBE_CHANNEL_URL,
        YOUTUBE_SUBSCRIBE_URL=YOUTUBE_SUBSCRIBE_URL,
        YOUTUBE_SHARE_URL=YOUTUBE_SHARE_URL
    )

# --- 9. تشغيل التطبيق ---
if __name__ == "__main__":
    print("Starting Flask-SocketIO server on http://0.0.0.0:5577")
    socketio.run(app, host='0.0.0.0', port=5577)
