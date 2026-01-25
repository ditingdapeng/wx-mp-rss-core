"""
多公众号示例 - 演示如何使用 wx-mp-rss-core 处理多个公众号

这个示例展示如何：
1. 为每个公众号生成独立的 JSON Feed
2. 生成聚合 JSON Feed
3. 批量处理多个公众号
"""

import logging
from wx_rss import WeChatMP

# 配置日志
logging.basicConfig(level=logging.INFO)


def example_individual_feeds():
    """示例：为每个公众号生成独立的 JSON Feed"""
    print("=" * 60)
    print("示例 1：为每个公众号生成独立的 JSON Feed")
    print("=" * 60)

    # 定义多个公众号
    feeds = [
        {
            "fakeid": "MzAxMDAwMDAx",
            "name": "技术博客",
            "intro": "分享技术文章和教程"
        },
        {
            "fakeid": "MzAxMDAwMDAy",
            "name": "产品思考",
            "intro": "产品设计与用户体验"
        },
        {
            "fakeid": "MzAxMDAwMDAz",
            "name": "行业观察",
            "intro": "行业动态与分析"
        },
    ]

    with WeChatMP(token_file="wx_token.json") as mp:
        if not mp._is_logged_in:
            print("\n请先登录...")
            return

        print(f"\n开始处理 {len(feeds)} 个公众号...\n")

        results = []

        for feed in feeds:
            try:
                print(f"正在处理: {feed['name']}")

                # 获取文章
                articles = mp.fetch_articles(
                    fakeid=feed["fakeid"],
                    count=5
                )

                # 生成 JSON Feed
                json_feed = mp.generate_json_feed(
                    mp_name=feed['name'],
                    mp_intro=feed['intro'],
                    articles=articles,
                    base_url=f"https://example.com/{feed['name']}",
                    feed_id=feed["fakeid"]
                )

                # 保存
                filename = f"feeds/{feed['name']}.json"
                import os
                os.makedirs("feeds", exist_ok=True)

                with open(filename, "w", encoding="utf-8") as f:
                    f.write(json_feed)

                print(f"✅ {feed['name']} -> {filename} ({len(articles)} 篇)")
                results.append({
                    "name": feed['name'],
                    "filename": filename,
                    "count": len(articles)
                })

            except Exception as e:
                print(f"❌ {feed['name']} 失败: {e}")
                results.append({
                    "name": feed['name'],
                    "filename": None,
                    "count": 0
                })

        # 汇总结果
        print("\n" + "=" * 60)
        print("处理结果汇总")
        print("=" * 60)
        success_count = sum(1 for r in results if r['filename'])
        print(f"成功: {success_count}/{len(feeds)}")
        for r in results:
            status = "✅" if r['filename'] else "❌"
            print(f"  {status} {r['name']}: {r['count']} 篇")


def example_aggregated_feed():
    """示例：生成聚合 JSON Feed"""
    print("\n" + "=" * 60)
    print("示例 2：生成聚合 JSON Feed")
    print("=" * 60)

    # 定义多个公众号
    feeds = [
        {"fakeid": "MzAxMDAwMDAx", "name": "技术博客"},
        {"fakeid": "MzAxMDAwMDAy", "name": "产品思考"},
        {"fakeid": "MzAxMDAwMDAz", "name": "行业观察"},
    ]

    with WeChatMP(token_file="wx_token.json") as mp:
        if not mp._is_logged_in:
            print("\n请先登录...")
            return

        all_articles = []
        feed_counts = {}

        print(f"\n开始获取 {len(feeds)} 个公众号的文章...\n")

        # 获取所有公众号的文章
        for feed in feeds:
            try:
                print(f"正在获取: {feed['name']}")
                articles = mp.fetch_articles(
                    fakeid=feed["fakeid"],
                    count=5
                )

                all_articles.extend(articles)
                feed_counts[feed['name']] = len(articles)
                print(f"✅ {feed['name']}: {len(articles)} 篇")

            except Exception as e:
                print(f"❌ {feed['name']} 失败: {e}")
                feed_counts[feed['name']] = 0

        # 生成聚合 JSON Feed
        if all_articles:
            # 按发布时间排序
            all_articles.sort(key=lambda x: x.get('publish_time', 0), reverse=True)

            json_feed = mp.generate_json_feed(
                mp_name="我的订阅聚合",
                mp_intro=f"来自 {len(feeds)} 个公众号的聚合订阅",
                articles=all_articles,
                base_url="https://example.com/aggregated"
            )

            # 保存
            filename = "feeds/aggregated.json"
            import os
            os.makedirs("feeds", exist_ok=True)

            with open(filename, "w", encoding="utf-8") as f:
                f.write(json_feed)

            print("\n" + "=" * 60)
            print("聚合结果")
            print("=" * 60)
            print(f"✅ 聚合 JSON Feed: {filename}")
            print(f"   总文章数: {len(all_articles)} 篇")
            for name, count in feed_counts.items():
                print(f"   {name}: {count} 篇")
        else:
            print("\n❌ 没有获取到任何文章")


