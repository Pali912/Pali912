#!/usr/bin/env python3
"""Generate assets/v3_rhythm.svg: every active GitHub contribution day is a note that falls onto an MPC pad.
Hit the pads in time: score, combo and PERFECT popups run on your real contribution data.
Usage: python rhythm.py [github_user] [output.svg]   (standard library only)"""
import re, sys, os, time, random, datetime, urllib.request
USER = sys.argv[1] if len(sys.argv) > 1 else 'Pali912'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'assets/v3_rhythm.svg'
BLUE, SHD, BEIGE, BEIGE_L, GREY, GREY_D = '#05538a', '#17375c', '#c6c5b9', '#e6e5de', '#7d8089', '#6f6d6e'
INK, RED, YEL, LCD, LCDT = '#1b1a1c', '#c8202c', '#f2b72a', '#6fb7c7', '#1b3b44'
MO = "font-family=\"'Courier New',Consolas,monospace\""; AR = "font-family=\"Arial,Helvetica,sans-serif\""
def fetch():
    req = urllib.request.Request(f'https://github.com/users/{USER}/contributions', headers={'User-Agent': 'Mozilla/5.0'})
    page = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'ignore')
    cells = re.findall(r'<td[^>]*?data-date="(\d{4}-\d{2}-\d{2})"[^>]*?data-level="(\d)"', page)
    if not cells: cells = [(d, l) for l, d in re.findall(r'data-level="(\d)"[^>]*?data-date="(\d{4}-\d{2}-\d{2})"', page)]
    m = re.search(r'([\d,]+)\s+contributions\s+in the last year', page)
    return sorted(set(cells)), (int(m.group(1).replace(',', '')) if m else None)
cells = None
for attempt in range(5):
    try: cells, total = fetch(); assert cells; break
    except Exception as e: err = e; cells = None; time.sleep(3 * (attempt + 1))
if cells is None:
    print('warning: using sample data (%s)' % err); random.seed(3); d0 = datetime.date.today() - datetime.timedelta(days=364)
    cells = [((d0 + datetime.timedelta(days=i)).isoformat(), str(random.choice([1, 1, 2, 3, 4]) if random.random() < 0.03 + 0.6 * (i / 364) ** 5 else 0)) for i in range(365)]; total = None
