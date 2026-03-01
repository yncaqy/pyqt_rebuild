"""
超链接按钮组件

提供类似超链接的按钮控件，用于 URL 导航。

功能特性:
- 链接样式带下划线
- 点击时在默认浏览器中打开 URL
- 主题集成，自动更新样式
- 悬停和已访问状态
- 支持文本和图标显示
"""

import logging
import webbrowser
from typing import Optional
from PyQt6.QtCore import Qt, QSize, QByteArray
from PyQt6.QtGui import QColor, QIcon, QPixmap, QEnterEvent
from PyQt6.QtWidgets import QPushButton, QWidget, QSizePolicy
from core.theme_manager import ThemeManager, Theme

logger = logging.getLogger(__name__)


class HyperlinkButtonConfig:
    """超链接按钮配置常量。"""

    # 水平尺寸策略：Minimum 表示按钮宽度根据内容自动调整
    DEFAULT_HORIZONTAL_POLICY = QSizePolicy.Policy.Minimum
    
    # 垂直尺寸策略：Fixed 表示按钮高度固定
    DEFAULT_VERTICAL_POLICY = QSizePolicy.Policy.Fixed
    
    # 默认图标尺寸（单位：像素）
    DEFAULT_ICON_SIZE = 16


class HyperlinkButton(QPushButton):
    """
    类似超链接的按钮控件，用于 URL 导航。

    功能特性:
    - 链接样式带下划线
    - 点击时在默认浏览器中打开 URL
    - 主题集成，自动更新样式
    - 悬停和已访问状态
    - 支持文本和图标显示

    示例:
        button = HyperlinkButton("点击这里", "https://example.com")
        button.clicked.connect(button.open_url)
    """

    def __init__(
        self,
        text: str = "",
        url: str = "",
        parent: Optional[QWidget] = None
    ):
        super().__init__(text, parent)

        self.setSizePolicy(
            HyperlinkButtonConfig.DEFAULT_HORIZONTAL_POLICY,
            HyperlinkButtonConfig.DEFAULT_VERTICAL_POLICY
        )

        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Theme] = None

        self._url = url
        self._icon_size = HyperlinkButtonConfig.DEFAULT_ICON_SIZE
        self._icon_content: Optional[str] = None
        self._colored_pixmap: Optional[QPixmap] = None

        self._setup_ui()
        self._theme_mgr.subscribe(self, self._on_theme_changed)

        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._current_theme = initial_theme
            self._apply_theme(initial_theme)

        self.clicked.connect(self._on_clicked)

        logger.debug(f"HyperlinkButton 已初始化，文本: '{text}'，URL: '{url}'")

    def _setup_ui(self) -> None:
        """初始化 UI 设置。"""
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFlat(True)

    def _on_theme_changed(self, theme: Theme) -> None:
        """主题变化回调。"""
        self._current_theme = theme
        self._apply_theme(theme)
        self._update_icon()

    def _apply_theme(self, theme: Theme) -> None:
        """应用主题样式。"""
        if not theme:
            return

        self._current_theme = theme

        link_color = theme.get_color('link.normal', QColor(0, 120, 212))
        link_hover = theme.get_color('link.hover', QColor(0, 100, 192))

        qss = f"""
        HyperlinkButton {{
            background-color: transparent;
            color: {link_color.name()};
            border: none;
            padding: 0px;
        }}
        HyperlinkButton:hover {{
            color: {link_hover.name()};
        }}
        """

        self.setStyleSheet(qss)

    def _get_icon_color(self) -> QColor:
        """根据当前主题获取图标颜色。"""
        if self._current_theme:
            return self._current_theme.get_color('link.normal', QColor(0, 120, 212))
        return QColor(0, 120, 212)

    def _update_icon(self) -> None:
        """使用当前主题颜色更新图标。"""
        if not self._icon_content:
            super().setIcon(QIcon())
            return

        color = self._get_icon_color()
        self._colored_pixmap = self._create_colored_pixmap(self._icon_content, color)

        if self._colored_pixmap:
            icon = QIcon(self._colored_pixmap)
            super().setIcon(icon)
            super().setIconSize(QSize(self._icon_size, self._icon_size))

    def _create_colored_pixmap(self, svg_content: str, color: QColor) -> Optional[QPixmap]:
        """
        从 SVG 内容创建着色像素图。

        Args:
            svg_content: SVG 内容字符串
            color: 要应用的颜色

        Returns:
            着色后的 QPixmap，失败返回 None
        """
        try:
            color_hex = color.name(QColor.NameFormat.HexRgb)
            svg_colored = svg_content.replace('currentColor', color_hex)

            if 'stroke="currentColor"' in svg_colored:
                svg_colored = svg_colored.replace('stroke="currentColor"', f'stroke="{color_hex}"')
            if 'fill="currentColor"' in svg_colored:
                svg_colored = svg_colored.replace('fill="currentColor"', f'fill="{color_hex}"')

            svg_bytes = QByteArray(svg_colored.encode('utf-8'))
            pixmap = QPixmap()
            pixmap.loadFromData(svg_bytes)

            if pixmap.isNull():
                return None

            if pixmap.width() != self._icon_size or pixmap.height() != self._icon_size:
                pixmap = pixmap.scaled(
                    self._icon_size, self._icon_size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )

            return pixmap
        except Exception as e:
            logger.error(f"创建着色像素图时出错: {e}")
            return None

    def _on_clicked(self) -> None:
        """处理按钮点击事件，打开 URL。"""
        if self._url:
            self.open_url()

    def open_url(self) -> bool:
        """
        在默认浏览器中打开 URL。

        Returns:
            成功打开返回 True，否则返回 False
        """
        if not self._url:
            logger.warning("HyperlinkButton 未设置 URL")
            return False

        try:
            result = webbrowser.open(self._url)
            if result:
                logger.debug(f"已打开 URL: {self._url}")
            return result
        except Exception as e:
            logger.error(f"打开 URL 失败 {self._url}: {e}")
            return False

    def setUrl(self, url: str) -> None:
        """
        设置点击时要打开的 URL。

        Args:
            url: URL 字符串
        """
        self._url = url
        logger.debug(f"URL 已设置为: {url}")

    def url(self) -> str:
        """
        获取当前 URL。

        Returns:
            当前 URL 字符串
        """
        return self._url

    def setIcon(self, icon: QIcon | str) -> None:
        """
        设置按钮图标。

        Args:
            icon: QIcon 对象或 SVG 字符串
        """
        if isinstance(icon, str):
            self._icon_content = icon
            self._update_icon()

            if self.text():
                original_text = self.text().lstrip()
                super().setText(f" {original_text}")
        else:
            self._icon_content = None
            self._colored_pixmap = None
            super().setIcon(icon)

    def setIconSize(self, size: QSize) -> None:
        """
        设置图标大小。

        Args:
            size: 图标尺寸
        """
        self._icon_size = size.width()
        self._update_icon()

    def enterEvent(self, event: QEnterEvent) -> None:
        """鼠标进入事件处理。"""
        super().enterEvent(event)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def cleanup(self) -> None:
        """清理资源，取消主题订阅。"""
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
