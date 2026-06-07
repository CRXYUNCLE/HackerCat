import sys
import os
import json
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import Qt, pyqtSlot, QObject, QTimer
from PyQt6.QtGui import QColor

class RageOverlay(QMainWindow):
    """Full-screen transparent overlay for chaos effects"""
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        self.setFixedSize(screen.width(), screen.height())
        
        self.view = QWebEngineView(self)
        self.view.setGeometry(0, 0, screen.width(), screen.height())
        self.view.page().setBackgroundColor(QColor(0, 0, 0, 0))
        self.view.setHtml(self.get_chaos_html())
    
    def get_chaos_html(self):
        return """
        <!DOCTYPE html>
        <html>
        <head>
        <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body {
            width: 100vw;
            height: 100vh;
            background: transparent;
            overflow: hidden;
            font-family: 'Courier New', monospace;
            position: relative;
        }
        @keyframes matrixRainFall {
            0% { transform: translateY(-100%); }
            100% { transform: translateY(100vh); }
        }
        @keyframes wordFall {
            0% { transform: translateY(-10vh) rotate(0deg); opacity: 1; }
            100% { transform: translateY(110vh) rotate(360deg); opacity: 0; }
        }
        .chaos-terminal, .chaos-popup {
            position: fixed;
            z-index: 100000;
        }
        .word-rain-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 50000;
            overflow: hidden;
        }
        .falling-word {
            position: absolute;
            white-space: nowrap;
            font-weight: bold;
            font-family: 'Courier New', monospace;
            text-shadow: 0 0 5px currentColor;
            animation: wordFall linear forwards;
        }
        #spawn-counter {
            position: fixed;
            bottom: 20px;
            right: 20px;
            color: #ff3366;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            font-weight: bold;
            background: rgba(0,0,0,0.7);
            padding: 5px 10px;
            border-radius: 5px;
            z-index: 200000;
            pointer-events: none;
            border: 1px solid #ff3366;
        }
        </style>
        </head>
        <body>
        <div class="word-rain-container" id="wordRainContainer"></div>
        <div id="spawn-counter">🔥 CHAOS INTENSIFIES: 0 spawned</div>
        <script>
            // ========== WORD RAIN BACKGROUND ==========
            const words = [
                "MEOW", "HACK", "ERROR", "FIREWALL", "KERNEL", "PANIC", "BREACH", 
                "EXPLOIT", "PAYLOAD", "ROOT", "ACCESS", "DENIED", "GRANTED", 
                "VIRUS", "MALWARE", "ENCRYPT", "DECRYPT", "INJECT", "BYPASS", 
                "CRASH", "OVERFLOW", "SIGSEGV", "SEGFAULT", "WARNING", "ALERT"
            ];
            
            function startWordRain() {
                const container = document.getElementById('wordRainContainer');
                if (!container) return;
                // More words for heavier flooding
                const wordCount = 150 + Math.floor(Math.random() * 100);
                for (let i = 0; i < wordCount; i++) {
                    const word = words[Math.floor(Math.random() * words.length)];
                    const span = document.createElement('div');
                    span.className = 'falling-word';
                    span.textContent = word;
                    const left = Math.random() * 100;
                    const fontSize = 14 + Math.random() * 38;
                    const duration = 3 + Math.random() * 7;  // faster fall
                    const delay = Math.random() * 5;
                    const colors = ['#00ff41', '#33ff88', '#00ccff', '#ff3366'];
                    const color = colors[Math.floor(Math.random() * colors.length)];
                    span.style.left = left + '%';
                    span.style.fontSize = fontSize + 'px';
                    span.style.color = color;
                    span.style.animationDuration = duration + 's';
                    span.style.animationDelay = delay + 's';
                    span.style.opacity = 0.5 + Math.random() * 0.5;
                    container.appendChild(span);
                }
            }
            
            function startMatrixRain() {
                const chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+";
                // More columns for denser rain
                const columns = Math.floor(window.innerWidth / 15);
                for (let i = 0; i < columns; i++) {
                    const col = document.createElement('div');
                    col.style.position = 'fixed';
                    col.style.left = (i * 15) + 'px';
                    col.style.top = '-100%';
                    col.style.color = '#00ff41';
                    col.style.fontSize = '14px';
                    col.style.fontWeight = 'bold';
                    col.style.whiteSpace = 'nowrap';
                    col.style.zIndex = '40000';
                    let text = '';
                    const len = Math.floor(Math.random() * 25) + 15;
                    for (let j = 0; j < len; j++) text += chars[Math.floor(Math.random() * chars.length)];
                    col.textContent = text;
                    document.body.appendChild(col);
                    const duration = Math.random() * 2 + 1.5;  // faster fall
                    col.style.animation = `matrixRainFall ${duration}s linear infinite`;
                    col.style.animationDelay = `${Math.random() * 3}s`;
                    setInterval(() => {
                        if (col.parentElement) {
                            let newText = '';
                            for (let j = 0; j < len; j++) newText += chars[Math.floor(Math.random() * chars.length)];
                            col.textContent = newText;
                        }
                    }, 150);
                }
            }
            
            // ========== TERMINALS AND POPUPS with accelerating spawn ==========
            let totalSpawned = 0;
            let spawnTimeout = null;
            
            function createFloatingPrompt(x, y) {
                const prompt = document.createElement('div');
                prompt.className = 'chaos-terminal';
                prompt.style.left = x + 'px';
                prompt.style.top = y + 'px';
                prompt.style.width = '450px';
                prompt.style.background = '#0a0a0a';
                prompt.style.border = '2px solid #00ff41';
                prompt.style.borderRadius = '5px';
                prompt.style.color = '#00ff41';
                prompt.style.boxShadow = '0 0 20px rgba(0,255,65,0.5)';
                prompt.innerHTML = `
                    <div style="background:#1a1a1a; padding:6px 10px; border-bottom:1px solid #00ff41; display:flex; justify-content:space-between; cursor:move;">
                        <span>⚠️ HACKER CAT TERMINAL ⚠️</span>
                        <span style="cursor:pointer;" onclick="this.closest('.chaos-terminal').remove()">✖</span>
                    </div>
                    <div style="padding:10px; font-size:11px;">
                        <div>[${Math.floor(Math.random()*9999)}] SYSTEM ALERT: Unauthorized cat detected!</div>
                        <div>[${Math.floor(Math.random()*9999)}] Bypassing firewall... 100%</div>
                        <div>[${Math.floor(Math.random()*9999)}] Injecting MEOWWARE...</div>
                        <div>>_ HACKER CAT SAYS: MEOW! 🐱</div>
                    </div>
                `;
                document.body.appendChild(prompt);
                setTimeout(() => prompt.remove(), 8000);
            }
            
            function createErrorPopup(x, y) {
                const errors = [
                    '🚨 CRITICAL ERROR: Kernel Panic!',
                    '⚠️ System Overload: Too many meows!',
                    '💀 cat.exe stopped working',
                    '🔥 CPU Temperature: 9000°C',
                    '📀 DISK ERROR: /dev/null is full',
                    '💣 RANSOMWARE: Pay 1000 treats!',
                    '🔒 SYSTEM LOCKED by Hacker Cat',
                    '⚡ VOLTAGE SURGE: Cat zap!',
                    '🌀 INFINITE LOOP DETECTED'
                ];
                const popup = document.createElement('div');
                popup.className = 'chaos-popup';
                popup.style.left = x + 'px';
                popup.style.top = y + 'px';
                popup.style.minWidth = '300px';
                popup.style.background = '#c0c0c0';
                popup.style.border = '3px solid #ffffff';
                popup.style.borderRadius = '8px';
                popup.innerHTML = `
                    <div style="background:#000080; color:white; padding:5px 8px; font-weight:bold;">⚠️ SYSTEM ALERT ⚠️</div>
                    <div style="background:#ffffff; padding:15px; color:#000000; text-align:center;">
                        <div style="margin-bottom:10px;">${errors[Math.floor(Math.random()*errors.length)]}</div>
                        <button onclick="this.closest('.chaos-popup').remove()">OK</button>
                    </div>
                `;
                document.body.appendChild(popup);
                setTimeout(() => popup.remove(), 7000);
            }
            
            function screenFlash() {
                const flash = document.createElement('div');
                flash.style.position = 'fixed';
                flash.style.top = 0; flash.style.left = 0;
                flash.style.width = '100%'; flash.style.height = '100%';
                flash.style.backgroundColor = '#00ff66';
                flash.style.opacity = '0.5';
                flash.style.zIndex = '99999';
                flash.style.pointerEvents = 'none';
                document.body.appendChild(flash);
                setTimeout(() => flash.remove(), 100);
            }
            
            function spawnRandomItem() {
                const w = window.innerWidth, h = window.innerHeight;
                const isTerminal = Math.random() < 0.6;
                const x = Math.random() * (w - (isTerminal ? 450 : 300));
                const y = Math.random() * (h - (isTerminal ? 280 : 150));
                if (isTerminal) {
                    createFloatingPrompt(x, y);
                } else {
                    createErrorPopup(x, y);
                }
                totalSpawned++;
                const counter = document.getElementById('spawn-counter');
                if (counter) counter.innerHTML = `🔥 CHAOS INTENSIFIES: ${totalSpawned} spawned`;
                if (totalSpawned % 3 === 0) screenFlash();  // more frequent flashes
            }
            
            // Accelerating spawn: starts at 230ms, decreases by 3ms each spawn (down to 30ms)
            let currentDelay = 230;   // 0.23 seconds
            const minDelay = 30;
            const decreaseStep = 3;
            
            function scheduleNext() {
                spawnRandomItem();
                if (currentDelay > minDelay) {
                    currentDelay = Math.max(minDelay, currentDelay - decreaseStep);
                }
                spawnTimeout = setTimeout(scheduleNext, currentDelay);
            }
            
            // Initial burst - even heavier (60 items instantly)
            function initialBurst() {
                for (let i = 0; i < 60; i++) {
                    setTimeout(() => spawnRandomItem(), i * 25);
                }
            }
            
            // Start everything
            startWordRain();
            startMatrixRain();
            initialBurst();
            scheduleNext();
            
            // Extra screen flashes every second for more chaos
            setInterval(() => {
                screenFlash();
            }, 1000);
            
            // Clean up after 15 seconds (rage overlay will be closed by Python)
            setTimeout(() => {
                if (spawnTimeout) clearTimeout(spawnTimeout);
            }, 15000);
        </script>
        </body>
        </html>
        """
    
    def closeEvent(self, event):
        self.view.setHtml("")
        event.accept()

