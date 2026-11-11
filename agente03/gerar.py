"""Carrossel Objeto: gera 5 slides 1080x1350 a partir de um JSON de conteúdo.
Uso: python3 gerar.py conteudo.json pasta_saida
"""
import json, sys, os, html, base64
from playwright.sync_api import sync_playwright

AZUL = "#3F5FD9"
PAPEL = "#EEECE6"

ICONS_IG = """
<svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 21s-7.5-4.6-9.5-9.2C1 8.3 3.3 5 6.6 5c2 0 3.6 1.1 5.4 3 1.8-1.9 3.4-3 5.4-3C20.7 5 23 8.3 21.5 11.8 19.5 16.4 12 21 12 21z"/></svg>
<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M20.5 11.5a8.5 8.5 0 1 1-3.4-6.8A8.5 8.5 0 0 1 20.5 11.5zM20.5 20.5l-2.6-2.6"/></svg>
<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M22 3 9.2 10.4M22 3l-7 18-4.6-8.6L2 8z"/></svg>
"""

CSS = f"""
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:#222; }}
.slide {{ width:1080px; height:1350px; position:relative; overflow:hidden;
  font-family:'Inter Display','Inter',sans-serif; color:#111; }}
.papel {{ background:{PAPEL}; }}
.azul {{ background:{AZUL}; color:#fff; }}
.grao::after {{ content:''; position:absolute; inset:0; pointer-events:none; opacity:.10;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='3' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .9 0'/></filter><rect width='300' height='300' filter='url(%23n)'/></svg>"); }}
.marca {{ position:absolute; font-family:'Inter'; font-weight:600; font-size:19px; letter-spacing:-.2px; text-transform:uppercase; z-index:5; }}
.tl {{ left:118px; top:104px; }} .tr {{ right:118px; top:104px; }}
.bl {{ left:118px; bottom:100px; }} .br {{ right:118px; bottom:100px; }}
.sombra .marca {{ text-shadow:0 1px 6px rgba(0,0,0,.45); color:#fff; }}

/* ---- miolo ---- */
.esq {{ position:absolute; left:48px; width:540px; top:50%; transform:translateY(-50%); }}
.tit {{ font-weight:700; font-size:66px; line-height:1.0; letter-spacing:-3.4px; white-space:nowrap; }}
.tit span {{ display:inline-block; border-bottom:5px solid currentColor; padding-bottom:4px; margin-bottom:14px; }}
.sub {{ margin-top:30px; font-family:'Inter'; font-size:33px; line-height:1.3; letter-spacing:-1.2px; font-weight:400; }}
.sub b {{ font-weight:700; }}
.fonte {{ margin-top:22px; font-family:'Inter'; font-size:19px; opacity:.6; letter-spacing:-.2px; }}

.card {{ position:absolute; left:611px; top:350px; width:422px; height:657px; border-radius:30px;
  border:2.5px solid #111; background:#fff; overflow:hidden; display:flex; flex-direction:column; }}
.azul .card {{ border-color:#fff; background:{AZUL}; }}
.card .topo {{ height:64px; display:flex; align-items:center; padding:0 18px; gap:12px; background:#fff; color:#111; border-bottom:2px solid #111; }}
.azul .card .topo {{ border-bottom-color:#fff; }}
.av {{ width:40px; height:40px; border-radius:50%; background:{AZUL}; color:#fff; font:700 15px 'Inter'; display:flex; align-items:center; justify-content:center; }}
.nome {{ font:500 14px 'Inter'; letter-spacing:-.3px; line-height:1.15; }}
.nome i {{ font-style:normal; color:{AZUL}; font-size:12px; display:block; }}
.dots {{ margin-left:auto; font:700 20px 'Inter'; }}
.foto {{ flex:1; position:relative; overflow:hidden; display:flex; align-items:center; justify-content:center; }}
.foto .obj {{ font-size:205px; line-height:1; transform:translateY(-8px) rotate(-6deg); filter:drop-shadow(0 18px 20px rgba(0,0,0,.25)); }}
.foto .num {{ position:absolute; z-index:3; top:26px; left:0; right:0; text-align:center; font:800 64px 'Inter Display'; letter-spacing:-3px; color:#fff; text-shadow:0 3px 14px rgba(0,0,0,.35); }}
.halftone::before {{ content:''; position:absolute; inset:0; z-index:2; pointer-events:none;
  background-image:radial-gradient(rgba(0,0,0,.28) 1.3px, transparent 1.6px); background-size:6px 6px; mix-blend-mode:multiply; }}
.leg {{ position:absolute; z-index:3; left:30px; right:30px; bottom:30px; background:#fff; color:#111; padding:12px 14px;
  font:400 25px/1.2 'Inter'; letter-spacing:-1px; text-align:center; }}
.leg b {{ font-weight:700; }}
.sticker {{ position:absolute; z-index:4; font-size:44px; }}
.acoes {{ height:64px; display:flex; align-items:center; gap:14px; padding:0 18px; background:#fff; color:#111; border-top:2px solid #111; }}
.azul .acoes {{ background:{AZUL}; color:#fff; border-top-color:#fff; }}
.acoes .pg {{ margin-left:52px; display:flex; gap:5px; }} .acoes .pg i {{ width:7px; height:7px; border-radius:50%; background:#bbb; }}
.acoes .pg i:first-child {{ background:{AZUL}; }} .azul .acoes .pg i:first-child {{ background:#fff; }}
.acoes .salvar {{ margin-left:auto; }}

/* ---- capa ---- */
.grade {{ position:absolute; inset:0; display:grid; grid-template-columns:1fr 1fr; grid-template-rows:1fr 1fr; }}
.tile {{ position:relative; overflow:hidden; display:flex; align-items:center; justify-content:center; }}
.tile .obj {{ font-size:330px; filter:drop-shadow(0 22px 26px rgba(0,0,0,.3)); }}
.capa-txt {{ position:absolute; left:0; right:0; top:50%; transform:translateY(-50%); z-index:6; display:flex; flex-direction:column; align-items:center; }}
.capa-txt span {{ background:{AZUL}; color:#fff; font:700 98px/1.0 'Inter Display'; letter-spacing:-5.5px; padding:6px 22px 14px; margin-top:-2px; white-space:nowrap; }}
.brilho {{ position:absolute; z-index:7; font-size:70px; }}

/* ---- capa de noticia (plantao de TV) ---- */
.cn {{ background:#0b1631; font-family:'Inter'; }}
.cn-foto {{ position:absolute; right:-60px; top:0; width:760px; height:1350px; background-size:cover; background-position:center 18%; }}
.cn-veu {{ position:absolute; inset:0; background:linear-gradient(90deg,#0b1631 30%,rgba(11,22,49,.85) 52%,rgba(11,22,49,0) 78%),linear-gradient(0deg,#0b1631 22%,rgba(11,22,49,0) 58%); }}
.cn-selo {{ position:absolute; left:70px; top:80px; display:flex; z-index:3; }}
.cn-selo b {{ background:#e11d2e; color:#fff; font:800 30px 'Inter Display'; letter-spacing:1px; padding:12px 22px; }}
.cn-selo span {{ background:#fff; color:#0b1631; font:700 30px 'Inter'; letter-spacing:.5px; padding:12px 22px; }}
.cn-data {{ position:absolute; left:70px; top:150px; color:#9fb0d6; font:600 24px 'Inter'; letter-spacing:2px; z-index:3; }}
.cn-bloco {{ position:absolute; left:70px; right:70px; bottom:150px; z-index:3; }}
.cn-num {{ color:#ffd23f; font-family:'Inter Display'; font-weight:900; line-height:1; letter-spacing:-.05em; margin-left:-6px; margin-bottom:18px; white-space:nowrap; }}
.cn-tit {{ color:#fff; font-family:'Inter Display'; font-weight:800; line-height:1.03; letter-spacing:-.045em; }}
.cn-sub {{ margin-top:30px; max-width:860px; color:#c9d3ea; font:500 32px/1.3 'Inter'; letter-spacing:-.8px; }}
.cn-rodape {{ position:absolute; left:0; right:0; bottom:0; height:96px; background:#e11d2e; display:flex; align-items:center; padding:0 70px; color:#fff; font:700 26px 'Inter'; letter-spacing:.4px; z-index:3; white-space:nowrap; }}
.cn-rodape span {{ margin-left:auto; padding-left:24px; font-weight:500; opacity:.9; overflow:hidden; text-overflow:ellipsis; }}

/* ---- final ---- */
.final .box {{ position:absolute; left:130px; right:130px; top:560px; z-index:6; background:{AZUL}; padding:16px 18px; font:400 33px/1.25 'Inter'; letter-spacing:-1.2px; text-align:center; color:#fff; border:2px solid rgba(255,255,255,.25); }}
.final .box b {{ font-weight:700; }}
.final .cta {{ position:absolute; left:0; right:0; top:760px; z-index:6; text-align:center; color:#fff; font:700 84px/1.02 'Inter Display'; letter-spacing:-4.5px; }}
.final .cta span {{ display:inline-block; border-bottom:4px solid #fff; padding-bottom:6px; margin-bottom:14px; }}
.final .obj {{ position:absolute; z-index:3; font-size:420px; left:50%; top:90px; transform:translateX(-50%) rotate(-8deg); filter:drop-shadow(0 30px 30px rgba(0,0,0,.35)); }}
.fotofundo {{ position:absolute; inset:0; background-size:cover; background-position:center 10%; z-index:1; }}
.fotofundo::after {{ content:''; position:absolute; inset:0; background:linear-gradient(180deg, rgba(20,30,80,0) 35%, rgba(20,30,80,.55) 60%, rgba(20,30,80,.75) 100%); }}
.com-foto .box {{ top:740px; left:110px; right:110px; font-size:30px; border:none; }}
.com-foto .cta {{ top:900px; font-size:70px; }}
"""


