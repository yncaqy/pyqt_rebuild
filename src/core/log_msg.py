#!/usr/bin/env python3
"""
Log Message Manager

提供完整的日志管理功能，集成 PyQt6 框架特性。

Features:
- 集中式日志管理（单例模式）
- 多级别日志记录（DEBUG, INFO, WARNING, ERROR, CRITICAL）
- 日志文件自动轮转和归档
- 实时日志监控和过滤
- 日志导出功能（支持多种格式）
- 性能优化的日志缓冲
- 线程安全的日志记录
- 与主题系统集成

Example:
    log_mgr = LogManager.instance()
    log_mgr.info("应用程序启动")
    log_mgr.error("发生错误", exc_info=True)

    # 获取日志记录器
    logger = log_mgr.get_logger("my_module")
    logger.debug("调试信息")

    # 导出日志
    log_mgr.export_logs("export.log")
"""

import json
import logging
import logging.handlers
import sys
import threading
from collections import deque
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Callable, Any, Tuple

from PyQt6.QtCore import QObject, pyqtSignal, QMutex, QMutexLocker


class LogLevel(Enum):
    """日志级别枚举"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


@dataclass
class LogEntry:
    """日志条目数据类"""
    timestamp: str
    level: str
    level_name: str
    logger_name: str
    message: str
    module: str
    function: str
    line: int
    thread: str
    process: int
    extra: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    def to_json(self) -> str:
        """转换为 JSON 字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class LogFilter:
    """日志过滤器"""

    def __init__(self):
        self._min_level: Optional[LogLevel] = None
        self._max_level: Optional[LogLevel] = None
        self._logger_names: Optional[List[str]] = None
        self._keywords: Optional[List[str]] = None
        self._time_range: Optional[Tuple[datetime, datetime]] = None
        self._custom_filter: Optional[Callable[[LogEntry], bool]] = None

    def set_level_range(self, min_level: Optional[LogLevel] = None,
                        max_level: Optional[LogLevel] = None) -> 'LogFilter':
        """设置日志级别范围"""
        self._min_level = min_level
        self._max_level = max_level
        return self

    def set_logger_names(self, names: List[str]) -> 'LogFilter':
        """设置日志记录器名称过滤"""
        self._logger_names = names
        return self

    def set_keywords(self, keywords: List[str]) -> 'LogFilter':
        """设置关键词过滤"""
        self._keywords = keywords
        return self

    def set_time_range(self, start: datetime, end: datetime) -> 'LogFilter':
        """设置时间范围过滤"""
        self._time_range = (start, end)
        return self

    def set_custom_filter(self, filter_func: Callable[[LogEntry], bool]) -> 'LogFilter':
        """设置自定义过滤函数"""
        self._custom_filter = filter_func
        return self

    def matches(self, entry: LogEntry) -> bool:
        """检查日志条目是否匹配过滤条件"""
        entry_level = LogLevel[entry.level]

        if self._min_level and entry_level.value < self._min_level.value:
            return False

        if self._max_level and entry_level.value > self._max_level.value:
            return False

        if self._logger_names and entry.logger_name not in self._logger_names:
            return False

        if self._keywords:
            if not any(keyword.lower() in entry.message.lower()
                      for keyword in self._keywords):
                return False

        if self._time_range:
            try:
                entry_time = datetime.fromisoformat(entry.timestamp)
                if not (self._time_range[0] <= entry_time <= self._time_range[1]):
                    return False
            except ValueError:
                return False

        if self._custom_filter and not self._custom_filter(entry):
            return False

        return True


