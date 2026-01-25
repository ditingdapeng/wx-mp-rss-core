"""
wx-mp-rss-core

微信公众号 RSS 核心库

提供轻量级的公众号文章抓取和 RSS 生成功能
"""

from .login import WeChatAuth
from .fetcher import ArticleFetcher
from .json_feed import JSONFeedGenerator
from .search import FeedSearcher
from .exceptions import *
from .logger import get_logger

__version__ = "0.2.0"
__all__ = [
    "WeChatMP",
    "WeChatAuth",
    "ArticleFetcher",
    "JSONFeedGenerator",
    "FeedSearcher",
    "get_logger",
    # 异常类
    "WXMPRSSError",
    "LoginError",
    "QRCodeTimeoutError",
    "FetchError",
    "NetworkError",
    "RateLimitError",
    "TokenExpiredError",
    "BrowserError",
]


class WeChatMP:
    """微信公众号 RSS 统一入口类"""

    def __init__(self, token_file: str = "wx_token.json"):
        """初始化

        Args:
            token_file: Token 保存文件路径
        """
        self.token_file = token_file
        self._auth = None
        self._fetcher = None
        self._logger = get_logger("wx_rss")
        self._is_logged_in = False

        # 尝试加载已有凭证
        self._load_credentials()

    def login(self, timeout: int = 180) -> dict:
        """执行登录流程

        Args:
            timeout: 二维码超时时间（秒）

        Returns:
            登录信息字典

        Raises:
            LoginError: 登录失败
        """
        self._logger.info("开始登录...")
        self._auth = WeChatAuth(token_file=self.token_file)
        result = self._auth.login(timeout=timeout)

        self._is_logged_in = result["is_logged_in"]

        # 初始化文章抓取器
        if self._is_logged_in:
            self._fetcher = ArticleFetcher(
                token=result["token"],
                cookies=result["cookies"]
            )

        return result

    def fetch_articles(
        self,
        fakeid: str,
        count: int = 10,
        with_content: bool = False
    ) -> list:
        """获取文章列表

        Args:
            fakeid: 公众号 fake_id
            count: 获取数量
            with_content: 是否包含正文内容

        Returns:
            文章列表

        Raises:
            LoginError: 未登录
            FetchError: 抓取失败
        """
        if not self._is_logged_in:
            raise LoginError("请先登录")

        if not self._fetcher:
            raise LoginError("抓取器未初始化，请先登录")

        self._logger.info(f"获取文章: fakeid={fakeid}, count={count}")

        if with_content:
            return self._fetcher.fetch_with_content(fakeid, count)
        else:
            return self._fetcher.fetch(fakeid, count)

    def generate_json_feed(
        self,
        mp_name: str,
        articles: list,
        mp_intro: str = "",
        base_url: str = "",
        mp_cover: str = "",
        full_text: bool = False,
        feed_id: str = ""
    ) -> str:
        """生成 JSON Feed

        Args:
            mp_name: 公众号名称
            articles: 文章列表
            mp_intro: 公众号简介
            base_url: 基础URL
            mp_cover: 公众号封面
            full_text: 是否包含全文
            feed_id: 公众号ID（可选）

        Returns:
            JSON Feed 字符串
        """
        self._logger.info(f"生成 JSON Feed: {mp_name}, 文章数: {len(articles)}")

        generator = JSONFeedGenerator(
            mp_name=mp_name,
            mp_intro=mp_intro or mp_name,
            base_url=base_url,
            mp_cover=mp_cover
        )

        return generator.generate(articles, full_text, feed_id)

    def cleanup(self) -> None:
        """清理资源"""
        if self._fetcher:
            self._fetcher.cleanup()
            self._fetcher = None

        if self._auth:
            self._auth.cleanup()
            self._auth = None

        self._is_logged_in = False
        self._logger.info("资源已清理")

    def search_feed(self, keyword: str, limit: int = 5) -> list:
        """搜索公众号

        Args:
            keyword: 公众号名称关键词
            limit: 返回结果数量，默认 5

        Returns:
            公众号列表

        Raises:
            LoginError: 未登录
            FetchError: 搜索失败
        """
        if not self._is_logged_in:
            raise LoginError("请先登录")

        if not self._auth:
            raise LoginError("认证器未初始化，请先登录")

        self._logger.info(f"搜索公众号: {keyword}")

        searcher = FeedSearcher(
            token=self._auth.token or "",  # type: ignore
            cookies=self._auth.cookies
        )

        return searcher.search_by_name(keyword, limit)

    def get_feed_fakeid(self, keyword: str) -> str:
        """获取公众号的 fakeid（便捷方法）

        Args:
            keyword: 公众号名称

        Returns:
            fakeid，如果未找到返回空字符串

        Example:
            >>> mp = WeChatMP()
            >>> mp.login()
            >>> fakeid = mp.get_feed_fakeid("精神抖擞王大鹏")
            >>> print(fakeid)
            'MjM5NTI2...'
        """
        if not self._is_logged_in:
            raise LoginError("请先登录")

        if not self._auth:
            raise LoginError("认证器未初始化，请先登录")

        searcher = FeedSearcher(
            token=self._auth.token or "",  # type: ignore
            cookies=self._auth.cookies
        )

        result = searcher.get_first_match(keyword)
        return result or ""

    def __enter__(self):
        """Context manager 入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 出口"""
        self.cleanup()

    # 私有方法

    def _load_credentials(self) -> None:
        """加载已有凭证"""
        import os
        if not os.path.exists(self.token_file):
            return

        try:
            self._auth = WeChatAuth(token_file=self.token_file)
            if self._auth.load_credentials():
                self._is_logged_in = True
                self._fetcher = ArticleFetcher(
                    token=self._auth.token,
                    cookies=self._auth.cookies
                )
                self._logger.info("已加载保存的登录凭证")
        except Exception as e:
            self._logger.warning(f"加载凭证失败: {e}")
