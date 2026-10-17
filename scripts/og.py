# Link-preview cards (1200x630) for the articles, in the site's style: white, Geist, neutral greys, indigo primary.
# usage: python3 scripts/og.py  -> public/<slug>/og-card.png for every card below (needs headless Chrome via puppeteer-core, see CHROME/PPTR)
# A card = title (the *starred* part in indigo) + subtitle + either a flow of boxes (the last one indigo) or a row of icons.
import os, re, subprocess, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = "/tmp/yunoo-og"
CARDS = {
    "software-factory": dict(title="Monte ta *software factory*", sub="Des tickets Linear codés, testés et livrés en PR par un agent IA.",
                             flow=[("Linear", "un ticket « factory »"), ("VPS ou GitHub Actions", "chaque heure"), ("Claude Code", "code et teste"), ("Pull request", "tu relis, tu merges")]),
    "rea": dict(title="Installe *REA* en local", sub="Donne à ton agent IA des outils de reverse engineering.",
                flow=[("Une appli", "web, Android, native"), ("REA", "outils d'analyse"), ("Ton agent IA", "Claude Code, Cursor…"), ("La réponse", "avec les preuves")]),
    "artcraft": dict(title="Les *13 applis* d'ArtCraft", sub="Gratuites et open source, une pour chaque logiciel créatif qu'on paye.",
                     icons=["photocraft", "filmcraft", "effectcraft", "vectorcraft", "designcraft", "figcraft", "lightcraft",
                            "soundcraft", "wordcraft", "deckcraft", "gridcraft", "pdfcraft", "cadcraft"]),
    "anatomy": dict(title="Installe *Anatomy*", sub="Le skill Claude Code qui transforme un concept en machine animée.",
                    flow=[("Un concept", "cache, file, rate limiter…"), ("/anatomy", "dans Claude Code"), ("Un vrai objet", "qui marche pareil"), ("Une machine", "animée, interactive")]),
}
ARROW = ('<div class="arrow"><svg viewBox="0 0 34 14"><path d="M1 7 H30" stroke="#a3a3a3" stroke-width="2" fill="none"/>'
         '<path d="M24 2 L31 7 L24 12" stroke="#a3a3a3" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg></div>')
CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body { width: 1200px; height: 630px; background: #fff; font-family: "Geist", sans-serif; color: #0a0a0a; overflow: hidden; }
.wrap { position: absolute; left: 88px; right: 88px; top: 0; bottom: 0; display: flex; flex-direction: column; justify-content: center; }
h1 { font-size: 72px; line-height: 1.06; font-weight: 600; letter-spacing: -2px; }
h1 span { color: #1c24b5; }
p { margin-top: 18px; font-size: 27px; line-height: 1.4; color: #737373; max-width: 960px; }
.flow { margin-top: 84px; display: flex; align-items: center; }
.node { border: 1.5px solid #e5e5e5; border-radius: 14px; background: #fff; padding: 14px 22px 15px; box-shadow: 0 1px 2px rgba(0,0,0,.04); }
.node b { display: block; font-size: 21px; font-weight: 600; white-space: nowrap; }
.node i { display: block; font-style: normal; font-size: 16px; color: #737373; margin-top: 3px; white-space: nowrap; }
.node.p { background: #1c24b5; border-color: #1c24b5; } .node.p b, .node.p i { color: #fafafa; }
.arrow { width: 46px; display: flex; align-items: center; justify-content: center; } .arrow svg { width: 34px; height: 14px; }
.icons { margin-top: 76px; display: flex; gap: 14px; }
.icons img { width: 66px; height: 66px; border-radius: 15px; box-shadow: 0 1px 2px rgba(0,0,0,.06); border: 1.5px solid #e5e5e5; }
"""


def fonts():   # Geist from Google Fonts, cached locally (Chrome cannot fetch them from a file:// page reliably)
    os.makedirs(TMP, exist_ok=True)
    out = ""
    ua = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"}
    css = urllib.request.urlopen(urllib.request.Request("https://fonts.googleapis.com/css2?family=Geist:wght@400;600&display=swap", headers=ua)).read().decode()
    for sub, b in re.findall(r"/\* (\S+) \*/\s*@font-face \{([^}]*)\}", css):
        if sub != "latin": continue
        w = re.search(r"font-weight: (\d+)", b).group(1); url = re.search(r"url\((\S+?)\)", b).group(1); fn = f"{TMP}/Geist-{w}.woff2"
        if not os.path.exists(fn): open(fn, "wb").write(urllib.request.urlopen(url).read())
        out += f"@font-face {{ font-family: 'Geist'; src: url('Geist-{w}.woff2'); font-weight: {w}; }}\n"
    return out


def card(c):
    title = re.sub(r"\*(.+?)\*", r"<span>\1</span>", c["title"])
    if "flow" in c:
        n = len(c["flow"])
        nodes = [f'<div class="node{" p" if k == n - 1 else ""}"><b>{a}</b><i>{b}</i></div>' for k, (a, b) in enumerate(c["flow"])]
        bottom = '<div class="flow">' + ARROW.join(nodes) + "</div>"
    else:
        bottom = '<div class="icons">' + "".join(f'<img src="file://{ROOT}/public/artcraft/{i}.webp">' for i in c["icons"]) + "</div>"
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{FONT_CSS}{CSS}</style></head><body><div class="wrap"><h1>{title}</h1><p>{c["sub"]}</p>{bottom}</div></body></html>'


SHOT = """const p = require(process.env.PPTR); (async () => { const b = await p.launch({ executablePath: process.env.CHROME, headless: true, args: ["--no-sandbox", "--allow-file-access-from-files"] });
const pg = await b.newPage(); await pg.setViewport({ width: 1200, height: 630, deviceScaleFactor: 2 }); await pg.goto(process.argv[2], { waitUntil: "networkidle0" });
await pg.evaluate(() => document.fonts.ready); await pg.screenshot({ path: process.argv[3] }); await b.close(); })();"""

FONT_CSS = fonts()
open(f"{TMP}/shot.cjs", "w").write(SHOT)
for slug, c in CARDS.items():
    html, png2x = f"{TMP}/{slug}.html", f"{TMP}/{slug}@2x.png"
    open(html, "w").write(card(c))
    subprocess.run(["node", f"{TMP}/shot.cjs", f"file://{html}", png2x], check=True)
    os.makedirs(f"{ROOT}/public/{slug}", exist_ok=True)
    subprocess.run(["sips", "-z", "630", "1200", png2x, "--out", f"{ROOT}/public/{slug}/og-card.png"], check=True, capture_output=True)
    print(f"public/{slug}/og-card.png")
