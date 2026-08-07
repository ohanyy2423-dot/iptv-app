import asyncio

async def fetch_all_codes():
    # قائمة أكواد مباشرة وثابتة لضمان ظهورها في التطبيق فوراً
    codes = [
        {
            'host': 'http://server.example.com:8080',
            'user': 'user_free_1',
            'pass': 'pass_123'
        },
        {
            'host': 'http://iptv.stream-Server.net:80',
            'user': 'vip_user99',
            'pass': 'secret456'
        }
    ]
    return codes

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
    <h2 style="text-align: center; color: #00bcd4;">أكواد Xtream المتوفرة</h2>
"""
    if not codes:
        html_content += "<p style='text-align: center;'>لا توجد أكواد حالياً.</p>"
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
