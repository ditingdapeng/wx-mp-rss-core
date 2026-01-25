# wx-mp-rss-core
WeChat MP article fetcher &amp; JSON Feed generator - Python core library

> 微信公众号 JSON Feed 核心库 - 轻量级的文章抓取和 JSON Feed 生成工具

## 简介

`wx-mp-rss-core` 是一个纯 Python 库，提供微信公众号文章抓取和 JSON Feed 生成功能。它不包含命令行工具、配置文件或数据库持久化，专注于提供简单易用的 Python API。

### 核心特点

- **轻量级**：只包含核心功能（登录 + 抓取 + JSON Feed 生成）
- **易集成**：可作为其他项目的依赖库
- **可编程**：通过 Python API 调用
- **多公众号支持**：支持单个或多个公众号批量处理
- **资源管理**：支持 context manager 自动清理资源
- **终端二维码显示**：登录时自动在终端显示二维码，无需打开图片文件
- **JSON Feed 格式**：遵循 we-mp-rss 的 JSON Feed 规范

## 系统要求

- Python 3.8+ （推荐 3.10+）
- macOS / Linux / Windows
- Firefox 或 Chromium 浏览器

## 安装

### 1. 安装 Python 包

```bash
pip install wx-mp-rss-core
```

### 2. 安装 Playwright 浏览器（必须！）

```bash
# 安装 Firefox
python -m playwright install firefox

# 或安装 Chromium
python -m playwright install chromium
```

### 3. 国内加速安装

```bash
# 设置镜像
export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/

# 安装浏览器
python -m playwright install firefox
```

### 4. 验证安装

```python
from playwright.sync_api import sync_playwright
print("Playwright 安装成功！")
```

## 快速开始

### 基础用法

```python
from wx_rss import WeChatMP

# 初始化
mp = WeChatMP(token_file="wx_token.json")

# 1. 登录（首次需要扫码）
if not mp._is_logged_in:
    print("请使用微信扫描生成的二维码登录...")
    mp.login()

# 2. 获取文章
articles = mp.fetch_articles(fakeid="MzAxMDAwMDAx", count=10)

# 3. 生成 JSON Feed
json_feed = mp.generate_json_feed(
    mp_name="我的公众号",
    mp_intro="这是我的公众号简介",
    articles=articles,
    feed_id="MzAxMDAwMDAx"
)

# 4. 保存到文件
with open("feed.json", "w", encoding="utf-8") as f:
    f.write(json_feed)

print(f"成功生成 JSON Feed，包含 {len(articles)} 篇文章")
```

> **⚠️ 重要提示**：
> - 示例中的 `MzAxMDAwMDAx` 只是占位符，**必须替换为真实的公众号 fakeid**
> - 在微信公众平台文章列表页 URL 中可以找到 fakeid 参数
> - 使用错误的 fakeid 会导致 JSON 解析错误

### 使用 Context Manager（推荐）

```python
from wx_rss import WeChatMP

# 自动管理资源
with WeChatMP() as mp:
    if not mp._is_logged_in:
        mp.login()

    articles = mp.fetch_articles(fakeid="MzAxMDAwMDAx", count=10)
    json_feed = mp.generate_json_feed(mp_name="测试", articles=articles)

# 自动清理浏览器资源
```

## JSON Feed 格式

生成的 JSON Feed 遵循 we-mp-rss 规范：

```json
{
  "name": "公众号名称",
  "link": "https://example.com",
  "description": "公众号简介",
  "language": "zh-CN",
  "cover": "封面图片URL",
  "items": [
    {
      "id": "article_id",
      "title": "文章标题",
      "description": "文章摘要",
      "link": "文章链接",
      "updated": "2024-01-01T12:00:00+08:00",
      "image": {
        "url": "封面图片URL"
      },
      "author": "作者名称",
      "content": "正文内容",
      "content_html": "正文HTML",
      "channel_name": "公众号名称",
      "feed": {
        "id": "mp_id",
        "name": "公众号名称",
        "cover": "封面URL",
        "intro": "简介"
      }
    }
  ]
}
```

## 搜索公众号

### 通过公众号名称搜索 fakeid

```python
from wx_rss import WeChatMP

with WeChatMP() as mp:
    if not mp._is_logged_in:
        mp.login()

    # 搜索公众号
    keyword = "精神抖擞王大鹏"
    results = mp.search_feed(keyword, limit=5)

    for feed in results:
        print(f"公众号: {feed['nickname']}")
        print(f"fakeid: {feed['fakeid']}")
        print(f"简介: {feed['signature']}")
        print()
```

