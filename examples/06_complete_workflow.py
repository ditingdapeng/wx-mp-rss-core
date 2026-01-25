"""
完整流程示例 - wx-mp-rss-core 使用示例

演示如何使用 wx-mp-rss-core 进行微信公众号文章抓取和 JSON Feed 生成
"""

import logging
from wx_rss import WeChatMP

# 配置日志
logging.basicConfig(level=logging.INFO)


def example_single_feed():
    """示例：获取单个公众号的 JSON Feed"""
    print("=" * 60)
    print("示例 1：获取单个公众号的 JSON Feed")
    print("=" * 60)

    # 使用 context manager 自动管理资源
    with WeChatMP() as mp:
        # 1. 登录（如果未登录）
        if not mp._is_logged_in:
            print("\n请使用微信扫描生成的二维码登录...")
            mp.login()

        # 2. 获取文章
        fakeid = "MzAxMDAwMDAx"  # 替换为实际的 fakeid
        articles = mp.fetch_articles(fakeid=fakeid, count=5)

        print(f"\n成功获取 {len(articles)} 篇文章")

        # 3. 生成 JSON Feed
        json_feed = mp.generate_json_feed(
            mp_name="我的公众号",
            articles=articles,
            mp_intro="这是我的公众号简介",
            base_url="https://example.com",
            feed_id=fakeid
        )

        # 4. 保存到文件
        filename = "feed.json"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(json_feed)

        print(f"JSON Feed 已保存到: {filename}")


def example_multi_feeds():
    """示例：获取多个公众号的 JSON Feed"""
    print("\n" + "=" * 60)
    print("示例 2：获取多个公众号的 JSON Feed")
    print("=" * 60)

    # 定义多个公众号
    feeds = [
        {"fakeid": "MzAxMDAwMDAx", "name": "公众号A", "intro": "简介A"},
        {"fakeid": "MzAxMDAwMDAy", "name": "公众号B", "intro": "简介B"},
    ]

    with WeChatMP() as mp:
        # 1. 登录（如果未登录）
        if not mp._is_logged_in:
            print("\n请使用微信扫描生成的二维码登录...")
            mp.login()

        # 2. 批量获取文章并生成 JSON Feed
        for feed in feeds:
            try:
                print(f"\n正在处理: {feed['name']}")

                articles = mp.fetch_articles(
                    fakeid=feed["fakeid"],
                    count=5
                )

                json_feed = mp.generate_json_feed(
                    mp_name=feed["name"],
                    articles=articles,
                    mp_intro=feed["intro"],
                    feed_id=feed["fakeid"]
                )

                filename = f"{feed['name']}.json"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(json_feed)

                print(f"✅ 成功: {feed['name']} -> {filename}")

            except Exception as e:
                print(f"❌ 失败: {feed['name']} - {e}")


def example_with_content():
    """示例：获取包含正文的文章"""
    print("\n" + "=" * 60)
    print("示例 3：获取包含正文内容的 JSON Feed")
    print("=" * 60)

    with WeChatMP() as mp:
        # 1. 登录（如果未登录）
        if not mp._is_logged_in:
            print("\n请使用微信扫描生成的二维码登录...")
            mp.login()

        # 2. 获取文章（包含正文）
        fakeid = "MzAxMDAwMDAx"
        articles = mp.fetch_articles(
            fakeid=fakeid,
            count=3,
            with_content=True  # 包含正文内容
        )

        print(f"\n成功获取 {len(articles)} 篇文章（含正文）")

        # 3. 生成 JSON Feed（包含全文）
        json_feed = mp.generate_json_feed(
            mp_name="我的公众号",
            articles=articles,
            full_text=True,  # 包含全文
            feed_id=fakeid
        )

        # 4. 保存
        filename = "feed_full.json"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(json_feed)

        print(f"JSON Feed 已保存到: {filename}")


def main():
    """主函数"""
    print("wx-mp-rss-core 使用示例\n")

    # 示例 1：单个公众号
    try:
        example_single_feed()
    except Exception as e:
        print(f"\n示例 1 出错: {e}")

    # 示例 2：多个公众号
    try:
        example_multi_feeds()
    except Exception as e:
        print(f"\n示例 2 出错: {e}")

    # 示例 3：包含正文
    try:
        example_with_content()
    except Exception as e:
        print(f"\n示例 3 出错: {e}")


if __name__ == "__main__":
    main()
