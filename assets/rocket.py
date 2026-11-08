#!/usr/bin/env python3
"""Generate assets/rocket.svg: a rocket blasts the asteroids that represent your GitHub contribution days.
Usage: python rocket.py [github_user] [output.svg]   (standard library only)"""
import re, sys, os, random, datetime, urllib.request
USER = sys.argv[1] if len(sys.argv) > 1 else 'Pali912'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'assets/rocket.svg'
BLUE, INK, BEIGE, BEIGE_L, YEL, RED, LCD = '#05538a', '#1b1a1c', '#c6c5b9', '#e6e5de', '#f2b72a', '#c8202c', '#6fb7c7'
MONO = "font-family=\"'Courier New',Consolas,monospace\""
def fetch():
    req = urllib.request.Request(f'https://github.com/users/{USER}/contributions', headers={'User-Agent': 'Mozilla/5.0'})
    page = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'ignore')
    cells = re.findall(r'<td[^>]*?data-date="(\d{4}-\d{2}-\d{2})"[^>]*?data-level="(\d)"', page)
    if not cells: cells = [(d, l) for l, d in re.findall(r'data-level="(\d)"[^>]*?data-date="(\d{4}-\d{2}-\d{2})"', page)]
    m = re.search(r'([\d,]+)\s+contributions\s+in the last year', page)
    return sorted(set(cells)), (int(m.group(1).replace(',', '')) if m else None)
import time
cells = None
for attempt in range(5):
    try:
        cells, total = fetch(); assert cells; break
    except Exception as e:
        err = e; cells = None; time.sleep(3 * (attempt + 1))
if cells is None:
    e = err; print('warning: using sample data (%s)' % e); random.seed(3); d0 = datetime.date.today() - datetime.timedelta(days=364)
    cells = [((d0 + datetime.timedelta(days=i)).isoformat(), str(random.choice([1, 1, 2, 3, 4]) if random.random() < 0.03 + 0.6 * (i / 364) ** 5 else 0)) for i in range(365)]; total = None
