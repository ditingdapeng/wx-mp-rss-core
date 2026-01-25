"""
登录模块单元测试
"""

import unittest
import tempfile
import os
import json
from wx_rss.login import WeChatAuth
from wx_rss.exceptions import LoginError, BrowserError


class TestWeChatAuth(unittest.TestCase):
    """测试 WeChatAuth 类"""

    def setUp(self):
        """测试前准备"""
        # 创建临时文件
        self.temp_token = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_token.close()
        self.token_file = self.temp_token.name

        self.temp_qrcode = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.png')
        self.temp_qrcode.close()
        self.qrcode_file = self.temp_qrcode.name

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.token_file):
            os.remove(self.token_file)
        if os.path.exists(self.qrcode_file):
            os.remove(self.qrcode_file)

    def test_init(self):
        """测试初始化"""
        auth = WeChatAuth(token_file=self.token_file, qrcode_file=self.qrcode_file)

        self.assertEqual(auth.token_file, self.token_file)
        self.assertEqual(auth.qrcode_file, self.qrcode_file)
        self.assertIsNone(auth.token)
        self.assertEqual(auth.cookies, {})
        self.assertIsNone(auth._browser)

    def test_init_default_params(self):
        """测试默认参数初始化"""
        auth = WeChatAuth()

        self.assertEqual(auth.token_file, "wx_token.json")
        self.assertEqual(auth.qrcode_file, "static/wx_qrcode.png")

    def test_check_login_status_no_credentials(self):
        """测试检查登录状态（无凭证）"""
        auth = WeChatAuth(token_file=self.token_file)

        # 没有凭证时应该返回 False
        self.assertFalse(auth.check_login_status())

    def test_check_login_status_with_token(self):
        """测试检查登录状态（有 token）"""
        auth = WeChatAuth(token_file=self.token_file)
        auth.token = "test_token"

        # 只有 token 没有 cookies 时应该返回 False
        self.assertFalse(auth.check_login_status())

    def test_check_login_status_with_credentials(self):
        """测试检查登录状态（完整凭证）"""
        auth = WeChatAuth(token_file=self.token_file)
        auth.token = "test_token"
        auth.cookies = {"key": "value"}

        # 有完整凭证时应该返回 True
        self.assertTrue(auth.check_login_status())

    def test_save_credentials(self):
        """测试保存凭证"""
        auth = WeChatAuth(token_file=self.token_file)
        auth.token = "test_token_123"
        auth.cookies = {"cookie1": "value1", "cookie2": "value2"}

        # 保存凭证
        auth.save_credentials()

        # 验证文件存在
        self.assertTrue(os.path.exists(self.token_file))

        # 验证文件内容
        with open(self.token_file, 'r') as f:
            data = json.load(f)
            self.assertEqual(data['token'], "test_token_123")
            self.assertEqual(data['cookies'], {"cookie1": "value1", "cookie2": "value2"})
            self.assertIn('created_at', data)

    def test_load_credentials_file_not_exists(self):
        """测试加载凭证（文件不存在）"""
        auth = WeChatAuth(token_file=self.token_file)

        # 文件不存在时应该返回 False
        self.assertFalse(auth.load_credentials())
        self.assertIsNone(auth.token)
        self.assertEqual(auth.cookies, {})

    def test_load_credentials_success(self):
        """测试加载凭证（成功）"""
        # 先创建凭证文件
        credentials = {
            "token": "saved_token",
            "cookies": {"cookie1": "value1"},
            "created_at": "2026-01-25T10:00:00"
        }
        with open(self.token_file, 'w') as f:
            json.dump(credentials, f)

        # 加载凭证
        auth = WeChatAuth(token_file=self.token_file)
        result = auth.load_credentials()

        # 验证加载成功
        self.assertTrue(result)
        self.assertEqual(auth.token, "saved_token")
        self.assertEqual(auth.cookies, {"cookie1": "value1"})

    def test_context_manager(self):
        """测试 context manager"""
        with WeChatAuth(token_file=self.token_file) as auth:
            auth.token = "test_token"
            self.assertIsNotNone(auth.token)

        # 退出后应该清理资源
        self.assertIsNone(auth._browser)

    def test_cleanup(self):
        """测试清理资源"""
        auth = WeChatAuth(token_file=self.token_file)
        auth.token = "test_token"

        # 清理
        auth.cleanup()

        # 验证浏览器资源已清理
        self.assertIsNone(auth._browser)
        self.assertIsNone(auth._page)
        self.assertIsNone(auth._playwright)


if __name__ == '__main__':
    unittest.main()