### 快速获取 fakeid

```python
from wx_rss import WeChatMP

with WeChatMP() as mp:
    if not mp._is_logged_in:
        mp.login()

    # 直接获取第一个匹配的 fakeid
    fakeid = mp.get_feed_fakeid("精神抖擞王大鹏")

    if fakeid:
        print(f"找到 fakeid: {fakeid}")

        # 立即抓取文章
        articles = mp.fetch_articles(fakeid=fakeid, count=5)
```

### 搜索 + 抓取完整流程

```python
from wx_rss import WeChatMP

with WeChatMP() as mp:
    mp.login()

    # 1. 搜索公众号
    keyword = "阮一峰的网络日志"
    results = mp.search_feed(keyword)

    if results:
        # 2. 获取 fakeid
        fakeid = results[0]['fakeid']
        feed_name = results[0]['nickname']

        # 3. 抓取文章
        articles = mp.fetch_articles(fakeid=fakeid, count=10)

        # 4. 生成 JSON Feed
        json_feed = mp.generate_json_feed(
            mp_name=feed_name,
            articles=articles,
            feed_id=fakeid
        )

        # 5. 保存
        with open(f"{feed_name}.json", "w") as f:
            f.write(json_feed)

        print(f"✅ 成功生成 {feed_name} 的 JSON Feed")
```

## 多公众号支持

### 独立 JSON Feed

```python
from wx_rss import WeChatMP

# 定义多个公众号
feeds = [
    {"fakeid": "MzAxMDAwMDAx", "name": "公众号A", "intro": "简介A"},
    {"fakeid": "MzAxMDAwMDAy", "name": "公众号B", "intro": "简介B"},
    {"fakeid": "MzAxMDAwMDAz", "name": "公众号C", "intro": "简介C"},
]

with WeChatMP() as mp:
    for feed in feeds:
        try:
            articles = mp.fetch_articles(fakeid=feed["fakeid"], count=10)
            json_feed = mp.generate_json_feed(
                mp_name=feed["name"],
                mp_intro=feed["intro"],
                articles=articles,
                feed_id=feed["fakeid"]
            )

            filename = f"{feed['name']}.json"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(json_feed)

            print(f"✅ {feed['name']} -> {filename}")

        except Exception as e:
            print(f"❌ {feed['name']} 失败: {e}")
```

### 聚合 JSON Feed

```python
from wx_rss import WeChatMP

feeds = [
    {"fakeid": "MzAxMDAwMDAx", "name": "公众号A"},
    {"fakeid": "MzAxMDAwMDAy", "name": "公众号B"},
]

with WeChatMP() as mp:
    all_articles = []

    # 获取所有公众号的文章
    for feed in feeds:
        try:
            articles = mp.fetch_articles(fakeid=feed["fakeid"], count=5)
            all_articles.extend(articles)
        except Exception as e:
            print(f"⚠️ 跳过 {feed['name']}: {e}")
            continue

    # 生成聚合 JSON Feed
    if all_articles:
        aggregated_feed = mp.generate_json_feed(
            mp_name="我的订阅聚合",
            mp_intro="多个公众号的聚合订阅",
            articles=all_articles
        )

        with open("all.json", "w", encoding="utf-8") as f:
            f.write(aggregated_feed)

        print(f"✅ 聚合 JSON Feed 已生成，包含 {len(all_articles)} 篇文章")
```

## 高级用法

### 获取文章正文

```python
with WeChatMP() as mp:
    # 获取包含正文的文章
    articles = mp.fetch_articles(
        fakeid="MzAxMDAwMDAx",
        count=5,
        with_content=True  # 包含正文内容
    )

    # 生成包含全文的 JSON Feed
    json_feed = mp.generate_json_feed(
        mp_name="我的公众号",
        articles=articles,
        full_text=True  # 包含全文
    )
```

### 分步接口（灵活控制）

```python
from wx_rss import WeChatAuth, ArticleFetcher, JSONFeedGenerator

# 步骤1：登录
auth = WeChatAuth(token_file="wx_token.json")
result = auth.login()
token = result["token"]
cookies = result["cookies"]

# 步骤2：抓取文章
fetcher = ArticleFetcher(token, cookies)
articles = fetcher.fetch(fakeid="MzAxMDAwMDAx", count=10)

# 步骤3：生成 JSON Feed
generator = JSONFeedGenerator(
    mp_name="我的公众号",
    mp_intro="公众号简介"
)
json_feed = generator.generate(articles)

# 步骤4：清理资源
fetcher.cleanup()
auth.cleanup()
```

## API 参考

