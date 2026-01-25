"""
抓取文章示例 - 演示如何使用 wx-mp-rss-core 抓取公众号文章

这个示例展示如何：
1. 初始化文章抓取器
2. 获取文章列表
3. 获取包含正文的文章
"""

import logging
from wx_rss import WeChatMP

# 配置日志
logging.basicConfig(level=logging.INFO)


def example_fetch_articles():
    """示例：获取文章列表"""
    print("=" * 60)
    print("示例 1：获取文章列表")
    print("=" * 60)

    # 使用 context manager
    with WeChatMP(token_file="wx_token.json") as mp:
        # 检查登录状态
        if not mp._is_logged_in:
            print("\n请先登录...")
            return

        # 获取文章列表
        fakeid = "MzAxMDAwMDAx"  # 替换为实际的 fakeid
        articles = mp.fetch_articles(fakeid=fakeid, count=5)

        print(f"\n成功获取 {len(articles)} 篇文章：\n")

        for i, article in enumerate(articles, 1):
            print(f"{i}. {article['title']}")
            print(f"   链接: {article['url']}")
            print(f"   发布时间: {article['publish_time']}")
            print(f"   摘要: {article['digest'][:50]}...")
            print()


def example_fetch_with_content():
    """示例：获取包含正文的文章"""
    print("\n" + "=" * 60)
    print("示例 2：获取包含正文的文章")
    print("=" * 60)

    with WeChatMP(token_file="wx_token.json") as mp:
        if not mp._is_logged_in:
            print("\n请先登录...")
            return

        # 获取包含正文的文章
        fakeid = "MzAxMDAwMDAx"
        articles = mp.fetch_articles(
            fakeid=fakeid,
            count=3,
            with_content=True  # 包含正文内容
        )

        print(f"\n成功获取 {len(articles)} 篇文章（含正文）：\n")

        for i, article in enumerate(articles, 1):
            print(f"{i}. {article['title']}")
            print(f"   正文长度: {len(article.get('content', ''))} 字符")
            if article.get('content'):
                # 显示正文前100个字符
                import re
                content_text = re.sub(r'<[^>]+>', '', article['content'])
                print(f"   正文预览: {content_text[:100]}...")
            print()


def example_batch_fetch():
    """示例：批量获取多个公众号的文章"""
    print("\n" + "=" * 60)
    print("示例 3：批量获取多个公众号的文章")
    print("=" * 60)

    # 定义多个公众号
    feeds = [
        {"fakeid": "MzAxMDAwMDAx", "name": "公众号A"},
        {"fakeid": "MzAxMDAwMDAy", "name": "公众号B"},
    ]

    with WeChatMP(token_file="wx_token.json") as mp:
        if not mp._is_logged_in:
            print("\n请先登录...")
            return

        results = {}

        for feed in feeds:
            try:
                print(f"\n正在获取: {feed['name']}")
                articles = mp.fetch_articles(
                    fakeid=feed["fakeid"],
                    count=5
                )
                results[feed['name']] = articles
                print(f"✅ 成功获取 {len(articles)} 篇文章")

            except Exception as e:
                print(f"❌ 失败: {e}")
                results[feed['name']] = []

        # 汇总结果
        print("\n" + "=" * 60)
        print("汇总结果")
        print("=" * 60)
        total = sum(len(articles) for articles in results.values())
        print(f"总共获取 {total} 篇文章")
        for name, articles in results.items():
            print(f"  {name}: {len(articles)} 篇")


def example_fetch_with_pagination():
    """示例：分页获取文章"""
    print("\n" + "=" * 60)
    print("示例 4：分页获取文章")
    print("=" * 60)

    with WeChatMP(token_file="wx_token.json") as mp:
        if not mp._is_logged_in:
            print("\n请先登录...")
            return

        fakeid = "MzAxMDAwMDAx"
        all_articles = []
        page_size = 5
        max_pages = 2

        for page in range(max_pages):
            begin = page * page_size
            print(f"\n获取第 {page + 1} 页（起始位置: {begin}）...")

            try:
                articles = mp.fetch_articles(
                    fakeid=fakeid,
                    count=page_size,
                    begin=begin
                )

                if not articles:
                    print("没有更多文章了")
                    break

                all_articles.extend(articles)
                print(f"✅ 获取了 {len(articles)} 篇文章")

            except Exception as e:
                print(f"❌ 获取失败: {e}")
                break

        print(f"\n总共获取 {len(all_articles)} 篇文章")


def main():
    """主函数"""
    print("wx-mp-rss-core 抓取文章示例\n")
    print("注意：运行前请确保已经登录（ wx_token.json 存在）\n")

    # 示例 1：获取文章列表
    try:
        example_fetch_articles()
    except Exception as e:
        print(f"\n示例 1 出错: {e}")

    # 示例 2：获取包含正文的文章
    try:
        example_fetch_with_content()
    except Exception as e:
        print(f"\n示例 2 出错: {e}")

    # 示例 3：批量获取
    try:
        example_batch_fetch()
    except Exception as e:
        print(f"\n示例 3 出错: {e}")

    # 示例 4：分页获取
    try:
        example_fetch_with_pagination()
    except Exception as e:
        print(f"\n示例 4 出错: {e}")


if __name__ == "__main__":
    main()