def example_both_feeds():
    """示例：同时生成独立和聚合 JSON Feed"""
    print("\n" + "=" * 60)
    print("示例 3：同时生成独立和聚合 JSON Feed")
    print("=" * 60)

    feeds = [
        {"fakeid": "MzAxMDAwMDAx", "name": "公众号A", "intro": "简介A"},
        {"fakeid": "MzAxMDAwMDAy", "name": "公众号B", "intro": "简介B"},
    ]

    with WeChatMP(token_file="wx_token.json") as mp:
        if not mp._is_logged_in:
            print("\n请先登录...")
            return

        all_articles = []

        # 为每个公众号生成独立 JSON Feed
        print("\n生成独立 JSON Feed：\n")
        for feed in feeds:
            try:
                articles = mp.fetch_articles(
                    fakeid=feed["fakeid"],
                    count=5
                )
                all_articles.extend(articles)

                json_feed = mp.generate_json_feed(
                    mp_name=feed['name'],
                    mp_intro=feed['intro'],
                    articles=articles,
                    feed_id=feed["fakeid"]
                )

                filename = f"feeds/{feed['name']}.json"
                import os
                os.makedirs("feeds", exist_ok=True)

                with open(filename, "w", encoding="utf-8") as f:
                    f.write(json_feed)

                print(f"✅ {feed['name']}: {len(articles)} 篇")

            except Exception as e:
                print(f"❌ {feed['name']}: {e}")

        # 生成聚合 JSON Feed
        if all_articles:
            all_articles.sort(key=lambda x: x.get('publish_time', 0), reverse=True)

            aggregated_feed = mp.generate_json_feed(
                mp_name="全部订阅",
                mp_intro="所有公众号的聚合",
                articles=all_articles
            )

            filename = "feeds/all.json"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(aggregated_feed)

            print(f"\n✅ 聚合 JSON Feed: {filename} ({len(all_articles)} 篇)")


def example_categories():
    """示例：按类别生成 JSON Feed"""
    print("\n" + "=" * 60)
    print("示例 4：按类别生成 JSON Feed")
    print("=" * 60)

    # 按类别分组
    categories = {
        "技术": [
            {"fakeid": "MzAxMDAwMDAx", "name": "后端技术"},
            {"fakeid": "MzAxMDAwMDAy", "name": "前端开发"},
        ],
        "产品": [
            {"fakeid": "MzAxMDAwMDAz", "name": "产品经理"},
            {"fakeid": "MzAxMDAwMDA0", "name": "用户体验"},
        ]
    }

    with WeChatMP(token_file="wx_token.json") as mp:
        if not mp._is_logged_in:
            print("\n请先登录...")
            return

        import os
        os.makedirs("feeds", exist_ok=True)

        for category, feeds in categories.items():
            print(f"\n处理类别: {category}")
            category_articles = []

            for feed in feeds:
                try:
                    articles = mp.fetch_articles(
                        fakeid=feed["fakeid"],
                        count=3
                    )
                    category_articles.extend(articles)
                    print(f"  ✅ {feed['name']}: {len(articles)} 篇")
                except Exception as e:
                    print(f"  ❌ {feed['name']}: {e}")

            # 生成类别聚合 JSON Feed
            if category_articles:
                category_articles.sort(key=lambda x: x.get('publish_time', 0), reverse=True)

                json_feed = mp.generate_json_feed(
                    mp_name=f"{category}类聚合",
                    mp_intro=f"{category}相关公众号的聚合",
                    articles=category_articles
                )

                filename = f"feeds/{category}.json"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(json_feed)

                print(f"  ✅ 类别 JSON Feed: {filename} ({len(category_articles)} 篇)")


def main():
    """主函数"""
    print("wx-mp-rss-core 多公众号示例\n")
    print("注意：运行前请确保已经登录（ wx_token.json 存在）\n")

    # 示例 1：独立 JSON Feed
    try:
        example_individual_feeds()
    except Exception as e:
        print(f"\n示例 1 出错: {e}")

    # 示例 2：聚合 JSON Feed
    try:
        example_aggregated_feed()
    except Exception as e:
        print(f"\n示例 2 出错: {e}")

    # 示例 3：同时生成
    try:
        example_both_feeds()
    except Exception as e:
        print(f"\n示例 3 出错: {e}")

    # 示例 4：按类别
    try:
        example_categories()
    except Exception as e:
        print(f"\n示例 4 出错: {e}")


if __name__ == "__main__":
    main()
