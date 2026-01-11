import sys
import os
import subprocess
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit,
    QPushButton, QLabel, QFileDialog, QMessageBox, QCheckBox
)
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt

# Set your DeepSeek API key
DEEPSEEK_API_KEY = "sk-0460ed1311d34433b8949b1c6e877391"  # Replace with your DeepSeek API key

# Change this to the path to your Blender executable
BLENDER_PATH = r"C:\Program Files\Blender Foundation\Blender 4.4\blender-launcher.exe"


class BlenderAIApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧠 Blender AI Animator")
        self.setGeometry(100, 100, 650, 600)
        self.set_dark_theme()

        layout = QVBoxLayout()

        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Describe the Blender animation you want...")
        layout.addWidget(QLabel("📝 Prompt:"))
        layout.addWidget(self.prompt_input)

        self.generate_button = QPushButton("⚙️ Generate & Run in Blender")
        self.generate_button.clicked.connect(self.run_pipeline)
        layout.addWidget(self.generate_button)

        self.render_checkbox = QCheckBox("🎬 Also render to .mpeg video")
        layout.addWidget(self.render_checkbox)

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

    def run_pipeline(self):
        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "Missing Prompt", "Please describe what animation you want.")
            return

        self.output_area.setPlainText("Generating Blender script...")

        try:
            # Step 1: Send prompt to DeepSeek API
            headers = {
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
            }
            data = {
                "model": "deepseek-coder",  # Assuming 'deepseek-coder' is the model for Blender scripting
                "messages": [
                    {"role": "system", "content": "You are a Blender bpy scripting expert. Output Blender animation code only."},
                    {"role": "user", "content": f"Create a Blender animation: {prompt}"}
                ],
                "temperature": 0.5,
                "max_tokens": 600
            }
            response = requests.post("https://api.deepseek.ai/chat/completion", json=data, headers=headers)

            # Step 2: Handle response
            if response.status_code == 200:
                script = response.json()["choices"][0]["message"]["content"]
                self.output_area.setPlainText(script)

                # Step 3: Save the script
                with open("generated_script.py", "w", encoding="utf-8") as f:
                    f.write(script)

                # Step 4: Ask for save location
                save_path, _ = QFileDialog.getSaveFileName(self, "Save .blend file", "", "Blender Files (*.blend)")
                if not save_path:
                    return

                # Step 5: Write the runner script
                runner_code = f"""
import bpy
exec(compile(open("generated_script.py").read(), "generated_script.py", 'exec'))
bpy.ops.wm.save_as_mainfile(filepath=r"{save_path}")
{"bpy.context.scene.render.filepath = r'" + save_path.replace(".blend", ".mpeg") + "'\\n"
 "bpy.context.scene.render.image_settings.file_format = 'FFMPEG'\\n"
 "bpy.context.scene.render.ffmpeg.format = 'MPEG4'\\n"
 "bpy.ops.render.render(animation=True)" if self.render_checkbox.isChecked() else ""}
"""
                with open("blender_runner.py", "w", encoding="utf-8") as f:
                    f.write(runner_code)

                # Step 6: Run Blender in background
                subprocess.run([BLENDER_PATH, "--background", "--python", "blender_runner.py"], check=True)

                QMessageBox.information(self, "✅ Done", f"Saved to .blend{(' and .mpeg' if self.render_checkbox.isChecked() else '')}!")
            else:
                raise Exception(f"Error from DeepSeek API: {response.text}")

        except Exception as e:
            self.output_area.setPlainText("")
            QMessageBox.critical(self, "❌ Error", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BlenderAIApp()
    window.show()
    sys.exit(app.exec_())
