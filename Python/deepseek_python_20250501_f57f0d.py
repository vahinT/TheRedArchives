import sys
import os
import subprocess
import requests
import platform
import tempfile
import shutil
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit,
    QPushButton, QLabel, QFileDialog, QMessageBox, 
    QCheckBox, QHBoxLayout, QProgressBar
)
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# Configuration - Use environment variables for sensitive data
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEFAULT_BLENDER_PATHS = {
    'Windows': [
        r"C:\Program Files\Blender Foundation\Blender\blender.exe",
        r"C:\Program Files (x86)\Blender Foundation\Blender\blender.exe"
    ],
    'Darwin': [
        "/Applications/Blender.app/Contents/MacOS/Blender",
        "/Applications/Blender/blender.app/Contents/MacOS/Blender"
    ],
    'Linux': [
        "/usr/bin/blender",
        "/usr/local/bin/blender",
        os.path.expanduser("~/.local/bin/blender")
    ]
}

class BlenderFinder:
    @staticmethod
    def find_blender():
        system = platform.system()
        possible_paths = DEFAULT_BLENDER_PATHS.get(system, [])
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
                
        # Try which/where command as fallback
        try:
            cmd = "where" if system == "Windows" else "which"
            path = subprocess.check_output([cmd, "blender"]).decode().strip()
            if path and os.path.exists(path):
                return path
        except:
            pass
            
        return None

