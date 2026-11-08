#!/usr/bin/env python3
"""Generate assets/rhythm.svg: a rhythm game where every GitHub contribution day is a falling note.
Usage: python rhythm.py [github_user] [output.svg]   (standard library only)"""
import re, sys, os, math, random, datetime, urllib.request
USER = sys.argv[1] if len(sys.argv) > 1 else 'Pali912'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'assets/rhythm.svg'
DEBUG = os.environ.get('RHYTHM_DEBUG') == '1'
MONO = "font-family=\"SFMono-Regular,Consolas,'Courier New',monospace\""
SANS = "font-family=\"'Helvetica Neue',Helvetica,Arial,sans-serif\""
def fetch():
    req = urllib.request.Request(f'https://github.com/users/{USER}/contributions', headers={'User-Agent': 'Mozilla/5.0'})
    page = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'ignore')
    cells = re.findall(r'<td[^>]*?data-date="(\d{4}-\d{2}-\d{2})"[^>]*?data-level="(\d)"', page)
    if not cells: cells = [(d, l) for l, d in re.findall(r'data-level="(\d)"[^>]*?data-date="(\d{4}-\d{2}-\d{2})"', page)]
    m = re.search(r'([\d,]+)\s+contributions\s+in the last year', page)
    return sorted(set(cells)), (int(m.group(1).replace(',', '')) if m else None)
try:
    cells, total = fetch(); assert cells
except Exception as e:
    print('warning: using sample data (%s)' % e); random.seed(3); d0 = datetime.date.today() - datetime.timedelta(days=364)
    cells = [((d0 + datetime.timedelta(days=i)).isoformat(), str(random.choice([0, 0, 0, 1, 1, 2, 3, 4]))) for i in range(365)]; total = None