def datauri(p):
    return "data:image/jpeg;base64," + base64.b64encode(open(p, "rb").read()).decode()


def marcas(m):
    return f"""<div class='marca tl'>{m['tl']}</div><div class='marca tr'>{m['tr']}</div>
<div class='marca bl'>{m['bl']}</div><div class='marca br'>{m['br']}</div>"""


def card(c, m):
    stickers = "".join(
        f"<div class='sticker' style='{s['pos']}'>{s['emoji']}</div>" for s in c.get("stickers", []))
    return f"""<div class='card'>
 <div class='topo'><div class='av'>{m['iniciais']}</div><div class='nome'>{m['nome_card']}<i>{m['arroba']}</i></div><div class='dots'>···</div></div>
 <div class='foto halftone' style='background:{c['fundo']}'>
   <div class='num'>{c['numero']}</div><div class='obj'>{c['objeto']}</div>
   <div class='leg'>{c['legenda']}</div>{stickers}
 </div>
 <div class='acoes'>{ICONS_IG}<div class='pg'><i></i><i></i><i></i><i></i></div>
   <svg class='salvar' width='30' height='30' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='1.8'><path d='M6 3h12v18l-6-5-6 5z'/></svg></div>
</div>"""


def slide_capa(s, m):
    def tile(t):
        if t.get("foto"):
            return f"<div class='tile halftone' style=\"background:url('{datauri(t['foto'])}') center 12%/165%\"></div>"
        return f"<div class='tile halftone' style='background:{t['fundo']}'><div class='obj'>{t['objeto']}</div></div>"
    tiles = "".join(tile(t) for t in s["tiles"])
    linhas = "".join(f"<span>{l}</span>" for l in s["linhas"])
    brilhos = "".join(f"<div class='brilho' style='{b}'>✨</div>" for b in s.get("brilhos", []))
    return f"<div class='slide sombra'><div class='grade'>{tiles}</div>{marcas(m)}<div class='capa-txt'>{linhas}</div>{brilhos}</div>"