### WeChatMP

统一入口类，整合登录、抓取、JSON Feed 生成功能。

#### 初始化

```python
WeChatMP(token_file: str = "wx_token.json")
```

**参数**：
- `token_file`: Token 保存文件路径

#### 方法

##### login()

```python
login(timeout: int = 180) -> dict
```

执行登录流程。

**参数**：
- `timeout`: 二维码超时时间（秒），默认 180（3分钟）

**返回**：
```python
{
    "token": str,
    "cookies": dict,
    "fakeid": str,
    "is_logged_in": bool
}
```

##### fetch_articles()

```python
fetch_articles(
    fakeid: str,
    count: int = 10,
    with_content: bool = False
) -> list
```

获取文章列表。

**参数**：
- `fakeid`: 公众号 fake_id
- `count`: 获取数量，默认 10
- `with_content`: 是否包含正文内容，默认 False

**返回**：文章列表

```python
[
    {
        "id": str,           # 文章 ID
        "title": str,        # 标题
        "url": str,          # 文章链接
        "cover": str,        # 封面图片
        "digest": str,       # 摘要
        "publish_time": int, # 发布时间戳
        "author": str,       # 作者
        "content": str       # 正文（with_content=True 时）
    },
    ...
]
```

##### generate_json_feed()

```python
generate_json_feed(
    mp_name: str,
    articles: list,
    mp_intro: str = "",
    base_url: str = "",
    mp_cover: str = "",
    full_text: bool = False,
    feed_id: str = ""
) -> str
```

生成 JSON Feed。

**参数**：
- `mp_name`: 公众号名称
- `articles`: 文章列表
- `mp_intro`: 公众号简介
- `base_url`: 基础URL
- `mp_cover`: 公众号封面
- `full_text`: 是否包含全文
- `feed_id`: 公众号ID（可选）

**返回**：JSON Feed 字符串

##### cleanup()

```python
cleanup() -> None
```

清理浏览器资源。

##### search_feed()

```python
search_feed(keyword: str, limit: int = 5) -> list
```

搜索公众号。

**参数**：
- `keyword`: 公众号名称关键词
- `limit`: 返回结果数量，默认 5

**返回**：公众号列表

```python
[
    {
        "fakeid": str,           # 公众号 fakeid
        "nickname": str,         # 公众号名称
        "round_head_img": str,  # 头像 URL
        "signature": str,       # 公众号简介
        "alias_name": str       # 别名
    },
    ...
]
```

##### get_feed_fakeid()

```python
get_feed_fakeid(keyword: str) -> str
```

获取公众号的 fakeid（便捷方法）。

**参数**：
- `keyword`: 公众号名称

**返回**：fakeid，如果未找到返回空字符串

```python
fakeid = mp.get_feed_fakeid("精神抖擞王大鹏")
# 返回: "MjM5NTI2..."
```

### JSONFeedGenerator

JSON Feed 生成类。

```python
JSONFeedGenerator(
    mp_name: str,
    mp_intro: str,
    base_url: str = "",
    mp_cover: str = ""
)
```

#### 方法

- `generate(articles: list, full_text: bool = False, feed_id: str = "") -> str`: 生成 JSON Feed
- `save(json_str: str, filename: str) -> None`: 保存 JSON Feed 到文件
- `format_time(timestamp: int) -> str`: 格式化时间为 ISO 8601

## 错误处理

### 自定义异常

```python
from wx_rss.exceptions import (
    LoginError,
    QRCodeTimeoutError,
    FetchError,
    NetworkError,
    RateLimitError,
    TokenExpiredError,
    BrowserError
)
```

### 错误处理示例

```python
from wx_rss import WeChatMP
from wx_rss.exceptions import LoginError, FetchError, TokenExpiredError

try:
    mp = WeChatMP()
    mp.login()
except LoginError as e:
    print(f"登录失败: {e}")
    print("请检查网络连接或重新扫码")
except TokenExpiredError as e:
    print(f"Token 已过期: {e}")
    print("请删除 wx_token.json 后重新登录")

try:
    articles = mp.fetch_articles(fakeid="MzAxMDAwMDAx", count=10)
except FetchError as e:
    print(f"抓取失败: {e}")
except RateLimitError as e:
    print(f"请求过频: {e}")
    print("请稍后再试")
```

## 最佳实践

### 1. 资源管理

**推荐：使用 context manager**

```python
with WeChatMP() as mp:
    articles = mp.fetch_articles(fakeid="xxx")
# 自动清理
```

**不推荐：忘记清理**

