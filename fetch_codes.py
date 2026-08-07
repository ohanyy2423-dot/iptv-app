import re
import urllib.request

# قائمة القنوات العامة
CHANNELS = [
    "https://t.me/s/iptv_links1", # استبدل أسماء القنوات بقنواتك
    "https://t.me/s/xtream_codes"
]

def fetch_xtream_codes():
    codes = []
    
    for channel in CHANNELS:
        try:
            req = urllib.request.Request(
                channel, 
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            html = urllib.request.urlopen(req).read().decode('utf-8')
            
            # البحث عن أشكال سيرفرات الـ Xtream (URL / Username / Password)
            matches = re.findall(r'(http://[^\s<"]+:\d+).*?Username:\s*([^\s<"]+).*?Password:\s*([^\s<"]+)', html, re.DOTALL)
            for m in matches:
                codes.append({
                    'host': m[0],
                    'user': m[1],
                    'pass': m[2]
                })
        except Exception as e:
            print(f"Error reading {channel}: {e}")
            
    return codes

def generate_html(codes):
    html_content = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IPTV Xtream Codes</title>
    <style>
        body { font-family: sans-serif; background: #121212; color: #fff; padding: 20px; }
        .card { background: #1e1e1e; padding: 15px; margin-bottom: 10px; border-radius: 8px; }
        p { margin: 5px 0; }
    </style>
</head>
<body>
    <h2>أكواد Xtream المتوفرة</h2>
"""
    if not codes:
        html_content += "<p>لا توجد أكواد متوفرة حالياً.</p>"
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
    codes = fetch_xtream_codes()
    generate_html(codes)
