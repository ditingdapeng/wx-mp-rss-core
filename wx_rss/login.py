"""
登录模块

提供微信扫码登录功能，基于 Playwright 浏览器自动化
"""

import os
import time
import json
from typing import Optional, Dict, Any
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright, Browser, Page
except ImportError:
    raise ImportError(
        "Playwright 未安装，请运行: pip install playwright && python -m playwright install firefox"
    )

from .logger import get_logger
from .exceptions import LoginError, QRCodeTimeoutError, BrowserError


class WeChatAuth:
    """微信登录认证类"""

    WX_LOGIN_URL = "https://mp.weixin.qq.com/"
    WX_HOME_URL = "https://mp.weixin.qq.com/cgi-bin/home"
    QR_CODE_FILE = "static/wx_qrcode.png"
    TOKEN_FILE = "wx_token.json"

    def __init__(self, token_file: str = None, qrcode_file: str = None):
        """初始化

        Args:
            token_file: Token 保存��件路径
            qrcode_file: 二维码图片保存路径
        """
        self.token_file = token_file or self.TOKEN_FILE
        self.qrcode_file = qrcode_file or self.QR_CODE_FILE
        self.token: Optional[str] = None
        self.cookies: Dict[str, str] = {}
        self._browser: Optional[Browser] = None
        self._page: Optional[Page] = None
        self._playwright = None
        self._logger = get_logger("wx_rss.login")

        # 确保目录存在
        Path(self.qrcode_file).parent.mkdir(parents=True, exist_ok=True)

    def login(self, timeout: int = 180) -> Dict[str, Any]:
        """执行登录流程

        Args:
            timeout: 二维码超时时间（秒）

        Returns:
            登录信息字典：{
                "token": str,
                "cookies": dict,
                "fakeid": str,
                "is_logged_in": bool
            }

        Raises:
            LoginError: 登录失败
            QRCodeTimeoutError: 二维码超时
            BrowserError: 浏览器错误
        """
        self._logger.info("开始登录流程...")

        try:
            # 启动浏览器
            self._start_browser()

            # 打开登录页面
            self._open_login_page()

            # 获取二维码
            self._get_qrcode()

            # 等待扫码
            self._wait_for_scan(timeout)

            # 提取 Token 和 Cookies
            self._extract_credentials()

            return {
                "token": self.token,
                "cookies": self.cookies,
                "fakeid": "",  # 从页面中提取
                "is_logged_in": True
            }

        except Exception as e:
            self._logger.error(f"登录失败: {e}")
            raise LoginError(f"登录失败: {e}") from e

        finally:
            # 登录成功后不关闭浏览器，由调用者决定
            pass

    def get_qrcode(self) -> str:
        """获取登录二维码

        Returns:
            二维码图片文件路径

        Raises:
            LoginError: 获取二维码失败
        """
        try:
            self._start_browser()
            self._open_login_page()
            self._get_qrcode()
            return self.qrcode_file
        except Exception as e:
            raise LoginError(f"获取二维码失败: {e}") from e

    def check_login_status(self) -> bool:
        """检查登录状态

        Returns:
            是否已登录
        """
        return self.token is not None and len(self.cookies) > 0

    def load_credentials(self) -> bool:
        """从文件加载凭证

        Returns:
            是否成功加载
        """
        if not os.path.exists(self.token_file):
            return False

        try:
            with open(self.token_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.token = data.get("token")
                self.cookies = data.get("cookies", {})
                self._logger.info("从文件加载凭证成功")
                return True
        except Exception as e:
            self._logger.error(f"加载凭证失败: {e}")
            return False

    def save_credentials(self) -> None:
        """保存凭证到文件"""
        try:
            data = {
                "token": self.token,
                "cookies": self.cookies,
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%S")
            }
            with open(self.token_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self._logger.info("凭证已保存")
        except Exception as e:
            self._logger.error(f"保存凭证失败: {e}")

    def cleanup(self) -> None:
        """清理浏览器资源"""
        if self._page:
            try:
                self._page.close()
                self._logger.debug("页面已关闭")
            except Exception as e:
                self._logger.warning(f"关闭页面失败: {e}")
            self._page = None

        if self._browser:
            try:
                self._browser.close()
                self._logger.debug("浏览器已关闭")
            except Exception as e:
                self._logger.warning(f"关闭浏览器失败: {e}")
            self._browser = None

        if self._playwright:
            try:
                self._playwright.stop()
                self._logger.debug("Playwright 已停止")
            except Exception as e:
                self._logger.warning(f"停止 Playwright 失败: {e}")
            self._playwright = None

    def __enter__(self):
        """Context manager 入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 出口"""
        self.cleanup()

    # 私有方法

    def _start_browser(self) -> None:
        """启动浏览器"""
        if self._browser is None:
            self._logger.info("正在启动浏览器...")
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.firefox.launch(headless=True)
            self._page = self._browser.new_page()
            self._logger.info("浏览器启动成功")

    def _open_login_page(self) -> None:
        """打开登录页面"""
        self._logger.info(f"正在打开登录页面: {self.WX_LOGIN_URL}")
        self._page.goto(self.WX_LOGIN_URL)
        self._page.wait_for_load_state("networkidle")

    def _get_qrcode(self) -> None:
        """获取并保存二维码"""
        try:
            # 等待二维码加载
            qrcode_selector = ".login__type__container__scan__qrcode"
            self._page.wait_for_selector(qrcode_selector, timeout=10000)

            # 截图保存二维码
            qrcode_element = self._page.locator(qrcode_selector)
            qrcode_element.screenshot(path=self.qrcode_file)

            self._logger.info(f"二维码已保存: {self.qrcode_file}")

            # 在终端显示二维码
            self._display_qrcode_in_terminal()

            # 验证二维码图片
            if not os.path.exists(self.qrcode_file) or os.path.getsize(self.qrcode_file) < 1000:
                raise BrowserError("二维码图片获取失败")

        except Exception as e:
            raise BrowserError(f"获取二维码失败: {e}") from e

    def _wait_for_scan(self, timeout: int = 180) -> None:
        """等待扫码登录

        Args:
            timeout: 超时时间（秒）

        Raises:
            QRCodeTimeoutError: 扫码超时
        """
        self._logger.info(f"等待扫码登录（{timeout}秒超时）...")

        start_time = time.time()
        check_interval = 2  # 每2秒检查一次

        while time.time() - start_time < timeout:
            try:
                # 检查是否跳转到首页
                current_url = self._page.url
                if self.WX_HOME_URL in current_url or "home" in current_url:
                    self._logger.info("检测到登录成功跳转")
                    return

                # 检查是否有错误提示
                body_text = self._page.locator("body").text_content()
                if "当前环境异常" in body_text:
                    raise LoginError("当前环境异常，请手动验证后重试")
                if "二维码已失效" in body_text:
                    raise QRCodeTimeoutError("二维码已失效")

                time.sleep(check_interval)

            except Exception as e:
                self._logger.warning(f"检查登录状态时出错: {e}")
                time.sleep(check_interval)

        raise QRCodeTimeoutError(f"扫码超时（{timeout}秒）")

    def _extract_credentials(self) -> None:
        """提取 Token 和 Cookies"""
        try:
            self._logger.info("正在提取登录凭证...")

            # 从 URL 中提取 Token
            current_url = self._page.url
            import re
            token_match = re.search(r'token=([^&]+)', current_url)
            if token_match:
                self.token = token_match.group(1)
                self._logger.info(f"成功提取 Token: {self.token[:10]}...")
            else:
                # 尝试从 localStorage 获取
                self.token = self._page.evaluate("() => localStorage.getItem('token') or ''")

            if not self.token:
                raise LoginError("无法提取 Token")

            # 获取 Cookies
            cookies_list = self._page.context.cookies()
            self.cookies = {
                cookie['name']: cookie['value']
                for cookie in cookies_list
            }

            self._logger.info(f"成功提取 {len(self.cookies)} 个 Cookie")

            # 保存凭证
            self.save_credentials()

        except Exception as e:
            raise LoginError(f"提取凭证失败: {e}") from e

    def _display_qrcode_in_terminal(self) -> None:
        """在终端显示二维码"""
        try:
            from PIL import Image
            
            # 读取二维码图片
            img = Image.open(self.qrcode_file).convert('L')  # 转为灰度
            
            # 缩放到适合终端的大小
            width = 40
            aspect_ratio = img.height / img.width
            height = int(width * aspect_ratio * 0.5)  # 终端字符高度约为宽度的2倍
            img = img.resize((width, height))
            
            # 转换为 ASCII
            pixels = img.load()
            chars = " ░▒▓█"  # 从亮到暗
            
            self._logger.info("=" * 50)
            self._logger.info("请使用微信扫描以下二维码登录（3分钟超时）:")
            self._logger.info("=" * 50)
            
            lines = []
            for y in range(height):
                line = ""
                for x in range(width):
                    pixel = pixels[x, y]
                    # 反转：深色像素用深色字符
                    char_idx = int((255 - pixel) / 256 * len(chars))
                    char_idx = min(char_idx, len(chars) - 1)
                    line += chars[char_idx] * 2  # 每个字符重复2次保持比例
                lines.append(line)
            
            # 输出二维码
            for line in lines:
                print(line)
            
            self._logger.info("=" * 50)
            self._logger.info(f"二维码图片路径: {self.qrcode_file}")
            self._logger.info("=" * 50)
            
        except Exception as e:
            self._logger.warning(f"终端显示二维码失败: {e}")
            self._logger.info(f"请手动打开二维码文件: {self.qrcode_file}")
