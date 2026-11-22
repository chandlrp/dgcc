"""materials/ 폴더를 읽어 files.json을 만들고 GitHub에 올린다.
usage: python publish.py           # files.json 갱신 + 커밋 + 푸시
       python publish.py --dry     # files.json만 갱신(올리지 않음)
- 폴더: 00_common(항상 공개) · D1_S1 D1_S2 · D2_S3 D2_S4 · D3_S5 D3_S6 · D4_workshop
- 사이트는 그날 00:00(트빌리시)부터 그날까지의 폴더 파일을 보여 준다.
- 이름이 . 또는 _ 로 시작하는 파일, ~$ 임시 파일은 무시하고 올리지도 않는다(.gitignore).
"""
import hashlib, json, os, subprocess, sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.abspath(__file__))
MAT = os.path.join(ROOT, 'materials')
ORDER = ['00_common', 'D1_S1', 'D1_S2', 'D2_S3', 'D2_S4', 'D3_S5', 'D3_S6', 'D4_workshop']
MAX_MB = 95   # GitHub는 100MB 넘는 파일을 거부

def skip(name):
    return name.startswith(('.', '_', '~$')) or name.lower() in ('thumbs.db', 'desktop.ini')

files, big = [], []
for d in ORDER:
    p = os.path.join(MAT, d)
    os.makedirs(p, exist_ok=True)
    for n in sorted(os.listdir(p), key=str.lower):
        fp = os.path.join(p, n)
        if skip(n) or not os.path.isfile(fp):
            continue
        size = os.path.getsize(fp)
        if size > MAX_MB * 1048576:
            big.append(f'{d}/{n} ({size/1048576:.0f} MB)'); continue
        h = hashlib.sha1(open(fp, 'rb').read()).hexdigest()[:10]
        files.append({'dir': d, 'name': n, 'size': size, 'v': h})
extra = [d for d in os.listdir(MAT) if os.path.isdir(os.path.join(MAT, d)) and d not in ORDER]

tb = datetime.now(timezone(timedelta(hours=4))).strftime('%Y-%m-%d %H:%M')
with open(os.path.join(ROOT, 'files.json'), 'w', encoding='utf-8') as f:
    json.dump({'updated': tb, 'files': files}, f, ensure_ascii=False, indent=1)

print(f'files.json: {len(files)} files (Tbilisi {tb})')
for d in ORDER:
    ns = [x['name'] for x in files if x['dir'] == d]
    print(f'  {d:12} {len(ns)}  ' + ', '.join(ns))
if big:
    print('!! 100MB 가까운 파일은 올릴 수 없음 → PDF로 줄여 주세요:', *big, sep='\n   ')
if extra:
    print('!! 사이트에 안 나오는 폴더(이름 확인):', ', '.join(extra))

if '--dry' in sys.argv:
    sys.exit(0)

def git(*a):
    return subprocess.run(['git', *a], cwd=ROOT, text=True, capture_output=True)

git('add', '-A')
if git('diff', '--cached', '--quiet').returncode == 0:
    print('바뀐 파일 없음 — 올릴 것이 없습니다.'); sys.exit(0)
r = git('commit', '-m', f'Update materials ({tb} Tbilisi)')
print(r.stdout.strip() or r.stderr.strip())
r = git('push', 'origin', 'HEAD')
if r.returncode:
    print('!! 푸시 실패:\n' + r.stderr); sys.exit(1)
print('올림 완료 — 1~2분 뒤 사이트에 반영됩니다.')
