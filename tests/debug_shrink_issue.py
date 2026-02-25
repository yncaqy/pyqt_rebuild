"""
Debug Shrink Issue - Detailed Analysis

This program will help us understand exactly what's happening during the shrink operation.
We'll add extensive logging to trace the resize logic step by step.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QWidget, QTextEdit
from PyQt6.QtCore import Qt, QPoint

from containers.frameless_window import FramelessWindow
from core.theme_manager import ThemeManager
from themes import DEFAULT_THEME, DARK_THEME, LIGHT_THEME


class DebugFramelessWindow(FramelessWindow):
    """Enhanced FramelessWindow with detailed debugging"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.debug_log = []
        
    def _resize_window(self, global_pos: QPoint):
        """Enhanced resize method with detailed logging"""
        print("\n=== DEBUG _resize_window CALLED ===")
        
        if self._geometry is None:
            print("❌ _geometry is None, returning early")
            return

        delta = global_pos - self._press_pos
        geo = self._geometry
        
        print(f"📊 Mouse delta: ({delta.x()}, {delta.y()})")
        print(f"📏 Original geometry: ({geo.left()}, {geo.top()}, {geo.width()}, {geo.height()})")
        
        # Minimum size constraints
        min_w = 400
        min_h = 300

        # Get current window geometry
        current_geo = self.geometry()
        current_w = current_geo.width()
        current_h = current_geo.height()
        
        print(f"📏 Current geometry: ({current_geo.left()}, {current_geo.top()}, {current_w}, {current_h})")
        print(f"📏 Minimum size: {min_w} x {min_h}")
        print(f"📏 Current size: {current_w} x {current_h}")
        print(f"📏 Edge being resized: {self._edge}")

        # CRITICAL: Check if already at minimum size and trying to shrink further
        shrink_prevented = False
        
        if 'top' in self._edge or 'bottom' in self._edge:
            print(f"🔍 Vertical edge detected")
            if current_h <= min_h:
                print(f"⚠️  Already at minimum height ({current_h} <= {min_h})")
                if ('top' in self._edge and delta.y() > 0):
                    print(f"🛑 Trying to shrink from TOP (delta.y={delta.y()} > 0), STOPPING")
                    shrink_prevented = True
                elif ('bottom' in self._edge and delta.y() < 0):
                    print(f"🛑 Trying to shrink from BOTTOM (delta.y={delta.y()} < 0), STOPPING")
                    shrink_prevented = True
                else:
                    print(f"✅ Not trying to shrink vertically, allowing movement")

        if 'left' in self._edge or 'right' in self._edge:
            print(f"🔍 Horizontal edge detected")
            if current_w <= min_w:
                print(f"⚠️  Already at minimum width ({current_w} <= {min_w})")
                if ('left' in self._edge and delta.x() > 0):
                    print(f"🛑 Trying to shrink from LEFT (delta.x={delta.x()} > 0), STOPPING")
                    shrink_prevented = True
                elif ('right' in self._edge and delta.x() < 0):
                    print(f"🛑 Trying to shrink from RIGHT (delta.x={delta.x()} < 0), STOPPING")
                    shrink_prevented = True
                else:
                    print(f"✅ Not trying to shrink horizontally, allowing movement")

        if shrink_prevented:
            print("🛑 SHUTDOWN: Preventing further resize due to minimum size constraint")
            return

        # Calculate new boundaries
        new_left = geo.left()
        new_top = geo.top()
        new_right = geo.right()
        new_bottom = geo.bottom()

        print(f"📐 Calculating new boundaries...")
        
        # Apply edge-specific resizing with minimum size enforcement
        if 'top' in self._edge:
            new_top = geo.top() + delta.y()
            print(f"👆 TOP edge: new_top = {geo.top()} + {delta.y()} = {new_top}")
            if geo.bottom() - new_top < min_h:
                new_top = geo.bottom() - min_h
                print(f"📏 Enforcing minimum height: new_top adjusted to {new_top}")

        if 'bottom' in self._edge:
            new_bottom = geo.bottom() + delta.y()
            print(f"👇 BOTTOM edge: new_bottom = {geo.bottom()} + {delta.y()} = {new_bottom}")
            if new_bottom - geo.top() < min_h:
                new_bottom = geo.top() + min_h
                print(f"📏 Enforcing minimum height: new_bottom adjusted to {new_bottom}")

        if 'left' in self._edge:
            new_left = geo.left() + delta.x()
            print(f"👈 LEFT edge: new_left = {geo.left()} + {delta.x()} = {new_left}")
            if geo.right() - new_left < min_w:
                new_left = geo.right() - min_w
                print(f"📏 Enforcing minimum width: new_left adjusted to {new_left}")

        if 'right' in self._edge:
            new_right = geo.right() + delta.x()
            print(f"👉 RIGHT edge: new_right = {geo.right()} + {delta.x()} = {new_right}")
            if new_right - geo.left() < min_w:
                new_right = geo.left() + min_w
                print(f"📏 Enforcing minimum width: new_right adjusted to {new_right}")

        new_width = new_right - new_left
        new_height = new_bottom - new_top
        print(f"📐 New calculated size: {new_width} x {new_height}")
        
        # CRITICAL: Only apply geometry change if it would actually modify the window
        if (new_left != geo.left() or new_top != geo.top() or
            new_right != geo.right() or new_bottom != geo.bottom()):
            print(f"✅ Geometry changing: ({new_left},{new_top},{new_width},{new_height})")
            print("🔧 Applying new geometry...")
            self.setGeometry(new_left, new_top, new_width, new_height)
            print("✅ Geometry applied successfully")
        else:
            print("ℹ️  No geometry change needed")


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Register themes
    theme_mgr = ThemeManager.instance()
    theme_mgr.register_theme_dict("default", DEFAULT_THEME)
    theme_mgr.register_theme_dict("dark", DARK_THEME)
    theme_mgr.register_theme_dict("light", LIGHT_THEME)
    theme_mgr.set_current_theme("light")

    # Create debug window
    window = DebugFramelessWindow()
    window.setTitle("🔬 Debug Shrink Issue")
    window.resize(450, 350)  # Close to minimum size for testing

    # Add debugging interface
    content = QWidget()
    layout = QVBoxLayout(content)
    layout.setContentsMargins(15, 15, 15, 15)

    title = QLabel("🔬 Shrink Issue Debugger")
    title.setStyleSheet("font-size: 16px; font-weight: bold; color: #e74c3c;")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)

    instructions = QLabel(
        "<b>Debug Instructions:</b><br><br>"
        "1. Open the console/terminal to see detailed logs<br>"
        "2. Drag the <b>TOP EDGE</b> downward to shrink the window<br>"
        "3. Watch the console output for step-by-step analysis<br>"
        "4. The window should <b>STOP MOVING</b> when it hits minimum height (300px)<br><br>"
        "<b>观察重点:</b><br>"
        "• 查看 'Already at minimum height' 消息<br>"
        "• 查看 'Trying to shrink from TOP' 消息<br>"
        "• 查看 'SHUTDOWN: Preventing further resize' 消息<br>"
        "• 查看最终是否还有 'Applying new geometry' 消息<br>"
    )
    instructions.setTextFormat(Qt.TextFormat.RichText)
    instructions.setWordWrap(True)

    size_info = QLabel("Current Size: 450 x 350 (接近最小尺寸 400x300)")
    size_info.setStyleSheet("font-size: 12px; font-weight: bold; color: #3498db;")
    size_info.setAlignment(Qt.AlignmentFlag.AlignCenter)

    layout.addWidget(title)
    layout.addWidget(instructions)
    layout.addWidget(size_info)
    layout.addStretch()

    window.setCentralWidget(content)

    # Center window
    screen = app.primaryScreen()
    if screen:
        geometry = screen.availableGeometry()
        window.move(
            geometry.center().x() - window.width() // 2,
            geometry.center().y() - window.height() // 2
        )

    window.show()
    print("=" * 60)
    print("🔬 DEBUG MODE ACTIVATED")
    print("请拖动窗口顶部边缘向下，观察控制台输出")
    print("=" * 60)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()