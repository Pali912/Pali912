#!/usr/bin/env python3
"""Generate assets/rocket.svg: a rocket that destroys your GitHub contribution asteroids.
Usage: python rocket.py [github_user] [output.svg]   (standard library only)"""
import re, sys, random, datetime, urllib.request

USER = sys.argv[1] if len(sys.argv) > 1 else 'Pali912'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'assets/rocket.svg'
INK, CREAM = '#2b211c', '#f3e5bd'
MONO = "font-family=\"SFMono-Regular,Consolas,'Courier New',monospace\""

def fetch():
    req = urllib.request.Request(f'https://github.com/users/{USER}/contributions', headers={'User-Agent': 'Mozilla/5.0'})
    page = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'ignore')
    cells = re.findall(r'<td[^>]*?data-date="(\d{4}-\d{2}-\d{2})"[^>]*?data-level="(\d)"', page)
    if not cells:
        cells = [(d, l) for l, d in re.findall(r'data-level="(\d)"[^>]*?data-date="(\d{4}-\d{2}-\d{2})"', page)]
    m = re.search(r'([\d,]+)\s+contributions\s+in the last year', page)
    return sorted(set(cells)), (int(m.group(1).replace(',', '')) if m else None)

try:
    cells, total = fetch()
    if not cells: raise RuntimeError('no cells parsed')
except Exception as e:
    print('warning: could not fetch contributions (%s); using sample data' % e)
    random.seed(3); d0 = datetime.date.today() - datetime.timedelta(days=364)
    cells = [((d0 + datetime.timedelta(days=i)).isoformat(), str(random.choice([0, 0, 0, 1, 1, 2, 3, 4]))) for i in range(365)]; total = None

