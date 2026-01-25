#!/usr/bin/env python3
"""测试 JSON Feed 生成完整流程"""

from wx_rss import WeChatMP

def main():
    print("=" * 50)
    print("wx-mp-rss-core v0.2.0 - JSON Feed 测试")
    print("=" * 50)
    
    with WeChatMP() as mp:
        # 1. 登录
        print("\n[1/4] 登录...")
        if not mp._is_logged_in:
            print("请使用微信扫描二维码登录...")
            mp.login()
        print("✅ 登录成功")
        
        # 2. 搜索公众号
        keyword = "精神抖擞王大鹏"
        print(f"\n[2/4] 搜索公众号: {keyword}")
        fakeid = mp.get_feed_fakeid(keyword)
        
        if not fakeid:
            print(f"❌ 未找到公众号: {keyword}")
            return
        print(f"✅ 找到 fakeid: {fakeid}")
        
        # 3. 抓取文章（包含正文内容）
        print(f"\n[3/4] 抓取文章（含正文）...")
        articles = mp.fetch_articles(fakeid=fakeid, count=3, with_content=True)
        print(f"✅ 获取 {len(articles)} 篇文章")
        
        for i, article in enumerate(articles, 1):
            print(f"   {i}. {article.get('title', '无标题')}")
        
        # 4. 生成 JSON Feed（包含正文）
        print(f"\n[4/4] 生成 JSON Feed（含正文）...")
        json_feed = mp.generate_json_feed(
            mp_name=keyword,
            mp_intro=f"{keyword} 的公众号",
            articles=articles,
            feed_id=fakeid,
            full_text=True  # 包含正文内容
        )
        
        # 保存文件
        filename = f"{keyword}.json"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(json_feed)
        
        print(f"✅ 已保存到: {filename}")
        
        # 显示部分内容
        print("\n" + "=" * 50)
        print("JSON Feed 预览 (前 500 字符):")
        print("=" * 50)
        print(json_feed[:500] + "...")

if __name__ == "__main__":
    main()
