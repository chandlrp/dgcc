"""자료 사이트 안내 포스터(A4) + QR만 PNG.  usage: python make_poster.py [주소]
기본 주소는 SITE. 저장소 이름이 바뀌면 주소를 넣어 다시 실행.
"""
import io, os, sys
import segno
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = sys.argv[1] if len(sys.argv) > 1 else 'https://chandlrp.github.io/dgcc/'
short = SITE.replace('https://', '').rstrip('/')
host, _, path = short.partition('/')
OUT = os.path.join(ROOT, '포스터'); os.makedirs(OUT, exist_ok=True)

qr = segno.make(SITE, error='m')
buf = io.BytesIO(); qr.save(buf, kind='svg', scale=10, border=0, dark='#08253D', xmldecl=False, svgns=True)
svg = buf.getvalue().decode('utf-8')
qr.save(os.path.join(OUT, 'QR_자료사이트.png'), scale=40, border=2)

HTML = f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Georgian:wght@500;700;800&family=Inter:wght@500;700;800&family=JetBrains+Mono:wght@700&display=swap" rel="stylesheet">
<style>
body{{margin:0; font-family:Inter,'Noto Sans Georgian',sans-serif; color:#18222B}}
#s{{width:794px; height:1123px; padding:38px; box-sizing:border-box; background:#fff; display:flex}}
.p{{flex:1; border-radius:26px; background:#FFFCF4; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; padding:30px}}
.tag{{background:#08253D; color:#F2C778; font-weight:800; font-size:16px; padding:9px 22px; white-space:nowrap; border-radius:999px}}
h1{{margin:26px 0 6px; font-size:44px; line-height:1.15; font-weight:800; color:#08253D}}
h1 small{{display:block; font-size:24px; color:#55626C; font-weight:500; margin-top:8px}}
.d{{font-size:19px; color:#55626C; margin-top:6px; line-height:1.5}}
.qr{{margin:30px 0 26px; padding:22px; border:6px solid #50D8C6; border-radius:28px; background:#fff}}
.qr svg{{width:300px; height:300px; display:block}}
.or{{font-size:17px; color:#55626C; margin-bottom:10px}}
.url{{font-family:'JetBrains Mono',monospace; font-weight:700; font-size:40px; color:#08253D; background:#fff; border:2px solid #E7DFCC; border-radius:18px; padding:14px 26px; letter-spacing:.01em}}
.url em{{font-style:normal; color:#1E7F8C}}
.n{{margin-top:26px; font-size:16px; color:#55626C; line-height:1.55}}
</style></head><body><div id="s"><div class="p">
<span class="tag">DGCC – Georgia AI &amp; Digital Government Capacity-Building</span>
<h1>განრიგი და მასალები<small>Schedule &amp; Session Materials</small></h1>
<div class="d"><b style="color:#08253D">24–26.11.2026</b><br>სესიის მასალები იხსნება ყოველდღე · Materials open day by day</div>
<div class="qr">{svg}</div>
<div class="or">ან აკრიფეთ ბრაუზერში · or type in your browser</div>
<div class="url">{host}/<em>{path}</em></div>
<div class="n">PDF · ტელეფონი და კომპიუტერი · Phone &amp; computer</div>
</div></div></body></html>"""

with sync_playwright() as p:
    b = p.chromium.launch(channel='chrome')
    pg = b.new_page(viewport={'width': 900, 'height': 1200}, device_scale_factor=3)
    pg.set_content(HTML, wait_until='networkidle'); pg.evaluate('document.fonts.ready')
    pg.locator('#s').screenshot(path=os.path.join(OUT, '자료사이트_포스터.png'))
    b.close()
print('poster →', OUT, '|', SITE)
