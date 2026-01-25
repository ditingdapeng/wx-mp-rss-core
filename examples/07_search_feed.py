"""
搜索公众号示例 - 演示如何通过公众号名称获取 fakeid

这个示例展示如何：
1. 搜索公众号
2. 获取 fakeid
3. 使用 fakeid 抓取文章
"""

import logging
from wx_rss import WeChatMP

# 配置日志
logging.basicConfig(level=logging.INFO)


def example_search_and_fetch():
    """示例：搜索公众号并抓取文章"""
    print("=" * 60)
    print("示例：搜索公众号并抓取文章")
    print("=" * 60)

    with WeChatMP() as mp:
        # 1. 登录（如果未登录）
        if not mp._is_logged_in:
            print("\n请使用微信扫描生成的二维码登录...")
            mp.login()

        # 2. 搜索公众号
        keyword = "精神抖擞王大鹏"  # 替换为你要搜索的公众号名称
        print(f"\n正在搜索公众号: {keyword}")

        try:
            results = mp.search_feed(keyword, limit=5)

            print(f"\n找到 {len(results)} 个相关公众号：\n")
            for i, feed in enumerate(results, 1):
                print(f"{i}. {feed['nickname']}")
                print(f"   fakeid: {feed['fakeid']}")
                print(f"   简介: {feed['signature']}")
                print(f"   头像: {feed['round_head_img']}")
                print()

            if not results:
                print("未找到匹配的公众号")
                return

            # 3. 使用第一个公众号的 fakeid 抓取文章
            fakeid = results[0]['fakeid']
            feed_name = results[0]['nickname']

            print(f"正在��取 '{feed_name}' 的文章...")
            articles = mp.fetch_articles(fakeid=fakeid, count=5)

            print(f"\n成功获取 {len(articles)} 篇文章：\n")
            for i, article in enumerate(articles, 1):
                print(f"{i}. {article['title']}")
                print(f"   发布时间: {article['publish_time']}")
                print()

        except Exception as e:
            print(f"\n搜索失败: {e}")


def example_quick_get_fakeid():
    """示例：快速获取 fakeid"""
    print("\n" + "=" * 60)
    print("示例：快速获取 fakeid")
    print("=" * 60)

    with WeChatMP() as mp:
        if not mp._is_logged_in:
            print("\n请使用微信扫描生成的二维码登录...")
            mp.login()

        # 直接获取第一个匹配的 fakeid
        keyword = "精神抖擞王大鹏"
        print(f"\n正在搜索: {keyword}")

        fakeid = mp.get_feed_fakeid(keyword)

        if fakeid:
            print(f"✅ 找到 fakeid: {fakeid}")

            # 立即抓取文章
            articles = mp.fetch_articles(fakeid=fakeid, count=3)
            print(f"✅ 成功获取 {len(articles)} 篇文章")
        else:
            print(f"❌ 未找到公众号: {keyword}")


def example_batch_search():
    """示例：批量搜索多个公众号"""
    print("\n" + "=" * 60)
    print("示例：批量搜索多个公众号")
    print("=" * 60)

    # 要搜索的公众号列表
    keywords = [
        "阮一峰的网络日志",
        "美团技术团队",
        "阿里技术"
    ]

    with WeChatMP() as mp:
        if not mp._is_logged_in:
            print("\n请使用微信扫描生成的二维码登录...")
            mp.login()

        results_map = {}

        for keyword in keywords:
            try:
                print(f"\n搜索: {keyword}")
                fakeid = mp.get_feed_fakeid(keyword)

                if fakeid:
                    results_map[keyword] = fakeid
                    print(f"✅ 找到: {fakeid}")
                else:
                    print(f"❌ 未找到")
                    results_map[keyword] = None

            except Exception as e:
                print(f"❌ 搜索失败: {e}")
                results_map[keyword] = None

        # 汇总结果
        print("\n" + "=" * 60)
        print("搜索结果汇总")
        print("=" * 60)

        for keyword, fakeid in results_map.items():
            if fakeid:
                print(f"✅ {keyword}: {fakeid}")
            else:
                print(f"❌ {keyword}: 未找到")


def main():
    """主函数"""
    print("wx-mp-rss-core 搜索公众号示例\n")

    # 示例 1：搜索并抓取
    try:
        example_search_and_fetch()
    except Exception as e:
        print(f"\n示例 1 出错: {e}")

    # 示例 2：快速获取 fakeid
    try:
        example_quick_get_fakeid()
    except Exception as e:
        print(f"\n示例 2 出错: {e}")

    # 示例 3：批量搜索
    try:
        example_batch_search()
    except Exception as e:
        print(f"\n示例 3 出错: {e}")


if __name__ == "__main__":
    main()
