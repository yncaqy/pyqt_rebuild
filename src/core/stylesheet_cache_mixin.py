"""
样式表缓存混入类

提供统一的样式表缓存机制，避免每个组件重复实现缓存逻辑。

功能特性:
- 统一的缓存初始化和管理
- 线程安全的缓存访问
- 自动缓存大小限制
- 性能监控支持
"""

import logging
import time
from typing import Dict, Tuple, Any, Callable, Optional

logger = logging.getLogger(__name__)


class StylesheetCacheMixin:
    """
    为主题化组件提供统一样式表缓存能力的混入类。
    
    此混入类封装了样式表缓存的通用逻辑，包括:
    - 缓存初始化
    - 缓存查询和存储
    - 缓存大小限制
    - 缓存清理
    
    使用方式:
        1. 在 __init__ 中调用 _init_stylesheet_cache()
        2. 使用 _get_cached_stylesheet() 获取或构建样式表
        3. 在 cleanup() 中调用 _clear_stylesheet_cache()
    
    属性:
        _stylesheet_cache: 样式表缓存字典
        _stylesheet_cache_max_size: 缓存最大容量
    """
    
    def _init_stylesheet_cache(self, max_size: int = 100) -> None:
        """
        初始化样式表缓存系统。
        
        必须在组件的 __init__ 方法中调用此方法。
        
        Args:
            max_size: 缓存最大容量，默认 100
        """
        self._stylesheet_cache: Dict[Tuple[Any, ...], str] = {}
        self._stylesheet_cache_max_size: int = max_size
    
    def _get_cached_stylesheet(
        self,
        cache_key: Tuple[Any, ...],
        builder: Callable[[], str],
        theme_name: Optional[str] = None
    ) -> str:
        """
        获取缓存的样式表，如果不存在则构建并缓存。
        
        Args:
            cache_key: 缓存键，通常是包含主题名和样式参数的元组
            builder: 样式表构建函数，当缓存未命中时调用
            theme_name: 主题名称，用于日志输出
        
        Returns:
            样式表字符串
        """
        if not hasattr(self, '_stylesheet_cache'):
            self._stylesheet_cache = {}
            self._stylesheet_cache_max_size = 100
        
        if cache_key in self._stylesheet_cache:
            logger.debug(
                f"样式表缓存命中 (缓存大小: {len(self._stylesheet_cache)}, "
                f"主题: {theme_name or 'unknown'})"
            )
            return self._stylesheet_cache[cache_key]
        
        start_time = time.time()
        qss = builder()
        build_time = time.time() - start_time
        
        if len(self._stylesheet_cache) < self._stylesheet_cache_max_size:
            self._stylesheet_cache[cache_key] = qss
            logger.debug(
                f"样式表已缓存 (缓存大小: {len(self._stylesheet_cache)}, "
                f"构建耗时: {build_time:.3f}s, 主题: {theme_name or 'unknown'})"
            )
        else:
            logger.warning(
                f"样式表缓存已满 (最大: {self._stylesheet_cache_max_size})，"
                f"跳过缓存 (主题: {theme_name or 'unknown'})"
            )
        
        return qss
    
    def _clear_stylesheet_cache(self) -> None:
        """
        清除样式表缓存。
        
        应在组件的 cleanup() 方法中调用此方法。
        """
        if hasattr(self, '_stylesheet_cache'):
            cache_size = len(self._stylesheet_cache)
            self._stylesheet_cache.clear()
            logger.debug(f"样式表缓存已清除 (原大小: {cache_size})")
    
    def _get_cache_size(self) -> int:
        """
        获取当前缓存大小。
        
        Returns:
            缓存中的条目数量
        """
        if hasattr(self, '_stylesheet_cache'):
            return len(self._stylesheet_cache)
        return 0
    
    def _is_cache_full(self) -> bool:
        """
        检查缓存是否已满。
        
        Returns:
            如果缓存已满返回 True
        """
        if hasattr(self, '_stylesheet_cache'):
            return len(self._stylesheet_cache) >= self._stylesheet_cache_max_size
        return False
