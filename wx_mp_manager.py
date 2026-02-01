"""
微信公众号文章管理器
提供公众号列表管理和批量抓取功能
"""

import json
import os
from typing import List, Dict, Optional
from pathlib import Path
from wx_rss import WeChatMP


class WXMPManager:
    """微信公众号管理器"""

    def __init__(self, feeds_file: str = "feeds.json", output_dir: str = "output"):
        """初始化

        Args:
            feeds_file: 公众号列表配置文件
            output_dir: JSON Feed 输出目录
        """
        self.feeds_file = feeds_file
        self.output_dir = output_dir
        self.feeds: List[Dict] = []

        # 确保输出目录存在
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # 加载列表
        self.load_feeds()

    def load_feeds(self) -> None:
        """从文件加载公众号列表"""
        if os.path.exists(self.feeds_file):
            with open(self.feeds_file, "r", encoding="utf-8") as f:
                self.feeds = json.load(f)
        else:
            # 默认公众号列表
            self.feeds = [
                {"name": "突围先生"},
                {"name": "雪球花甲老头"},
                {"name": "成元子"},
                {"name": "Datawhale"},
                {"name": "AGI智码"}
            ]
            self.save_feeds()

    def save_feeds(self) -> None:
        """保存公众号列表到文件"""
        with open(self.feeds_file, "w", encoding="utf-8") as f:
            json.dump(self.feeds, f, ensure_ascii=False, indent=2)

    def add_feed(self, name: str, fakeid: Optional[str] = None) -> Dict:
        """添加公众号到列表

        Args:
            name: 公众号名称
            fakeid: 公众号 fakeid（可选，如果不提供会自动搜索）

        Returns:
            添加的公众号信息
        """
        # 检查是否已存在
        for feed in self.feeds:
            if feed["name"] == name:
                return {"success": False, "message": f"公众号 {name} 已存在"}

        # 添加到列表
        new_feed = {"name": name}
        if fakeid:
            new_feed["fakeid"] = fakeid

        self.feeds.append(new_feed)
        self.save_feeds()

        return {"success": True, "message": f"✅ 已添加公众号: {name}", "feed": new_feed}

    def remove_feed(self, name: str) -> Dict:
        """从列表删除公众号

        Args:
            name: 公众号名称

        Returns:
            删除结果
        """
        original_count = len(self.feeds)
        self.feeds = [f for f in self.feeds if f["name"] != name]

        if len(self.feeds) < original_count:
            self.save_feeds()
            return {"success": True, "message": f"✅ 已删除公众号: {name}"}
        else:
            return {"success": False, "message": f"❌ 未找到公众号: {name}"}

    def list_feeds(self) -> List[Dict]:
        """获取公众号列表

        Returns:
            公众号列表
        """
        return self.feeds

    def fetch_all_feeds(self, count: int = 10) -> Dict:
        """批量抓取所有公众号的文章

        Args:
            count: 每个公众号抓取的文章数量

        Returns:
            抓取结果统计
        """
        if not self.feeds:
            return {"success": False, "message": "公众号列表为空"}

        results = {
            "success": True,
            "total": len(self.feeds),
            "succeeded": [],
            "failed": []
        }

        with WeChatMP() as mp:
            # 登录（如果需要）
            if not mp._is_logged_in:
                print("需要登录，请扫描二维码...")
                mp.login()

            # 遍历所有公众号
            for feed_config in self.feeds:
                name = feed_config["name"]

                try:
                    # 如果没有 fakeid，先搜索
                    if "fakeid" not in feed_config:
                        print(f"正在搜索公众号: {name}")
                        search_results = mp.search_feed(name)

                        if not search_results:
                            results["failed"].append({
                                "name": name,
                                "error": "未找到公众号"
                            })
                            continue

                        # 保存 fakeid
                        feed_config["fakeid"] = search_results[0]["fakeid"]
                        feed_config["nickname"] = search_results[0]["nickname"]
                        self.save_feeds()

                    fakeid = feed_config["fakeid"]
                    feed_name = feed_config.get("nickname", name)

                    # 抓取文章
                    print(f"正在抓取: {feed_name}")
                    articles = mp.fetch_articles(fakeid=fakeid, count=count)

                    if not articles:
                        results["failed"].append({
                            "name": feed_name,
                            "error": "未获取到文章"
                        })
                        continue

                    # 生成 JSON Feed
                    json_feed = mp.generate_json_feed(
                        mp_name=feed_name,
                        articles=articles,
                        feed_id=fakeid
                    )

                    # 保存到文件
                    output_file = os.path.join(self.output_dir, f"{feed_name}.json")
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(json_feed)

                    results["succeeded"].append({
                        "name": feed_name,
                        "articles_count": len(articles),
                        "output_file": output_file
                    })

                    print(f"✅ {feed_name}: {len(articles)} 篇文章")

                except Exception as e:
                    results["failed"].append({
                        "name": name,
                        "error": str(e)
                    })
                    print(f"❌ {name}: {e}")

        return results


def main():
    """示例：命令行使用"""
    manager = WXMPManager()

    # 添加公众号
    manager.add_feed("阮一峰的网络日志")
    manager.add_feed("datawhale")

    # 查看列表
    print("\n当前公众号列表:")
    for feed in manager.list_feeds():
        print(f"  - {feed['name']}")

    # 批量抓取
    print("\n开始批量抓取...")
    results = manager.fetch_all_feeds(count=5)

    # 输出结果
    print(f"\n抓取完成:")
    print(f"  成功: {len(results['succeeded'])}")
    print(f"  失败: {len(results['failed'])}")

    if results['succeeded']:
        print("\n成功的公众号:")
        for item in results['succeeded']:
            print(f"  ✅ {item['name']}: {item['articles_count']} 篇文章")

    if results['failed']:
        print("\n失败的公众号:")
        for item in results['failed']:
            print(f"  ❌ {item['name']}: {item['error']}")


if __name__ == "__main__":
    main()
