"""
Frameless Window Component

Provides modern frameless window support with:
- Custom title bar with window controls
- Window dragging via title bar
- Edge resizing
- Theme integration
- Platform-specific features (Windows 11 rounded corners, etc.)

Classes:
    WindowConfig: Configuration constants for frameless window
    TitleBar: Custom title bar with window controls
    FramelessWindow: Main frameless window class
"""

import sys
import logging
import time
from typing import Optional, Dict, Tuple, Any
from PyQt6.QtCore import Qt, QPoint, QEvent, QTimer
from PyQt6.QtGui import QColor, QCursor, QIcon, QMouseEvent
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy, QLayout
)
from core.theme_manager import ThemeManager, Theme
from core.font_manager import FontManager
from core.platform import get_platform_instance
from core.icon_manager import IconManager

# Initialize logger
logger = logging.getLogger(__name__)


class WindowConfig:
    """Configuration constants for frameless window behavior."""

    # Edge detection
    DEFAULT_EDGE_MARGIN = 6  # pixels
    TITLEBAR_EDGE_MARGIN = 6  # pixels

    # Title bar dimensions
    TITLEBAR_HEIGHT = 40
    TITLEBAR_BUTTON_WIDTH = 46
    TITLEBAR_BUTTON_HEIGHT = 40
    TITLEBAR_ICON_SIZE = 24
    TITLEBAR_ICON_SPACING = 12  # spacing between icon and title
    TITLEBAR_LAYOUT_MARGIN_LEFT = 10  # left margin of title bar layout

    # Icon sizes
    BUTTON_ICON_SOURCE_SIZE = 32  # source size for loading (HiDPI support)
    BUTTON_ICON_DISPLAY_SIZE = 20  # display size on button
    BUTTON_COLORED_ICON_SOURCE_SIZE = 32  # source size for colored icons

    # Window constraints
    MIN_WINDOW_WIDTH = 400
    MIN_WINDOW_HEIGHT = 300

    # Performance tuning
    EVENT_FILTER_THRESHOLD_MS = 16  # ~60fps
    MAX_EDGE_CACHE_SIZE = 1000

    # Content margins
    CONTENT_MARGIN = 10

    # Default color values (fallback when theme is not available)
    DEFAULT_TITLEBAR_TEXT_COLOR = QColor(220, 220, 220)
    DEFAULT_TITLEBAR_BG_COLOR = QColor(30, 30, 30)
    DEFAULT_BUTTON_HOVER_COLOR = QColor(50, 50, 50)
    DEFAULT_CLOSE_HOVER_COLOR = QColor(231, 76, 60)
    DEFAULT_WINDOW_BG_COLOR = QColor(25, 25, 25)
    DEFAULT_BORDER_COLOR = QColor(40, 40, 40)

    # Cursors for edge resizing
    CURSOR_MAP = {
        'top': Qt.CursorShape.SizeVerCursor,
        'bottom': Qt.CursorShape.SizeVerCursor,
        'left': Qt.CursorShape.SizeHorCursor,
        'right': Qt.CursorShape.SizeHorCursor,
        'top-left': Qt.CursorShape.SizeFDiagCursor,
        'top-right': Qt.CursorShape.SizeBDiagCursor,
        'bottom-left': Qt.CursorShape.SizeBDiagCursor,
        'bottom-right': Qt.CursorShape.SizeFDiagCursor,
        'none': Qt.CursorShape.ArrowCursor
    }


