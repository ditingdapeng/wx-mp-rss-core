"""
JSON Feed 生成模块

提供微信公众号文章的 JSON Feed 格式生成功能
遵循 we-mp-rss 的 JSON Feed 规范
"""

import json
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional


class JSONFeedGenerator:
    """JSON Feed 生成类"""

    def __init__(
        self,
        mp_name: str,
        mp_intro: str,
        base_url: str = "",
        mp_cover: str = ""
    ):
        """初始化

        Args:
            mp_name: 公众号名称
            mp_intro: 公众号简介
            base_url: 基础URL
            mp_cover: 公众号封面
        """
        self.mp_name = mp_name
        self.mp_intro = mp_intro
        self.base_url = base_url
        self.mp_cover = mp_cover

    def generate(
        self,
        articles: List[Dict[str, Any]],
        full_text: bool = False,
        feed_id: str = ""
    ) -> str:
        """生成 JSON Feed

        Args:
            articles: 文章列表
            full_text: 是否包含全文
            feed_id: 公众号ID（可选）

        Returns:
            JSON Feed 字符串
        """
        # 构建 feed 信息
        feed_data = {
            "name": self.mp_name,
            "link": self.base_url or "",
            "description": self.mp_intro or self.mp_name,
            "language": "zh-CN",
            "cover": self.mp_cover or "",
            "items": []
        }

        # 如果有 feed_id，添加 feed 对象
        if feed_id:
            feed_data["feed"] = {
                "id": feed_id,
                "name": self.mp_name,
                "cover": self.mp_cover or "",
                "intro": self.mp_intro or ""
            }

        # 添加文章条目
        for article in articles:
            item = self._build_item(article, full_text, feed_id)
            feed_data["items"].append(item)

        # 转换为 JSON 字符串
        return json.dumps(feed_data, ensure_ascii=False, indent=2)

    def save(self, json_str: str, filename: str) -> None:
        """保存 JSON Feed 到文件

        Args:
            json_str: JSON Feed 字符串
            filename: 文件名
        """
        with open(filename, "w", encoding="utf-8") as f:
            f.write(json_str)

    def format_time(self, timestamp: int) -> str:
        """格式化时间为 ISO 8601 格式

        Args:
            timestamp: Unix 时间戳（秒）

        Returns:
            ISO 8601 格式时间字符串
        """
        try:
            if isinstance(timestamp, int):
                # 如果是毫秒时间戳，转换为秒
                if timestamp > 1000000000000:
                    timestamp = timestamp // 1000
                dt = datetime.fromtimestamp(timestamp, tz=timezone(timedelta(hours=8)))
            else:
                dt = datetime.fromisoformat(timestamp)

            return dt.isoformat()

        except Exception as e:
            # 失败时返回当前时间
            return datetime.now(timezone(timedelta(hours=8))).isoformat()

    # 私有方法

    def _build_item(
        self,
        article: Dict[str, Any],
        full_text: bool = False,
        feed_id: str = ""
    ) -> Dict[str, Any]:
        """构建文章条目

        Args:
            article: 文章数据
            full_text: 是否包含全文
            feed_id: 公众号ID

        Returns:
            文章条目字典
        """
        item = {
            "id": article.get("id", ""),
            "title": article.get("title", ""),
            "description": article.get("digest", "") or article.get("title", ""),
            "link": article.get("url", ""),
            "updated": self.format_time(article.get("publish_time", 0))
        }

        # 可选字段：封面图片
        if article.get("cover"):
            item["image"] = {
                "url": article["cover"]
            }

        # 可选字段：作者
        if article.get("author"):
            item["author"] = article["author"]

        # 可选字段：正文内容
        if full_text and article.get("content"):
            item["content"] = article["content"]
            item["content_html"] = article["content"]

        # 如果有 feed_id，添加 feed 对象
        if feed_id:
            item["feed"] = {
                "id": feed_id,
                "name": self.mp_name,
                "cover": self.mp_cover or "",
                "intro": self.mp_intro or ""
            }
            item["channel_name"] = self.mp_name

        return item
