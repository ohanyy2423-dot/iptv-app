import os
import re
import asyncio
from playwright.async_api import async_playwright
from telethon import TelegramClient

# بيانات التليجرام (تنسحب من Secrets)
API_ID = int(os.environ.get("TG_API_ID", 0))
API_HASH = os.environ.get("TG_API_HASH", "")

# القنوات والمجموعات الـ 7 المحددة من الصور
CHANNELS = [
    'APK2KING',
    'SOMA_TECHPRO',
    'GHOSTS_PRO',
    'IPTV_MAX',
    'bobtech1_2026',
    'Technolgeria',
    'ASMR_GOLD'
]

async def bypass_and_get_codes(url):
    """فتح الرابط المخفي والضغط على الأزرار واستخراج الأكواد"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        page = await context.new_page()
        
        try:
            await page.goto(url, timeout=60000)
            
            buttons_to_click = ["تحميل", "تخطي", "Get Link", "Download", "Continue", "رابط التحميل"]
            for btn_text in buttons_to_click:
                try:
                    button = page.locator(f'text="{btn_text}"').first
                    if await button.is_visible():
                        await button.click()
                        await page.wait_for_timeout(5000)
                except Exception:
                    continue

            await page.wait_for_timeout(15000)
            content = await page.content()
            await browser.close()
            return content
        except Exception as e:
            print(f"خطأ أثناء تخطي الرابط {url}: {e}")
            await browser.close()
            return ""

def extract_xtream_info(text):
    """استخراج بيانات Xtream باستخدام Regex"""
    hosts = re.findall(r'https?://[^\s:]+:\d+', text)
    users = re.findall(r'username[=:\s]+([^\s]+)', text, re.IGNORECASE)
    passes = re.findall(r'password[=:\s]+([^\s]+)', text, re.IGNORECASE)
    
    results = []
    for i in range(min(len(users), len(passes))):
        host = hosts[i] if i < len(hosts) else "http://example-server.com:8080"
        results.append({"host": host, "user": users[i], "pass": passes[i]})
    return results

async def main():
    codes_list = []
    
    async with TelegramClient('session', API_ID, API_HASH) as client:
        for channel in CHANNELS:
            try:
                print(f"جاري المسح في: {channel}")
                # قراءة آخر 5 رسائل من كل مصدر
                async for message in client.iter_messages(channel, limit=5):
                    msg_text = message.text or ""
                    
                    # 1. الأكواد المباشرة
                    direct_codes = extract_xtream_info(msg_text)
                    codes_list.extend(direct_codes)
                    
                    # 2. روابط اختصار الأكواد
                    urls = re.findall(r'https?://[^\s]+', msg_text)
                    for url in urls:
                        if "t.me" not in url:
                            print(f"جاري جلب الرابط المختصر: {url}")
                            page_html = await bypass_and_get_codes(url)
                            extracted = extract_xtream_info(page_html)
                            codes_list.extend(extracted)
            except Exception as e:
                print(f"تعذر القراءة من {channel}: {e}")

    generate_html(codes_list)

def generate_html(codes):
    """تحديث ملف index.html بالبيانات الجديدة"""
    cards_html = ""
    for idx, item in enumerate(codes, 1):
        cards_html += f"""
        <div class="card">
            <h3>سيرفر {idx}</h3>
            <p><b>Host:</b> {item['host']}</p>
            <p><b>User:</b> {item['user']}</p>
            <p><b>Pass:</b> {item['pass']}</p>
        </div>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>أكواد Xtream المحدثة</title>
    <style>
        body {{ font-family: sans-serif; background: #121212; color: #fff; text-align: center; padding: 15px; }}
        .card {{ background: #1e1e1e; padding: 15px; margin: 10px auto; max-width: 400px; border-radius: 8px; border: 1px solid #333; }}
        p {{ margin: 5px 0; color: #00ff88; word-break: break-all; }}
    </style>
</head>
<body>
    <h2>أحدث أكواد Xtream الشغالة</h2>
    {cards_html if cards_html else "<p>جاري تحديث الأكواد...</p>"}
</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("تم تحديث ملف index.html بنجاح.")

if __name__ == "__main__":
    asyncio.run(main())
