#!/usr/bin/env python

# vendor_taichi.py - 3D VFX & Animation Tool using Taichi & PyQt5

# Features:
# - Sphere, liquid particle, cloth physics (gravity, collisions)
# - Blender-style dark UI with dockable panels
# - Outliner, Properties panels, color picker
# - Cloth subdivision
# - Render-to-MP4 with FFmpeg, snapshot & reset

import sys, os, subprocess, importlib, tempfile, shutil
from pathlib import Path

# --- Virtualenv Relaunch ---
VENV_PY = r"C:\Users\vah..."  # Adjust to your taichi-env path
if os.path.normcase(sys.executable) != os.path.normcase(VENV_PY):
    if Path(VENV_PY).exists():
        os.execv(VENV_PY, [VENV_PY] + sys.argv)
    else:
        print(f"Warning: Virtualenv not found at {VENV_PY}")

# --- Auto-install dependencies ---
def ensure_packages():
    pkgs = ['PyQt5', 'PyOpenGL', 'numpy', 'imageio', 'imageio-ffmpeg', 'taichi']
    for pkg in pkgs:
        try:
            importlib.import_module(pkg.replace('-', '_'))
        except ImportError:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg, '--no-cache-dir'])
ensure_packages()

# --- Imports ---
import numpy as np
import taichi as ti
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QDockWidget, QToolBar, QToolButton,
    QListWidget, QVBoxLayout, QWidget, QPushButton, QColorDialog,
    QFileDialog, QStatusBar, QMessageBox, QOpenGLWidget
)
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt, QTimer
from OpenGL.GL import *
from OpenGL.GLU import gluNewQuadric, gluSphere
from imageio import imwrite

# --- Dark Theme ---
def set_dark_theme(app):
    app.setStyle('Fusion')
    pal = QPalette()
    pal.setColor(QPalette.Window, QColor(53, 53, 53)); pal.setColor(QPalette.WindowText, Qt.white)
    pal.setColor(QPalette.Base, QColor(35, 35, 35)); pal.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    pal.setColor(QPalette.ToolTipBase, Qt.white); pal.setColor(QPalette.ToolTipText, Qt.white)
    pal.setColor(QPalette.Text, Qt.white); pal.setColor(QPalette.Button, QColor(53, 53, 53))
    pal.setColor(QPalette.ButtonText, Qt.white); pal.setColor(QPalette.BrightText, Qt.red)
    app.setPalette(pal)

# --- Taichi Physics Setup ---
ti.init(arch=ti.cpu)
dt = 1.0 / 60.0
gravity = ti.Vector([0.0, -9.8, 0.0])

# Simulation constants
nmax_sph = 32
nmax_par = 2048
MAX_CLOTH = 50
cloth_res = ti.field(ti.i32, shape=())

# Fields: spheres
sphere_pos = ti.Vector.field(3, ti.f32, shape=nmax_sph)
sphere_vel = ti.Vector.field(3, ti.f32, shape=nmax_sph)
sphere_rad = ti.field(ti.f32, shape=nmax_sph)
sphere_cnt = ti.field(ti.i32, shape=())

# Fields: particles
part_pos = ti.Vector.field(3, ti.f32, shape=nmax_par)
part_vel = ti.Vector.field(3, ti.f32, shape=nmax_par)
part_cnt = ti.field(ti.i32, shape=())

# Fields: cloth
tcloth = ti.Vector.field(3, ti.f32, shape=(MAX_CLOTH, MAX_CLOTH))
vcloth = ti.Vector.field(3, ti.f32, shape=(MAX_CLOTH, MAX_CLOTH))

@ti.kernel
def init_sim():
    sphere_cnt[None] = 0
    part_cnt[None] = 0
    cloth_res[None] = 10
    for i in range(cloth_res[None]):
        for j in range(cloth_res[None]):
            tcloth[i, j] = ti.Vector([i * 0.5 - (cloth_res[None]-1)*0.25, 5.0, j * 0.5 - (cloth_res[None]-1)*0.25])
            vcloth[i, j] = ti.Vector([0.0, 0.0, 0.0])

