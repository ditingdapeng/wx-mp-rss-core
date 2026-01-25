"""
错误处理示例 - 演示如何使用 wx-mp-rss-core 处理各种异常

这个示例展示如何：
1. 捕获和处理特定异常
2. 实现重试机制
3. 优雅地处理错误
"""

import logging
import time
from wx_rss import WeChatMP
from wx_rss.exceptions import (
    LoginError,
    QRCodeTimeoutError,
    FetchError,
    NetworkError,
    RateLimitError,
    TokenExpiredError,
    BrowserError
)

# 配置日志
logging.basicConfig(level=logging.INFO)


def example_basic_error_handling():
    """示例：基础错误处理"""
    print("=" * 60)
    print("示例 1：基础错误处理")
    print("=" * 60)

    try:
        mp = WeChatMP(token_file="wx_token.json")

        # 尝试登录
        if not mp._is_logged_in:
            print("\n正在登录...")
            result = mp.login(timeout=60)
            print(f"✅ 登录成功！")

    except LoginError as e:
        print(f"\n❌ 登录失败: {e}")
        print("建议：请检查网络连接或重新扫码")

    except QRCodeTimeoutError as e:
        print(f"\n❌ 二维码超时: {e}")
        print("建议：请在 60 秒内完成扫码")

    except BrowserError as e:
        print(f"\n❌ 浏览器错误: {e}")
        print("建议：请确保 Playwright 浏览器已正确安装")

    except Exception as e:
        print(f"\n❌ 未知错误: {e}")


def example_fetch_error_handling():
    """示例：抓取文章的错误处理"""
    print("\n" + "=" * 60)
    print("示例 2：抓取文章的错误处理")
    print("=" * 60)

    mp = WeChatMP(token_file="wx_token.json")

    try:
        if not mp._is_logged_in:
            print("\n未登录，跳过抓取示例")
            return

        # 尝试抓取文章
        fakeid = "MzAxMDAwMDAx"
        articles = mp.fetch_articles(fakeid=fakeid, count=5)
        print(f"\n✅ 成功获取 {len(articles)} 篇文章")

    except TokenExpiredError as e:
        print(f"\n❌ Token 已过期: {e}")
        print("建议：请删除 wx_token.json 后重新登录")

    except FetchError as e:
        print(f"\n❌ 抓取失败: {e}")
        print("建议：请检查 fakeid 是否正确")

    except NetworkError as e:
        print(f"\n❌ 网络错误: {e}")
        print("建议：请检查网络连接")

    except RateLimitError as e:
        print(f"\n❌ 频率限制: {e}")
        print("建议：请稍后再试")

    finally:
        mp.cleanup()