```python
mp = WeChatMP()
articles = mp.fetch_articles(fakeid="xxx")
# 没有清理，浏览器进程继续运行...
```

### 2. 多公众号处理

**推荐：串行处理 + 异常隔离**

```python
mp = WeChatMP()
results = {}

for feed in feeds:
    try:
        articles = mp.fetch_articles(fakeid=feed["fakeid"])
        results[feed['name']] = articles
    except Exception as e:
        print(f"获取 {feed['name']} 失败: {e}")
        results[feed['name']] = None
        continue
```

### 3. 日志配置

```python
import logging

# 开发环境
logging.basicConfig(level=logging.DEBUG)

# 生产环境
logging.basicConfig(level=logging.INFO)

mp = WeChatMP()
```

## 限制说明

1. **不支持并行抓取**：由于 Playwright 浏览器实例不能跨线程共享，只能串行处理多个公众号
2. **需要人工扫码**：首次登录需要微信扫码（默认 3 分钟超时，二维码会在终端显示）
3. **Token 有效期**：约 3-7 天，过期后需要重新登录
4. **单次获取限制**：最多获取最近 10-20 篇文章

## 示例代码

项目包含完整的示例代码，位于 `examples/` 目录：

- `01_login.py` - 登录示例
- `02_fetch_articles.py` - 抓取文章示例
- `03_generate_json_feed.py` - 生成 JSON Feed 示例
- `04_multi_feeds.py` - 多公众号示例
- `05_error_handling.py` - 错误处理示例
- `06_complete_workflow.py` - 完整流程���例
- `07_search_feed.py` - 搜索公众号示例

运行示例：

```bash
cd examples
python 06_complete_workflow.py
```

## 与 we-mp-rss 的关系

本项目遵循 we-mp-rss 的 JSON Feed 规范，可以与 we-mp-rss 项目无缝集成：

- **数据结构一致**：文章数据结构与 we-mp-rss 兼容
- **JSON Feed 格式统一**：生成符合 we-mp-rss 规范的 JSON Feed
- **可独立使用**：轻量级设计，无需数据库和 Web 服务

## 常见问题

### Q: Playwright 安装失败？

A: 使用国内镜像加速：

```bash
export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/
python -m playwright install firefox
```

### Q: 如何获取公众号 fakeid？

A: **方法 1 - 从微信公众平台获取**：
1. 登录 https://mp.weixin.qq.com/
2. 进入"素材管理" → "图文消息"
3. 选择任意公众号，点击进入文章列表
4. 查看 URL 中的 `fakeid` 参数

**方法 2 - 从 we-mp-rss 数据库获取**：
```python
# 如果使用过 we-mp-rss 项目，可以从数据库查询
# fakeid 对应 Feed 表中的 faker_id 字段
```

**重要提示**：
- 示例代码中的 `MzAxMDAwMDAx` 只是占位符，不是真实 ID
- 使用前必须替换为真实的公众号 fakeid
- 否则会返回 "Expecting value: line 1 column 1" 错误

### Q: 为什么返回 JSON 解析错误？

A: 可能的原因：
1. **fakeid 错误**：使用示例中的占位符，未替换为真实 ID
2. **Token 过期**：删除 `wx_token.json` 重新登录
3. **网络问题**：检查网络连接

```python
# 错误示例：使用占位符 fakeid
articles = mp.fetch_articles(fakeid="MzAxMDAwMDAx", count=10)  # ❌

# 正确示例：使用真实 fakeid
articles = mp.fetch_articles(fakeid="MjIzMzQ0NTU2Nzg5", count=10)  # ✅
```

### Q: Token 过期怎么办？

A: 删除 `wx_token.json` 文件，重新运行登录程序。

### Q: 支持并行抓取吗？

A: 不支持。由于 Playwright 浏览器实例的限制，只能串行处理。

## 依赖项

```
playwright>=1.40.0      # 浏览器自动化
beautifulsoup4>=4.0.0  # HTML 解析
requests>=2.32.0       # HTTP 请求
Pillow>=10.0.0         # 图片处理
qrcode>=7.0.0          # 生成二维码
```

## 致谢

本项目基于 [we-mp-rss](https://github.com/rachelos/we-mp-rss) 进行开发，感谢原作者的贡献。

## 许可证

MIT License

## 作者

Your Name

## 链接

- GitHub: https://github.com/yourusername/wx-mp-rss-core
- 原项目: https://github.com/rachelos/we-mp-rss
- 文档: https://github.com/yourusername/wx-mp-rss-core/wiki
- 问题反馈: https://github.com/yourusername/wx-mp-rss-core/issues