def slide_capa_noticia(s, m):
    """Capa estilo PLANTAO DE TV (escolhida pelo Jackson em 11/11/2026)."""
    foto = datauri(s.get("foto", "agente03/jackson.jpg"))
    linhas = s["linhas"]
    maior = max(len(l) for l in linhas)
    tam = min(78, int(1880 / max(maior, 1)))
    tit = "<br>".join((f"<span style='color:#ffd23f'>{l}</span>" if i == len(linhas) - 1 else l) for i, l in enumerate(linhas))
    num = s.get("numero", "")
    tnum = min(230, int(1500 / max(len(num), 1)))
    sub = f"<div class='cn-sub'>{s['sub']}</div>" if s.get("sub") else ""
    return f"""<div class='slide cn'>
<div class='cn-foto' style="background-image:url('{foto}')"></div><div class='cn-veu'></div>
<div class='cn-selo'><b>&#9679; NOTÍCIA</b><span>{s.get('categoria', 'MERCADO IMOBILIÁRIO').upper()}</span></div>
<div class='cn-data'>{s.get('data', '').upper()}</div>
<div class='cn-bloco'><div class='cn-num' style='font-size:{tnum}px'>{num}</div>
<div class='cn-tit' style='font-size:{tam}px'>{tit}</div>{sub}</div>
<div class='cn-rodape'>JACKSON PIRES · CRECI 323400<span style='font-size:{26 if len(s.get("fonte", "")) < 26 else 22}px'>{s.get('fonte', '')}</span></div></div>"""


