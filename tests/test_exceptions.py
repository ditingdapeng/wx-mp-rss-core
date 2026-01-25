"""
异常类单元测试
"""

import unittest
from wx_rss.exceptions import (
    WXMPRSSError,
    LoginError,
    QRCodeTimeoutError,
    FetchError,
    NetworkError,
    RateLimitError,
    TokenExpiredError,
    BrowserError
)


class TestExceptions(unittest.TestCase):
    """测试自定义异常类"""

    def test_wxmp_rss_error(self):
        """测试基础异常类"""
        error = WXMPRSSError("基础错误")
        self.assertEqual(str(error), "基础错误")
        self.assertIsInstance(error, Exception)

    def test_login_error(self):
        """测试登录错误"""
        error = LoginError("登录失败")
        self.assertEqual(str(error), "登录失败")
        self.assertIsInstance(error, WXMPRSSError)

    def test_qrcode_timeout_error(self):
        """测试二维码超时错误"""
        error = QRCodeTimeoutError("二维码超时")
        self.assertEqual(str(error), "二维码超时")
        self.assertIsInstance(error, WXMPRSSError)

    def test_fetch_error(self):
        """测试抓取错误"""
        error = FetchError("抓取失败")
        self.assertEqual(str(error), "抓取失败")
        self.assertIsInstance(error, WXMPRSSError)

    def test_network_error(self):
        """测试网络错误"""
        error = NetworkError("网络错误")
        self.assertEqual(str(error), "网络错误")
        self.assertIsInstance(error, WXMPRSSError)

    def test_rate_limit_error(self):
        """测试频率限制错误"""
        error = RateLimitError("频率限制")
        self.assertEqual(str(error), "频率限制")
        self.assertIsInstance(error, WXMPRSSError)

    def test_token_expired_error(self):
        """测试 Token 过期错误"""
        error = TokenExpiredError("Token 过期")
        self.assertEqual(str(error), "Token 过期")
        self.assertIsInstance(error, WXMPRSSError)

    def test_browser_error(self):
        """测试浏览器错误"""
        error = BrowserError("浏览器错误")
        self.assertEqual(str(error), "浏览器错误")
        self.assertIsInstance(error, WXMPRSSError)

    def test_exception_hierarchy(self):
        """测试异常继承关系"""
        # 所有异常都应该继承自 WXMPRSSError
        exceptions = [
            LoginError("test"),
            QRCodeTimeoutError("test"),
            FetchError("test"),
            NetworkError("test"),
            RateLimitError("test"),
            TokenExpiredError("test"),
            BrowserError("test")
        ]

        for exc in exceptions:
            self.assertIsInstance(exc, WXMPRSSError)

    def test_exception_raising(self):
        """测试异常抛出"""
        # 测试可以正确抛出和捕获异常
        with self.assertRaises(LoginError):
            raise LoginError("测试")

        with self.assertRaises(QRCodeTimeoutError):
            raise QRCodeTimeoutError("测试")

        with self.assertRaises(FetchError):
            raise FetchError("测试")

    def test_exception_chaining(self):
        """测试异常链"""
        try:
            try:
                raise ValueError("原始错误")
            except ValueError as e:
                raise LoginError("登录失败") from e
        except LoginError as exc:
            self.assertIsNotNone(exc.__cause__)
            self.assertIsInstance(exc.__cause__, ValueError)


if __name__ == '__main__':
    unittest.main()