def example_retry_mechanism():
    """示例：实现重试机制"""
    print("\n" + "=" * 60)
    print("示例 3：实现重试机制")
    print("=" * 60)

    def fetch_with_retry(mp, fakeid, max_retries=3):
        """带重试的抓取函数"""
        for attempt in range(max_retries):
            try:
                print(f"\n尝试 {attempt + 1}/{max_retries}...")
                articles = mp.fetch_articles(fakeid=fakeid, count=5)
                print(f"✅ 成功获取 {len(articles)} 篇文章")
                return articles

            except NetworkError as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 指数退避: 1, 2, 4
                    print(f"⚠️  网络错误，{wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    print(f"❌ 网络错误，已达最大重试次数")
                    raise

            except RateLimitError as e:
                if attempt < max_retries - 1:
                    wait_time = 60  # 频率限制等待 60 秒
                    print(f"⚠️  频率限制，{wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    print(f"❌ 频率限制，已达最大重试次数")
                    raise

            except (TokenExpiredError, FetchError) as e:
                # 这些错误不应该重试
                print(f"❌ {type(e).__name__}: {e}")
                raise

    mp = WeChatMP(token_file="wx_token.json")

    if not mp._is_logged_in:
        print("\n未登录，跳过重试示例")
        mp.cleanup()
        return

    try:
        articles = fetch_with_retry(mp, "MzAxMDAwMDAx")
        print(f"\n最终成功获取 {len(articles)} 篇文章")
    except Exception as e:
        print(f"\n所有重试均失败: {e}")
    finally:
        mp.cleanup()


def example_batch_error_handling():
    """示例：批量处理的错误隔离"""
    print("\n" + "=" * 60)
    print("示例 4：批量处理的错误隔离")
    print("=" * 60)

    # 定义多个公众号
    feeds = [
        {"fakeid": "MzAxMDAwMDAx", "name": "公众号A"},
        {"fakeid": "MzAxMDAwMDAy", "name": "公众号B"},
        {"fakeid": "INVALID_ID", "name": "无效ID（测试错误）"},
        {"fakeid": "MzAxMDAwMDAz", "name": "公众号C"},
    ]

    mp = WeChatMP(token_file="wx_token.json")

    if not mp._is_logged_in:
        print("\n未登录，跳过批量处理示例")
        mp.cleanup()
        return

    results = {}

    print(f"\n处理 {len(feeds)} 个公众号...\n")

    for feed in feeds:
        try:
            print(f"正在处理: {feed['name']}")
            articles = mp.fetch_articles(
                fakeid=feed["fakeid"],
                count=5
            )
            results[feed['name']] = {
                'status': 'success',
                'articles': articles,
                'count': len(articles)
            }
            print(f"✅ {feed['name']}: {len(articles)} 篇")

        except TokenExpiredError as e:
            print(f"❌ {feed['name']}: Token 已过期")
            results[feed['name']] = {'status': 'error', 'error': str(e)}

        except FetchError as e:
            print(f"❌ {feed['name']}: 抓取失败")
            results[feed['name']] = {'status': 'error', 'error': str(e)}

        except Exception as e:
            print(f"❌ {feed['name']}: 未知错误 - {e}")
            results[feed['name']] = {'status': 'error', 'error': str(e)}

    mp.cleanup()

    # 汇总结果
    print("\n" + "=" * 60)
    print("处理结果汇总")
    print("=" * 60)

    success_count = sum(1 for r in results.values() if r['status'] == 'success')
    error_count = len(results) - success_count

    print(f"成功: {success_count}，失败: {error_count}\n")

    for name, result in results.items():
        status = "✅" if result['status'] == 'success' else "❌"
        if result['status'] == 'success':
            print(f"{status} {name}: {result['count']} 篇")
        else:
            print(f"{status} {name}: {result['error']}")


def example_context_manager_error_handling():
    """示例：使用 context manager 的错误处理"""
    print("\n" + "=" * 60)
    print("示例 5：使用 Context Manager 的错误处理")
    print("=" * 60)

    print("\n使用 context manager 可以自动清理资源，即使发生异常\n")

    try:
        with WeChatMP(token_file="wx_token.json") as mp:
            if not mp._is_logged_in:
                print("未登录，跳过示例")
                return

            articles = mp.fetch_articles(fakeid="MzAxMDAwMDAx", count=5)
            print(f"✅ 成功获取 {len(articles)} 篇文章")

            # 即使这里发生异常，cleanup 也会自动执行
            # raise Exception("模拟错误")

    except TokenExpiredError as e:
        print(f"\n❌ Token 已过期: {e}")
        print("资源已自动清理")

    except FetchError as e:
        print(f"\n❌ 抓取失败: {e}")
        print("资源已自动清理")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print("资源已自动清理")


def example_logging_errors():
    """示例：记录错误日志"""
    print("\n" + "=" * 60)
    print("示例 6：记录错误日志")
    print("=" * 60)

    # 配置日志到文件
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('wx_rss_errors.log'),
            logging.StreamHandler()
        ]
    )

    logger = logging.getLogger("wx_rss_example")

    try:
        mp = WeChatMP(token_file="wx_token.json")

        if not mp._is_logged_in:
            print("\n未登录，跳过示例")
            return

        articles = mp.fetch_articles(fakeid="MzAxMDAwMDAx", count=5)
        print(f"\n✅ 成功获取 {len(articles)} 篇文章")

    except TokenExpiredError as e:
        logger.error(f"Token 已过期: {e}")
        print("\n❌ 错误已记录到日志文件")

    except FetchError as e:
        logger.error(f"抓取失败: {e}")
        print("\n❌ 错误已记录到日志文件")

    finally:
        mp.cleanup()


def main():
    """主函数"""
    print("wx-mp-rss-core 错误处理示例\n")
    print("注意：运行前请确保已经登录（ wx_token.json 存在）\n")

    # 示例 1：基础错误处理
    try:
        example_basic_error_handling()
    except Exception as e:
        print(f"\n示例 1 出错: {e}")

    # 示例 2：抓取错误处理
    try:
        example_fetch_error_handling()
    except Exception as e:
        print(f"\n示例 2 出错: {e}")

    # 示例 3：重试机制
    try:
        example_retry_mechanism()
    except Exception as e:
        print(f"\n示例 3 出错: {e}")

    # 示例 4：批量错误隔离
    try:
        example_batch_error_handling()
    except Exception as e:
        print(f"\n示例 4 出错: {e}")

    # 示例 5：Context Manager
    try:
        example_context_manager_error_handling()
    except Exception as e:
        print(f"\n示例 5 出错: {e}")

    # 示例 6：日志记录
    try:
        example_logging_errors()
    except Exception as e:
        print(f"\n示例 6 出错: {e}")


if __name__ == "__main__":
    main()
