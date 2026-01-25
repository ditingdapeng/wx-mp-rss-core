# 如何获取公众号 fakeid

## 方法 1：使用搜索功能（推荐）

wx-mp-rss-core 提供了内置的搜索功能：

```python
from wx_rss import WeChatMP

with WeChatMP() as mp:
    mp.login()

    # 搜索公众号
    results = mp.search_feed("精神抖擞王大鹏", limit=5)

    for feed in results:
        print(f"公众号: {feed['nickname']}")
        print(f"fakeid: {feed['fakeid']}")
        print(f"简介: {feed['signature']}")
```

**快速获取第一个匹配结果**：

```python
fakeid = mp.get_feed_fakeid("精神抖擞王大鹏")
print(f"fakeid: {fakeid}")
```

## 方法 2：从微信公众平台获取

### 步骤：

1. **登录微信公众平台**
   - 访问：https://mp.weixin.qq.com/
   - 使用公众号管理员微信扫码登录

2. **进入素材管理**
   - 点击左侧菜单 "素材管理"
   - 选择 "图文消息"

3. **新建/编辑图文**
   - 点击 "新建图文消息" 或编辑已有文章

4. **插入超链接**
   - 在编辑器工具栏中点击 "超链接" 图标
   - 选择 "其他公众号"

5. **搜索目标公众号**
   - 输入公众号名称，例如："精神抖擞王大鹏"
   - 在搜索结果中找到目标公众号

6. **查看 fakeid**
   - 选中公众号后，查看浏览器开发者工具
   - 在 Network 标签中查看请求参数
   - 找到 `fakeid` 参数值

## 方法 3：从文章页面获取

### 步骤：

1. **打开公众号文章**
   - 访问目标公众号的任意文章
   - 例如：https://mp.weixin.qq.com/s/xxxxx

2. **查看页面源代码**
   - 右键 → "查看网页源代码"
   - 搜索 `fakeid` 或 `__biz`

3. **提取 fakeid**
   - 从 URL 中提取 `__biz` 参数
   - 或从源码中搜索 `var fakeid = "xxx"`

## 方法 4：使用浏览器开发者工具

### 步骤：

1. **打开微信公众平台**
   - 登录后进入任意功能页面

2. **打开开发者工具**
   - F12 或右键 → "检查"

3. **查看 Network 请求**
   - 在 Network 标签中筛选 `appmsg` 或 `searchbiz`
   - 查看请求参数中的 `fakeid`

## 示例代码

### 完整示例：搜索 + 抓取

```python
from wx_rss import WeChatMP

# 1. 初始化并登录
mp = WeChatMP()
mp.login()

# 2. 搜索公众号
keyword = "精神抖擞王大鹏"
results = mp.search_feed(keyword, limit=5)

print(f"找到 {len(results)} 个公众号：")
for feed in results:
    print(f"  - {feed['nickname']}: {feed['fakeid']}")

# 3. 使用第一个公众号的 fakeid
if results:
    fakeid = results[0]['fakeid']
    feed_name = results[0]['nickname']

    # 4. 抓取文章
    articles = mp.fetch_articles(fakeid=fakeid, count=5)

    print(f"\n成功从 '{feed_name}' 获取 {len(articles)} 篇文章")
```

## 常见问题

### Q: 搜索不到公众号？

A: 可能的原因：
- 公众号名称输入错误
- 该公众号已被封禁或注销
- 你的账号没有搜索权限（尝试使用其他公众号账号登录）

### Q: fakeid 格式是什么？

A: fakeid 通常是以 `M` 开头的字符串，例如：
- `MjM5NTI2NDI3MTMwMw==`（带等号，Base64 编码）
- `MzAxMDAwMDAx`（不带等号）

### Q: 为什么搜索返回多个结果？

A: 搜索是模糊匹配，会返回所有名称中包含关键词的公众号。你可以：
1. 使用完整的公众号名称
2. 查看返回结果中的 `signature`（简介）来确认
3. 选择正确的 fakeid

## 测试搜索功能

```bash
cd /Users/dapeng/Code/information/wx-mp-rss-core
python3 examples/07_search_feed.py
```

这个示例会演示：
- 搜索公众号
- 获取 fakeid
- 使用 fakeid 抓取文章
