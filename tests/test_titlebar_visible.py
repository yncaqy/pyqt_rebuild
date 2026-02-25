"""
Test TitleBar Visibility

This script helps verify that the title bar exists and is visible.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from containers.frameless_window import FramelessWindow
from core.theme_manager import ThemeManager
from themes import DARK_THEME, LIGHT_THEME

print("=" * 70)
print("FramelessWindow TitleBar Test")
print("=" * 70)
print()

# Create application
app = QApplication(sys.argv)

# Setup themes
theme_mgr = ThemeManager.instance()
theme_mgr.register_theme_dict('dark', DARK_THEME)
theme_mgr.register_theme_dict('light', LIGHT_THEME)
theme_mgr.set_theme('dark')

# Create frameless window
window = FramelessWindow()
window.setTitle("TitleBar Test Window")
window.resize(900, 700)

# Create content
content = QWidget()
layout = QVBoxLayout(content)
layout.setContentsMargins(20, 20, 20, 20)
layout.setSpacing(20)

# Title
title = QLabel("FramelessWindow - TitleBar Visibility Test")
title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
title.setAlignment(Qt.AlignmentFlag.AlignCenter)
layout.addWidget(title)

# Info text
info = QLabel("""
<h3>How to verify the title bar:</h3>
<ul>
    <li><b>Look at the top of the window</b> - You should see three buttons: [─] [□] [✕]</li>
    <li><b>Title text</b> - "TitleBar Test Window" on the left</li>
    <li><b>Height</b> - The title bar is 40 pixels tall</li>
    <li><b>Background</b> - Dark gray (#2d2d2d) in dark theme</li>
</ul>

<h3>What you can do:</h3>
<ul>
    <li><b>Drag</b> - Click and drag the title bar to move the window</li>
    <li><b>Double-click</b> - Double-click the title bar to maximize/restore</li>
    <li><b>Buttons</b> - Click the [─] [□] [✕] buttons to minimize/maximize/close</li>
</ul>

<h3>Why might it be hard to see?</h3>
<ul>
    <li>The title bar blends with the content (same background color)</li>
    <li>There's no visible border/separation line</li>
    <li>The buttons only highlight when you hover over them</li>
</ul>
""")
info.setWordWrap(True)
info.setTextFormat(Qt.TextFormat.RichText)
layout.addWidget(info)

# Color indicator
color_info = QLabel()
color_info.setStyleSheet("""
    QLabel {
        background-color: #2d2d2d;
        color: white;
        padding: 10px;
        border: 2px solid #555;
    }
""")
color_info.setText(
    "This box shows the title bar background color (#2d2d2d). "
    "Look for this color at the top of the window."
)
color_info.setWordWrap(True)
layout.addWidget(color_info)

# Test buttons
btn_layout = QHBoxLayout()

print_btn = QPushButton("Print TitleBar Info")
print_btn.clicked.connect(lambda: print_titlebar_info(window))
btn_layout.addWidget(print_btn)

toggle_theme_btn = QPushButton("Toggle Theme")
toggle_theme_btn.clicked.connect(lambda: toggle_theme(theme_mgr))
btn_layout.addWidget(toggle_theme_btn)

btn_layout.addStretch()
layout.addLayout(btn_layout)

# Add close button
close_btn = QPushButton("Close Window")
close_btn.clicked.connect(window.close)
layout.addWidget(close_btn)

layout.addStretch()

# Set content
window.setCentralWidget(content)

# Print initial info
print("\n--- TitleBar Information ---")
print_titlebar_info(window)

print("\n" + "=" * 70)
print("Window is now displayed.")
print("Follow the instructions above to verify the title bar.")
print("=" * 70)

window.show()

def print_titlebar_info(window):
    """Print title bar information."""
    tb = window.title_bar
    print()
    print(f"TitleBar Object: {tb}")
    print(f"  Visible: {tb.isVisible()}")
    print(f"  Height: {tb.height()} px")
    print(f"  Width: {tb.width()} px")
    print(f"  Position: ({tb.x()}, {tb.y()})")
    print(f"  Title Text: '{tb.title_label.text()}'")
    print(f"  Icon Label: {tb.icon_label}")
    print(f"  Minimize Button: {tb.minimize_btn}")
    print(f"  Maximize Button: {tb.maximize_btn}")
    print(f"  Close Button: {tb.close_btn}")
    print()

def toggle_theme(theme_mgr):
    """Toggle between dark and light themes."""
    current = theme_mgr.current_theme()
    if current and current.name == 'dark':
        theme_mgr.set_theme('light')
        print("[INFO] Switched to light theme")
    else:
        theme_mgr.set_theme('dark')
        print("[INFO] Switched to dark theme")

sys.exit(app.exec())
