#!/usr/bin/env python3
"""
自定义滚动条组件

提供带圆角的自定义绘制滚动条。
"""

import logging
from typing import Optional
from PyQt6.QtCore import Qt, QRect, QPoint
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QPainterPath
from PyQt6.QtWidgets import QScrollBar, QWidget, QStyle, QStyleOptionSlider

from src.core.theme_manager import ThemeManager, Theme

logger = logging.getLogger(__name__)


class CustomScrollBar(QScrollBar):
    """
    自定义滚动条，支持圆角和悬停效果。

    功能特性:
    - 圆角滑块，平滑边角
    - 细到宽的悬停效果
    - 主题集成
    """

    def __init__(self, orientation: Qt.Orientation, parent: Optional[QWidget] = None):
        """
        初始化自定义滚动条。

        Args:
            orientation: 滚动条方向（水平或垂直）
            parent: 父控件
        """
        super().__init__(orientation, parent)

        self._theme_mgr = ThemeManager.instance()
        self._handle_color = QColor(120, 120, 120)
        self._handle_hover_color = QColor(90, 90, 90)
        self._is_hovering = False
        self._thin_width = 6
        self._wide_width = 10

        self._theme_mgr.subscribe(self, self._on_theme_changed)

        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._apply_theme(initial_theme)

    def _on_theme_changed(self, theme: Theme) -> None:
        """
        处理主题变化通知。

        Args:
            theme: 新主题
        """
        self._apply_theme(theme)

    def _apply_theme(self, theme: Theme) -> None:
        """
        应用主题到滚动条。

        Args:
            theme: 主题对象
        """
        if not theme:
            return

        self._handle_color = theme.get_color('scrollbar.handle.normal', QColor(120, 120, 120))
        self._handle_hover_color = theme.get_color('scrollbar.handle.hover', QColor(90, 90, 90))

        self.setStyleSheet("background: transparent;")
        self.update()

    def enterEvent(self, event):
        """鼠标进入事件。"""
        self._is_hovering = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """鼠标离开事件。"""
        self._is_hovering = False
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        """绘制事件。"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        opt = QStyleOptionSlider()
        self.initStyleOption(opt)

        groove_rect = self.style().subControlRect(
            QStyle.ComplexControl.CC_ScrollBar,
            opt,
            QStyle.SubControl.SC_ScrollBarGroove,
            self
        )

        slider_rect = self.style().subControlRect(
            QStyle.ComplexControl.CC_ScrollBar,
            opt,
            QStyle.SubControl.SC_ScrollBarSlider,
            self
        )

        width = self._wide_width if self._is_hovering else self._thin_width
        radius = width // 2

        if self.orientation() == Qt.Orientation.Vertical:
            self._draw_vertical_handle(painter, groove_rect, slider_rect, width, radius)
        else:
            self._draw_horizontal_handle(painter, groove_rect, slider_rect, width, radius)

        painter.end()

    def _draw_vertical_handle(self, painter: QPainter, groove_rect: QRect,
                              slider_rect: QRect, width: int, radius: int):
        """
        绘制垂直滚动条滑块。

        Args:
            painter: 绘制器
            groove_rect: 滑槽矩形
            slider_rect: 滑块矩形
            width: 滑块宽度
            radius: 圆角半径
        """
        x = groove_rect.x() + (groove_rect.width() - width) // 2
        y = slider_rect.y()
        h = slider_rect.height()

        if h < radius * 2:
            h = radius * 2

        color = self._handle_hover_color if self._is_hovering else self._handle_color
        color = QColor(color)
        if not self._is_hovering:
            color.setAlpha(150)

        path = QPainterPath()
        path.addRoundedRect(x, y, width, h, radius, radius)

        painter.fillPath(path, QBrush(color))

    def _draw_horizontal_handle(self, painter: QPainter, groove_rect: QRect,
                                slider_rect: QRect, width: int, radius: int):
        """
        绘制水平滚动条滑块。

        Args:
            painter: 绘制器
            groove_rect: 滑槽矩形
            slider_rect: 滑块矩形
            width: 滑块高度
            radius: 圆角半径
        """
        y = groove_rect.y() + (groove_rect.height() - width) // 2
        x = slider_rect.x()
        w = slider_rect.width()

        if w < radius * 2:
            w = radius * 2

        color = self._handle_hover_color if self._is_hovering else self._handle_color
        color = QColor(color)
        if not self._is_hovering:
            color.setAlpha(150)

        path = QPainterPath()
        path.addRoundedRect(x, y, w, width, radius, radius)

        painter.fillPath(path, QBrush(color))

    def cleanup(self):
        """清理资源并取消主题订阅。"""
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)

    def deleteLater(self):
        """安排控件删除，自动执行清理。"""
        self.cleanup()
        super().deleteLater()
