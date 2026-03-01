"""
日志配置模块

提供全局日志配置功能，支持环境变量和运行时配置。
"""
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def setup_logging(
    level: Optional[str] = None,
    log_file: Optional[str] = None,
    console_output: bool = True,
    format_string: Optional[str] = None
) -> None:
    """
    配置全局日志。

    Args:
        level: 日志级别，可选 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
               默认从环境变量 LOG_LEVEL 读取，否则使用 INFO
        log_file: 日志文件路径，如果指定则同时输出到文件
        console_output: 是否输出到控制台，默认 True
        format_string: 自定义日志格式字符串

    示例:
        # 开发环境 - 详细日志
        setup_logging('DEBUG')

        # 生产环境 - 只记录警告及以上
        setup_logging('WARNING')

        # 同时输出到文件
        setup_logging('INFO', log_file='app.log')
    """
    log_level = level or os.environ.get('LOG_LEVEL', 'INFO')
    level_value = getattr(logging, log_level.upper(), logging.INFO)

    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    handlers = []

    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level_value)
        console_handler.setFormatter(logging.Formatter(format_string, datefmt='%Y-%m-%d %H:%M:%S'))
        handlers.append(console_handler)

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level_value)
        file_handler.setFormatter(logging.Formatter(format_string, datefmt='%Y-%m-%d %H:%M:%S'))
        handlers.append(file_handler)

    logging.basicConfig(
        level=level_value,
        format=format_string,
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=handlers if handlers else None
    )


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志记录器。

    Args:
        name: 日志记录器名称，通常使用 __name__

    Returns:
        配置好的 Logger 实例

    示例:
        logger = get_logger(__name__)
        logger.debug("这是一条调试信息")
    """
    return logging.getLogger(name)


class LoggerMixin:
    """
    日志混入类，为类提供日志功能。

    使用方式:
        class MyClass(LoggerMixin):
            def my_method(self):
                self.logger.debug("方法被调用")
    """

    @property
    def logger(self) -> logging.Logger:
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger(self.__class__.__module__ + '.' + self.__class__.__name__)
        return self._logger


def log_function_call(func):
    """
    函数调用日志装饰器。

    记录函数的调用和返回值。

    示例:
        @log_function_call
        def my_function(x, y):
            return x + y
    """
    logger = logging.getLogger(func.__module__)

    def wrapper(*args, **kwargs):
        logger.debug(f"调用 {func.__name__}(args={args}, kwargs={kwargs})")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} 返回: {result}")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} 抛出异常: {e}")
            raise

    return wrapper
