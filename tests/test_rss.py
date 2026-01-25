"""
RSS 生成模块单元测试
"""

import unittest
from datetime import datetime, timezone, timedelta
from wx_rss.rss import RSSGenerator


class TestRSSGenerator(unittest.TestCase):
    """测试 RSSGenerator 类"""

    def setUp(self):
        """测试前准备"""
        self.generator = RSSGenerator(
            mp_name="测试公众号",
            mp_intro="这是测试公众号的简介",
            base_url="https://example.com",
            mp_cover="https://example.com/cover.jpg"
        )

        # 测试文章数据
        self.test_articles = [
            {
                "id": "001",
                "title": "测试文章1",
                "url": "https://example.com/article1",
                "cover": "https://example.com/cover1.jpg",
                "digest": "这是测试文章1的摘要",
                "publish_time": 1706140800,
                "author": "测试作者",
                "content": "<p>这是测试文章1的正文</p>"
            },
            {
                "id": "002",
                "title": "测试文章2",
                "url": "https://example.com/article2",
                "cover": "https://example.com/cover2.jpg",
                "digest": "这是测试文章2的摘要",
                "publish_time": 1706227200,
                "author": "测试作者",
                "content": "<p>这是测试文章2的正文</p>"
            }
        ]

    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.generator.mp_name, "测试公众号")
        self.assertEqual(self.generator.mp_intro, "这是测试公众号的简介")
        self.assertEqual(self.generator.base_url, "https://example.com")
        self.assertEqual(self.generator.mp_cover, "https://example.com/cover.jpg")

    def test_init_minimal_params(self):
        """测试最小参数初始化"""
        gen = RSSGenerator(
            mp_name="测试",
            mp_intro="简介"
        )

        self.assertEqual(gen.mp_name, "测试")
        self.assertEqual(gen.mp_intro, "简介")
        self.assertEqual(gen.base_url, "")
        self.assertEqual(gen.mp_cover, "")

    def test_generate_basic_rss(self):
        """测试生成基础 RSS"""
        rss_xml = self.generator.generate(self.test_articles)

        # 验证 XML 声明
        self.assertIn('<?xml version="1.0" encoding="utf-8"?>', rss_xml)

        # 验证 RSS 元素
        self.assertIn('<rss version="2.0">', rss_xml)
        self.assertIn('<channel>', rss_xml)

        # 验证频道信息
        self.assertIn('<title>测试公众号</title>', rss_xml)
        self.assertIn('<link>https://example.com</link>', rss_xml)
        self.assertIn('<description>这是测试公众号的简介</description>', rss_xml)

        # 验证文章条目
        self.assertIn('<item>', rss_xml)
        self.assertIn('<title>测试文章1</title>', rss_xml)
        self.assertIn('<title>测试文章2</title>', rss_xml)

    def test_generate_full_text_rss(self):
        """测试生成包含全文的 RSS"""
        rss_xml = self.generator.generate(self.test_articles, full_text=True)

        # 验证包含 content 命名空间
        self.assertIn('xmlns:content="http://purl.org/rss/1.0/modules/content/"', rss_xml)

        # 验证包含正文（HTML 转义后的格式）
        self.assertIn('<content:encoded>', rss_xml)
        self.assertIn('&lt;p&gt;这是测试文章1的正文&lt;/p&gt;', rss_xml)

    def test_generate_rss_with_cover(self):
        """测试生成包含封面的 RSS"""
        rss_xml = self.generator.generate(self.test_articles, add_cover=True)

        # 验证包含封面
        self.assertIn('<image>', rss_xml)
        self.assertIn('<url>https://example.com/cover.jpg</url>', rss_xml)

        # 验证文章封面
        self.assertIn('<enclosure', rss_xml)

    def test_generate_atom(self):
        """测试生成 Atom 格式"""
        atom_xml = self.generator.generate_atom(self.test_articles)

        # 验证 Atom 声明
        self.assertIn('<?xml version="1.0" encoding="utf-8"?>', atom_xml)
        self.assertIn('<feed', atom_xml)
        self.assertIn('xmlns="http://www.w3.org/2005/Atom"', atom_xml)

        # 验证频道信息
        self.assertIn('<title>测试公众号</title>', atom_xml)
        self.assertIn('<id>https://example.com</id>', atom_xml)

        # 验证文章条目
        self.assertIn('<entry>', atom_xml)
        self.assertIn('<title>测试文章1</title>', atom_xml)

    def test_generate_atom_full_text(self):
        """测试生成包含全文的 Atom"""
        atom_xml = self.generator.generate_atom(self.test_articles, full_text=True)

        # 验证包含正文（HTML 转义后的格式）
        self.assertIn('<content', atom_xml)
        self.assertIn('&lt;p&gt;这是测试文章1的正文&lt;/p&gt;', atom_xml)

    def test_format_time(self):
        """测试时间格式化"""
        timestamp = 1706140800  # 2024-01-25 00:00:00 UTC

        formatted = self.generator.format_time(timestamp)

        # 验证格式
        self.assertIsInstance(formatted, str)
        self.assertIn('Jan', formatted)
        self.assertIn('2024', formatted)

    def test_format_time_invalid(self):
        """测试时间格式化（无效时间戳）"""
        # 时间戳为 0 时返回 Unix 纪元时间
        formatted = self.generator.format_time(0)

        self.assertIsInstance(formatted, str)
        self.assertIn('1970', formatted)  # Unix 纪元

    def test_empty_articles(self):
        """测试空文章列表"""
        rss_xml = self.generator.generate([])

        # 应该生成有效的 RSS，但没有 item
        self.assertIn('<rss version="2.0">', rss_xml)
        self.assertIn('<channel>', rss_xml)
        self.assertNotIn('<item>', rss_xml)

    def test_article_with_missing_fields(self):
        """测试缺少字段的文章"""
        incomplete_articles = [
            {
                "id": "001",
                "title": "测试文章",
                # 缺少其他字段
            }
        ]

        rss_xml = self.generator.generate(incomplete_articles)

        # 应该生成有效的 RSS，使用默认值
        self.assertIn('<title>测试文章</title>', rss_xml)


if __name__ == '__main__':
    unittest.main()
