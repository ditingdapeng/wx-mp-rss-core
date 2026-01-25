"""
登录示例 - 演示如何使用 wx-mp-rss-core 进行微信登录

这个示例展示如何：
1. 初始化登录认证器
2. 执行登录流程
3. 保存和加载凭证
"""

import logging
from wx_rss import WeChatAuth

# 配置日志
logging.basicConfig(level=logging.INFO)


def example_basic_login():
    """基础登录示例"""
    print("=" * 60)
    print("示例 1：基础登录流程")
    print("=" * 60)

    # 初始化认证器
    auth = WeChatAuth(token_file="wx_token.json")

    try:
        # 执行登录
        print("\n正在启动浏览器...")
        result = auth.login(timeout=60)

        print(f"\n登录成功！")
        print(f"Token: {result['token'][:20]}...")
        print(f"Cookies 数量: {len(result['cookies'])}")
        print(f"登录状态: {result['is_logged_in']}")

    except Exception as e:
        print(f"\n登录失败: {e}")
    finally:
        # 清理资源
        auth.cleanup()


def example_load_credentials():
    """加载已保存的凭证示例"""
    print("\n" + "=" * 60)
    print("示例 2：加载已保存的凭证")
    print("=" * 60)

    auth = WeChatAuth(token_file="wx_token.json")

    # 尝试加载凭证
    if auth.load_credentials():
        print("\n✅ 成功加载已保存的凭证")
        print(f"Token: {auth.token[:20] if auth.token else 'None'}...")
        print(f"登录状态: {auth.check_login_status()}")
    else:
        print("\n❌ 未找到已保存的凭证，需要重新登录")


def example_qrcode_only():
    """只获取二维码示例"""
    print("\n" + "=" * 60)
    print("示例 3：获取登录二维码")
    print("=" * 60)

    auth = WeChatAuth(token_file="wx_token.json")

    try:
        # 只获取二维码，不等待扫码
        qrcode_path = auth.get_qrcode()
        print(f"\n二维码已保存到: {qrcode_path}")
        print("请使用微信扫描二维码登录")

        # 这里可以自定义等待逻辑
        import time
        print("\n等待扫码中...")
        for i in range(10):
            time.sleep(3)
            if auth.check_login_status():
                print("✅ 检测到登录成功！")
                break
            print(f"等待中... ({i+1}/10)")

    except Exception as e:
        print(f"\n获取二维码失败: {e}")
    finally:
        auth.cleanup()


def example_context_manager():
    """使用 context manager 示例（推荐）"""
    print("\n" + "=" * 60)
    print("示例 4：使用 Context Manager")
    print("=" * 60)

    # 自动管理资源
    with WeChatAuth(token_file="wx_token.json") as auth:
        try:
            result = auth.login(timeout=60)
            print(f"\n登录成功！")
            print(f"Token: {result['token'][:20]}...")
        except Exception as e:
            print(f"\n登录失败: {e}")

    # 自动清理资源（即使发生异常）


def main():
    """主函数"""
    print("wx-mp-rss-core 登录示例\n")

    # 示例 1：基础登录
    try:
        example_basic_login()
    except Exception as e:
        print(f"\n示例 1 出错: {e}")

    # 示例 2：加载凭证
    try:
        example_load_credentials()
    except Exception as e:
        print(f"\n示例 2 出错: {e}")

    # 示例 3：获取二维码
    # 注释掉以避免重复登录
    # try:
    #     example_qrcode_only()
    # except Exception as e:
    #     print(f"\n示例 3 出错: {e}")

    # 示例 4：Context Manager
    # 注释掉以避免重复登录
    # try:
    #     example_context_manager()
    # except Exception as e:
    #     print(f"\n示例 4 出错: {e}")


if __name__ == "__main__":
    main()