class TitleBar(QWidget):
    """
    Custom title bar for frameless window.

    Features:
    - Window title display
    - Minimize/Maximize/Close buttons
    - Double-click to maximize
    - Drag to move window

    Attributes:
        icon_label: QLabel for window icon
        title_label: QLabel for window title
        minimize_btn: Minimize button
        maximize_btn: Maximize/restore button
        close_btn: Close button
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setFixedHeight(WindowConfig.TITLEBAR_HEIGHT)
        self._theme_mgr = ThemeManager.instance()
        self._font_mgr = FontManager.instance()
        self._icon_mgr = IconManager.instance()
        self._icon = None
        self._dragging = False
        self._drag_position = QPoint()
        self._window = None
        self._edge_margin = WindowConfig.TITLEBAR_EDGE_MARGIN

        # Stylesheet cache for TitleBar
        self._stylesheet_cache: Dict[Tuple[Any, ...], str] = {}

        # Enable mouse tracking
        self.setMouseTracking(True)

        # Create layout
        self._init_ui()
        self._init_control_buttons()

        # Subscribe to theme changes
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        
        # Apply initial theme
        current_theme = self._theme_mgr.current_theme()
        if current_theme:
            self._apply_theme(current_theme)
    
    def _on_theme_changed(self, theme: Theme) -> None:
        """Handle theme change notification from theme manager.
        
        Args:
            theme: New theme to apply
        """
        self._apply_theme(theme)

    def _init_ui(self) -> None:
        """Initialize UI layout."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(WindowConfig.TITLEBAR_LAYOUT_MARGIN_LEFT, 0, 0, 0)
        main_layout.setSpacing(0)

        # Icon label
        self.icon_label = QLabel()
        self.icon_label.setObjectName("iconLabel")  # 设置 objectName 用于样式选择器
        self.icon_label.setFixedSize(
            WindowConfig.TITLEBAR_ICON_SIZE,
            WindowConfig.TITLEBAR_ICON_SIZE
        )
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.icon_label)
        # 添加固定宽度的spacing作为图标和标题之间的间距
        main_layout.addSpacing(WindowConfig.TITLEBAR_ICON_SPACING)

        # Title label
        self.title_label = QLabel()
        self.title_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )
        self.title_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        main_layout.addWidget(self.title_label)

        # Spacer for window buttons
        main_layout.addStretch()

    def _init_control_buttons(self):
        """Initialize window control buttons."""
        # 为最小化按钮加载 SVG 图标
        self.minimize_btn = self._create_button("", "minimize", "window_minimize")
        # 为最大化按钮加载 SVG 图标
        self.maximize_btn = self._create_button("", "maximize", "window_maximize")
        # 为关闭按钮加载 SVG 图标
        self.close_btn = self._create_button("", "close", "window_close")

        # Button layout
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(0)
        btn_layout.addWidget(self.minimize_btn)
        btn_layout.addWidget(self.maximize_btn)
        btn_layout.addWidget(self.close_btn)

        main_layout = self.layout()
        main_layout.addLayout(btn_layout)

    def _create_button(self, text: str, name: str, icon_name: str = None) -> QPushButton:
        """Create a window control button with specified text and object name.

        Args:
            text: Button text/label
            name: Object name for styling (e.g., 'minimize', 'maximize', 'close')
            icon_name: Optional SVG icon name to load from IconManager

        Returns:
            Configured QPushButton instance
        """
        btn = QPushButton(text)
        btn.setFixedSize(
            WindowConfig.TITLEBAR_BUTTON_WIDTH,
            WindowConfig.TITLEBAR_BUTTON_HEIGHT
        )
        btn.setObjectName(f"titlebar_{name}_btn")
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        # Load icon if provided
        if icon_name:
            try:
                # Load icon at larger size for better rendering quality
                # High-DPI displays will look much better with larger source
                icon = self._icon_mgr.get_icon(icon_name, WindowConfig.BUTTON_ICON_SOURCE_SIZE)
                if not icon.isNull():
                    btn.setIcon(icon)
                    from PyQt6.QtCore import QSize
                    btn.setIconSize(QSize(WindowConfig.BUTTON_ICON_DISPLAY_SIZE,
                                         WindowConfig.BUTTON_ICON_DISPLAY_SIZE))
                    btn.setProperty("no-text", "true")
                    btn.setText("")  # Clear text when using icon
                    logger.info(f"Loaded icon '{icon_name}' for button '{name}'")
                else:
                    logger.warning(f"Icon '{icon_name}' is null, failed to load")
            except Exception as e:
                logger.warning(f"Failed to load icon {icon_name}: {e}")

        return btn

    def _update_button_icon(self, button: QPushButton, icon_name: str, color: QColor, button_type: str) -> None:
        """Update button icon with theme color (generic method for all window control buttons).

        Args:
            button: QPushButton instance to update
            icon_name: Icon name to load from IconManager
            color: Theme color to apply to the icon
            button_type: Button type name for logging (e.g., 'close', 'minimize', 'maximize')
        """
        try:
            # Load icon at larger size for better rendering quality
            # Use IconManager's get_colored_icon method to apply theme color
            colored_icon = self._icon_mgr.get_colored_icon(icon_name, color,
                                                          WindowConfig.BUTTON_COLORED_ICON_SOURCE_SIZE)
            if not colored_icon.isNull():
                button.setIcon(colored_icon)
                from PyQt6.QtCore import QSize
                button.setIconSize(QSize(WindowConfig.BUTTON_ICON_DISPLAY_SIZE,
                                       WindowConfig.BUTTON_ICON_DISPLAY_SIZE))
                logger.debug(f"{button_type.capitalize()} button icon updated with color: {color.name()}")
            else:
                logger.warning(f"Failed to create colored icon for {button_type} button")
        except Exception as e:
            logger.warning(f"Error updating {button_type} button icon: {e}")

    def _update_close_button_icon(self, color: QColor) -> None:
        """Update close button icon with theme color.

        Args:
            color: Theme color to apply to the icon
        """
        self._update_button_icon(self.close_btn, 'window_close', color, 'close')

    def _update_minimize_button_icon(self, color: QColor) -> None:
        """Update minimize button icon with theme color.

        Args:
            color: Theme color to apply to the icon
        """
        self._update_button_icon(self.minimize_btn, 'window_minimize', color, 'minimize')

    def _update_maximize_button_icon(self, color: QColor) -> None:
        """Update maximize button icon with theme color.

        Args:
            color: Theme color to apply to the icon
        """
        self._update_button_icon(self.maximize_btn, 'window_maximize', color, 'maximize')

    def _toggle_maximize(self):
        """Toggle between maximized and normal state."""
        if self._window:
            # Use Qt's built-in maximize
            if self._window.isMaximized():
                self._window.showNormal()
            else:
                self._window.showMaximized()
            # Update icon after state change
            self._update_maximize_icon_state()

    def _update_maximize_icon_state(self):
        """Update maximize button icon based on window state."""
        if not self._window:
            return

        try:
            # Get current theme color
            theme = self._theme_mgr.current_theme()
            if not theme:
                return

            text_color = theme.get_color('titlebar.text', WindowConfig.DEFAULT_TITLEBAR_TEXT_COLOR)

            # Use appropriate icon based on window state
            if self._window.isMaximized():
                # Show restore icon
                colored_icon = self._icon_mgr.get_colored_icon('window_restore', text_color,
                                                              WindowConfig.BUTTON_COLORED_ICON_SOURCE_SIZE)
            else:
                # Show maximize icon
                colored_icon = self._icon_mgr.get_colored_icon('window_maximize', text_color,
                                                              WindowConfig.BUTTON_COLORED_ICON_SOURCE_SIZE)

            if not colored_icon.isNull():
                from PyQt6.QtCore import QSize
                self.maximize_btn.setIcon(colored_icon)
                self.maximize_btn.setIconSize(QSize(WindowConfig.BUTTON_ICON_DISPLAY_SIZE,
                                                   WindowConfig.BUTTON_ICON_DISPLAY_SIZE))
                logger.debug(f"Maximize button icon updated: {'restore' if self._window.isMaximized() else 'maximize'}")
        except Exception as e:
            logger.warning(f"Error updating maximize button icon state: {e}")

    def _apply_theme(self, theme: Theme) -> None:
        """Apply theme to title bar with caching.

        Args:
            theme: Theme object containing color and style definitions
        """
        logger.debug(f"TitleBar._apply_theme called with theme: {theme.name if hasattr(theme, 'name') else 'unknown'}")

        if not theme:
            logger.debug("Theme is None, returning")
            return

        bg_color = theme.get_color('titlebar.background', WindowConfig.DEFAULT_TITLEBAR_BG_COLOR)
        text_color = theme.get_color('titlebar.text', WindowConfig.DEFAULT_TITLEBAR_TEXT_COLOR)
        hover_bg = theme.get_color('titlebar.button.hover', WindowConfig.DEFAULT_BUTTON_HOVER_COLOR)
        close_hover = theme.get_color('titlebar.button.close_hover', WindowConfig.DEFAULT_CLOSE_HOVER_COLOR)
        border_color = theme.get_color('window.border', WindowConfig.DEFAULT_BORDER_COLOR)

        # Apply theme color to all button icons
        self._update_minimize_button_icon(text_color)
        self._update_maximize_button_icon(text_color)
        self._update_close_button_icon(text_color)

        # Get themed fonts
        title_font = self._font_mgr.get_font('title', theme)
        header_font = self._font_mgr.get_font('header', theme)
        
        # Extract font properties
        title_family = title_font.family()
        title_size = title_font.pointSize()
        title_weight = 'bold' if title_font.bold() else 'normal'
        
        header_family = header_font.family()
        header_size = header_font.pointSize()
        header_weight = 'bold' if header_font.bold() else 'normal'

        # Check if window is maximized
        is_maximized = self._window.isMaximized() if self._window else False

        # Create cache key
        cache_key = (
            bg_color.name(),
            text_color.name(),
            hover_bg.name(),
            close_hover.name(),
            border_color.name(),
            title_family,
            title_size,
            title_weight,
            header_family,
            header_size,
            header_weight,
            sys.platform == 'win32',
            is_maximized
        )

        # Check cache
        if cache_key not in self._stylesheet_cache:
            # Only apply rounded corners and bottom border when not maximized
            if sys.platform == 'win32' and not is_maximized:
                # Windows 11: let system handle rounded corners
                border_radius_css = "border-top-left-radius: 8px; border-top-right-radius: 8px;"
                border_bottom_css = f"border-bottom: 1px solid {border_color.name()};"
            else:
                border_radius_css = ""
                border_bottom_css = "border-bottom: none;"

            stylesheet = f"""
                TitleBar {{
                    background-color: {bg_color.name()};
                    {border_bottom_css}
                    {border_radius_css}
                }}
                QLabel {{
                    color: {text_color.name()};
                    font-family: "{title_family}";
                    font-size: {title_size}px;
                    font-weight: {title_weight};
                }}
                QPushButton {{
                    background: transparent;
                    border: none;
                    color: {text_color.name()};
                    font-family: "{header_family}";
                    font-size: {header_size}px;
                    font-weight: {header_weight};
                    border-radius: 0px;
                    /* 图标居中 */
                }}
                QPushButton:hover {{
                    background-color: {close_hover.name()};
                    color: white;
                }}
                /* 有图标的按钮样式 */
                QPushButton[no-text="true"] {{
                    padding: 0px;
                }}
                QPushButton#titlebar_close_btn {{
                    padding: 0px;
                }}
            """

            # Cache the stylesheet
            self._stylesheet_cache[cache_key] = stylesheet

        # Apply cached stylesheet
        self.setStyleSheet(self._stylesheet_cache[cache_key])

        # Force style refresh
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
        logger.debug("TitleBar style applied")

    def setTitle(self, title: str) -> None:
        """Set window title.

        Args:
            title: Window title text
        """
        self.title_label.setText(title)

    def setIcon(self, icon: QIcon) -> None:
        """Set window icon.

        Args:
            icon: QIcon to display in title bar
        """
        self._icon = icon
        self.icon_label.setPixmap(icon.pixmap(24, 24))

    def setWindow(self, window: 'FramelessWindow') -> None:
        """Set reference to parent window."""
        self._window = window
        # Connect button signals
        self.minimize_btn.clicked.connect(window.showMinimized)
        self.maximize_btn.clicked.connect(self._toggle_maximize)
        self.close_btn.clicked.connect(window.close)

    def _is_on_top_edge(self, pos: QPoint) -> bool:
        """Check if position is on top edge for resize detection.

        Args:
            pos: Local position within the title bar

        Returns:
            True if y position is within edge margin
        """
        margin = self._edge_margin
        return pos.y() <= margin

    def mousePressEvent(self, event):
        """Handle mouse press for window dragging."""
        if event.button() != Qt.MouseButton.LeftButton:
            return
            
        # 优先检查是否在调整大小边缘
        local_pos = event.position()
        if local_pos and self._is_on_top_edge(local_pos.toPoint()):
            event.ignore()
            return
            
        # 检查窗口是否正在调整大小
        if self._window and getattr(self._window, '_resizing', False):
            event.ignore()
            return
            
        # 开始拖拽
        self._dragging = True
        pos = event.globalPosition()
        self._drag_position = pos.toPoint() if pos else QPoint()

    def mouseMoveEvent(self, event):
        """Handle mouse move for window dragging."""
        # 不在拖拽状态或不是左键按下时不处理
        if not self._dragging or event.buttons() != Qt.MouseButton.LeftButton:
            return
            
        # 检查窗口状态
        if not self._window or self._window.isMaximized():
            return
            
        # 执行窗口移动
        pos = event.globalPosition()
        if pos:
            current_pos = pos.toPoint()
            delta = current_pos - self._drag_position
            new_pos = self._window.pos() + delta
            self._window.move(new_pos)
            self._drag_position = current_pos

    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False

    def mouseDoubleClickEvent(self, event):
        """Handle double-click to toggle maximize."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._toggle_maximize()

    def cleanup(self):
        """Clean up resources and unsubscribe from events."""
        # Unsubscribe from theme manager to prevent memory leaks
        if hasattr(self, '_theme_mgr') and self._theme_mgr:
            self._theme_mgr.unsubscribe(self)
            # 不要将_theme_mgr设为None，保持引用以便后续安全访问

        # Clear window reference
        self._window = None


class FramelessWindow(QWidget):
    """
    Modern frameless window with custom title bar.

    Features:
    - Frameless window with custom chrome
    - Custom title bar with window controls
    - Window dragging via title bar
    - Edge resizing
    - Theme integration
    - Maximize/Restore support
    - Platform-specific features (Windows 11 rounded corners, etc.)

    Attributes:
        title_bar: TitleBar instance for window controls
        content_container: Main container widget
        content_widget: Content area for user widgets
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        # Get platform instance for platform-specific operations
        self._platform = get_platform_instance()

        # Get icon manager for default icons
        self._icon_mgr = IconManager.instance()

        # Set frameless window flags
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowMinMaxButtonsHint
        )

        # Initialize state using config constants
        self._press_pos = QPoint()
        self._geometry = None
        self._edge = 'none'
        self._edge_margin = WindowConfig.DEFAULT_EDGE_MARGIN
        self._resizing = False
        self._theme = None
        self._last_cursor = None
        self._is_maximized = False
        self._saved_geometry = None

        # Edge detection cache
        self._edge_cache: Dict[Tuple[int, int], str] = {}
        self._cache_window_size: Optional[Tuple[int, int]] = None

        # Stylesheet cache
        self._stylesheet_cache: Dict[Tuple[Any, ...], str] = {}

        # Event filter throttling
        self._last_event_filter_time = 0
        self._event_filter_threshold = WindowConfig.EVENT_FILTER_THRESHOLD_MS

        # Enable mouse tracking
        self.setMouseTracking(True)

        # Initialize UI
        self._init_ui()

        # Install event filters on child widgets
        self._install_event_filters()
        self._install_event_filter_recursive(self)

        # Subscribe to theme changes
        ThemeManager.instance().subscribe(self, self._on_theme_changed)
        # 立即应用当前主题，确保初始化时就有正确的样式
        current_theme = ThemeManager.instance().current_theme()
        if current_theme:
            self._on_theme_changed(current_theme)

    def _set_default_icon(self) -> None:
        """Set default window icon from IconManager."""
        try:
            # Get default icon from IconManager
            icon = self._icon_mgr.get_icon('default_window_icon', 24)
            if not icon.isNull():
                self.setWindowIcon(icon)
                logger.info("Default window icon set successfully")
            else:
                logger.warning("Failed to load default window icon")
        except Exception as e:
            logger.error(f"Error setting default window icon: {e}")

    def _init_ui(self):
        """Initialize window UI."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Content container
        self.content_container = QWidget()
        self.content_container.setObjectName("contentContainer")
        self.content_container.setMouseTracking(True)
        main_layout.addWidget(self.content_container)

        # Container layout
        container_layout = QVBoxLayout(self.content_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # Title bar
        self.title_bar = TitleBar(self)
        self.title_bar.setWindow(self)
        container_layout.addWidget(self.title_bar)

        # Set default window icon
        self._set_default_icon()

        # Content widget
        self.content_widget = QWidget()
        self.content_widget.setObjectName("contentWidget")
        self.content_widget.setMouseTracking(True)
        container_layout.addWidget(self.content_widget)

    def _install_event_filters(self):
        """Install event filters on all child widgets."""
        widgets = [self.content_container, self.title_bar, self.content_widget]
        for widget in widgets:
            if widget:
                widget.installEventFilter(self)

    def _install_event_filter_recursive(self, widget):
        """Recursively install event filter on widget and its children."""
        if widget is None:
            return
        widget.installEventFilter(self)
        for child in widget.findChildren(QWidget):
            if child is not widget:
                child.installEventFilter(self)

    def _is_on_resize_edge(self, pos: QPoint, widget: Optional[QWidget] = None) -> bool:
        """Check if position is on a resize edge.

        Args:
            pos: Local position relative to the widget
            widget: The widget to check (if None, use self)

        Returns:
            True if on resize edge, False otherwise
        """
        """Check if position is on a resize edge.

        Args:
            pos: Local position relative to the widget
            widget: The widget to check (if None, use self)

        Returns:
            True if on resize edge, False otherwise
        """
        if widget is None:
            widget = self

        margin = self._edge_margin
        w = widget.width()
        h = widget.height()

        return (
            pos.x() <= margin or
            pos.x() >= w - margin or
            pos.y() <= margin or
            pos.y() >= h - margin
        )

    def setEdgeMargin(self, margin: int) -> None:
        """Set edge margin for resize detection.

        Args:
            margin: Edge margin in pixels
        """
        self._edge_margin = margin

    def _get_resize_edge(self, pos: QPoint) -> str:
        """Detect which edge mouse is on with caching support."""
        # Clear cache if window size changed
        current_size = (self.width(), self.height())
        if self._cache_window_size != current_size:
            self._edge_cache.clear()
            self._cache_window_size = current_size

        # Check cache
        cache_key = (pos.x(), pos.y())
        if cache_key in self._edge_cache:
            return self._edge_cache[cache_key]

        # Calculate edge
        margin = self._edge_margin
        w, h = current_size

        # Guard against invalid window dimensions
        if w <= 0 or h <= 0:
            return 'none'

        # Check for corner edges first
        edge = []
        if pos.y() < margin:
            edge.append('top')
        elif pos.y() > h - margin:
            edge.append('bottom')

        if pos.x() < margin:
            edge.append('left')
        elif pos.x() > w - margin:
            edge.append('right')

        result = '-'.join(edge) if edge else 'none'

        # Cache the result (limit cache size to prevent memory bloat)
        if len(self._edge_cache) < WindowConfig.MAX_EDGE_CACHE_SIZE:
            self._edge_cache[cache_key] = result

        return result

    def _update_cursor(self, edge: str) -> None:
        """Update cursor shape based on edge.

        Args:
            edge: Edge identifier (e.g., 'top', 'left', 'top-left', 'none')
        """
        new_cursor = WindowConfig.CURSOR_MAP.get(edge, Qt.CursorShape.ArrowCursor)
        if new_cursor != self._last_cursor:
            self.setCursor(new_cursor)
            self._last_cursor = new_cursor

    def _resize_window(self, global_pos: QPoint) -> None:
        """Resize window based on mouse movement during resize operation.

        Args:
            global_pos: Current global mouse position
        """
        """Resize window based on mouse movement."""
        try:
            if self._geometry is None:
                return

            delta = global_pos - self._press_pos
            geo = self._geometry

            # Minimum size constraints
            min_w = WindowConfig.MIN_WINDOW_WIDTH
            min_h = WindowConfig.MIN_WINDOW_HEIGHT

            # Get current window geometry
            current_geo = self.geometry()
            current_w = current_geo.width()
            current_h = current_geo.height()

            # CRITICAL: Check if already at minimum size and trying to shrink further
            # This prevents window movement when at minimum size
            if 'top' in self._edge or 'bottom' in self._edge:
                if current_h <= min_h:
                    # Already at minimum height, check if trying to shrink
                    if ('top' in self._edge and delta.y() > 0) or \
                       ('bottom' in self._edge and delta.y() < 0):
                        return  # Trying to shrink beyond minimum, stop completely

            if 'left' in self._edge or 'right' in self._edge:
                if current_w <= min_w:
                    # Already at minimum width, check if trying to shrink
                    if ('left' in self._edge and delta.x() > 0) or \
                       ('right' in self._edge and delta.x() < 0):
                        return  # Trying to shrink beyond minimum, stop completely

            # Calculate new boundaries
            new_left = geo.left()
            new_top = geo.top()
            new_right = geo.right()
            new_bottom = geo.bottom()

            # Apply edge-specific resizing with minimum size enforcement
            if 'top' in self._edge:
                new_top = geo.top() + delta.y()
                if geo.bottom() - new_top < min_h:
                    new_top = geo.bottom() - min_h
            if 'bottom' in self._edge:
                new_bottom = geo.bottom() + delta.y()
                if new_bottom - geo.top() < min_h:
                    new_bottom = geo.top() + min_h
            if 'left' in self._edge:
                new_left = geo.left() + delta.x()
                if geo.right() - new_left < min_w:
                    new_left = geo.right() - min_w
            if 'right' in self._edge:
                new_right = geo.right() + delta.x()
                if new_right - geo.left() < min_w:
                    new_right = geo.left() + min_w

            # CRITICAL: Only apply geometry change if it would actually modify the window
            # This prevents spurious position changes when at minimum size
            if (new_left != geo.left() or new_top != geo.top() or
                new_right != geo.right() or new_bottom != geo.bottom()):
                self.setGeometry(new_left, new_top, new_right - new_left, new_bottom - new_top)
        except Exception as e:
            logger.error(f"_resize_window error: {e}")

    def mousePressEvent(self, event):
        """Handle mouse press for resizing."""
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                pos = event.globalPosition()
                if pos is None:
                    return

                self._press_pos = pos.toPoint()
                self._geometry = self.frameGeometry()

                local_pos = event.position()
                if local_pos is None:
                    return

                self._edge = self._get_resize_edge(local_pos.toPoint())
                if self._edge != 'none':
                    self._resizing = True
                    # Stop TitleBar from handling drag when resizing
                    if hasattr(self, 'title_bar'):
                        self.title_bar._dragging = False
                    # Grab mouse to ensure we receive all mouse events
                    try:
                        self.grabMouse()
                    except Exception as grab_error:
                        logger.warning(f"Failed to grab mouse: {grab_error}")
                        # Ensure mouse is released if grab fails
                        self.releaseMouse()
                    event.accept()
        except Exception as e:
            logger.error(f"mousePressEvent error: {e}")

    def mouseMoveEvent(self, event):
        """Handle mouse move for cursor update and resizing."""
        try:
            if not self._resizing:
                # Update cursor
                pos = event.position()
                if pos is not None:
                    edge = self._get_resize_edge(pos.toPoint())
                    self._update_cursor(edge)
            elif event.buttons() == Qt.MouseButton.LeftButton:
                # Resize window
                global_pos = event.globalPosition()
                if global_pos is not None:
                    self._resize_window(global_pos.toPoint())
        except Exception as e:
            logger.error(f"mouseMoveEvent error: {e}")

    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._resizing = False
            self._edge = 'none'

            # Release mouse grab
            self.releaseMouse()

            # CRITICAL: Ensure TitleBar dragging state is reset
            if hasattr(self, 'title_bar') and self.title_bar:
                self.title_bar._dragging = False

            # Reset cursor to current edge state after resize
            try:
                pos = event.position()
                if pos is not None:
                    edge = self._get_resize_edge(pos.toPoint())
                    self._update_cursor(edge)
            except Exception:
                pass

    def eventFilter(self, obj, event):
        """Event filter to capture mouse events from child widgets with throttling."""
        try:
            # Only process mouse move events from child widgets
            if obj is self:
                return False

            # Don't process if currently resizing
            if self._resizing:
                return False

            if event.type() == QEvent.Type.MouseMove:
                # Don't update cursor if title bar is being dragged
                if hasattr(self, 'title_bar') and self.title_bar._dragging:
                    return False

                # Throttle event processing to reduce CPU usage
                current_time = time.time() * 1000  # Convert to milliseconds
                if current_time - self._last_event_filter_time < self._event_filter_threshold:
                    return False
                self._last_event_filter_time = current_time

                # Get global mouse position directly
                pos = event.globalPosition()
                if pos is None:
                    return False

                global_pos = pos.toPoint()
                window_pos = self.mapFromGlobal(global_pos)

                # Quick bounds check before expensive calculations
                w, h = self.width(), self.height()
                if not (0 <= window_pos.x() <= w and 0 <= window_pos.y() <= h):
                    return False

                # Only process if near edges (optimization)
                margin = self._edge_margin * 2  # Use larger margin for early detection
                if not (window_pos.x() < margin or window_pos.x() > w - margin or
                        window_pos.y() < margin or window_pos.y() > h - margin):
                    # Not near any edge, reset cursor once
                    if self._last_cursor != Qt.CursorShape.ArrowCursor:
                        self.setCursor(Qt.CursorShape.ArrowCursor)
                        self._last_cursor = Qt.CursorShape.ArrowCursor
                    return False

                # Process edge detection
                edge = self._get_resize_edge(window_pos)
                self._update_cursor(edge)
        except Exception as e:
            logger.debug(f"Event filter error: {e}", exc_info=True)
        return False

    def changeEvent(self, event):
        """Handle window state changes (maximize/restore)."""
        # Clear edge cache on resize
        if event.type() == QEvent.Type.Resize:
            self._edge_cache.clear()

        if event.type() == QEvent.Type.WindowStateChange:
            is_now_maximized = self.isMaximized()

            # Only process if state actually changed
            if is_now_maximized != self._is_maximized:
                self._is_maximized = is_now_maximized

                # Update maximize button icon
                if hasattr(self, 'title_bar'):
                    self.title_bar._update_maximize_icon_state()

                # Handle platform-specific corner preference
                hwnd = int(self.winId())
                if is_now_maximized:
                    # Disable rounded corners when maximized
                    self._platform.set_corner_preference(hwnd, rounded=False)
                else:
                    # Re-enable rounded corners when restored
                    self._platform.set_corner_preference(hwnd, rounded=True)

                # Handle geometry
                if is_now_maximized and not self._saved_geometry:
                    # External maximize, save geometry
                    self._saved_geometry = self.normalGeometry()

                    # Platform-specific maximization adjustment
                    QTimer.singleShot(0, self._adjust_maximized_geometry)

                # Reapply theme to update borders and radius
                if self._theme:
                    self._apply_theme(self._theme)
                    # 标题栏主题会在_on_theme_changed中统一处理

    def _adjust_maximized_geometry(self):
        """Adjust window geometry when maximized to fill screen using platform-specific implementation."""
        if self._is_maximized:
            hwnd = int(self.winId())
            self._platform.maximize_window(hwnd)


    def _on_theme_changed(self, theme: Theme) -> None:
        """Handle theme change notification.

        Args:
            theme: New theme to apply
        """
        try:
            self._apply_theme(theme)
            # TitleBar now subscribes to theme changes itself
        except Exception as e:
            logger.error(f"Error applying theme to FramelessWindow: {e}")
            import traceback
            traceback.print_exc()

    def _apply_theme(self, theme: Theme) -> None:
        """Apply theme to window with optimized style refresh.

        Args:
            theme: Theme object containing color and style definitions
        """
        logger.debug(f"FramelessWindow._apply_theme called with theme: {theme.name if hasattr(theme, 'name') else 'unknown'}")

        if not theme:
            logger.debug("Theme is None, returning")
            return

        self._theme = theme
        bg_color = theme.get_color('window.background', WindowConfig.DEFAULT_WINDOW_BG_COLOR)
        border_color = theme.get_color('window.border', WindowConfig.DEFAULT_BORDER_COLOR)

        logger.debug(f"Background color: {bg_color.name()}, Border color: {border_color.name()}, Is maximized: {self._is_maximized}")

        # Create cache key
        cache_key = (
            bg_color.name(),
            border_color.name(),
            self._is_maximized,
            sys.platform == 'win32'
        )

        # Check cache
        if cache_key in self._stylesheet_cache:
            qss = self._stylesheet_cache[cache_key]
        else:
            # Build stylesheet
            if self._is_maximized:
                border_radius = 0
                border_css = "border: none;"
            elif sys.platform == 'win32' and not self._is_maximized:
                # Windows 11: let system handle rounded corners
                border_radius = 0
                border_css = f"border: 1px solid {border_color.name()};"
            else:
                # Other platforms: use CSS border-radius
                border_radius = theme.get_value('window.border_radius', 10)
                border_css = f"border: 1px solid {border_color.name()};"

            # Set object name for CSS selector
            self.setObjectName("FramelessWindow")

            qss = f"""
                #{self.objectName()} {{
                    background-color: {bg_color.name()};
                    {border_css}
                    border-radius: {border_radius}px;
                }}
            """

            # Cache the stylesheet
            self._stylesheet_cache[cache_key] = qss

        # Apply style to main window
        self.setStyleSheet(qss)

        # Apply background to key containers only (not all children)
        bg_style = f"background-color: {bg_color.name()};"

        if hasattr(self, 'content_container'):
            self.content_container.setStyleSheet(bg_style)

        if hasattr(self, 'content_widget'):
            self.content_widget.setStyleSheet(bg_style)

        # Optimized refresh: only refresh main window and immediate children
        # Qt's setStyleSheet automatically propagates to children
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

        logger.debug("Stylesheet applied to main window")

    def setWindowTitle(self, title: str) -> None:
        """Set window title (QWidget standard interface).

        This method overrides QWidget's setWindowTitle to also update the title bar.

        Args:
            title: Window title text
        """
        super().setWindowTitle(title)
        self.title_bar.setTitle(title)

    def setTitle(self, title: str) -> None:
        """Set window title (convenience method, alias for setWindowTitle).

        Args:
            title: Window title text
        """
        self.setWindowTitle(title)

    def setWindowIcon(self, icon: QIcon) -> None:
        """Set window icon.

        Args:
            icon: QIcon to display
        """
        super().setWindowIcon(icon)
        self.title_bar.setIcon(icon)

    def setMinimizeButtonVisible(self, visible: bool) -> None:
        """Set minimize button visibility.

        Args:
            visible: True to show the minimize button, False to hide it
        """
        if hasattr(self, 'title_bar') and self.title_bar:
            self.title_bar.minimize_btn.setVisible(visible)

    def setMaximizeButtonVisible(self, visible: bool) -> None:
        """Set maximize button visibility.

        Args:
            visible: True to show the maximize button, False to hide it
        """
        if hasattr(self, 'title_bar') and self.title_bar:
            self.title_bar.maximize_btn.setVisible(visible)

    def setCloseButtonVisible(self, visible: bool) -> None:
        """Set close button visibility.

        Args:
            visible: True to show the close button, False to hide it
        """
        if hasattr(self, 'title_bar') and self.title_bar:
            self.title_bar.close_btn.setVisible(visible)

    def setMinimizeButtonEnabled(self, enabled: bool) -> None:
        """Set minimize button enabled state.

        Args:
            enabled: True to enable the minimize button, False to disable it
        """
        if hasattr(self, 'title_bar') and self.title_bar:
            self.title_bar.minimize_btn.setEnabled(enabled)

    def setMaximizeButtonEnabled(self, enabled: bool) -> None:
        """Set maximize button enabled state.

        Args:
            enabled: True to enable the maximize button, False to disable it
        """
        if hasattr(self, 'title_bar') and self.title_bar:
            self.title_bar.maximize_btn.setEnabled(enabled)

    def setCloseButtonEnabled(self, enabled: bool) -> None:
        """Set close button enabled state.

        Args:
            enabled: True to enable the close button, False to disable it
        """
        if hasattr(self, 'title_bar') and self.title_bar:
            self.title_bar.close_btn.setEnabled(enabled)

    def titleBar(self) -> Optional['TitleBar']:
        """Get the title bar widget.

        Returns:
            TitleBar instance or None if not initialized
        """
        return self.title_bar if hasattr(self, 'title_bar') else None

    def setCentralWidget(self, widget: QWidget) -> None:
        """Set central content widget (QMainWindow-style).

        Args:
            widget: Widget to set as the central content

        Note:
            This clears any existing layout and widgets.
        """
        # Clear existing content
        layout = self.content_widget.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                child_widget = item.widget()
                if child_widget:
                    child_widget.deleteLater()

        # Add new widget
        new_layout = QVBoxLayout(self.content_widget)
        new_layout.setContentsMargins(
            WindowConfig.CONTENT_MARGIN,
            WindowConfig.CONTENT_MARGIN,
            WindowConfig.CONTENT_MARGIN,
            WindowConfig.CONTENT_MARGIN
        )
        new_layout.addWidget(widget)

    def getCentralWidget(self) -> Optional[QWidget]:
        """Get central content widget.

        Returns:
            The central widget or None if not set
        """
        layout = self.content_widget.layout()
        if layout and layout.count() > 0:
            return layout.itemAt(0).widget()
        return None

    def getContentWidget(self) -> QWidget:
        """Get content widget container.

        Returns:
            The content widget container
        """
        return self.content_widget

    def setLayout(self, layout: QLayout) -> None:
        """Set layout for the content area (QWidget-style).

        This allows FramelessWindow to be used just like QWidget:

            window = FramelessWindow()
            layout = QVBoxLayout()
            layout.addWidget(widget1)
            layout.addWidget(widget2)
            window.setLayout(layout)

        Args:
            layout: Layout to apply to the content area
        """
        # Clear existing layout
        existing_layout = self.content_widget.layout()
        if existing_layout:
            # Transfer parent to new layout
            layout.setParent(self.content_widget)

            # Move items from old layout to new layout
            while existing_layout.count():
                item = existing_layout.takeAt(0)
                if item.widget():
                    layout.addWidget(item.widget())
                elif item.layout():
                    layout.addItem(item)

            # Delete old layout
            existing_layout.setParent(None)
            del existing_layout

        # Apply margins and set new layout
        layout.setContentsMargins(
            WindowConfig.CONTENT_MARGIN,
            WindowConfig.CONTENT_MARGIN,
            WindowConfig.CONTENT_MARGIN,
            WindowConfig.CONTENT_MARGIN
        )
        self.content_widget.setLayout(layout)

    def addWidget(self, widget: QWidget) -> None:
        """Convenience method to add a widget to the content area.

        Creates a QVBoxLayout if one doesn't exist and adds the widget.

        Args:
            widget: Widget to add

        Example:
            window = FramelessWindow()
            window.addWidget(label1)
            window.addWidget(button1)
        """
        layout = self.content_widget.layout()

        # Create layout if it doesn't exist
        if layout is None:
            layout = QVBoxLayout(self.content_widget)
            layout.setContentsMargins(
                WindowConfig.CONTENT_MARGIN,
                WindowConfig.CONTENT_MARGIN,
                WindowConfig.CONTENT_MARGIN,
                WindowConfig.CONTENT_MARGIN
            )

        layout.addWidget(widget)

    def addLayout(self, layout: QLayout) -> None:
        """Convenience method to add a sub-layout to the content area.

        Args:
            layout: Layout to add

        Example:
            window = FramelessWindow()
            main_layout = window.contentLayout
            sub_layout = QHBoxLayout()
            sub_layout.addWidget(button1)
            sub_layout.addWidget(button2)
            main_layout.addLayout(sub_layout)
        """
        parent_layout = self.content_widget.layout()

        # Create layout if it doesn't exist
        if parent_layout is None:
            parent_layout = QVBoxLayout(self.content_widget)
            parent_layout.setContentsMargins(
                WindowConfig.CONTENT_MARGIN,
                WindowConfig.CONTENT_MARGIN,
                WindowConfig.CONTENT_MARGIN,
                WindowConfig.CONTENT_MARGIN
            )

        parent_layout.addLayout(layout)

    @property
    def contentLayout(self) -> Optional[QLayout]:
        """Get the layout of the content area.

        Returns:
            The content area's layout or None if not set

        Example:
            window = FramelessWindow()
            window.contentLayout.addWidget(widget)
        """
        return self.content_widget.layout()

    @contentLayout.setter
    def contentLayout(self, layout: QLayout) -> None:
        """Set the layout of the content area.

        Args:
            layout: Layout to apply

        Example:
            window = FramelessWindow()
            window.contentLayout = QVBoxLayout()
        """
        self.setLayout(layout)

    def showEvent(self, event):
        """Handle show event to enable platform-specific window features."""
        super().showEvent(event)
        if event.isAccepted():
            # Apply initial theme
            if not self._theme:
                current_theme = ThemeManager.instance().current_theme()
                if current_theme:
                    self._on_theme_changed(current_theme)

            # Enable platform-specific features (e.g., rounded corners on Windows 11)
            hwnd = int(self.winId())
            self._platform.set_corner_preference(hwnd, rounded=True)

    def closeEvent(self, event):
        """Handle close event."""
        # Save window state before closing
        if hasattr(self, 'title_bar'):
            self.title_bar._window = None
            # Critical: Call cleanup to unsubscribe from theme manager
            self.title_bar.cleanup()

        # Unsubscribe self from theme manager
        ThemeManager.instance().unsubscribe(self)

        super().closeEvent(event)