first = datetime.date.fromisoformat(cells[0][0]); off = (first.weekday() + 1) % 7
notes = []
for ds, lv in cells:
    n = (datetime.date.fromisoformat(ds) - first).days + off
    if int(lv) > 0: notes.append((n // 7, n % 7, int(lv)))
notes.sort(); ncols = max(n // 7 for n in range((datetime.date.fromisoformat(cells[-1][0]) - first).days + off + 1)) + 1
total = total if total is not None else len(notes)
W, H = 960, 440; CX = 480; YT, YH = 70, 318; WF, WN = 34, 100
D = 1.9; STEP = .28; T0 = 2.3
LC = {1: '#f2b72a', 2: '#e8788f', 3: '#5fc9c0', 4: '#c8202c'}; PTS = {1: 100, 2: 200, 3: 300, 4: 500}
NAMES = 'CDEFGAB'
wid = lambda u: WF + (WN - WF) * u
cx = lambda l, u: CX + (l - 3) * wid(u)
yy = lambda u: YT + (YH - YT) * u
hit = lambda c: T0 + c * STEP
last = max(hit(c) for c, _, _ in notes); T = last + 4.2
pc = lambda s: '%.3f' % (s / T * 100)
css = []
def kf(name, pts): css.append('@keyframes %s{%s}' % (name, ''.join('%s%%{%s}' % (pc(t), v) for t, v in pts)))
# per-lane fall paths (shared by all notes in the lane, offset by animation-delay)
K = 10
for l in range(7):
    pts = []
    for k in range(K + 1):
        f = k / K; u = f ** 1.8; s = wid(u) / WN
        pts.append((f * D, f'opacity:{0 if k==0 else 1};transform:translate({cx(l,u):.1f}px,{yy(u):.1f}px) scale({s:.3f})'))
    pts.append((D + .01, 'opacity:0;transform:translate(%.1fpx,%.1fpx) scale(1)' % (cx(l, 1), yy(1)))); pts.append((T, 'opacity:0'))
    kf(f'fl{l}', pts)
css.append('@keyframes bu{0%%{opacity:.9;transform:scale(.3)}%s%%{opacity:0;transform:scale(2.4)}100%%{opacity:0;transform:scale(2.4)}}' % pc(.45))
css.append('@keyframes kp{0%%{opacity:.95}%s%%{opacity:.5}%s%%{opacity:0}100%%{opacity:0}}' % (pc(.12), pc(.38)))
css.append('@keyframes pf{0%%{opacity:0;transform:translateY(8px)}%s%%{opacity:1;transform:translateY(0)}%s%%{opacity:0;transform:translateY(-26px)}100%%{opacity:0}}' % (pc(.08), pc(.8)))
css.append('@keyframes rush{0%%{opacity:0}%s%%{opacity:.5}100%%{opacity:0}}' % pc(.05))
css.append('@keyframes kick{0%{transform:scale(1.1)}22%{transform:scale(1)}100%{transform:scale(1)}}@keyframes eq{0%,100%{transform:scaleY(.15)}50%{transform:scaleY(1)}}@keyframes gl{0%,100%{opacity:.25}50%{opacity:.8}}')
css.append('@keyframes fc{0%%{opacity:0}%s%%{opacity:0}%s%%{opacity:1}%s%%{opacity:1}%s%%{opacity:0}100%%{opacity:0}}' % (pc(last + .8), pc(last + 1.1), pc(T - .7), pc(T - .4)))
BEAT = 60 / 92
base = ('.nt{animation-duration:%.3fs;animation-iteration-count:infinite;animation-timing-function:linear}' % T) + ('' if DEBUG else '.nt{opacity:0}') + \
       '.ev{opacity:0;animation-duration:%.3fs;animation-iteration-count:infinite;animation-timing-function:linear}.bu{transform-box:fill-box;transform-origin:center;animation-name:bu}.kp{animation-name:kp}.pf{animation-name:pf}.fc{animation:fc %.3fs linear infinite;opacity:0}' % (T, T) + \
       '.cone{transform-box:fill-box;transform-origin:center;animation:kick %.3fs ease-out infinite}.eqb{transform-box:fill-box;transform-origin:50%% 100%%;animation:eq 1s ease-in-out infinite}.gl{animation:gl %.2fs ease-in-out infinite}' % (BEAT, BEAT * 4)
for l in range(7): base += f'.fl{l}{{animation-name:fl{l}}}'
# ---------------- scene ----------------
bars = ''.join(f'<rect class="eqb" x="{12+i*19.6:.1f}" y="{440-h}" width="11" height="{h}" rx="3" fill="url(#eg)" style="animation-duration:{random.uniform(.5,1.2):.2f}s;animation-delay:-{random.uniform(0,1.2):.2f}s"/>' for i,h in ((i, random.randrange(70, 200)) for i in range(48)))
hw = lambda u: wid(u) * 3.5
hwy = f'<polygon points="{CX-hw(0):.1f},{YT} {CX+hw(0):.1f},{YT} {CX+hw(1):.1f},{YH} {CX-hw(1):.1f},{YH}" fill="url(#hg)" stroke="#1b1a1c" stroke-width="3.5" stroke-linejoin="round"/>'
lanes = ''.join(f'<line x1="{CX+(i-3.5)*WF:.1f}" y1="{YT}" x2="{CX+(i-3.5)*WN:.1f}" y2="{YH}" stroke="#1b1a1c" stroke-opacity=".4" stroke-width="1.6"/>' for i in range(8))
rush = ''
for j in range(6):
    steps = ''.join(f'{pc(f*1.6)}%{{transform:translate({CX}px,{yy(f**1.8):.1f}px) scale({wid(f**1.8)*7:.1f},1)}}' for f in [i/8 for i in range(9)])
    css.append(f'@keyframes rs{j}{{{steps}}}')
    rush += f'<rect class="rl" x="-.5" y="-.8" width="1" height="1.6" fill="#c6c5b9" opacity=".3" style="animation:rs{j} {BEAT*2:.3f}s linear infinite -{j*BEAT*2/6:.3f}s"/>'
keys = ''
for l in range(7):
    x = CX + (l - 3.5) * WN
    keys += f'<rect x="{x+2:.1f}" y="{YH+10}" width="{WN-4}" height="104" rx="6" fill="#e6e5de" stroke="#1b1a1c" stroke-width="3"/><text x="{x+WN/2:.1f}" y="{YH+104}" text-anchor="middle" {MONO} font-size="11" font-weight="700" fill="#1b1a1c">{NAMES[l]}</text>'
for b in (1, 2, 4, 5, 6):
    x = CX + (b - 3.5) * WN; keys += f'<rect x="{x-17:.1f}" y="{YH+10}" width="34" height="62" rx="4" fill="#1b1a1c"/>'
ev = notes_svg = ''
score = 0; order = sorted(notes, key=lambda n: (n[0], n[1]))
for i, (c, l, lv) in enumerate(order):
    th = hit(c); col = LC[lv]
    notes_svg += f'<g class="nt fl{l}" style="animation-delay:{th-D:.2f}s"><rect x="-37" y="-8" width="74" height="16" rx="5" fill="{col}" stroke="#1b1a1c" stroke-width="3"/><rect x="-33" y="-6" width="66" height="4" rx="2" fill="#fff" opacity=".35"/></g>'
    x = cx(l, 1); ev += f'<circle class="ev bu" cx="{x:.1f}" cy="{YH}" r="26" fill="none" stroke="{col}" stroke-width="3" style="animation-delay:{th:.2f}s"/>'
    ev += f'<rect class="ev kp" x="{CX+(l-3.5)*WN+2:.1f}" y="{YH+10}" width="{WN-4}" height="104" rx="6" fill="{col}" style="animation-delay:{th:.2f}s"/>'
    if i % 5 == 0: ev += f'<text class="ev pf" x="{x:.1f}" y="{YH-24}" text-anchor="middle" {SANS} font-size="15" font-weight="800" fill="{col}" stroke="#1b1a1c" stroke-width="3.5" paint-order="stroke" style="animation-delay:{th:.2f}s">PERFECT</text>'
    score += PTS[lv]
# combo/score counters: one element per distinct hit time
groups = {}
for i, (c, l, lv) in enumerate(order): groups.setdefault(c, []).append(i)
cols = sorted(groups); run = 0; run_s = 0; counters = ''
for gi, c in enumerate(cols):
    for i in groups[c]: run += 1; run_s += PTS[order[i][2]]
    th = hit(c); end = hit(cols[gi + 1]) if gi + 1 < len(cols) else T - .45
    kf(f'cn{gi}', [(0, 'opacity:0'), (th - .001, 'opacity:0'), (th, 'opacity:1'), (end - .001, 'opacity:1'), (end, 'opacity:0'), (T, 'opacity:0')])
    counters += (f'<g style="animation:cn{gi} {T:.3f}s linear infinite;opacity:0"><text x="{W-28}" y="96" text-anchor="end" {SANS} font-size="38" font-weight="800" fill="#f1f0e6" stroke="#1b1a1c" stroke-width="5" paint-order="stroke">x{run}</text>'
                 f'<text x="28" y="96" {SANS} font-size="38" font-weight="800" fill="#f1f0e6" stroke="#1b1a1c" stroke-width="5" paint-order="stroke">{run_s:06d}</text></g>')
final = run_s
subs = ''.join(f'<g><rect x="{x-44}" y="{y-44}" width="88" height="88" rx="14" fill="#c6c5b9" stroke="#1b1a1c" stroke-width="3.5"/><circle cx="{x}" cy="{y}" r="36" fill="#2a2a30" stroke="#1b1a1c" stroke-width="4"/><g class="cone"><circle cx="{x}" cy="{y}" r="30" fill="url(#cn)"/><circle cx="{x}" cy="{y}" r="11" fill="url(#dc)"/></g></g>' for x, y in ((62, 390), (898, 390)))
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="A rhythm game where each of {USER}'s GitHub contribution days is a falling note played on a piano keyboard">
<title>Contribution rhythm game</title>
<defs><linearGradient id="hg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7d8089"/><stop offset="1" stop-color="#6f6d6e"/></linearGradient><linearGradient id="eg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2b84c0" stop-opacity=".55"/><stop offset="1" stop-color="#2b84c0" stop-opacity=".12"/></linearGradient>
<radialGradient id="cn" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#34344a"/><stop offset=".7" stop-color="#16161f"/><stop offset="1" stop-color="#0a0a10"/></radialGradient><radialGradient id="dc" cx=".4" cy=".35"><stop offset="0" stop-color="#4b4b63"/><stop offset="1" stop-color="#14141c"/></radialGradient>
<clipPath id="cp"><rect width="{W}" height="{H}" rx="20"/></clipPath></defs>
<style>{base}{''.join(css)}</style>
<g clip-path="url(#cp)"><rect width="{W}" height="{H}" fill="#05538a"/>{bars}{subs}{hwy}{lanes}{rush}
<rect x="{CX-WN*3.5}" y="{YH-2}" width="{WN*7}" height="4" rx="2" fill="#f2b72a" stroke="#1b1a1c" stroke-width="1.5" opacity=".95"/><rect class="gl" x="{CX-WN*3.5}" y="{YH-8}" width="{WN*7}" height="16" fill="#f2b72a" opacity=".25"/>
{keys}{notes_svg}{ev}</g>

<text x="28" y="34" {MONO} font-size="11" font-weight="700" letter-spacing="2" fill="#bcd9ee">TRACK 03 · RHYTHM GAME</text><text x="{W-28}" y="34" text-anchor="end" {MONO} font-size="11" font-weight="700" letter-spacing="2" fill="#bcd9ee">{total:04d} CONTRIBUTIONS = {len(notes)} NOTES</text>
<text x="28" y="56" {MONO} font-size="9" letter-spacing="2" fill="#7fb1d6">SCORE</text><text x="{W-28}" y="56" text-anchor="end" {MONO} font-size="9" letter-spacing="2" fill="#7fb1d6">COMBO</text>{counters}
<g class="fc"><rect x="{CX-150}" y="150" width="300" height="64" rx="14" fill="#c6c5b9" stroke="#1b1a1c" stroke-width="3.5"/><text x="{CX}" y="190" text-anchor="middle" {SANS} font-size="26" font-weight="800" fill="#1b1a1c">FULL COMBO!</text></g></svg>'''
os.makedirs(os.path.dirname(OUT) or '.', exist_ok=True); open(OUT, 'w', encoding='utf-8').write(svg)
print(f'wrote {OUT}: {len(notes)} notes, loop {T:.1f}s, final score {final}, {len(svg)//1024} KB')