class WorkerThread(QThread):
    finished = pyqtSignal(str, bool)
    progress = pyqtSignal(str)
    
    def __init__(self, prompt, render_video, blender_path, api_key):
        super().__init__()
        self.prompt = prompt
        self.render_video = render_video
        self.blender_path = blender_path
        self.api_key = api_key
        self.temp_dir = None
        self.should_cancel = False
        
    def run(self):
        try:
            self.progress.emit("Creating temporary workspace...")
            self.temp_dir = tempfile.mkdtemp(prefix="blender_ai_")
            
            # Step 1: Generate script via API
            self.progress.emit("Generating Blender script via API...")
            script = self.generate_blender_script()
            if self.should_cancel:
                self.finished.emit("Operation cancelled", False)
                return
                
            # Step 2: Save scripts
            self.progress.emit("Preparing Blender files...")
            script_path = os.path.join(self.temp_dir, "generated_script.py")
            runner_path = os.path.join(self.temp_dir, "blender_runner.py")
            
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script)
                
            # Step 3: Run Blender
            self.progress.emit("Executing in Blender...")
            success = self.execute_blender(script_path, runner_path)
            
            if success:
                self.finished.emit(f"Operation completed successfully!\nFiles saved in: {self.temp_dir}", True)
            else:
                self.finished.emit("Blender execution failed", False)
                
        except Exception as e:
            self.finished.emit(f"Error: {str(e)}", False)
            
    def generate_blender_script(self):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = {
            "model": "deepseek-coder",
            "messages": [
                {"role": "system", "content": "You are a Blender bpy scripting expert. Output complete, valid Blender animation code only."},
                {"role": "user", "content": f"Create a Blender animation: {self.prompt}"}
            ],
            "temperature": 0.5,
            "max_tokens": 1500
        }
        
        try:
            response = requests.post(
                "https://api.deepseek.ai/v1/chat/completions",
                json=data,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
            
    def execute_blender(self, script_path, runner_path):
        # Create runner script
        runner_code = f"""
import bpy
import sys

try:
    with open(r"{script_path}", "r", encoding="utf-8") as f:
        script = f.read()
    exec(script)
    bpy.ops.wm.save_as_mainfile(filepath=r"{os.path.join(self.temp_dir, "output.blend")}")
"""
        if self.render_video:
            runner_code += f"""
    bpy.context.scene.render.filepath = r"{os.path.join(self.temp_dir, "output.mpeg")}"
    bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
    bpy.context.scene.render.ffmpeg.format = 'MPEG4'
    bpy.ops.render.render(animation=True)
"""
        runner_code += "\nexcept Exception as e:\n    print(f\"Error: {str(e)}\", file=sys.stderr)\n"
        
        with open(runner_path, "w", encoding="utf-8") as f:
            f.write(runner_code)
            
        try:
            subprocess.run(
                [self.blender_path, "--background", "--python", runner_path],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=300  # 5 minute timeout
            )
            return True
        except subprocess.SubprocessError as e:
            raise Exception(f"Blender execution failed: {str(e)}")
            
    def cancel(self):
        self.should_cancel = True
        
    def __del__(self):
        # Cleanup temp directory if not needed
        if hasattr(self, 'temp_dir') and self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except:
                pass

class BlenderAIApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧠 Blender AI Animator")
        self.setGeometry(100, 100, 700, 700)
        self.set_dark_theme()
        
        self.worker_thread = None
        self.blender_path = self.detect_blender()
        
        layout = QVBoxLayout()
        
        # Blender Path Selection
        path_layout = QHBoxLayout()
        self.path_label = QLabel(f"Blender Path: {self.blender_path if self.blender_path else 'Not found!'}")
        path_btn = QPushButton("Browse...")
        path_btn.clicked.connect(self.set_blender_path)
        path_layout.addWidget(self.path_label)
        path_layout.addWidget(path_btn)
        layout.addLayout(path_layout)
        
        # API Key
        api_layout = QHBoxLayout()
        api_layout.addWidget(QLabel("DeepSeek API Key:"))
        self.api_key_input = QTextEdit()
        self.api_key_input.setMaximumHeight(30)
        self.api_key_input.setText(DEEPSEEK_API_KEY)
        api_layout.addWidget(self.api_key_input)
        layout.addLayout(api_layout)
        
        # Prompt Input
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Describe the Blender animation you want...")
        layout.addWidget(QLabel("📝 Prompt:"))
        layout.addWidget(self.prompt_input)
        
        # Options
        self.render_checkbox = QCheckBox("🎬 Also render to video")
        layout.addWidget(self.render_checkbox)
        
        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate mode
        self.progress_bar.hide()
        self.status_label = QLabel("Ready")
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.generate_button = QPushButton("⚙️ Generate & Run")
        self.generate_button.clicked.connect(self.run_pipeline)
        self.cancel_button = QPushButton("✖ Cancel")
        self.cancel_button.clicked.connect(self.cancel_operation)
        self.cancel_button.setEnabled(False)
        btn_layout.addWidget(self.generate_button)
        btn_layout.addWidget(self.cancel_button)
        layout.addLayout(btn_layout)
        
        # Output
        layout.addWidget(QLabel("📜 Generated Script:"))
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        layout.addWidget(self.output_area)
        
        self.setLayout(layout)
        
    def set_dark_theme(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(30, 30, 30))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(40, 40, 40))
        dark_palette.setColor(QPalette.AlternateBase, QColor(30, 30, 30))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(45, 45, 45))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        self.setPalette(dark_palette)
        
    def detect_blender(self):
        path = BlenderFinder.find_blender()
        if path:
            return os.path.normpath(path)
        return None
        
    def set_blender_path(self):
        if platform.system() == "Windows":
            filter = "Executable (*.exe)"
        else:
            filter = "Executable (*)"
            
        path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Blender Executable", 
            "", 
            filter
        )
        
        if path and os.path.exists(path):
            self.blender_path = path
            self.path_label.setText(f"Blender Path: {path}")
            
    def run_pipeline(self):
        if not self.blender_path or not os.path.exists(self.blender_path):
            QMessageBox.critical(self, "Error", "Blender executable not found! Please specify the path.")
            return
            
        api_key = self.api_key_input.toPlainText().strip()
        if not api_key:
            QMessageBox.critical(self, "Error", "DeepSeek API key is required!")
            return
            
        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            QMessageBox.critical(self, "Error", "Please describe what animation you want.")
            return
            
        # Disable UI during operation
        self.generate_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.progress_bar.show()
        self.status_label.setText("Starting...")
        
        # Start worker thread
        self.worker_thread = WorkerThread(
            prompt,
            self.render_checkbox.isChecked(),
            self.blender_path,
            api_key
        )
        self.worker_thread.finished.connect(self.on_worker_finished)
        self.worker_thread.progress.connect(self.update_progress)
        self.worker_thread.start()
        
    def cancel_operation(self):
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.cancel()
            self.status_label.setText("Cancelling...")
            self.cancel_button.setEnabled(False)
            
    def update_progress(self, message):
        self.status_label.setText(message)
        
    def on_worker_finished(self, message, success):
        self.progress_bar.hide()
        self.generate_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        
        if success:
            self.output_area.setPlainText(message)
            QMessageBox.information(self, "Success", message)
        else:
            self.status_label.setText("Failed")
            QMessageBox.critical(self, "Error", message)
            
        self.worker_thread = None
        
    def closeEvent(self, event):
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.cancel()
            self.worker_thread.wait(2000)  # Wait up to 2 seconds
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Check dependencies
    try:
        from PyQt5.QtWidgets import QApplication
        import requests
    except ImportError as e:
        QMessageBox.critical(None, "Missing Dependencies", 
            f"Required packages are missing: {str(e)}\n"
            "Please install them with: pip install PyQt5 requests")
        sys.exit(1)
        
    window = BlenderAIApp()
    window.show()
    sys.exit(app.exec_())