class Bridge(QObject):
    @pyqtSlot()
    def startFullscreenRage(self):
        print("Starting full-screen rage overlay")
        self.overlay = RageOverlay()
        self.overlay.show()
        QTimer.singleShot(15000, self.stopFullscreenRage)  # 15 seconds
    
    @pyqtSlot()
    def stopFullscreenRage(self):
        if hasattr(self, 'overlay') and self.overlay:
            self.overlay.close()
            self.overlay = None

class ScreenMate(QMainWindow):
    def __init__(self, config_path=None):
        super().__init__()
        self.config = self.load_config(config_path)
        
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(280, 360)
        
        self.view = QWebEngineView(self)
        self.view.setFixedSize(280, 360)
        self.view.page().setBackgroundColor(QColor(0, 0, 0, 0))
        self.setCentralWidget(self.view)
        
        # Set up bridge
        self.channel = QWebChannel()
        self.bridge = Bridge()
        self.channel.registerObject("pybridge", self.bridge)
        self.view.page().setWebChannel(self.channel)
        
        # Load HTML
        script_dir = os.path.dirname(os.path.abspath(__file__))
        html_path = os.path.join(script_dir, "screenmate.html")
        
        if os.path.exists(html_path):
            with open(html_path, 'r', encoding='utf-8') as f:
                html = f.read()
                self.view.setHtml(html)
        else:
            self.view.setHtml("<h1>Error: screenmate.html not found</h1>")
        
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.width() - 300, screen.height() - 380)
        
        self.drag_position = None
        self.view.mousePressEvent = self.mouse_press
        self.view.mouseMoveEvent = self.mouse_move
        self.view.mouseReleaseEvent = self.mouse_release
        
    def mouse_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    def mouse_move(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position is not None:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    def mouse_release(self, event):
        self.drag_position = None
        event.accept()
        
    def load_config(self, config_path):
        default = {"mouse_follow": True, "rage_enabled": True, "follow_speed": 5}
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    saved = json.load(f)
                    default.update(saved)
            except Exception as e:
                print(f"Config error: {e}")
        return default

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    config_path = sys.argv[1] if len(sys.argv) > 1 else None
    mate = ScreenMate(config_path)
    mate.show()
    sys.exit(app.exec())
