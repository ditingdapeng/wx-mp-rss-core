"""
搜索公众号模块

提供通过公众号名称搜索并获取 fakeid 的功能
"""

import json
from typing import List, Dict, Any, Optional
from wx_rss.logger import get_logger
from wx_rss.exceptions import FetchError


class FeedSearcher:
    """公众号搜索类"""

    def __init__(self, token: str, cookies: Dict[str, str]):
        """初始化

        Args:
            token: 微信 Token
            cookies: Cookie 字典
        """
        self.token = token
        self.cookies = cookies
        self._logger = get_logger("wx_rss.search")

    def search_by_name(
        self,
        keyword: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """通过公众号名称搜索

        Args:
            keyword: 公众号名称关键词
            limit: 返回结果数量，默认 5

        Returns:
            公众号列表

        Raises:
            FetchError: 搜索失败
        """
        self._logger.info(f"搜索公众号: {keyword}")

        try:
            import requests

            # 构造搜索 API URL
            url = "https://mp.weixin.qq.com/cgi-bin/searchbiz"
            params = {
                "action": "search_biz",
                "begin": 0,
                "count": limit,
                "query": keyword,
                "token": self.token,
                "lang": "zh_CN",
                "f": "json",
                "ajax": 1
            }

            # 构造请求头
            headers = {
                "Cookie": self._format_cookies(),
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Referer": "https://mp.weixin.qq.com/"
            }

            # 发送请求
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()

            # 解析响应
            data = response.json()
            
            # 调试日志
            self._logger.debug(f"API 响应: {json.dumps(data, ensure_ascii=False)[:500]}")

            # 检查错误
            if data.get("base_resp", {}).get("ret") != 0:
                err_msg = data.get("base_resp", {}).get("err_msg", "未知错误")
                ret_code = data.get("base_resp", {}).get("ret")
                raise FetchError(f"搜索 API 错误: {err_msg} (code: {ret_code})")

            # searchbiz API 直接返回 list，不在 publish_page 中
            # 提取公众号列表
            results = []
            for item in data.get("list", []):
                result = {
                    "fakeid": item.get("fakeid", ""),
                    "nickname": item.get("nickname", ""),
                    "round_head_img": item.get("round_head_img", ""),
                    "signature": item.get("signature", ""),
                    "alias_name": item.get("alias_name", "")
                }
                results.append(result)

            self._logger.info(f"搜索到 {len(results)} 个公众号")
            return results

        except Exception as e:
            self._logger.error(f"搜索公众号失败: {e}")
            raise FetchError(f"搜索公众号失败: {e}") from e

    def _format_cookies(self) -> str:
        """格式化 cookies 为字符串

        Returns:
            cookies 字符串
        """
        return '; '.join([f"{k}={v}" for k, v in self.cookies.items()])

    def get_first_match(self, keyword: str) -> Optional[str]:
        """获取第一个匹配的 fakeid

        Args:
            keyword: 公众号名称关键词

        Returns:
            fakeid，如果未找到返回 None
        """
        results = self.search_by_name(keyword, limit=5)

        # 精确匹配
        for result in results:
            if result["nickname"] == keyword:
                self._logger.info(f"找到精确匹配: {result['nickname']} -> {result['fakeid']}")
                return result["fakeid"]

        # 模糊匹配（包含关键词）
        for result in results:
            if keyword in result["nickname"]:
                self._logger.info(f"找到模糊匹配: {result['nickname']} -> {result['fakeid']}")
                return result["fakeid"]

        self._logger.warning(f"未找到公众号: {keyword}")
        return None