class MemoryLogHandler(logging.Handler):
    """内存日志处理器，用于实时日志监控"""

    def __init__(self, max_entries: int = 1000):
        super().__init__()
        self._entries: deque = deque(maxlen=max_entries)
        self._mutex = QMutex()
        self._callbacks: List[Callable[[LogEntry], None]] = []

    def emit(self, record: logging.LogRecord) -> None:
        """处理日志记录"""
        try:
            entry = self._create_log_entry(record)

            with QMutexLocker(self._mutex):
                self._entries.append(entry)

            for callback in self._callbacks:
                try:
                    callback(entry)
                except Exception:
                    pass
        except Exception:
            self.handleError(record)

    def _create_log_entry(self, record: logging.LogRecord) -> LogEntry:
        """创建日志条目"""
        return LogEntry(
            timestamp=datetime.fromtimestamp(record.created).isoformat(),
            level=record.levelname,
            level_name=logging.getLevelName(record.levelno),
            logger_name=record.name,
            message=record.getMessage(),
            module=record.module,
            function=record.funcName,
            line=record.lineno,
            thread=record.threadName,
            process=record.process,
            extra=getattr(record, 'extra', None)
        )

    def get_entries(self, log_filter: Optional[LogFilter] = None) -> List[LogEntry]:
        """获取日志条目"""
        with QMutexLocker(self._mutex):
            entries = list(self._entries)

        if log_filter:
            entries = [e for e in entries if log_filter.matches(e)]

        return entries

    def clear(self) -> None:
        """清空日志条目"""
        with QMutexLocker(self._mutex):
            self._entries.clear()

    def add_callback(self, callback: Callable[[LogEntry], None]) -> None:
        """添加回调函数"""
        self._callbacks.append(callback)

    def remove_callback(self, callback: Callable[[LogEntry], None]) -> None:
        """移除回调函数"""
        if callback in self._callbacks:
            self._callbacks.remove(callback)


