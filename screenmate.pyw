import sys
import os
import json
from PyQt6.QtWidgets import QApplication, QMainWindow, QMenu
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, QUrl, QEvent, QTimer, QPoint
from PyQt6.QtGui import QAction, QColor
import math

class ScreenMate(QMainWindow):
    def __init__(self, config_path=None):
        super().__init__()
        
        # Load config
        self.config = self.load_config(config_path)
        
        # Mouse following variables
        self.target_pos = None
        self.follow_timer = None
        self.cat_speed = self.config.get("follow_speed", 5) / 5.0
        
        # Window setup
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(280, 360)
        
        # Start at bottom-right
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.width() - 300, screen.height() - 380)
        
        # Web view
        self.view = QWebEngineView(self)
        self.view.setFixedSize(280, 360)
        self.view.page().setBackgroundColor(QColor(0, 0, 0, 0))
        self.setCentralWidget(self.view)
        
        # Load HTML - try multiple locations
        html_content = self.load_html_content()
        
        if html_content:
            # Load HTML directly as string to avoid file path issues
            self.view.setHtml(html_content)
        else:
            # Fallback error message
            error_html = """
            <html>
            <body style="background:black; color:#00ff88; font-family:monospace; padding:20px;">
                <h1>🐱 Hacker Cat Error</h1>
                <p>Could not load screenmate.html</p>
                <p>Please ensure the HTML file exists in the same directory.</p>
            </body>
            </html>
            """
            self.view.setHtml(error_html)
            print("Error: Could not load screenmate.html")
        
        # Drag state
        self._drag_pos = None
        self.view.installEventFilter(self)
        
        # Wait for page to load then apply config
        self.view.loadFinished.connect(self.apply_config_to_page)
        
        # Start mouse following if enabled
        if self.config.get("mouse_follow", True):
            self.start_mouse_following()
    
    def load_html_content(self):
        """Load HTML content from various possible locations"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Try different possible locations
        possible_paths = [
            os.path.join(script_dir, "screenmate.html"),
            os.path.join(os.getcwd(), "screenmate.html"),
            os.path.join(os.path.dirname(sys.executable), "screenmate.html"),
            "screenmate.html"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        return f.read()
                except Exception as e:
                    print(f"Error reading {path}: {e}")
        
        return None
        
    def load_config(self, config_path):
        """Load settings from file"""
        default = {
            "mouse_follow": True,
            "rage_enabled": True,
            "follow_speed": 5
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    saved = json.load(f)
                    default.update(saved)
            except Exception as e:
                print(f"Error loading config: {e}")
        return default
        
    def apply_config_to_page(self):
        """Send config settings to HTML page"""
        js = f"""
        (function() {{
            if(typeof window !== 'undefined') {{
                window.mouseFollowEnabled = {str(self.config.get('mouse_follow', True)).lower()};
                window.rageEnabled = {str(self.config.get('rage_enabled', True)).lower()};
                window.followSpeed = {self.config.get('follow_speed', 5)};
                
                if(typeof window.applySettings === 'function') {{
                    window.applySettings();
                }}
                
                console.log('Settings applied to cat!');
            }}
        }})();
        """
        self.view.page().runJavaScript(js)
        
    def start_mouse_following(self):
        """Start timer to make cat follow mouse"""
        self.follow_timer = QTimer()
        self.follow_timer.timeout.connect(self.follow_mouse)
        self.follow_timer.start(16)  # ~60 FPS
        
    def follow_mouse(self):
        """Move cat toward cursor position"""
        if not self.config.get("mouse_follow", True):
            return
            
        # Don't follow if being dragged
        if self._drag_pos is not None:
            return
            
        cat_pos = self.pos()
        cat_center = QPoint(cat_pos.x() + self.width() // 2, cat_pos.y() + self.height() // 2)
        cursor_global = QApplication.primaryScreen().cursor().pos()
        
        # Calculate distance
        dx = cursor_global.x() - cat_center.x()
        dy = cursor_global.y() - cat_center.y()
        distance = math.hypot(dx, dy)
        
        # Only move if cursor is within 400px and not too close
        if distance < 400 and distance > 15:
            # Move toward cursor with speed based on distance and config
            speed = min(12, max(2, distance / 30)) * self.cat_speed
            move_x = dx / distance * min(speed, abs(dx))
            move_y = dy / distance * min(speed, abs(dy))
            
            new_x = cat_pos.x() + move_x
            new_y = cat_pos.y() + move_y
            
            # Keep on screen
            screen = QApplication.primaryScreen().availableGeometry()
            new_x = max(0, min(screen.width() - self.width(), new_x))
            new_y = max(0, min(screen.height() - self.height(), new_y))
            
            self.move(int(new_x), int(new_y))
            
            # Send mouse position to HTML for eyes
            rel_x = cursor_global.x() - self.x()
            rel_y = cursor_global.y() - self.y()
            eye_js = f"""
            if(typeof window.updatePupils === 'function') {{
                window.mouseX = {rel_x};
                window.mouseY = {rel_y};
                window.updatePupils();
            }}
            """
            self.view.page().runJavaScript(eye_js)
            
    def eventFilter(self, obj, event):
        if obj is self.view:
            t = event.type()
            
            if t == QEvent.Type.MouseButtonPress:
                btn = event.button()
                if btn == Qt.MouseButton.LeftButton:
                    # Temporarily disable following while dragging
                    self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                    if self.follow_timer:
                        self.follow_timer.stop()
                    return True
                elif btn == Qt.MouseButton.RightButton:
                    self._show_menu(event.globalPosition().toPoint())
                    return True
                    
            elif t == QEvent.Type.MouseMove:
                if self._drag_pos and (event.buttons() & Qt.MouseButton.LeftButton):
                    self.move(event.globalPosition().toPoint() - self._drag_pos)
                return True
                
            elif t == QEvent.Type.MouseButtonRelease:
                self._drag_pos = None
                if self.follow_timer and self.config.get("mouse_follow", True):
                    self.follow_timer.start(16)
                return True
                
        return super().eventFilter(obj, event)
        
    def _show_menu(self, global_pos):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background : #0a0f0a;
                color       : #00ff88;
                border      : 1px solid #00ff88;
                font-family : 'Courier New', monospace;
                font-size   : 11px;
                padding     : 5px 0;
            }
            QMenu::item          { padding: 8px 25px; }
            QMenu::item:selected { background: #00ff88; color: #000; }
        """)
        
        # Show current settings status
        follow_status = "✓" if self.config.get("mouse_follow", True) else "✗"
        rage_status = "✓" if self.config.get("rage_enabled", True) else "✗"
        
        menu.addAction(f"🐭 Mouse Follow: {follow_status}").setEnabled(False)
        menu.addAction(f"😾 Rage System: {rage_status}").setEnabled(False)
        menu.addSeparator()
        
        act_settings = QAction("⚙️ Open Settings", self)
        act_settings.triggered.connect(self.open_settings)
        menu.addAction(act_settings)
        
        menu.addSeparator()
        
        act_quit = QAction("❌ Quit", self)
        act_quit.triggered.connect(QApplication.instance().quit)
        menu.addAction(act_quit)
        
        menu.exec(global_pos)
        
    def open_settings(self):
        """Reopen settings window"""
        import subprocess
        launcher = None
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        for name in ["launcher.pyw", "launcher.py"]:
            test_path = os.path.join(script_dir, name)
            if os.path.exists(test_path):
                launcher = test_path
                break
        
        if launcher and os.path.exists(launcher):
            subprocess.Popen([sys.executable, launcher])
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    
    # Get config path from command line
    config_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    mate = ScreenMate(config_path)
    mate.show()
    
    sys.exit(app.exec())