def slide_miolo(s, m):
    tit = "<br>".join(f"<span>{l}</span>" for l in s["titulo"])
    fonte = f"<div class='fonte'>{s['fonte']}</div>" if s.get("fonte") else ""
    return f"""<div class='slide {s['cor']} grao'>{marcas(m)}
<div class='esq'><div class='tit'>{tit}</div><div class='sub'>{s['texto']}</div>{fonte}</div>
{card(s['card'], m)}</div>"""


def slide_final(s, m):
    cta = "<br>".join(f"<span>{l}</span>" for l in s["cta"])
    if s.get("foto"):
        return f"""<div class='slide azul final com-foto halftone sombra'>
<div class='fotofundo' style=\"background-image:url('{datauri(s['foto'])}')\"></div>{marcas(m)}
<div class='box'>{s['caixa']}</div>
<div class='cta'>{cta}</div></div>"""
    return f"""<div class='slide azul final grao halftone sombra'>{marcas(m)}
<div class='obj'>{s['objeto']}</div>
<div class='box'>{s['caixa']}</div>
<div class='cta'>{cta}</div></div>"""


def main(cfg_path, out):
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    m = cfg["marca"]
    partes = []
    for s in cfg["slides"]:
        partes.append({"capa": slide_capa, "capa_noticia": slide_capa_noticia, "miolo": slide_miolo, "final": slide_final}[s["tipo"]](s, m))
    doc = f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{''.join(partes)}</body></html>"
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "carrossel.html"), "w", encoding="utf-8").write(doc)
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome")
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        pg.set_content(doc)
        pg.wait_for_timeout(600)
        for i, el in enumerate(pg.query_selector_all(".slide"), 1):
            el.screenshot(path=os.path.join(out, f"slide{i:02d}.png"))
        b.close()
    # JPG para o Instagram
    from PIL import Image
    for i in range(1, len(partes) + 1):
        Image.open(os.path.join(out, f"slide{i:02d}.png")).convert("RGB").save(
            os.path.join(out, f"slide{i:02d}.jpg"), quality=93)
    print("ok", len(partes))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