class LogManager(QObject):
    """
    日志管理器（单例模式）

    提供集中式日志管理功能，支持多级别日志记录、文件轮转、
    实时监控和日志导出等功能。

    Signals:
        log_entry_added: 当新日志条目添加时发出
        log_level_changed: 当日志级别改变时发出
    """

    _instance: Optional['LogManager'] = None
    _lock = threading.Lock()

    log_entry_added = pyqtSignal(LogEntry)
    log_level_changed = pyqtSignal(str)

    def __new__(cls) -> 'LogManager':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def instance(cls) -> 'LogManager':
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return

        super().__init__()

        self._log_dir: Path = Path('logs')
        self._current_level: LogLevel = LogLevel.INFO
        self._loggers: Dict[str, logging.Logger] = {}
        self._memory_handler: Optional[MemoryLogHandler] = None
        self._file_handler: Optional[logging.Handler] = None
        self._console_handler: Optional[logging.Handler] = None
        self._mutex = QMutex()
        self._initialized = True

        self._setup_logging()

    def _setup_logging(self) -> None:
        """设置日志系统"""
        self._log_dir.mkdir(exist_ok=True)

        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)

        root_logger.handlers.clear()

        self._setup_console_handler()
        self._setup_file_handler()
        self._setup_memory_handler()

    def _setup_console_handler(self) -> None:
        """设置控制台处理器"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self._current_level.value)
        console_handler.setFormatter(self._get_formatter())

        root_logger = logging.getLogger()
        root_logger.addHandler(console_handler)

        self._console_handler = console_handler

    def _setup_file_handler(self) -> None:
        """设置文件处理器（支持轮转）"""
        log_file = self._log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"

        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(self._get_formatter())

        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)

        self._file_handler = file_handler

    def _setup_memory_handler(self) -> None:
        """设置内存处理器"""
        memory_handler = MemoryLogHandler(max_entries=1000)
        memory_handler.setLevel(logging.DEBUG)

        def on_log_entry(entry: LogEntry) -> None:
            self.log_entry_added.emit(entry)

        memory_handler.add_callback(on_log_entry)

        root_logger = logging.getLogger()
        root_logger.addHandler(memory_handler)

        self._memory_handler = memory_handler

    def _get_formatter(self) -> logging.Formatter:
        """获取日志格式化器"""
        return logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def set_log_level(self, level: LogLevel) -> None:
        """设置日志级别"""
        with QMutexLocker(self._mutex):
            self._current_level = level

            if self._console_handler:
                self._console_handler.setLevel(level.value)

            self.log_level_changed.emit(level.name)

    def get_log_level(self) -> LogLevel:
        """获取当前日志级别"""
        return self._current_level

    def get_logger(self, name: str) -> logging.Logger:
        """获取指定名称的日志记录器"""
        if name not in self._loggers:
            logger = logging.getLogger(name)
            logger.setLevel(logging.DEBUG)
            self._loggers[name] = logger
        return self._loggers[name]

    def debug(self, message: str, **kwargs) -> None:
        """记录 DEBUG 级别日志"""
        self.get_logger('LogManager').debug(message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """记录 INFO 级别日志"""
        self.get_logger('LogManager').info(message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """记录 WARNING 级别日志"""
        self.get_logger('LogManager').warning(message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """记录 ERROR 级别日志"""
        self.get_logger('LogManager').error(message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """记录 CRITICAL 级别日志"""
        self.get_logger('LogManager').critical(message, **kwargs)

    def get_recent_logs(self, count: int = 100,
                        log_filter: Optional[LogFilter] = None) -> List[LogEntry]:
        """获取最近的日志条目"""
        if self._memory_handler:
            entries = self._memory_handler.get_entries(log_filter)
            return entries[-count:] if count < len(entries) else entries
        return []

    def get_all_logs(self, log_filter: Optional[LogFilter] = None) -> List[LogEntry]:
        """获取所有日志条目"""
        if self._memory_handler:
            return self._memory_handler.get_entries(log_filter)
        return []

    def clear_logs(self) -> None:
        """清空内存中的日志"""
        if self._memory_handler:
            self._memory_handler.clear()

    def export_logs(self, file_path: str,
                    format_type: str = 'text',
                    log_filter: Optional[LogFilter] = None) -> bool:
        """导出日志到文件"""
        try:
            entries = self.get_all_logs(log_filter)
            export_path = Path(file_path)
            export_path.parent.mkdir(parents=True, exist_ok=True)

            if format_type == 'json':
                self._export_json(entries, export_path)
            elif format_type == 'csv':
                self._export_csv(entries, export_path)
            else:
                self._export_text(entries, export_path)

            return True
        except Exception as e:
            self.error(f"导出日志失败: {e}")
            return False

    def _export_text(self, entries: List[LogEntry], file_path: Path) -> None:
        """导出为文本格式"""
        with open(file_path, 'w', encoding='utf-8') as f:
            for entry in entries:
                f.write(f"[{entry.timestamp}] [{entry.level}] [{entry.logger_name}] {entry.message}\n")

    def _export_json(self, entries: List[LogEntry], file_path: Path) -> None:
        """导出为 JSON 格式"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump([e.to_dict() for e in entries], f, ensure_ascii=False, indent=2)

    def _export_csv(self, entries: List[LogEntry], file_path: Path) -> None:
        """导出为 CSV 格式"""
        import csv
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            if entries:
                writer = csv.DictWriter(f, fieldnames=entries[0].to_dict().keys())
                writer.writeheader()
                for entry in entries:
                    writer.writerow(entry.to_dict())

    def get_log_files(self) -> List[Path]:
        """获取所有日志文件"""
        if self._log_dir.exists():
            return sorted(self._log_dir.glob('*.log'))
        return []

    def cleanup_old_logs(self, days: int = 30) -> int:
        """清理旧日志文件"""
        cleaned = 0
        cutoff = datetime.now().timestamp() - (days * 24 * 3600)

        for log_file in self.get_log_files():
            if log_file.stat().st_mtime < cutoff:
                try:
                    log_file.unlink()
                    cleaned += 1
                except Exception as e:
                    self.error(f"删除日志文件失败 {log_file}: {e}")

        return cleaned


def get_logger(name: str) -> logging.Logger:
    """便捷函数：获取日志记录器"""
    return LogManager.instance().get_logger(name)


def set_log_level(level: LogLevel) -> None:
    """便捷函数：设置日志级别"""
    LogManager.instance().set_log_level(level)


def get_log_manager() -> LogManager:
    """便捷函数：获取日志管理器实例"""
    return LogManager.instance()