first = datetime.date.fromisoformat(cells[0][0]); off = (first.weekday() + 1) % 7
notes = []
for ds, lv in cells:
    n = (datetime.date.fromisoformat(ds) - first).days + off
    if int(lv) > 0: notes.append((n // 7, n % 7, int(lv)))
notes.sort(); total = total if total is not None else len(notes)
W, H = 960, 420
PX0, PY0, PS, PG = 573, 40, 76, 10           # pad grid origin / size / gap
PANEL = (548, 24, 384, 372)
D = 1.9; T0 = 2.4; STEP = .30
HITY = PY0 + 3 * (PS + PG); DIST = HITY - (PY0 - PS - 14)
PTS = {1: 100, 2: 200, 3: 300, 4: 500}; LC = {1: '#f2b72a', 2: '#e8788f', 3: '#5fc9c0', 4: '#f08a3c'}
# schedule: lane from day+week, de-collide notes that share a lane in the same week
sched = []; used = {}
for c, r, lv in notes:
    lane = (r + c) % 4; k = used.setdefault((c, lane), 0); used[(c, lane)] += 1
    sched.append((T0 + c * STEP + k * .55, lane, lv))
sched.sort(); last = sched[-1][0]; T = last + 4.4
pc = lambda s: '%.3f' % (s / T * 100); css = []
def kf(n, pts): css.append('@keyframes %s{%s}' % (n, ''.join('%s%%{%s}' % (pc(t), v) for t, v in pts)))
css.append('@keyframes fall{0%%{opacity:1;transform:translateY(0)}%s%%{opacity:1;transform:translateY(%.1fpx)}%s%%{opacity:0;transform:translateY(%.1fpx)}100%%{opacity:0}}' % (pc(D), DIST, pc(D + .01), DIST))
css.append('@keyframes fp{0%%{opacity:.98}%s%%{opacity:.8}%s%%{opacity:0}100%%{opacity:0}}' % (pc(.12), pc(.42)))
css.append('@keyframes bu{0%%{opacity:.95;transform:scale(.5)}%s%%{opacity:0;transform:scale(1.9)}100%%{opacity:0;transform:scale(1.9)}}' % pc(.45))
css.append('@keyframes pf{0%%{opacity:0;transform:translateY(6px)}%s%%{opacity:1;transform:translateY(0)}%s%%{opacity:0;transform:translateY(-22px)}100%%{opacity:0}}' % (pc(.08), pc(.8)))
css.append('@keyframes fcm{0%%{opacity:0}%s%%{opacity:0}%s%%{opacity:1}%s%%{opacity:1}%s%%{opacity:0}100%%{opacity:0}}' % (pc(last + .9), pc(last + 1.2), pc(T - .7), pc(T - .4)))
css.append('@keyframes lp{0%,100%{fill:#13131a}50%{fill:#5be37a}}@keyframes lr{0%,100%{fill:#13131a}50%{fill:#ff5a4d}}@keyframes cur{50%{opacity:0}}@keyframes kk{0%,100%{transform:scale(1)}50%{transform:scale(1.07)}}')
css.append(f'.nt{{opacity:0;animation:fall {T:.3f}s linear infinite}}.ev{{opacity:0;animation-duration:{T:.3f}s;animation-iteration-count:infinite;animation-timing-function:linear}}.fp{{animation-name:fp}}.bu{{transform-box:fill-box;transform-origin:center;animation-name:bu}}.pf{{animation-name:pf}}.fcm{{opacity:0;animation:fcm {T:.3f}s linear infinite}}.lg{{animation:lp 1.3s steps(1) infinite}}.lrd{{animation:lr 1.3s steps(1) infinite}}.cur{{animation:cur .9s steps(1) infinite}}')
lane_x = lambda l: PX0 + l * (PS + PG)
# pads
pads = ''
for r in range(4):
    for c in range(4):
        pads += f'<rect x="{lane_x(c)}" y="{PY0+r*(PS+PG)}" width="{PS}" height="{PS}" rx="6" fill="{GREY_D}" stroke="{INK}" stroke-width="4"/>'
notes_svg = ev = counters = ''; run = 0; score = 0; names = ['PERFECT'] * 6 + ['GREAT']
for i, (th, lane, lv) in enumerate(sched):
    x = lane_x(lane); col = LC[lv]; ystart = PY0 - PS - 14
    notes_svg += f'<g class="nt" style="animation-delay:{th-D:.3f}s"><rect x="{x+6}" y="{ystart+6}" width="{PS-12}" height="{PS-12}" rx="6" fill="{col}" stroke="{INK}" stroke-width="3.5"/><rect x="{x+12}" y="{ystart+12}" width="{PS-24}" height="7" rx="3" fill="#fff" opacity=".4"/></g>'
    dl = f'style="animation-delay:{th:.3f}s"'
    ev += f'<rect class="ev fp" x="{x+3}" y="{HITY+3}" width="{PS-6}" height="{PS-6}" rx="4" fill="{col}" {dl}/><circle class="ev bu" cx="{x+PS/2}" cy="{HITY+PS/2}" r="{PS/2}" fill="none" stroke="{INK}" stroke-width="5" {dl}/><circle class="ev bu" cx="{x+PS/2}" cy="{HITY+PS/2}" r="{PS/2}" fill="none" stroke="{col}" stroke-width="2.5" {dl}/>'
    if i % 4 == 0: ev += f'<text class="ev pf" x="{x+PS/2}" y="{HITY-6}" text-anchor="middle" {AR} font-size="13" font-weight="900" fill="{col}" stroke="{INK}" stroke-width="3.5" paint-order="stroke" {dl}>{names[(i//4)%7]}</text>'
    run += 1; score += PTS[lv]; nxt = sched[i + 1][0] if i + 1 < len(sched) else T - .45
    kf(f'cn{i}', [(0, 'opacity:0'), (max(th - .001, 0.001), 'opacity:0'), (th, 'opacity:1'), (max(nxt - .001, th + .001), 'opacity:1'), (nxt, 'opacity:0'), (T, 'opacity:0')])
    counters += (f'<g style="animation:cn{i} {T:.3f}s linear infinite;opacity:0"><text x="60" y="118" {MO} font-size="38" font-weight="700" fill="{LCDT}">{score:06d}</text>'
                 f'<text x="488" y="118" text-anchor="end" {MO} font-size="38" font-weight="700" fill="{LCDT}">x{run}</text></g>')
trans = ''
for x, w, l, c, cls in ((40, 52, 'REC', RED, 'lrd'), (104, 62, 'OVER DUB', RED, ''), (178, 52, 'STOP', BEIGE_L, ''), (242, 52, 'PLAY', BEIGE_L, ''), (306, 62, 'PLAY START', BEIGE_L, '')):
    trans += f'<text x="{x+w/2}" y="248" text-anchor="middle" {AR} font-size="6.5" font-weight="800" fill="{INK}">{l}</text><rect x="{x}" y="254" width="{w}" height="30" rx="3" fill="{c}" stroke="{INK}" stroke-width="3"/>'
    if cls: trans += f'<circle class="{cls}" cx="{x+9}" cy="246" r="2.8" fill="#13131a"/>'
trans += '<circle class="lg" cx="251" cy="246" r="2.8" fill="#13131a"/>'
knobs = ''.join(f'<circle cx="{x}" cy="{352}" r="22" fill="#2a2a30" stroke="{INK}" stroke-width="3"/><circle cx="{x}" cy="352" r="14" fill="{col}" stroke="{INK}" stroke-width="2.5"/><line x1="{x}" y1="352" x2="{x+dx}" y2="{352+dy}" stroke="#f4f3ec" stroke-width="3" stroke-linecap="round"/>' for x, col, dx, dy in ((62, RED, -6, -12), (132, '#d7d6cc', 9, -9)))
btnrow = ''.join(f'<rect x="{x}" y="318" width="{w}" height="14" rx="2" fill="{BEIGE_L}" stroke="{INK}" stroke-width="2.4"/>' for x, w in ((200, 34), (246, 34), (292, 34), (338, 34), (384, 34), (430, 34)))
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="A rhythm game: each active GitHub contribution day is a note that falls onto an MPC pad">
<title>Contribution rhythm game</title><style>{''.join(css)}</style><defs><clipPath id="pc"><rect x="{PX0-6}" y="{PY0-6}" width="{4*PS+3*PG+12}" height="{4*PS+3*PG+12}" rx="6"/></clipPath></defs>
<rect width="{W}" height="{H}" rx="18" fill="{BLUE}"/><rect x="8" y="8" width="944" height="404" rx="14" fill="{BEIGE}" stroke="{INK}" stroke-width="3.5"/>
<rect x="28" y="24" width="508" height="204" rx="6" fill="#1f1e24" stroke="{INK}" stroke-width="4"/><rect x="44" y="40" width="476" height="172" fill="{LCD}" stroke="{INK}" stroke-width="3"/>
<text x="56" y="62" {MO} font-size="12" font-weight="700" fill="{LCDT}">SEQ 01  03 · CONTRIBUTIONS</text><text x="508" y="62" text-anchor="end" {MO} font-size="12" font-weight="700" fill="{LCDT}">{len(notes)} NOTES · TOTAL {total:04d}</text><line x1="52" y1="70" x2="512" y2="70" stroke="{LCDT}" stroke-width="1.5" opacity=".6"/>
<text x="60" y="88" {MO} font-size="10" font-weight="700" fill="#2a5560">SCORE</text><text x="488" y="88" text-anchor="end" {MO} font-size="10" font-weight="700" fill="#2a5560">COMBO</text>
<text x="60" y="118" {MO} font-size="38" font-weight="700" fill="{LCDT}" opacity=".18">000000</text>{counters}
<text x="60" y="158" {MO} font-size="13" font-weight="700" fill="{LCDT}">ACCURACY 100%</text><text x="60" y="196" {MO} font-size="13" font-weight="700" fill="{LCDT}">PLAY &gt; BAR 1</text><text class="cur" x="508" y="196" text-anchor="end" {MO} font-size="13" font-weight="700" fill="{LCDT}">▮</text>
{trans}{btnrow}{knobs}
<rect x="{PANEL[0]}" y="{PANEL[1]}" width="{PANEL[2]}" height="{PANEL[3]}" rx="6" fill="{GREY}" stroke="{INK}" stroke-width="3.5"/>
{pads}<g clip-path="url(#pc)">{notes_svg}</g>{ev}
<g class="fcm"><rect x="{PX0+8}" y="150" width="{4*PS+3*PG-16}" height="70" rx="8" fill="{BEIGE}" stroke="{INK}" stroke-width="3.5"/><text x="{PX0+(4*PS+3*PG)/2}" y="194" text-anchor="middle" {AR} font-size="28" font-weight="900" fill="{INK}">FULL COMBO!</text></g></svg>'''
os.makedirs(os.path.dirname(OUT) or '.', exist_ok=True); open(OUT, 'w', encoding='utf-8').write(svg)
print(f'wrote {OUT}: {len(notes)} notes, loop {T:.1f}s, final score {score}, {len(svg)//1024} KB')
