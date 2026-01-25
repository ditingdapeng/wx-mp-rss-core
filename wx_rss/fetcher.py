"""
文章抓取模块

提供微信公众号文��抓取功能，基于 Playwright + BeautifulSoup 混合架构
"""

import time
import re
import json
from typing import List, Dict, Any, Optional, Union

try:
    from playwright.sync_api import sync_playwright, Browser, Page
    from bs4 import BeautifulSoup
except ImportError:
    raise ImportError(
        "依赖未安装，请运行: pip install playwright beautifulsoup4 && python -m playwright install firefox"
    )

from .logger import get_logger
from .exceptions import FetchError, NetworkError, RateLimitError, TokenExpiredError


class ArticleFetcher:
    """文章抓取类（Playwright + BeautifulSoup 混合架构）"""

    def __init__(
        self,
        token: str,
        cookies: Dict[str, str],
        headless: bool = True,
        browser_type: str = "firefox"
    ):
        """初始化

        Args:
            token: 微信 Token
            cookies: Cookie 字典
            headless: 是否无头模式（默认 True）
            browser_type: 浏览器类型（firefox/chromium）
        """
        self.token = token
        self.cookies = cookies
        self.headless = headless
        self.browser_type = browser_type
        self._browser: Optional[Browser] = None
        self._page: Optional[Page] = None
        self._playwright = None
        self._logger = get_logger("wx_rss.fetcher")

    def fetch(
        self,
        fakeid: str,
        count: int = 5,
        begin: int = 0
    ) -> List[Dict[str, Any]]:
        """获取文章列表

        Args:
            fakeid: 公众号 fake_id
            count: 获取数量
            begin: 起始位置

        Returns:
            文章列表

        Raises:
            FetchError: 抓取失败
            NetworkError: 网络错误
            TokenExpiredError: Token 过期
        """
        self._logger.info(f"开始获取文章列表: fakeid={fakeid}, count={count}")

        try:
            # 启动浏览器
            self._start_browser()

            # 构造文章列表 API URL（参考 we-mp-rss 实现）
            api_url = f"https://mp.weixin.qq.com/cgi-bin/appmsgpublish"
            params = {
                "sub": "list",
                "sub_action": "list_ex",  # 重要：使用 list_ex 获取文章列表
                "begin": begin,
                "count": count,
                "fakeid": fakeid,
                "token": self.token,
                "lang": "zh_CN",
                "f": "json",
                "ajax": 1  # 数字，不是字符串
            }

            # 访问 API
            self._logger.debug(f"访问 API: {api_url}")
            response = self._page.goto(f"{api_url}?{self._build_query_string(params)}")

            # 检查响应
            if not response.ok:
                raise NetworkError(f"HTTP {response.status}: {response.status_text}")

            # 检查是否需要重新登录
            current_url = self._page.url
            if "login" in current_url.lower():
                raise TokenExpiredError("Token 已过期，请重新登录")

            # 解析响应
            content = self._page.content()
            articles = self._parse_response(content)  # type: ignore

            self._logger.info(f"成功获取 {len(articles)} 篇文章")
            return articles

        except TokenExpiredError:
            raise
        except NetworkError:
            raise
        except Exception as e:
            self._logger.error(f"获取文章失败: {e}")
            raise FetchError(f"获取文章失败: {e}") from e

    def fetch_with_content(
        self,
        fakeid: str,
        count: int = 5,
        begin: int = 0
    ) -> List[Dict[str, Any]]:
        """获取文章列表（包含正文内容）

        Args:
            fakeid: 公众号 fake_id
            count: 获取数量
            begin: 起始位置

        Returns:
            文章列表（包含 content 字段）
        """
        self._logger.info(f"开始获取文章（含正文）: fakeid={fakeid}, count={count}")

        # 先获取文章列表
        articles = self.fetch(fakeid, count, begin)

        # 获取每篇文章的正文
        for i, article in enumerate(articles):
            try:
                self._logger.info(f"正在获取第 {i+1}/{len(articles)} 篇文章的正文")
                content = self._fetch_article_content(article["url"])
                article["content"] = content
                time.sleep(1)  # 避免请求过快
            except Exception as e:
                self._logger.warning(f"获取文章正文失败: {article['title']}, {e}")
                article["content"] = ""

        return articles

    def cleanup(self) -> None:
        """清理浏览器资源"""
        if self._page:
            try:
                self._page.close()
            except Exception:
                pass
            self._page = None

        if self._browser:
            try:
                self._browser.close()
            except Exception:
                pass
            self._browser = None

        if self._playwright:
            try:
                self._playwright.stop()
            except Exception:
                pass
            self._playwright = None

    def __enter__(self):
        """Context manager 入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 出口"""
        self.cleanup()

    # 私有方法

    def _start_browser(self) -> None:
        """启动浏览器"""
        if self._browser is None:
            self._logger.info("正在启动浏览器...")
            self._playwright = sync_playwright().start()

            if self.browser_type == "firefox":
                self._browser = self._playwright.firefox.launch(headless=self.headless)
            elif self.browser_type == "chromium":
                self._browser = self._playwright.chromium.launch(headless=self.headless)
            else:
                raise ValueError(f"不支持的浏览器类型: {self.browser_type}")

            self._page = self._browser.new_page()

            # 添加 Cookies
            self._page.context.add_cookies([
                {"name": name, "value": value, "domain": ".weixin.qq.com", "path": "/"}
                for name, value in self.cookies.items()
            ])

            self._logger.info(f"浏览器启动成功（{self.browser_type}）")

    def _build_query_string(self, params: Dict[str, Any]) -> str:
        """构建查询字符串"""
        return "&".join([f"{k}={v}" for k, v in params.items()])

    def _extract_article_id(self, url: str) -> str:
        """从文章 URL 中提取文章 ID

        Args:
            url: 文章 URL

        Returns:
            文章 ID
        """
        try:
            # 从 URL 中提取最后一部分作为 ID
            # 例如：https://mp.weixin.qq.com/s/abc123 -> abc123
            import re
            match = re.search(r"/([^/]+)$", url)
            if match:
                return match.group(1)
            return ""
        except Exception:
            return ""

    def _parse_response(self, content: Union[bytes, str]) -> List[Dict[str, Any]]:
        """解析 API 响应（参考 we-mp-rss 实现）

        Args:
            content: 响应内容

        Returns:
            文章列表
        """
        try:
            import json
            import re
            # 兼容 bytes 和 str
            if isinstance(content, bytes):
                content = content.decode("utf-8")

            # 记录原始响应用于调试
            self._logger.debug(f"响应内容（前200字符）: {content[:200]}")

            # 处理 HTML 包装的 JSON（Firefox 会将 JSON 包装在 <pre> 标签中）
            if content.strip().startswith("<"):
                match = re.search(r"<pre[^>]*>(.*?)</pre>", content, re.DOTALL)
                if match:
                    content = match.group(1)
                else:
                    # 尝试提取 body 内容
                    match = re.search(r"<body[^>]*>(.*?)</body>", content, re.DOTALL)
                    if match:
                        content = match.group(1).strip()

            data = json.loads(content)
            
            # 检查 base_resp 错误（如 invalid args）
            if "base_resp" in data:
                base_resp = data["base_resp"]
                if base_resp.get("ret") != 0:
                    error_msg = base_resp.get("err_msg", "未知错误")
                    raise FetchError(f"API 返回错误: {error_msg} (code: {base_resp.get('ret')})")

            # 检查返回码
            if data.get("ret") != 0 and data.get("ret") is not None:
                error_msg = data.get("msg", "未知错误")
                raise FetchError(f"API 返回错误: {error_msg}")

            # 解析 publish_page（这是 JSON 字符串，需要再次解析）
            publish_page_str = data.get("publish_page", "{}")
            if isinstance(publish_page_str, str):
                publish_page = json.loads(publish_page_str)
            else:
                publish_page = publish_page_str

            # 获取文章列表
            article_list = publish_page.get("publish_list", [])

            articles = []
            for item in article_list:
                try:
                    # publish_info 也是 JSON 字符串，需要解析
                    publish_info_str = item.get("publish_info", "{}")
                    if isinstance(publish_info_str, str):
                        publish_info = json.loads(publish_info_str)
                    else:
                        publish_info = publish_info_str

                    # 获取 appmsgex 列表（第一个是文章）
                    appmsgex = publish_info.get("appmsgex", [])
                    if not appmsgex:
                        continue

                    article_data = appmsgex[0]  # 取第一篇文章

                    article = {
                        "id": self._extract_article_id(article_data.get("link", "")),
                        "title": article_data.get("title", ""),
                        "url": article_data.get("link", ""),
                        "cover": article_data.get("cover", ""),
                        "digest": article_data.get("digest", ""),
                        "publish_time": self._parse_publish_time(article_data.get("update_time")),
                        "author": "",  # API 不返回作者信息
                        "content": ""
                    }
                    articles.append(article)

                except Exception as e:
                    self._logger.warning(f"解析文章项失败: {e}")
                    continue

            return articles

        except json.JSONDecodeError as e:
            self._logger.error(f"JSON 解析失败: {e}")
            self._logger.error(f"响应内容: {content[:500]}")
            raise FetchError(f"JSON 解析失败: {e}") from e
        except Exception as e:
            self._logger.error(f"解析响应失败: {e}")
            raise FetchError(f"解析响应失败: {e}") from e

    def _parse_publish_time(self, timestamp: Optional[int]) -> int:
        """解析发布时间

        Args:
            timestamp: 时间戳或秒数

        Returns:
            Unix 时间戳（秒）
        """
        if timestamp is None:
            return int(time.time())

        # 如果是秒级时间戳，直接返回
        if timestamp < 10000000000:
            return timestamp

        # 如果是毫秒级时间戳，转换为秒
        return timestamp // 1000

    def _fetch_article_content(self, url: str) -> str:
        """获取单篇文章的正文内容

        Args:
            url: 文章 URL

        Returns:
            正文 HTML

        Raises:
            FetchError: 获取失败
        """
        try:
            self._logger.debug(f"访问文章: {url}")
            self._page.goto(url)
            self._page.wait_for_load_state("networkidle")

            # 检查异常情况
            body_text = self._page.locator("body").text_content()
            if "当前环境异常" in body_text:
                raise FetchError("当前环境异常")
            if "该内容已被发布者删除" in body_text:
                raise FetchError("文章已被删除")
            if "内容审核中" in body_text:
                raise FetchError("内容审核中")

            # 使用 BeautifulSoup 解析
            soup = BeautifulSoup(self._page.content(), 'html.parser')

            # 提取正文
            content_elem = soup.select_one("#js_content")
            if content_elem:
                return str(content_elem)

            return ""

        except Exception as e:
            self._logger.error(f"获取文章正文失败: {e}")
            raise FetchError(f"获取文章正文失败: {e}") from e
