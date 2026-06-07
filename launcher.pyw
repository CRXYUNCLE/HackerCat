import sys
import os
import json
import subprocess
import winreg
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QCheckBox, QSlider, QGroupBox,
                             QMessageBox)
from PyQt6.QtCore import Qt, QTimer

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cat_config.json")

class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.load_config()
        self.init_ui()
        
    def load_config(self):
        """Load saved settings or create default"""
        default_config = {
            "auto_startup": False,
            "mouse_follow": True,
            "rage_enabled": True,
            "follow_speed": 5,
            "first_run": True
        }
        
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    saved = json.load(f)
                    default_config.update(saved)
            except:
                pass
        else:
            default_config["first_run"] = True
            
        self.config = default_config
        
    def save_config(self):
        """Save current settings"""
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)
            
    def set_auto_startup(self, enabled):
        """Add or remove from Windows registry for auto-start"""
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            exe_path = sys.argv[0]
            
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                if enabled:
                    winreg.SetValueEx(key, "HackerCat", 0, winreg.REG_SZ, exe_path)
                else:
                    try:
                        winreg.DeleteValue(key, "HackerCat")
                    except:
                        pass
            return True
        except Exception as e:
            print(f"Auto-startup error: {e}")
            return False
            
    def init_ui(self):
        """Create the settings window UI"""
        self.setWindowTitle("🐱 Hacker Cat - Settings")
        self.setFixedSize(500, 550)
        self.setWindowFlags(Qt.WindowType.WindowCloseButtonHint)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #0a0f0a;
                color: #00ff88;
                font-family: 'Courier New', monospace;
            }
            QGroupBox {
                border: 2px solid #00ff88;
                border-radius: 8px;
                margin-top: 12px;
                font-weight: bold;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QCheckBox {
                spacing: 8px;
                font-size: 12px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #00ff88;
                border-radius: 3px;
                background-color: #0a0f0a;
            }
            QCheckBox::indicator:checked {
                background-color: #00ff88;
                border-color: #00ff88;
            }
            QPushButton {
                background-color: #0a0f0a;
                border: 2px solid #00ff88;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #00ff88;
                color: #0a0f0a;
            }
            QSlider::groove:horizontal {
                border: 1px solid #00ff88;
                height: 6px;
                background: #1a2a1a;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #00ff88;
                border: 1px solid #00ff88;
                width: 14px;
                height: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
            QLabel {
                font-size: 11px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Title
        title = QLabel("🐱‍💻 HACKER CAT SETTINGS 🐱‍💻")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # ===== GENERAL SETTINGS =====
        general_group = QGroupBox("⚙️ GENERAL")
        general_layout = QVBoxLayout()
        
        self.auto_startup_check = QCheckBox("✓ Auto-run on Windows startup")
        self.auto_startup_check.setChecked(self.config.get("auto_startup", False))
        self.auto_startup_check.toggled.connect(self.on_auto_startup_toggled)
        general_layout.addWidget(self.auto_startup_check)
        
        general_group.setLayout(general_layout)
        layout.addWidget(general_group)
        
        # ===== MOUSE FOLLOWING =====
        mouse_group = QGroupBox("🐭 MOUSE FOLLOWING")
        mouse_layout = QVBoxLayout()
        
        self.mouse_follow_check = QCheckBox("✓ Cat follows your mouse cursor")
        self.mouse_follow_check.setChecked(self.config.get("mouse_follow", True))
        self.mouse_follow_check.toggled.connect(self.on_mouse_follow_toggled)
        mouse_layout.addWidget(self.mouse_follow_check)
        
        # Speed slider
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Follow Speed:"))
        self.follow_speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.follow_speed_slider.setMinimum(1)
        self.follow_speed_slider.setMaximum(10)
        self.follow_speed_slider.setValue(self.config.get("follow_speed", 5))
        self.follow_speed_slider.setEnabled(self.config.get("mouse_follow", True))
        self.follow_speed_slider.valueChanged.connect(self.on_speed_changed)
        speed_layout.addWidget(self.follow_speed_slider)
        
        self.speed_label = QLabel(f"Speed: {self.config.get('follow_speed', 5)}/10")
        speed_layout.addWidget(self.speed_label)
        mouse_layout.addLayout(speed_layout)
        
        info_label = QLabel("💡 The cat will slowly move toward your cursor like a real pet!")
        info_label.setStyleSheet("color: #88ff88; font-size: 9px;")
        mouse_layout.addWidget(info_label)
        
        mouse_group.setLayout(mouse_layout)
        layout.addWidget(mouse_group)
        
        # ===== RAGE SYSTEM =====
        rage_group = QGroupBox("😾 RAGE SYSTEM")
        rage_layout = QVBoxLayout()
        
        self.rage_enabled_check = QCheckBox("✓ Enable Rage Meter (click for chaos!)")
        self.rage_enabled_check.setChecked(self.config.get("rage_enabled", True))
        rage_layout.addWidget(self.rage_enabled_check)
        
        rage_info = QLabel("💢 Rage builds when you click the cat. At 100% → CHAOS MODE!")
        rage_info.setStyleSheet("color: #ff6688; font-size: 9px;")
        rage_layout.addWidget(rage_info)
        
        rage_group.setLayout(rage_layout)
        layout.addWidget(rage_group)
        
        # ===== BUTTONS =====
        button_layout = QHBoxLayout()
        
        self.launch_btn = QPushButton("🚀 LAUNCH CAT")
        self.launch_btn.setStyleSheet("background: #00ff88; color: #0a0f0a; font-size: 14px; padding: 10px;")
        self.launch_btn.clicked.connect(self.launch_cat)
        
        button_layout.addWidget(self.launch_btn)
        layout.addLayout(button_layout)
        
        # Show welcome message on first run
        if self.config.get("first_run", False):
            self.show_welcome()
            self.config["first_run"] = False
            self.save_config()
        
        self.setLayout(layout)
        
    def on_mouse_follow_toggled(self, checked):
        self.follow_speed_slider.setEnabled(checked)
        
    def on_auto_startup_toggled(self, checked):
        self.config["auto_startup"] = checked
        self.set_auto_startup(checked)
            
    def on_speed_changed(self, value):
        self.speed_label.setText(f"Speed: {value}/10")
        self.config["follow_speed"] = value
        
    def show_welcome(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("🐱 Welcome to Hacker Cat!")
        msg.setText("🐱‍💻 MEOW! Welcome to Hacker Cat!\n\n"
                   "This chaotic cat will live on your desktop!\n\n"
                   "Click LAUNCH CAT to start!")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()
        
    def save_current_config(self):
        """Save all current settings"""
        self.config["mouse_follow"] = self.mouse_follow_check.isChecked()
        self.config["rage_enabled"] = self.rage_enabled_check.isChecked()
        self.config["follow_speed"] = self.follow_speed_slider.value()
        self.save_config()
        
    def launch_cat(self):
        """Launch the main cat window with current settings"""
        self.save_current_config()
        
        # Get the directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Find screenmate.pyw or screenmate.py
        cat_script = None
        for name in ["screenmate.pyw", "screenmate.py"]:
            test_path = os.path.join(script_dir, name)
            if os.path.exists(test_path):
                cat_script = test_path
                break
        
        if not cat_script:
            error_msg = QMessageBox(self)
            error_msg.setWindowTitle("Error")
            error_msg.setText(f"❌ Could not find screenmate!\n\nLooking in:\n{script_dir}")
            error_msg.exec()
            return
        
        # Launch with console to see errors
        try:
            python_exe = sys.executable
            
            # IMPORTANT: REMOVE CREATE_NO_WINDOW to see errors!
            subprocess.Popen([python_exe, cat_script, CONFIG_FILE])
            
            self.close()
        except Exception as e:
            error_msg = QMessageBox(self)
            error_msg.setWindowTitle("Error")
            error_msg.setText(f"❌ Failed to launch cat:\n{str(e)}")
            error_msg.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SettingsWindow()
    window.show()
    sys.exit(app.exec())
