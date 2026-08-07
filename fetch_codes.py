import re
import urllib.request
import asyncio
from playwright.async_api import async_playwright

# قنوات التليجرام التي تحتوي على منشورات بروابط
CHANNELS = [
    "https://t.me/s/SOMATECHPRO", # القناة الخاصة بك أو أي قناة مشابهة
    "https://t.me/s/IPTV_XTREAM_FREE_CODES"
]

async def extract_codes_from_url(page, url):
    codes = []
    try:
        print(f"Opening link: {url}")
        # الانتقال للرابط وانتظار التحميل
        await page.goto(url, timeout=30000, wait_until="domcontentloaded")
        content = await page.content()
        
        # البحث عن أشكال الـ Xtream داخل الصفحة (Host, Username, Password)
        matches = re.findall(r'(http://[^\s<"]+:\d+).*?Username:\s*([^\s<"]+).*?Password:\s*([^\s<"]+)', content, re.DOTALL | re.IGNORECASE)
        for m in matches:
            codes.append({
                'host': m[0],
                'user': m[1],
                'pass': m[2]
            })
            
        # صيغة أخرى شائعة (URL / USER / PASS)
        if not codes:
            urls = re.findall(r'http://[^\s<"]+:\d+', content)
            users = re.findall(r'username\s*[:=]\s*([^\s<"]+)', content, re.IGNORECASE)
            passes = re.findall(r'password\s*[:=]\s*([^\s<"]+)', content, re.IGNORECASE)
            
            for i in range(min(len(urls), len(users), len(passes))):
                codes.append({
                    'host': urls[i],
                    'user': users[i],
                    'pass': passes[i]
                })
    except Exception as e:
        print(f"Error visiting {url}: {e}")
    return codes

async def fetch_all_codes():
    all_codes = []
    links_to_visit = []

    # 1. جلب منشورات القنوات واستخراج أي روابط خارجية داخلها
    for channel in CHANNELS:
        try:
            req = urllib.request.Request(channel, headers={'User-Agent': 'Mozilla/5.0'})
            html = urllib.request.urlopen(req).read().decode('utf-8')
            
            # استخراج روابط التحميل المختصرة من القناة
            found_links = re.findall(r'href="(https?://[^"]+)"', html)
            for link in found_links:
                # تصفية الروابط لتأخذ روابط التحميل فقط وتتجاهل روابط التليجرام الداخلية
                if "t.me" not in link and "telegram" not in link:
                    links_to_visit.append(link)
                    
            # أيضاً استخراج أي أكواد مكتوبة مباشرة في القناة إن وجدت
            direct_matches = re.findall(r'(http://[^\s<"]+:\d+).*?Username:\s*([^\s<"]+).*?Password:\s*([^\s<"]+)', html, re.DOTALL | re.IGNORECASE)
            for m in direct_matches:
                all_codes.append({'host': m[0], 'user': m[1], 'pass': m[2]})
        except Exception as e:
            print(f"Error fetching channel {channel}: {e}")

    # 2. تشغيل متصفح وهمي بـ Playwright لفتح روابط التحميل واستخراج الأكواد منها
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        page = await context.new_page()

        # تجربة فتح أول 5 روابط جُدُد من القنوات
        for link in links_to_visit[:5]:
            codes = await extract_codes_from_url(page, link)
            all_codes.extend(codes)

        await browser.close()

    # حذف التكرار
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
    <h2>أكواد Xtream المتوفرة تلقائياً</h2>
"""
    if not codes:
        html_content += "<p>جاري تحديث الأكواد من المصادر... يرجى إعادة المحاولة لاحقاً.</p>"
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