first = datetime.date.fromisoformat(cells[0][0]); off = (first.weekday() + 1) % 7
rocks = []
for ds, lv in cells:
    n = (datetime.date.fromisoformat(ds) - first).days + off
    if int(lv) > 0: rocks.append((n // 7, n % 7, int(lv)))
ncols = max(c for c, _, _ in [(n // 7, 0, 0) for n in range((datetime.date.fromisoformat(cells[-1][0]) - first).days + off + 1)]) + 1
total = total if total is not None else len(rocks)

W, H, MX, MY, P, S = 960, 320, 24, 50, 17.2, 14
RY = 254  # rocket nose y
COL = {1: '#4b5088', 2: '#6f78c8', 3: '#a4abf0', 4: '#ffe066'}
DARK = {1: '#363a68', 2: '#505aa8', 3: '#7e86d4', 4: '#d9b52e'}

# ---- timeline ----
by_col = {}
for c, r, lv in rocks: by_col.setdefault(c, []).append((r, lv))
t = 1.0; shots = []; stops = []; prev = None
cx = lambda c: MX + c * P + S / 2
for c in sorted(by_col):
    if prev is not None: t += 0.08 + abs(c - prev) * 0.028
    stops.append((t, cx(c)))
    for r, lv in sorted(by_col[c], reverse=True):
        shots.append((c, r, lv, t + 0.06)); t += 0.14
    stops.append((t, cx(c))); prev = c
t_end = t; t_regen = t_end + 3.0; T = t_regen + 1.0
x0 = stops[0][1] if stops else W / 2
pc = lambda s: '%.3f' % (s / T * 100)
css = []
def kf(name, pts): css.append('@keyframes %s{%s}' % (name, ''.join('%s%%{%s}' % (pc(a), v) for a, v in pts)))

# rocket path
pts = [(0, f'transform:translateX({x0:.1f}px)'), (1.0, f'transform:translateX({x0:.1f}px)')]
pts += [(a, f'transform:translateX({x:.1f}px)') for a, x in stops]
pts += [(t_end + .6, f'transform:translateX({stops[-1][1]:.1f}px)'), (t_regen, f'transform:translateX({x0:.1f}px)'), (T, f'transform:translateX({x0:.1f}px)')]
kf('rk', pts)
kf('lz', [(0, 'opacity:1'), (.07, 'opacity:1'), (.08, 'opacity:0'), (T, 'opacity:0')])
kf('fx', [(0, 'opacity:.95;transform:scale(1)'), (.18, 'opacity:0;transform:scale(1.9)'), (T, 'opacity:0;transform:scale(1.9)')])
for i, (dx, dy) in enumerate(((-17, -9), (15, -13), (2, 17)), 1):
    kf(f'd{i}', [(0, 'opacity:1;transform:translate(0,0)'), (.55, f'opacity:0;transform:translate({dx}px,{dy}px)'), (T, f'opacity:0;transform:translate({dx}px,{dy}px)')])
kf('cl', [(0, 'opacity:0'), (t_end + .3, 'opacity:0'), (t_end + .4, 'opacity:1'), (t_regen - .2, 'opacity:1'), (t_regen - .1, 'opacity:0'), (T, 'opacity:0')])
css.append('@keyframes ff{0%,49%{opacity:1}50%,100%{opacity:0}}@keyframes tw{50%{opacity:.2}}@keyframes bl{0%,60%{opacity:1}61%,100%{opacity:.3}}')

# ---- drawing ----
random.seed(5)
stars = ''.join(f'<rect class="{random.choice(["s1","s2","s3","","",""])}" x="{random.randrange(6,W-6)}" y="{random.randrange(6,H-6)}" width="{s}" height="{s}" fill="#cfd6ff" opacity="{random.choice([.2,.35,.5])}"/>' for s in [random.choice([1.5, 2, 2, 3]) for _ in range(70)])
have = {(c, r) for c, r, _ in rocks}
empty = ''.join(f'<rect x="{MX+c*P+S/2-1:.1f}" y="{MY+r*P+S/2-1:.1f}" width="2" height="2" fill="#23263d"/>' for c in range(ncols) for r in range(7) if (c, r) not in have)
rock_svg = deb = lasers = ''
for i, (c, r, lv, ts) in enumerate(shots):
    x, y = MX + c * P, MY + r * P; th = ts + .05; col, dk = COL[lv], DARK[lv]
    kf(f'a{i}', [(0, 'opacity:1'), (th - .01, 'opacity:1'), (th, 'opacity:0'), (t_regen, 'opacity:0'), (t_regen + .5, 'opacity:1'), (T, 'opacity:1')])
    css.append(f'.a{i}{{animation:a{i} {T:.2f}s linear infinite}}')
    k = (c * 7 + r) % 3
    rock_svg += (f'<g class="a{i}"><rect x="{x+3:.1f}" y="{y:.1f}" width="8" height="{S}" fill="{col}"/><rect x="{x:.1f}" y="{y+3:.1f}" width="{S}" height="8" fill="{col}"/><rect x="{x+1:.1f}" y="{y+1:.1f}" width="12" height="12" fill="{col}"/>'
                 f'<rect x="{x+3+k*2:.1f}" y="{y+3:.1f}" width="3" height="3" fill="{dk}"/><rect x="{x+8:.1f}" y="{y+8:.1f}" width="3" height="3" fill="{dk}"/></g>')
    ccx, ccy = x + S / 2, y + S / 2; dl = f'style="animation-delay:{th:.2f}s"'
    deb += f'<rect class="fx fl" x="{ccx-5:.1f}" y="{ccy-5:.1f}" width="10" height="10" fill="#fff" {dl}/>'
    for j in (1, 2, 3): deb += f'<rect class="dd d{j}" x="{ccx-1.5:.1f}" y="{ccy-1.5:.1f}" width="3" height="3" fill="{col}" {dl}/>'
    lasers += f'<g class="lz" style="animation-delay:{ts:.2f}s"><rect x="{ccx-1.5:.1f}" y="{y+S:.1f}" width="3" height="{RY-(y+S):.1f}" fill="#ffe066"/><rect x="{ccx-.5:.1f}" y="{y+S:.1f}" width="1" height="{RY-(y+S):.1f}" fill="#fff"/></g>'
rk = ["....W....", "...WWW...", "..WWWWW..", "..WBBBW..", "..WBBBW..", "..WWWWW..", ".RWWWWWR.", "RRWWWWWRR", "RR.WWW.RR", "R..WWW..R"]
RC = {'W': '#eef1f8', 'B': '#4fb3ff', 'R': '#ff5d5d'}
rs = ''
for r, row in enumerate(rk):
    for c, ch in enumerate(row):
        if ch != '.': rs += f'<rect x="{(c-4.5)*3:.1f}" y="{RY+r*3}" width="3" height="3" fill="{RC[ch]}"/>'
fl = lambda cls, cols: f'<g class="{cls}">' + ''.join(f'<rect x="{x*3}" y="{RY+30+y*3}" width="{w*3}" height="3" fill="{cc}"/>' for x, y, w, cc in cols) + '</g>'
flame = fl('f1', [(-1.5, 0, 3, '#ffe066'), (-1, 1, 2, '#ff9f1c'), (-.5, 2, 1, '#ff5d5d')]) + fl('f2', [(-1.5, 0, 3, '#ff9f1c'), (-1, 1, 2, '#ffe066'), (-.5, 2, 2, '#ff9f1c')])
bub = (f'<g fill="{INK}"><rect x="360" y="120" width="240" height="44"/><rect x="356" y="124" width="248" height="36"/></g><g fill="{CREAM}"><rect x="364" y="124" width="232" height="36"/><rect x="360" y="128" width="240" height="28"/></g>'
       f'<text x="480" y="148" text-anchor="middle" {MONO} font-size="14" font-weight="700" fill="{INK}">FIELD CLEARED!</text>')
hud = (f'<text x="{MX}" y="30" {MONO} font-size="11" font-weight="700" letter-spacing="2" fill="#8e92aa">LEVEL 2 · CLEAR THE FIELD</text>'
       f'<text x="{W-MX-62}" y="30" text-anchor="end" {MONO} font-size="11" font-weight="700" letter-spacing="2" fill="#8e92aa">SCORE</text>'
       f'<text x="{W-MX}" y="30" text-anchor="end" {MONO} font-size="11" font-weight="700" letter-spacing="2" fill="#ffe066">{total:06d}</text>')
ground = ''.join(f'<rect x="{x}" y="298" width="{w}" height="3" fill="#1c1e32"/>' for x, w in ((30, 40), (130, 24), (260, 56), (420, 30), (560, 48), (700, 26), (820, 60)))
anim = (f'.rk{{transform:translateX({x0:.1f}px);animation:rk {T:.2f}s cubic-bezier(.45,0,.3,1) infinite}}.lz{{opacity:0;animation:lz {T:.2f}s linear infinite}}'
        f'.fl,.dd{{opacity:0;animation-duration:{T:.2f}s;animation-iteration-count:infinite;animation-timing-function:linear}}.fl{{animation-name:fx}}.d1{{animation-name:d1}}.d2{{animation-name:d2}}.d3{{animation-name:d3}}'
        f'.fx{{transform-box:fill-box;transform-origin:center}}.cl{{opacity:0;animation:cl {T:.2f}s linear infinite}}'
        '.f1{animation:ff .2s steps(1) infinite}.f2{animation:ff .2s steps(1) infinite -.1s}.s1{animation:tw 3s ease-in-out infinite}.s2{animation:tw 5s ease-in-out infinite -2s}.s3{animation:tw 4s ease-in-out infinite -1s}')
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="A rocket destroys the asteroids that represent {USER}'s GitHub contributions">
<title>Rocket vs. contribution asteroids</title><style>{anim}{''.join(css)}</style>
<rect width="{W}" height="{H}" rx="20" fill="#0b0b12"/>{stars}{empty}{ground}{rock_svg}{deb}{lasers}
<g class="rk">{rs}{flame}</g><g class="cl">{bub}</g>{hud}</svg>'''
import os; os.makedirs(os.path.dirname(OUT) or '.', exist_ok=True)
open(OUT, 'w', encoding='utf-8').write(svg)
print(f'wrote {OUT}: {len(rocks)} asteroids, {len(shots)} shots, loop {T:.1f}s, {len(svg)//1024} KB')
