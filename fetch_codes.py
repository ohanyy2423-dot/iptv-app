import re
import urllib.request
import asyncio
from playwright.async_api import async_playwright

# قناة التليجرام المستهدفة
CHANNELS = [
    "https://t.me/s/iq_iptv"
]

async def extract_codes_from_page(page, url):
    codes = []
    try:
        print(f"Checking URL: {url}")
        await page.goto(url, timeout=25000, wait_until="domcontentloaded")
        content = await page.content()
        
        # البحث عن صيغ الـ Xtream المختلفة داخل الصفحة أو الروابط المستهدفة
        matches = re.findall(r'(http[s]?://[^\s<"]+:\d+).*?Username:\s*([^\s<"]+).*?Password:\s*([^\s<"]+)', content, re.DOTALL | re.IGNORECASE)
        for m in matches:
            codes.append({
                'host': m[0],
                'user': m[1],
                'pass': m[2]
            })
            
        # صيغة بديلة في حال اختلاف التنسيق
        if not codes:
            urls = re.findall(r'http[s]?://[^\s<"]+:\d+', content)
            users = re.findall(r'username\s*[:=]\s*([^\s<"]+)', content, re.IGNORECASE)
            passes = re.findall(r'password\s*[:=]\s*([^\s<"]+)', content, re.IGNORECASE)
            
            for i in range(min(len(urls), len(users), len(passes))):
                codes.append({
                    'host': urls[i],
                    'user': users[i],
                    'pass': passes[i]
                })
    except Exception as e:
        print(f"Error processing {url}: {e}")
        
    return codes

async def fetch_all_codes():
    all_codes = []
    external_links = []

    # 1. جلب محتوى قناة التليجرام العامة
    for channel in CHANNELS:
        try:
            req = urllib.request.Request(channel, headers={'User-Agent': 'Mozilla/5.0'})
            html = urllib.request.urlopen(req).read().decode('utf-8')
            
            # البحث عن أي أكواد مكتوبة مباشرة داخل المنشورات
            direct_matches = re.findall(r'(http[s]?://[^\s<"]+:\d+).*?Username:\s*([^\s<"]+).*?Password:\s*([^\s<"]+)', html, re.DOTALL | re.IGNORECASE)
            for m in direct_matches:
                all_codes.append({'host': m[0], 'user': m[1], 'pass': m[2]})
                
            # استخراج روابط التحميل أو الروابط الخارجية الموجودة بالمنشورات
            links = re.findall(r'href="(https?://[^"]+)"', html)
            for link in links:
                if "t.me" not in link and "telegram.org" not in link:
                    external_links.append(link)
        except Exception as e:
            print(f"Error reading channel {channel}: {e}")

    # 2. استخدام المتصفح الخفي لتفقد الروابط الخارجية واستخراج الأكواد من داخلها
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        page = await context.new_page()

        # فحص أول 5 روابط كحد أقصى لسرعة التنفيذ
        for link in list(set(external_links))[:5]:
            codes = await extract_codes_from_page(page, link)
            all_codes.extend(codes)

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
        .card { background: #1e1e1e; padding: 15px; margin-bottom: 12px; border-radius: 8px; border-right: 4px solid #007bff; }
        p { margin: 6px 0; word-break: break-all; }
        b { color: #00bcd4; }
    </style>
</head>
<body>
    <h2>أكواد Xtream المتوفرة</h2>
"""
    if not codes:
        html_content += "<p>جاري تحديث الأكواد... يرجى إعادة المحاولة بعد قليل.</p>"
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

