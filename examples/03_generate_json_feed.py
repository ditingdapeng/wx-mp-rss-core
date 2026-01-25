"""
生成 JSON Feed 示例 - 演示如何使用 wx-mp-rss-core 生成 JSON Feed

这个示例展示如何：
1. 生成基础 JSON Feed
2. 生成包含全文的 JSON Feed
3. 生成带 feed_id 的 JSON Feed
4. 自定义 JSON Feed 样式
"""

import logging
import json
from wx_rss import WeChatMP, JSONFeedGenerator

# 配置日志
logging.basicConfig(level=logging.INFO)


def example_basic_json_feed():
    """示例：生成基础 JSON Feed"""
    print("=" * 60)
    print("示例 1：生成基础 JSON Feed")
    print("=" * 60)

    with WeChatMP(token_file="wx_token.json") as mp:
        if not mp._is_logged_in:
            print("\n请先登录...")
            return

        # 获取文章
        fakeid = "MzAxMDAwMDAx"
        articles = mp.fetch_articles(fakeid=fakeid, count=5)

        # 生成 JSON Feed
        json_feed = mp.generate_json_feed(
            mp_name="我的公众号",
            mp_intro="这是我的公众号简介",
            articles=articles,
            base_url="https://example.com"
        )

        # 保存到文件
        filename = "feed_basic.json"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(json_feed)

        print(f"\n✅ JSON Feed 已生成: {filename}")
        print(f"   包含 {len(articles)} 篇文章")


def example_full_text_json_feed():
    """示例：生成包含全文的 JSON Feed"""
    print("\n" + "=" * 60)
    print("示例 2：生成包含全文的 JSON Feed")
    print("=" * 60)

    with WeChatMP(token_file="wx_token.json") as mp:
        if not mp._is_logged_in:
            print("\n请先登录...")
            return

        # 获取文章（包含正文）
        fakeid = "MzAxMDAwMDAx"
        articles = mp.fetch_articles(
            fakeid=fakeid,
            count=3,
            with_content=True
        )

        # 生成包含全文的 JSON Feed
        json_feed = mp.generate_json_feed(
            mp_name="我的公众号",
            mp_intro="这是我的公众号简介",
            articles=articles,
            full_text=True  # 包含全文
        )

        # 保存
        filename = "feed_fulltext.json"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(json_feed)

        print(f"\n✅ 全文 JSON Feed 已生成: {filename}")
        print(f"   包含 {len(articles)} 篇文章（含正文）")


def example_json_feed_with_id():
    """示例：生成带 feed_id 的 JSON Feed"""
    print("\n" + "=" * 60)
    print("示例 3：生成带 feed_id 的 JSON Feed")
    print("=" * 60)

    with WeChatMP(token_file="wx_token.json") as mp:
        if not mp._is_logged_in:
            print("\n请先登录...")
            return

        # 获取文章
        fakeid = "MzAxMDAwMDAx"
        articles = mp.fetch_articles(fakeid=fakeid, count=5)

        # 生成带 feed_id 的 JSON Feed
        json_feed = mp.generate_json_feed(
            mp_name="我的公众号",
            mp_intro="这是我的公众号简介",
            articles=articles,
            feed_id=fakeid  # 添加 feed_id
        )

        # 保存
        filename = "feed_with_id.json"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(json_feed)

        print(f"\n✅ 带 feed_id 的 JSON Feed 已生成: {filename}")
        print(f"   包含 {len(articles)} 篇文章")

        # 显示 feed_id 在文章中的位置
        feed_data = json.loads(json_feed)
        if feed_data.get("items"):
            first_item = feed_data["items"][0]
            if first_item.get("feed"):
                print(f"\n文章中的 feed 对象示例：")
                print(json.dumps(first_item["feed"], ensure_ascii=False, indent=2))


def example_custom_json_feed():
    """示例：自定义 JSON Feed 样式"""
    print("\n" + "=" * 60)
    print("示例 4：自定义 JSON Feed 样式")
    print("=" * 60)

    with WeChatMP(token_file="wx_token.json") as mp:
        if not mp._is_logged_in:
            print("\n请先登录...")
            return

        # 获取文章
        fakeid = "MzAxMDAwMDAx"
        articles = mp.fetch_articles(fakeid=fakeid, count=5)

        # 使用 JSONFeedGenerator 自定义生成
        generator = JSONFeedGenerator(
            mp_name="技术博客",
            mp_intro="分享技术文章和教程",
            base_url="https://myblog.com",
            mp_cover="https://example.com/cover.jpg"
        )

        # 生成自定义 JSON Feed
        json_feed = generator.generate(
            articles=articles,
            full_text=False,
            feed_id=fakeid
        )

        # 保存
        filename = "feed_custom.json"
        generator.save(json_feed, filename)

        print(f"\n✅ 自定义 JSON Feed 已生成: {filename}")
        print(f"   包含封面图片")
        print(f"   包含 {len(articles)} 篇文章")


def example_json_feed_with_metadata():
    """示例：添加元数据的 JSON Feed"""
    print("\n" + "=" * 60)
    print("示例 5：添加完整元数据的 JSON Feed")
    print("=" * 60)

    with WeChatMP(token_file="wx_token.json") as mp:
        if not mp._is_logged_in:
            print("\n请先登录...")
            return

        # 获取文章（包含正文）
        fakeid = "MzAxMDAwMDAx"
        articles = mp.fetch_articles(
            fakeid=fakeid,
            count=3,
            with_content=True
        )

        # 生成完整的 JSON Feed
        json_feed = mp.generate_json_feed(
            mp_name="我的公众号",
            mp_intro="这是我的公众号简介，专注于技术分享",
            articles=articles,
            base_url="https://example.com/feed",
            mp_cover="https://example.com/cover.jpg",
            full_text=True,
            feed_id=fakeid
        )

        # 保存
        filename = "feed_complete.json"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(json_feed)

        print(f"\n✅ 完整 JSON Feed 已生成: {filename}")
        print(f"   包含：封面、简介、全文、feed_id")
        print(f"   包含 {len(articles)} 篇文章")

        # 显示 JSON Feed 预览
        print("\nJSON Feed 预览（前800字符）：")
        print("-" * 60)
        print(json_feed[:800])
        print("...")


def main():
    """主函数"""
    print("wx-mp-rss-core 生成 JSON Feed 示例\n")
    print("注意：运行前请确保已经登录（ wx_token.json 存在）\n")

    # 示例 1：基础 JSON Feed
    try:
        example_basic_json_feed()
    except Exception as e:
        print(f"\n示例 1 出错: {e}")

    # 示例 2：全文 JSON Feed
    try:
        example_full_text_json_feed()
    except Exception as e:
        print(f"\n示例 2 出错: {e}")

    # 示例 3：带 feed_id
    try:
        example_json_feed_with_id()
    except Exception as e:
        print(f"\n示例 3 出错: {e}")

    # 示例 4：自定义 JSON Feed
    try:
        example_custom_json_feed()
    except Exception as e:
        print(f"\n示例 4 出错: {e}")

    # 示例 5：完整元数据
    try:
        example_json_feed_with_metadata()
    except Exception as e:
        print(f"\n示例 5 出错: {e}")


if __name__ == "__main__":
    main()
