"""
SimpleMediaPlayBar Component

A simple media playback control bar with play/pause button,
progress slider, and volume control.

Features:
- Play/Pause toggle button
- Progress slider with time display
- Volume control with mute toggle
- Theme integration
- Fluent design style
- Unified ThemedComponentBase base class

Reference: https://github.com/zhiyiYo/PyQt-Fluent-Widgets
"""

from typing import Optional, Any, Tuple
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSlider,
    QSizePolicy, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QTime, QTimer, QSize
from PyQt6.QtGui import QColor, QIcon

from core.themed_component_base import ThemedComponentBase
from core.style_override import StyleOverrideMixin
from core.stylesheet_cache_mixin import StylesheetCacheMixin
from core.theme_manager import ThemeManager
from components.buttons.tool_button import ToolButton


class MediaPlayButton(ToolButton):
    """Play/Pause toggle button with icon switching."""
    
    playToggled = pyqtSignal(bool)
    
    def __init__(self, parent: Optional[QWidget] = None):
        self._is_playing = False
        
        super().__init__(parent)
        self._update_play_icon()
    
    def _apply_theme(self, theme: Optional[Any] = None) -> None:
        self._update_play_icon()
    
    def _update_play_icon(self) -> None:
        is_dark = True
        if self._theme:
            is_dark = self._theme.is_dark
        suffix = '_white' if is_dark else '_black'
        
        icon_name = f'Pause{suffix}' if self._is_playing else f'Play{suffix}'
        self.setIconSource(icon_name)
    
    def isPlaying(self) -> bool:
        return self._is_playing
    
    def setPlaying(self, playing: bool) -> None:
        if self._is_playing != playing:
            self._is_playing = playing
            self._update_play_icon()
            self.playToggled.emit(playing)
    
    def toggle(self) -> None:
        self.setPlaying(not self._is_playing)
    
    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle()
        super().mouseReleaseEvent(event)


class VolumeButton(ToolButton):
    """Volume button with mute toggle and volume slider popup."""
    
    volumeChanged = pyqtSignal(int)
    muteToggled = pyqtSignal(bool)
    
    def __init__(self, parent: Optional[QWidget] = None):
        self._volume = 100
        self._is_muted = False
        
        super().__init__(parent)
        self._update_volume_icon()
    
    def _apply_theme(self, theme: Optional[Any] = None) -> None:
        self._update_volume_icon()
    
    def _update_volume_icon(self) -> None:
        is_dark = True
        if self._theme:
            is_dark = self._theme.is_dark
        suffix = '_white' if is_dark else '_black'
        
        if self._is_muted or self._volume == 0:
            icon_name = f'Mute{suffix}'
        else:
            icon_name = f'Speakers{suffix}'
        self.setIconSource(icon_name)
    
    def volume(self) -> int:
        return self._volume
    
    def setVolume(self, volume: int) -> None:
        volume = max(0, min(100, volume))
        if self._volume != volume:
            self._volume = volume
            self._update_volume_icon()
            self.volumeChanged.emit(volume)
    
    def isMuted(self) -> bool:
        return self._is_muted
    
    def setMuted(self, muted: bool) -> None:
        if self._is_muted != muted:
            self._is_muted = muted
            self._update_volume_icon()
            self.muteToggled.emit(muted)
    
    def toggleMute(self) -> None:
        self.setMuted(not self._is_muted)
    
    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggleMute()
        super().mouseReleaseEvent(event)


