"""
自定义异常类

定义 wx-mp-rss-core 库的所有异常类型
"""


class WXMPRSSError(Exception):
    """基础异常类

    所有自定义异常的基类
    """
    pass


class LoginError(WXMPRSSError):
    """登录失败"""
    pass


class QRCodeTimeoutError(WXMPRSSError):
    """二维码超时"""
    pass


class FetchError(WXMPRSSError):
    """文章抓取失败"""
    pass


class NetworkError(WXMPRSSError):
    """网络错误"""
    pass


class RateLimitError(WXMPRSSError):
    """频率限制"""
    pass


class TokenExpiredError(WXMPRSSError):
    """Token 过期"""
    pass


class BrowserError(WXMPRSSError):
    """浏览器错误"""
    pass