@ti.kernel
def step_sim():
    # Sphere physics
    for i in range(sphere_cnt[None]):
        v = sphere_vel[i] + gravity * dt
        p = sphere_pos[i] + v * dt
        if p.y < sphere_rad[i]: p.y = sphere_rad[i]; v.y *= -0.5
        for j in range(i+1, sphere_cnt[None]):
            d = p - sphere_pos[j]; dist = d.norm(); rsum = sphere_rad[i] + sphere_rad[j]
            if 0 < dist < rsum:
                n = d / dist
                vi = sphere_vel[i].dot(n); vj = sphere_vel[j].dot(n)
                sphere_vel[i] += (vj - vi) * n; sphere_vel[j] += (vi - vj) * n
                corr = (rsum - dist) * 0.5; p += n * corr; sphere_pos[j] -= n * corr
        sphere_vel[i] = v; sphere_pos[i] = p
    
    # Particle physics
    for i in range(part_cnt[None]):
        v = part_vel[i] + gravity * dt
        p2 = part_pos[i] + v * dt
        if p2.y < 0: p2.y = 0; v *= -0.5
        for k in range(sphere_cnt[None]):
            d = p2 - sphere_pos[k]; dist = d.norm()
            if 0 < dist < sphere_rad[k]:
                n = d / dist; v = v - 2 * v.dot(n) * n; p2 = sphere_pos[k] + n * sphere_rad[k]
        part_vel[i] = v; part_pos[i] = p2

    # Cloth physics & collisions
    res = cloth_res[None]
    for i in range(res):
        for j in range(res):
            f = gravity
            for di, dj in ti.static([(1, 0), (0, 1)]):
                ni, nj = i + di, j + dj
                if ni < res and nj < res:
                    d = tcloth[ni, nj] - tcloth[i, j]
                    rest = ti.sqrt(di*di + dj*dj) * 0.5
                    f += (d.norm() - rest) * d.normalized() * 50.0
            v2 = vcloth[i, j] + f * dt
            p3 = tcloth[i, j] + v2 * dt
            if p3.y < 0: p3.y = 0; v2 *= -0.5
            for k in range(sphere_cnt[None]):
                d2 = p3 - sphere_pos[k]; dist2 = d2.norm()
                if 0 < dist2 < sphere_rad[k]:
                    n2 = d2 / dist2; v2 = v2 - 2 * v2.dot(n2) * n2; p3 = sphere_pos[k] + n2 * sphere_rad[k]
            vcloth[i, j] = v2; tcloth[i, j] = p3

# --- GUI & Rendering ---
# --- Main Application ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D VFX & Animation Tool")
        self.setGeometry(100, 100, 1200, 800)

        # Define sphere colors
        self.sphere_colors = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)]  # Add more colors as needed

        # Menu & Toolbars
        toolbar = QToolBar(self)
        self.addToolBar(toolbar)
        
        reset_btn = QToolButton()
        reset_btn.setText('Reset')
        reset_btn.clicked.connect(self.reset_sim)
        toolbar.addWidget(reset_btn)

        # Dock Widgets
        outliner_dock = QDockWidget('Outliner', self)
        outliner_widget = QListWidget()
        outliner_widget.addItem("Cloth")
        outliner_dock.setWidget(outliner_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, outliner_dock)

        # Viewport (GL)
        self.viewport = GLViewportWidget(self)
        self.setCentralWidget(self.viewport)

        # Status bar
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)

        # Timer for simulation step
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.simulate)
        self.timer.start(int(1000 * dt))

        init_sim()

    def simulate(self):
        step_sim()
        self.viewport.update()

    def reset_sim(self):
        init_sim()
        self.viewport.update()

# --- GL Rendering ---
from OpenGL.GL import *
from OpenGL.GLU import *


class GLViewportWidget(QOpenGLWidget):
    def initializeGL(self): 
        glEnable(GL_DEPTH_TEST)  # Enable depth testing
        glClearColor(0.1, 0.1, 0.1, 1)  # Set background color

    def resizeGL(self, w, h): 
        glViewport(0, 0, w, h)  # Set viewport size
        glMatrixMode(GL_PROJECTION)  
        glLoadIdentity()  
        asp = w / h if h else 1  
        glFrustum(-asp, asp, -1, 1, 1.5, 100)  # Set up projection matrix
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Clear the screen
        glLoadIdentity()
        glTranslatef(0, -1.5, -15)  # Translate the scene

        # Create a quadric object for sphere rendering
        quad = gluNewQuadric()

        # ground
        glColor3f(0.3, 0.8, 0.3)  # Set color for ground
        glBegin(GL_QUADS)
        glVertex3f(-10, 0, -10)
        glVertex3f(10, 0, -10)
        glVertex3f(10, 0, 10)
        glVertex3f(-10, 0, 10)
        glEnd()

        # spheres
        for i in range(sphere_cnt[None]):
            p = sphere_pos[i]
            color = self.parent().sphere_colors[i % len(self.parent().sphere_colors)]  # Get color for the sphere
            glPushMatrix()
            glTranslatef(p.x, p.y, p.z)  # Translate sphere to its position
            glColor3f(*color)  # Set the color for the sphere
            gluSphere(quad, sphere_rad[i], 16, 16)  # Render the sphere
            glPopMatrix()

        # particles (optional if you have particles)
        for i in range(part_cnt[None]):
            p = part_pos[i]
            glPushMatrix()
            glTranslatef(p.x, p.y, p.z)
            glColor3f(1.0, 0.0, 0.0)  # Red color for particles
            gluSphere(quad, 0.2, 16, 16)  # Render the particle (adjust size as necessary)
            glPopMatrix()

        # cloth (optional if you have cloth)
        for i in range(cloth_res[None]):
            for j in range(cloth_res[None]):
                p = tcloth[i, j]
                glPushMatrix()
                glTranslatef(p.x, p.y, p.z)
                glColor3f(0.5, 0.5, 1.0)  # Blue color for cloth nodes
                gluSphere(quad, 0.1, 16, 16)  # Render the cloth node
                glPopMatrix()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    set_dark_theme(app)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())