class TimeLabel(QLabel, StyleOverrideMixin, StylesheetCacheMixin):
    """Time display label for media playback."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._init_style_override()
        self._init_stylesheet_cache()
        
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Any] = None
        
        self._setup_ui()
        
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._current_theme = initial_theme
            self._apply_theme(initial_theme)
    
    def _setup_ui(self) -> None:
        self.setText("00:00")
        self.setMinimumWidth(45)
    
    def _on_theme_changed(self, theme: Any) -> None:
        self._current_theme = theme
        self._apply_theme(theme)
    
    def _apply_theme(self, theme: Optional[Any] = None) -> None:
        color = self.get_style_color(self._current_theme, 'mediabar.text', QColor(180, 180, 180))
        self.setStyleSheet(f"color: {color.name()}; background: transparent; font-size: 12px;")
    
    def setTime(self, seconds: int) -> None:
        minutes = seconds // 60
        secs = seconds % 60
        self.setText(f"{minutes:02d}:{secs:02d}")
    
    def cleanup(self) -> None:
        self._theme_mgr.unsubscribe(self)
        self._clear_stylesheet_cache()
        self.clear_overrides()


class SimpleMediaPlayBar(QWidget, StyleOverrideMixin, StylesheetCacheMixin):
    """
    Simple media playback control bar.
    
    A fluent design style media control bar with:
    - Play/Pause button
    - Progress slider with time display
    - Volume control button
    - Style override support
    - Stylesheet caching
    """
    
    playToggled = pyqtSignal(bool)
    positionChanged = pyqtSignal(int)
    volumeChanged = pyqtSignal(int)
    muteToggled = pyqtSignal(bool)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._init_style_override()
        self._init_stylesheet_cache()
        
        self._theme_mgr = ThemeManager.instance()
        self._current_theme: Optional[Any] = None
        self._duration = 0
        self._position = 0
        
        self._setup_ui()
        self._connect_signals()
        self._theme_mgr.subscribe(self, self._on_theme_changed)
        
        initial_theme = self._theme_mgr.current_theme()
        if initial_theme:
            self._current_theme = initial_theme
            self._apply_theme(initial_theme)
    
    def _setup_ui(self) -> None:
        self.setFixedHeight(48)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        self._main_layout = QHBoxLayout(self)
        self._main_layout.setContentsMargins(12, 8, 12, 8)
        self._main_layout.setSpacing(8)
        
        self._play_button = MediaPlayButton()
        self._play_button.setFixedSize(32, 32)
        self._play_button.setIconSize(QSize(16, 16))
        
        self._current_time = TimeLabel()
        
        self._progress_slider = QSlider(Qt.Orientation.Horizontal)
        self._progress_slider.setRange(0, 1000)
        self._progress_slider.setValue(0)
        self._progress_slider.setFixedHeight(20)
        self._progress_slider.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self._total_time = TimeLabel()
        
        self._volume_button = VolumeButton()
        self._volume_button.setFixedSize(32, 32)
        self._volume_button.setIconSize(QSize(16, 16))
        
        self._volume_slider = QSlider(Qt.Orientation.Horizontal)
        self._volume_slider.setRange(0, 100)
        self._volume_slider.setValue(100)
        self._volume_slider.setFixedWidth(80)
        self._volume_slider.setFixedHeight(20)
        self._volume_slider.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self._main_layout.addWidget(self._play_button)
        self._main_layout.addWidget(self._current_time)
        self._main_layout.addWidget(self._progress_slider, 1)
        self._main_layout.addWidget(self._total_time)
        self._main_layout.addWidget(self._volume_button)
        self._main_layout.addWidget(self._volume_slider)
    
    def _connect_signals(self) -> None:
        self._play_button.playToggled.connect(self.playToggled.emit)
        self._play_button.playToggled.connect(self._on_play_toggled)
        
        self._progress_slider.valueChanged.connect(self._on_progress_changed)
        self._progress_slider.sliderMoved.connect(self._on_slider_moved)
        
        self._volume_button.volumeChanged.connect(self.volumeChanged.emit)
        self._volume_button.muteToggled.connect(self.muteToggled.emit)
        
        self._volume_slider.valueChanged.connect(self._on_volume_slider_changed)
    
    def _on_theme_changed(self, theme: Any) -> None:
        self._current_theme = theme
        self._apply_theme(theme)
    
    def _apply_theme(self, theme: Optional[Any] = None) -> None:
        bg_color = self.get_style_color(self._current_theme, 'mediabar.background', QColor(45, 45, 45))
        groove_color = self.get_style_color(self._current_theme, 'mediabar.groove', QColor(60, 60, 60))
        filled_color = self.get_style_color(self._current_theme, 'mediabar.filled', QColor(0, 120, 212))
        handle_color = self.get_style_color(self._current_theme, 'mediabar.handle', QColor(255, 255, 255))
        
        slider_cache_key: Tuple[str, str, str, str] = (
            groove_color.name(),
            filled_color.name(),
            handle_color.name(),
            'slider'
        )
        
        def build_slider_stylesheet() -> str:
            return f"""
                QSlider {{
                    background: transparent;
                }}
                QSlider::groove:horizontal {{
                    height: 4px;
                    background: {groove_color.name()};
                    border-radius: 2px;
                }}
                QSlider::sub-page:horizontal {{
                    background: {filled_color.name()};
                    border-radius: 2px;
                }}
                QSlider::add-page:horizontal {{
                    background: {groove_color.name()};
                    border-radius: 2px;
                }}
                QSlider::handle:horizontal {{
                    background: {handle_color.name()};
                    width: 12px;
                    height: 12px;
                    margin: -4px 0;
                    border-radius: 6px;
                }}
                QSlider::handle:horizontal:hover {{
                    background: {filled_color.name()};
                }}
            """
        
        slider_style = self._get_cached_stylesheet(slider_cache_key, build_slider_stylesheet)
        
        self._progress_slider.setStyleSheet(slider_style)
        self._volume_slider.setStyleSheet(slider_style)
        
        bar_cache_key: Tuple[str] = (bg_color.name(),)
        
        def build_bar_stylesheet() -> str:
            return f"""
                SimpleMediaPlayBar {{
                    background: {bg_color.name()};
                    border-radius: 8px;
                }}
            """
        
        bar_style = self._get_cached_stylesheet(bar_cache_key, build_bar_stylesheet)
        self.setStyleSheet(bar_style)
    
    def _on_play_toggled(self, playing: bool) -> None:
        pass
    
    def _on_progress_changed(self, value: int) -> None:
        if self._duration > 0:
            position = int(value * self._duration / 1000)
            if position != self._position:
                self._position = position
                self._current_time.setTime(position)
                self.positionChanged.emit(position)
    
    def _on_slider_moved(self, value: int) -> None:
        if self._duration > 0:
            position = int(value * self._duration / 1000)
            self._position = position
            self._current_time.setTime(position)
    
    def _on_volume_slider_changed(self, value: int) -> None:
        self._volume_button.setVolume(value)
    
    def setDuration(self, seconds: int) -> None:
        self._duration = max(0, seconds)
        self._total_time.setTime(self._duration)
    
    def duration(self) -> int:
        return self._duration
    
    def setPosition(self, seconds: int) -> None:
        if self._duration > 0:
            self._position = max(0, min(seconds, self._duration))
            slider_value = int(self._position * 1000 / self._duration)
            self._progress_slider.blockSignals(True)
            self._progress_slider.setValue(slider_value)
            self._progress_slider.blockSignals(False)
            self._current_time.setTime(self._position)
    
    def position(self) -> int:
        return self._position
    
    def setVolume(self, volume: int) -> None:
        volume = max(0, min(100, volume))
        self._volume_slider.setValue(volume)
        self._volume_button.setVolume(volume)
    
    def volume(self) -> int:
        return self._volume_button.volume()
    
    def setMuted(self, muted: bool) -> None:
        self._volume_button.setMuted(muted)
    
    def isMuted(self) -> bool:
        return self._volume_button.isMuted()
    
    def isPlaying(self) -> bool:
        return self._play_button.isPlaying()
    
    def setPlaying(self, playing: bool) -> None:
        self._play_button.setPlaying(playing)
    
    def play(self) -> None:
        self.setPlaying(True)
    
    def pause(self) -> None:
        self.setPlaying(False)
    
    def cleanup(self) -> None:
        self._theme_mgr.unsubscribe(self)
        self._current_time.cleanup()
        self._play_button.cleanup()
        self._volume_button.cleanup()
        self._clear_stylesheet_cache()
        self.clear_overrides()
