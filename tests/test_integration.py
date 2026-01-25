"""
集成测试 - 测试完整的微信 RSS 流程
"""

import unittest
import tempfile
import os
from wx_rss import WeChatMP
from wx_rss.exceptions import LoginError, TokenExpiredError


class TestWeChatMP(unittest.TestCase):
    """测试 WeChatMP 统一入口类"""

    def setUp(self):
        """测试前准备"""
        self.temp_token = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_token.close()
        self.token_file = self.temp_token.name

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.token_file):
            os.remove(self.token_file)

    def test_init(self):
        """测试初始化"""
        mp = WeChatMP(token_file=self.token_file)

        self.assertEqual(mp.token_file, self.token_file)
        # _auth 会在 _load_credentials 中创建
        self.assertIsNotNone(mp._auth)
        self.assertIsNone(mp._fetcher)
        self.assertFalse(mp._is_logged_in)

    def test_init_default_token_file(self):
        """测试默认 token 文件"""
        mp = WeChatMP()

        self.assertEqual(mp.token_file, "wx_token.json")

    def test_load_credentials_not_exists(self):
        """测试加载不存在的凭证"""
        mp = WeChatMP(token_file=self.token_file)

        # 文件不存在时不应该加载凭证
        self.assertFalse(mp._is_logged_in)

    def test_load_credentials_from_file(self):
        """测试从文件加载凭证"""
        # 创建凭证文件
        import json
        credentials = {
            "token": "test_token",
            "cookies": {"cookie1": "value1"},
            "created_at": "2026-01-25T10:00:00"
        }
        with open(self.token_file, 'w') as f:
            json.dump(credentials, f)

        # 重新初始化应该加载凭证
        mp = WeChatMP(token_file=self.token_file)
        self.assertTrue(mp._is_logged_in)

    def test_fetch_articles_not_logged_in(self):
        """测试未登录时获取文章"""
        mp = WeChatMP(token_file=self.token_file)

        # 未登录时应该抛出 LoginError
        with self.assertRaises(LoginError):
            mp.fetch_articles(fakeid="MzAxMDAwMDAx", count=5)

    def test_fetch_articles_fetcher_not_initialized(self):
        """测试抓取器未初始化"""
        mp = WeChatMP(token_file=self.token_file)
        mp._is_logged_in = True  # 模拟已登录

        # 抓取器未初始化时应该抛出 LoginError
        with self.assertRaises(LoginError):
            mp.fetch_articles(fakeid="MzAxMDAwMDAx", count=5)

    def test_generate_rss(self):
        """测试生成 RSS"""
        mp = WeChatMP(token_file=self.token_file)

        # 测试文章数据
        articles = [
            {
                "id": "001",
                "title": "测试文章",
                "url": "https://example.com/article",
                "digest": "摘要",
                "publish_time": 1706140800
            }
        ]

        rss_xml = mp.generate_rss(
            mp_name="测试公众号",
            articles=articles,
            mp_intro="简介"
        )

        # 验证 RSS 内容
        self.assertIn('<?xml version="1.0" encoding="utf-8"?>', rss_xml)
        self.assertIn('<title>测试公众号</title>', rss_xml)
        self.assertIn('<title>测试文章</title>', rss_xml)

    def test_generate_rss_full_text(self):
        """测试生成包含全文的 RSS"""
        mp = WeChatMP(token_file=self.token_file)

        articles = [
            {
                "id": "001",
                "title": "测试文章",
                "url": "https://example.com/article",
                "digest": "摘要",
                "publish_time": 1706140800,
                "content": "<p>正文内容</p>"
            }
        ]

        rss_xml = mp.generate_rss(
            mp_name="测试公众号",
            articles=articles,
            full_text=True
        )

        # 验证包含全文（HTML 转义后的格式）
        self.assertIn('<content:encoded>', rss_xml)
        self.assertIn('&lt;p&gt;正文内容&lt;/p&gt;', rss_xml)

    def test_generate_rss_atom(self):
        """测试生成 Atom 格式"""
        mp = WeChatMP(token_file=self.token_file)

        articles = [
            {
                "id": "001",
                "title": "测试文章",
                "url": "https://example.com/article",
                "digest": "摘要",
                "publish_time": 1706140800
            }
        ]

        atom_xml = mp.generate_rss(
            mp_name="测试公众号",
            articles=articles,
            format_type="atom"
        )

        # 验证 Atom 格式
        self.assertIn('<feed', atom_xml)
        self.assertIn('xmlns="http://www.w3.org/2005/Atom"', atom_xml)

    def test_context_manager(self):
        """测试 context manager"""
        with WeChatMP(token_file=self.token_file) as mp:
            self.assertIsNotNone(mp)

        # 退出后应该清理资源
        self.assertIsNone(mp._fetcher)
        self.assertIsNone(mp._auth)

    def test_cleanup(self):
        """测试清理资源"""
        mp = WeChatMP(token_file=self.token_file)
        mp._is_logged_in = True

        # 清理
        mp.cleanup()

        # 验证资源已清理
        self.assertIsNone(mp._fetcher)
        self.assertIsNone(mp._auth)
        self.assertFalse(mp._is_logged_in)


if __name__ == '__main__':
    unittest.main()
