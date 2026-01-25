"""
日志系统

提供统一的日志配置和管理
"""

import logging
import sys
from typing import Optional

DEFAULT_LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


def setup_logger(
    name: str = "wx_rss",
    level: int = DEFAULT_LOG_LEVEL,
    log_file: Optional[str] = None
) -> logging.Logger:
    """配置日志系统

    Args:
        name: 日志器名称
        level: 日志级别（DEBUG, INFO, WARNING, ERROR）
        log_file: 日志文件路径（可选）

    Returns:
        配置好的 logger 实例
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(console_handler)

    # 文件输出（可选）
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "wx_rss") -> logging.Logger:
    """获取已配置的 logger

    Args:
        name: 日志器名称

    Returns:
        logger 实例
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger
