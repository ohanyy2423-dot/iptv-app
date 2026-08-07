import re
import urllib.request
import asyncio
from playwright.async_api import async_playwright

# قنوات التليجرام المستهدفة
CHANNELS = [
    "https://t.me/s/iq_iptv"
]

async def fetch_all_codes():
    all_codes = []
    links_to_visit = []

    # 1. سحب روابط المنشورات من القناة
    for channel in CHANNELS:
        try:
            req = urllib.request.Request(channel, headers={'User-Agent': 'Mozilla/5.0'})
            html = urllib.request.urlopen(req).read().decode('utf-8')
            
            # استخراج جميع الروابط الموجودة في المنشورات
            found_links = re.findall(r'href="(https?://[^"]+)"', html)
            for link in found_links:
                if "t.me" not in link and "telegram.org" not in link and "google.com" not in link:
                    links_to_visit.append(link)
        except Exception as e:
            print(f"Error reading channel: {e}")

    # 2. تشغيل المتصفح الخفي لدخول الروابط واستخراج الأكواد الفعلية
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # فحص أحدث الروابط
        for link in list(set(links_to_visit))[:4]:
            try:
                print(f"Visiting target link: {link}")
                await page.goto(link, timeout=30000, wait_until="domcontentloaded")
                
                # الانتظار حتى تحمّل الصفحة تماماً وتتخطى أي عداد تليجرام أو إعلانات
                await asyncio.sleep(6)

                # محاولة النقر على أي زر تخطي أو تحميل قد يظهر في الصفحة
                for btn_selector in ["a.btn", "button#download", "a:has-text('Get Link')", "a:has-text('Proceed')", "input[type='submit']"]:
                    try:
                        if await page.locator(btn_selector).count() > 0:
                            await page.click(btn_selector, timeout=3000)
                            await asyncio.sleep(4)
                    except:
                        pass

                # قراءة محتوى الصفحة بالكامل بعد التخطي
                content = await page.content()
                
                # البحث الذكي عن صيغة سيرفرات الـ Xtream (Host + User + Pass)
                matches = re.findall(r'(http[s]?://[^\s<"]+:\d+).*?(?:username|user)\s*[:=]?\s*([^\s<"]+).*?(?:password|pass)\s*[:=]?\s*([^\s<"]+)', content, re.DOTALL | re.IGNORECASE)
                for m in matches:
                    all_codes.append({
                        'host': m[0],
                        'user': m[1].strip('"\'<>'),
                        'pass': m[2].strip('"\'<>')
                    })
                    
                # صيغة بديلة للبحث في النصوص المباشرة داخل الصفحة
                if not matches:
                    alt_matches = re.findall(r'(http[s]?://[^\s<>"\']+:\d+)\s+([^\s<>"\']+)\s+([^\s<>"\']+)', content)
                    for am in alt_matches:
                        if len(am[1]) > 2 and len(am[2]) > 2 and "http" not in am[1]:
                            all_codes.append({
                                'host': am[0],
                                'user': am[1],
                                'pass': am[2]
                            })

            except Exception as e:
                print(f"Skipping link due to error: {e}")

        await browser.close()

    # إزالة الأكواد المكررة
    unique_codes = [dict(t) for t in {tuple(d.items()) for d in all_codes}]
    return unique_codes

def generate_html(codes):
    html_content = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IPTV Xtream Codes</title>
    <style>
        body { font-family: system-ui, sans-serif; background: #121212; color: #fff; padding: 20px; }
        .card { background: #1e1e1e; padding: 15px; margin-bottom: 12px; border-radius: 8px; border-right: 4px solid #007bff; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        p { margin: 6px 0; word-break: break-all; }
        b { color: #00bcd4; }
    </style>
</head>
<body>
    <h2 style="text-align: center; color: #00bcd4;">أكواد Xtream المستخرجة تلقائياً</h2>
"""
    if not codes:
        html_content += "<p style='text-align: center;'>جاري البحث وسحب الأكواد الجديدة... انتظر التحديث القادم.</p>"
    else:
        for c in codes:
            html_content += f"""
    <div class="card">
        <p><b>Host:</b> {c['host']}</p>
        <p><b>Username:</b> {c['user']}</p>
        <p><b>Password:</b> {c['pass']}</p>
    </div>"""

    html_content += """
</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    codes = asyncio.run(fetch_all_codes())
    generate_html(codes)
