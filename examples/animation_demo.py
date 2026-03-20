"""
动画系统演示程序

演示如何使用动画系统：
1. 全局动画开关
2. 动画预设
3. 组件动画混入
4. 自定义动画配置
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QCheckBox, QSlider, QGroupBox,
    QComboBox, QSpinBox
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont

from core.animation import (
    AnimationManager, AnimationConfig, AnimationPreset,
    AnimatableMixin, EasingType, SlideDirection
)


class AnimatedPopup(QFrame, AnimatableMixin):
    """带动画效果的弹出面板。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setFixedSize(200, 150)
        self.setStyleSheet("""
            AnimatedPopup {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 8px;
            }
        """)

        layout = QVBoxLayout(self)
        label = QLabel("动画弹出面板")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: white; font-size: 14px;")
        layout.addWidget(label)

        self.setup_animation(AnimationPreset.FLYOUT, AnimationPreset.FLYOUT_HIDE)
        self.hide()

    def show_at(self, pos: QPoint):
        """在指定位置显示。"""
        self.move(pos)
        self.show()
        self.animate_show()

    def hide_animated(self):
        """带动画隐藏。"""
        self.animate_hide()
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(150, self.hide)


class AnimatedButton(QPushButton, AnimatableMixin):
    """带动画效果的按钮。"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(36)
        self.setStyleSheet("""
            AnimatedButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
            }
            AnimatedButton:hover {
                background-color: #1084d8;
            }
            AnimatedButton:pressed {
                background-color: #006cbd;
            }
        """)

        self.setup_animation(AnimationPreset.BUTTON, AnimationPreset.BUTTON_RELEASE)

    def mousePressEvent(self, event):
        self.animate_show()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.animate_hide()
        super().mouseReleaseEvent(event)


class AnimationDemoWindow(QMainWindow):
    """动画系统演示窗口。"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("动画系统演示 - WinUI 3 风格")
        self.setMinimumSize(800, 600)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")

        self._animation_manager = AnimationManager.instance()
        self._popup = None

        self._init_ui()

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("动画系统演示")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        global_group = QGroupBox("全局动画设置")
        global_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #3d3d3d;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        global_layout = QHBoxLayout(global_group)

        self.enable_checkbox = QCheckBox("启用动画")
        self.enable_checkbox.setChecked(self._animation_manager.is_enabled())
        self.enable_checkbox.stateChanged.connect(self._on_enable_changed)
        self.enable_checkbox.setStyleSheet("font-size: 14px;")
        global_layout.addWidget(self.enable_checkbox)

        global_layout.addWidget(QLabel("动画速度:"))
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(50, 200)
        self.speed_slider.setValue(100)
        self.speed_slider.setFixedWidth(200)
        self.speed_slider.valueChanged.connect(self._on_speed_changed)
        global_layout.addWidget(self.speed_slider)

        self.speed_label = QLabel("1.0x")
        self.speed_label.setFixedWidth(50)
        global_layout.addWidget(self.speed_label)

        global_layout.addStretch()
        main_layout.addWidget(global_group)

        preset_group = QGroupBox("动画预设演示")
        preset_group.setStyleSheet(global_group.styleSheet())
        preset_layout = QVBoxLayout(preset_group)

        preset_buttons_layout = QHBoxLayout()

        presets = [
            ("Flyout", AnimationPreset.FLYOUT),
            ("Popup", AnimationPreset.POPUP),
            ("Dialog", AnimationPreset.DIALOG),
            ("Tooltip", AnimationPreset.TOOLTIP),
            ("Fade", AnimationPreset.FADE_ONLY),
        ]

        for name, preset in presets:
            btn = QPushButton(name)
            btn.setFixedHeight(36)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3d3d3d;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #4d4d4d;
                }
            """)
            btn.clicked.connect(lambda checked, p=preset: self._show_preset_demo(p))
            preset_buttons_layout.addWidget(btn)

        preset_layout.addLayout(preset_buttons_layout)
        main_layout.addWidget(preset_group)

        custom_group = QGroupBox("自定义动画配置")
        custom_group.setStyleSheet(global_group.styleSheet())
        custom_layout = QVBoxLayout(custom_group)

        config_row = QHBoxLayout()

        config_row.addWidget(QLabel("时长(ms):"))
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(50, 1000)
        self.duration_spin.setValue(200)
        self.duration_spin.setFixedWidth(80)
        config_row.addWidget(self.duration_spin)

        config_row.addWidget(QLabel("缓动曲线:"))
        self.easing_combo = QComboBox()
        self.easing_combo.addItems([
            "OutCubic", "InCubic", "InOutCubic",
            "OutQuad", "InQuad", "InOutQuad",
            "OutBack", "InBack", "Linear"
        ])
        self.easing_combo.setFixedWidth(120)
        config_row.addWidget(self.easing_combo)

        config_row.addWidget(QLabel("缩放:"))
        self.scale_spin = QSpinBox()
        self.scale_spin.setRange(50, 150)
        self.scale_spin.setValue(95)
        self.scale_spin.setFixedWidth(80)
        self.scale_spin.setSuffix("%")
        config_row.addWidget(self.scale_spin)

        config_row.addStretch()
        custom_layout.addLayout(config_row)

        custom_btn = QPushButton("执行自定义动画")
        custom_btn.setFixedHeight(36)
        custom_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1084d8;
            }
        """)
        custom_btn.clicked.connect(self._show_custom_demo)
        custom_layout.addWidget(custom_btn)

        main_layout.addWidget(custom_group)

        button_group = QGroupBox("按钮动画演示")
        button_group.setStyleSheet(global_group.styleSheet())
        button_layout = QHBoxLayout(button_group)

        for i in range(3):
            btn = AnimatedButton(f"动画按钮 {i + 1}")
            button_layout.addWidget(btn)

        button_layout.addStretch()
        main_layout.addWidget(button_group)

        main_layout.addStretch()

        info_label = QLabel(
            "提示：取消勾选'启用动画'后，所有动画效果将立即禁用。\n"
            "调整动画速度可以加快或减慢所有动画效果。"
        )
        info_label.setStyleSheet("color: #888; font-size: 12px;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(info_label)

    def _on_enable_changed(self, state):
        """动画开关变化。"""
        enabled = state == Qt.CheckState.Checked.value
        self._animation_manager.set_enabled(enabled)

    def _on_speed_changed(self, value):
        """动画速度变化。"""
        factor = value / 100.0
        self._animation_manager.set_scale_factor(factor)
        self.speed_label.setText(f"{factor:.1f}x")

    def _show_preset_demo(self, show_preset):
        """显示预设动画演示。"""
        if self._popup is None:
            self._popup = AnimatedPopup(self)

        hide_preset = AnimationPreset.FLYOUT_HIDE
        if show_preset == AnimationPreset.POPUP:
            hide_preset = AnimationPreset.POPUP_HIDE
        elif show_preset == AnimationPreset.DIALOG:
            hide_preset = AnimationPreset.DIALOG_HIDE
        elif show_preset == AnimationPreset.TOOLTIP:
            hide_preset = AnimationPreset.TOOLTIP_HIDE
        elif show_preset == AnimationPreset.FADE_ONLY:
            hide_preset = AnimationPreset.FADE_ONLY_HIDE

        self._popup._show_config = show_preset
        self._popup._hide_config = hide_preset

        center = self.rect().center()
        pos = self.mapToGlobal(QPoint(center.x() - 100, center.y() - 75))
        self._popup.show_at(pos)

        from PyQt6.QtCore import QTimer
        QTimer.singleShot(1500, self._hide_popup)

    def _hide_popup(self):
        """隐藏弹出面板。"""
        if self._popup:
            self._popup.hide_animated()

    def _show_custom_demo(self):
        """显示自定义动画演示。"""
        easing_map = {
            "OutCubic": EasingType.OUT_CUBIC,
            "InCubic": EasingType.IN_CUBIC,
            "InOutCubic": EasingType.IN_OUT_CUBIC,
            "OutQuad": EasingType.OUT_QUAD,
            "InQuad": EasingType.IN_QUAD,
            "InOutQuad": EasingType.IN_OUT_QUAD,
            "OutBack": EasingType.OUT_BACK,
            "InBack": EasingType.IN_BACK,
            "Linear": EasingType.LINEAR,
        }

        easing_name = self.easing_combo.currentText()
        scale = self.scale_spin.value() / 100.0

        config = AnimationConfig(
            duration=self.duration_spin.value(),
            easing=easing_map.get(easing_name, EasingType.OUT_CUBIC),
            opacity_start=0.0,
            opacity_end=1.0,
            scale_start=scale,
            scale_end=1.0,
        )

        hide_config = AnimationConfig(
            duration=self.duration_spin.value(),
            easing=EasingType.IN_CUBIC,
            opacity_start=1.0,
            opacity_end=0.0,
            scale_start=1.0,
            scale_end=scale,
        )

        if self._popup is None:
            self._popup = AnimatedPopup(self)

        self._popup._show_config = config
        self._popup._hide_config = hide_config

        center = self.rect().center()
        pos = self.mapToGlobal(QPoint(center.x() - 100, center.y() - 75))
        self._popup.show_at(pos)

        from PyQt6.QtCore import QTimer
        QTimer.singleShot(1500, self._hide_popup)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = AnimationDemoWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