first = datetime.date.fromisoformat(cells[0][0]); off = (first.weekday() + 1) % 7
rocks = []; last_n = (datetime.date.fromisoformat(cells[-1][0]) - first).days + off
for ds, lv in cells:
    n = (datetime.date.fromisoformat(ds) - first).days + off
    if int(lv) > 0: rocks.append((n // 7, n % 7, int(lv)))
ncols = last_n // 7 + 1; total = total if total is not None else len(rocks)
W, H, MX, MY, P, S, RY = 960, 330, 24, 62, 17.2, 14, 262
COL = {1: '#c6c5b9', 2: '#f2b72a', 3: '#f08a3c', 4: '#c8202c'}
by_col = {}
for c, r, lv in rocks: by_col.setdefault(c, []).append((r, lv))
cx = lambda c: MX + c * P + S / 2
t = 1.0; shots = []; stops = []; prev = None
for c in sorted(by_col):
    if prev is not None: t += 0.08 + abs(c - prev) * 0.028
    stops.append((t, cx(c)))
    for r, lv in sorted(by_col[c], reverse=True): shots.append((c, r, lv, t + 0.06)); t += 0.14
    stops.append((t, cx(c))); prev = c
t_end = t; t_regen = t_end + 3.0; T = t_regen + 1.0; x0 = stops[0][1] if stops else W / 2
pc = lambda s: '%.3f' % (s / T * 100); css = []
def kf(name, pts): css.append('@keyframes %s{%s}' % (name, ''.join('%s%%{%s}' % (pc(a), v) for a, v in pts)))
pts = [(0, f'transform:translateX({x0:.1f}px)'), (1.0, f'transform:translateX({x0:.1f}px)')] + [(a, f'transform:translateX({x:.1f}px)') for a, x in stops]
pts += [(t_end + .6, f'transform:translateX({stops[-1][1]:.1f}px)'), (t_regen, f'transform:translateX({x0:.1f}px)'), (T, f'transform:translateX({x0:.1f}px)')]; kf('rk', pts)
kf('lz', [(0, 'opacity:1'), (.07, 'opacity:1'), (.08, 'opacity:0'), (T, 'opacity:0')])
kf('fx', [(0, 'opacity:1;transform:scale(.6)'), (.18, 'opacity:0;transform:scale(1.7)'), (T, 'opacity:0;transform:scale(1.7)')])
for i, (dx, dy) in enumerate(((-17, -9), (15, -13), (2, 17)), 1):
    kf(f'd{i}', [(0, 'opacity:1;transform:translate(0,0)'), (.55, f'opacity:0;transform:translate({dx}px,{dy}px)'), (T, f'opacity:0;transform:translate({dx}px,{dy}px)')])
kf('cl', [(0, 'opacity:0'), (t_end + .3, 'opacity:0'), (t_end + .4, 'opacity:1'), (t_regen - .2, 'opacity:1'), (t_regen - .1, 'opacity:0'), (T, 'opacity:0')])
css.append('@keyframes ff{0%,49%{opacity:1}50%,100%{opacity:0}}@keyframes tw{50%{opacity:.2}}')
random.seed(5)
stars = ''.join(f'<rect class="{random.choice(["s1","s2",""])}" x="{random.randrange(8,W-8)}" y="{random.randrange(8,H-8)}" width="{s}" height="{s}" fill="#bcd9ee" opacity="{random.choice([.3,.5,.7])}"/>' for s in [random.choice([2,2,3]) for _ in range(50)])
have = {(c, r) for c, r, _ in rocks}
empty = ''.join(f'<rect x="{MX+c*P+S/2-1:.1f}" y="{MY+r*P+S/2-1:.1f}" width="2" height="2" fill="#2b84c0"/>' for c in range(ncols) for r in range(7) if (c, r) not in have)
rock_svg = deb = lasers = ''
for i, (c, r, lv, ts) in enumerate(shots):
    x, y = MX + c * P, MY + r * P; th = ts + .05; col = COL[lv]
    kf(f'a{i}', [(0, 'opacity:1'), (th - .01, 'opacity:1'), (th, 'opacity:0'), (t_regen, 'opacity:0'), (t_regen + .5, 'opacity:1'), (T, 'opacity:1')])
    css.append(f'.a{i}{{animation:a{i} {T:.2f}s linear infinite}}')
    rock_svg += (f'<g class="a{i}"><polygon points="{x+3:.1f},{y+.5:.1f} {x+11:.1f},{y+.5:.1f} {x+13.5:.1f},{y+4:.1f} {x+13.5:.1f},{y+10:.1f} {x+10:.1f},{y+13.5:.1f} {x+4:.1f},{y+13.5:.1f} {x+.5:.1f},{y+10:.1f} {x+.5:.1f},{y+4:.1f}" fill="{col}" stroke="{INK}" stroke-width="1.8" stroke-linejoin="round"/>'
                 f'<rect x="{x+4:.1f}" y="{y+4:.1f}" width="3" height="3" rx="1" fill="{INK}" opacity=".35"/><rect x="{x+8:.1f}" y="{y+8:.1f}" width="2.4" height="2.4" rx="1" fill="{INK}" opacity=".35"/></g>')
    ccx, ccy = x + S / 2, y + S / 2; dl = f'style="animation-delay:{th:.2f}s"'
    star = ' '.join(f'{ccx+(11 if k%2==0 else 5)*__import__("math").cos(k*3.14159/4):.1f},{ccy+(11 if k%2==0 else 5)*__import__("math").sin(k*3.14159/4):.1f}' for k in range(8))
    deb += f'<polygon class="fx fl" points="{star}" fill="#fff3a8" stroke="{INK}" stroke-width="1.6" {dl}/>'
    for j in (1, 2, 3): deb += f'<rect class="dd d{j}" x="{ccx-2:.1f}" y="{ccy-2:.1f}" width="4" height="4" fill="{col}" stroke="{INK}" stroke-width="1.2" {dl}/>'
    lasers += f'<g class="lz" style="animation-delay:{ts:.2f}s"><rect x="{ccx-2:.1f}" y="{y+S:.1f}" width="4" height="{RY-(y+S):.1f}" fill="{YEL}" stroke="{INK}" stroke-width="1.3"/></g>'
rocket = (f'<path d="M0,{RY} C9,{RY+8} 10,{RY+22} 8,{RY+34} L-8,{RY+34} C-10,{RY+22} -9,{RY+8} 0,{RY} Z" fill="{BEIGE_L}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'
          f'<path d="M0,{RY} C4,{RY+3} 6,{RY+6} 7,{RY+9} L-7,{RY+9} C-6,{RY+6} -4,{RY+3} 0,{RY} Z" fill="{RED}" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>'
          f'<circle cx="0" cy="{RY+19}" r="4.6" fill="{LCD}" stroke="{INK}" stroke-width="2"/>'
          f'<polygon points="-8,{RY+22} -17,{RY+37} -8,{RY+34}" fill="{RED}" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/><polygon points="8,{RY+22} 17,{RY+37} 8,{RY+34}" fill="{RED}" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>'
          f'<g class="f1"><polygon points="-5,{RY+35} 0,{RY+52} 5,{RY+35}" fill="{YEL}" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/></g><g class="f2"><polygon points="-5,{RY+35} 0,{RY+46} 5,{RY+35}" fill="#f08a3c" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/></g>')
hud = (f'<rect x="{MX}" y="14" width="230" height="26" rx="3" fill="{LCD}" stroke="{INK}" stroke-width="3"/><text x="{MX+10}" y="32" {MONO} font-size="13" font-weight="700" fill="#1b3b44">03 · CONTRIBUTIONS</text>'
       f'<rect x="{W-MX-170}" y="14" width="170" height="26" rx="3" fill="{LCD}" stroke="{INK}" stroke-width="3"/><text x="{W-MX-10}" y="32" text-anchor="end" {MONO} font-size="13" font-weight="700" fill="#1b3b44">SCORE {total:05d}</text>')
bub = (f'<rect x="{W/2-120}" y="120" width="240" height="56" rx="6" fill="{BEIGE}" stroke="{INK}" stroke-width="3.5"/><text x="{W/2}" y="155" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="900" fill="{INK}">FIELD CLEARED!</text>')
ground = ''.join(f'<rect x="{x}" y="318" width="{w}" height="3" fill="#2b84c0"/>' for x, w in ((30, 40), (130, 24), (260, 56), (420, 30), (560, 48), (700, 26), (820, 60)))
anim = (f'.rk{{transform:translateX({x0:.1f}px);animation:rk {T:.2f}s cubic-bezier(.45,0,.3,1) infinite}}.lz{{opacity:0;animation:lz {T:.2f}s linear infinite}}'
        f'.fl,.dd{{opacity:0;animation-duration:{T:.2f}s;animation-iteration-count:infinite;animation-timing-function:linear}}.fl{{animation-name:fx}}.d1{{animation-name:d1}}.d2{{animation-name:d2}}.d3{{animation-name:d3}}'
        f'.fx{{transform-box:fill-box;transform-origin:center}}.cl{{opacity:0;animation:cl {T:.2f}s linear infinite}}'
        '.f1{animation:ff .2s steps(1) infinite}.f2{animation:ff .2s steps(1) infinite -.1s}.s1{animation:tw 3s ease-in-out infinite}.s2{animation:tw 5s ease-in-out infinite -2s}')
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="A rocket blasting the asteroids that represent {USER}'s GitHub contributions">
<title>Rocket vs. contribution asteroids</title><style>{anim}{''.join(css)}</style>
<rect width="{W}" height="{H}" rx="18" fill="{BLUE}"/>{stars}{empty}{ground}{rock_svg}{deb}{lasers}<g class="rk">{rocket}</g><g class="cl">{bub}</g>{hud}</svg>'''
os.makedirs(os.path.dirname(OUT) or '.', exist_ok=True); open(OUT, 'w', encoding='utf-8').write(svg)
print(f'wrote {OUT}: {len(rocks)} asteroids, loop {T:.1f}s, {len(svg)//1024} KB')
