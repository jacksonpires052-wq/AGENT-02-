"""Story de notícia, layout LEVE (colorido e descontraído, mas sério no conteúdo). 1080x1920 JPG.
Uso: python3 agente03/story_leve.py noticia.json saida.jpg
Mesmos campos do Boletim (story.py). A cor de fundo muda pelo número da notícia (pasta AAAA-MM-DD-NN).
"""
import json, sys, html, asyncio, os, re, base64
sys.path.insert(0, os.path.dirname(__file__))
from story import categoria, data_fmt

AQUI = os.path.dirname(os.path.abspath(__file__))
def fonte(nome, arq, peso):
    b = base64.b64encode(open(os.path.join(AQUI, "fontes", arq), "rb").read()).decode()
    return f"@font-face{{font-family:'{nome}';font-weight:{peso};src:url(data:font/woff2;base64,{b}) format('woff2')}}"
FONTES = "".join([fonte("Brico", f"bricolage-grotesque-latin-{p}-normal.woff2", p) for p in (400, 600, 800)] +
                 [fonte("DM", f"dm-sans-latin-{p}-normal.woff2", p) for p in (400, 500, 700)])

# fundo, destaque do número, cor do texto do destaque
CORES = [("#FFC93C", "#1B1B2F", "#FFC93C"), ("#7CC4FF", "#FF7A59", "#FFFFFF"), ("#FF8A65", "#1B1B2F", "#FFD84D"),
         ("#5FD3B0", "#1B1B2F", "#B8F5E4"), ("#B79CFF", "#FFC93C", "#1B1B2F")]

def pagina(n, edicao, total=10):
    e = lambda k: html.escape(str(n.get(k, "")))
    bg, chip, chiptxt = CORES[(edicao - 1) % len(CORES)]
    pontos = "".join(f'<i class="{"on" if i < edicao else ""}"></i>' for i in range(total))
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>{FONTES}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;background:{bg};color:#1B1B2F;font-family:DM;position:relative;overflow:hidden}}
.b1{{position:absolute;width:520px;height:520px;border-radius:50%;background:#ffffff40;top:-140px;right:-160px}}
.b2{{position:absolute;width:360px;height:360px;border-radius:50%;border:28px solid #1B1B2F14;bottom:120px;left:-150px}}
.est{{position:absolute;font:800 90px Brico;color:#1B1B2F}}
.wrap{{position:absolute;top:230px;left:80px;right:80px;bottom:240px;display:flex;flex-direction:column}}
.top{{display:flex;justify-content:space-between;align-items:center}}
.pill{{font:700 28px DM;background:#1B1B2F;color:#fff;border-radius:60px;padding:14px 28px;letter-spacing:1px}}
.pts{{display:flex;gap:10px}}.pts i{{width:18px;height:18px;border-radius:50%;background:#1B1B2F30;display:block}}.pts i.on{{background:#1B1B2F}}
.card{{margin-top:56px;background:#FFF8EC;border-radius:56px;padding:56px 56px 48px;border:4px solid #1B1B2F;box-shadow:14px 14px 0 #1B1B2F;transform:rotate(-1.2deg)}}
.cat{{display:inline-block;font:700 26px DM;letter-spacing:3px;color:#1B1B2F;background:{bg};border:3px solid #1B1B2F;border-radius:40px;padding:10px 22px}}
.num{{margin-top:34px;display:inline-block;font:800 190px/1 Brico;letter-spacing:-6px;background:{chip};color:{chiptxt};padding:18px 34px 26px;border-radius:40px;transform:rotate(-3deg);white-space:nowrap}}
.leg{{margin-top:30px;font:500 38px/1.3 DM;color:#3A3A55}}
.tit{{margin-top:40px;font:800 66px/1.08 Brico;letter-spacing:-1px}}
.muda{{margin-top:40px;background:#1B1B2F;color:#fff;border-radius:44px;padding:40px 44px;transform:rotate(1deg)}}
.muda h4{{font:700 26px DM;letter-spacing:3px;color:{bg if bg != "#FFC93C" else "#FFC93C"};margin-bottom:14px}}
.muda p{{font:400 36px/1.42 DM}}
.esp{{flex:1}}
.fonte{{font:500 24px/1.35 DM;color:#1B1B2Fb0;margin-bottom:18px}}.fonte b{{font-weight:700;color:#1B1B2F;margin-right:8px}}
.rod{{display:flex;align-items:center;justify-content:space-between;background:#FFF8EC;border:4px solid #1B1B2F;border-radius:60px;padding:18px 18px 18px 36px}}
.rod b{{font:800 34px Brico;display:block}}.rod small{{font:500 24px DM;color:#3A3A55}}
.selo{{font:700 22px DM;letter-spacing:2px;background:#1B1B2F;color:#fff;border-radius:40px;padding:14px 22px}}
</style></head><body><div class="b1"></div><div class="b2"></div>
<div class="est" style="top:150px;left:60px;transform:rotate(12deg)">✦</div>
<div class="est" style="bottom:330px;right:70px;font-size:70px;transform:rotate(-8deg)">✦</div>
<div class="wrap" id="w">
 <div class="top"><div class="pill">Notícia do dia · {html.escape(data_fmt(n.get("data")))}</div><div class="pts">{pontos}</div></div>
 <div class="card" id="c">
  <div class="cat">{html.escape(categoria(n))}</div><br>
  <div class="num" id="n">{e("numero")}</div>
  <div class="leg">{e("numero_legenda")}</div>
  <div class="tit" id="t">{e("titulo")}</div>
 </div>
 <div class="muda"><h4>E PARA VOCÊ?</h4><p>{e("texto")}</p></div>
 <div class="esp"></div>
 <div class="fonte"><b>Fonte:</b>{e("fonte")}</div>
 <div class="rod"><div><b>Jackson Pires</b><small>Corretor de imóveis | CRECI 323400</small></div><div class="selo">SOROCABA E REGIÃO</div></div>
</div>
<script>
const w=document.getElementById('w'),n=document.getElementById('n'),t=document.getElementById('t'),c=document.getElementById('c');
let ns=190; while(n.offsetWidth>c.clientWidth-112 && ns>100){{ns-=8;n.style.fontSize=ns+'px'}}
let fs=66; while(w.scrollHeight>w.clientHeight+1 && fs>48){{fs-=2;t.style.fontSize=fs+'px'}}
document.body.dataset.estouro=w.scrollHeight-w.clientHeight;
</script></body></html>'''

async def render(n, saida, edicao):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(channel="chrome")
        pg = await b.new_page(viewport={"width": 1080, "height": 1920})
        await pg.set_content(pagina(n, edicao)); await pg.wait_for_timeout(500)
        est = int(await pg.evaluate("document.body.dataset.estouro"))
        await pg.screenshot(path=saida + ".png"); await b.close()
    from PIL import Image
    Image.open(saida + ".png").convert("RGB").save(saida, quality=93); os.remove(saida + ".png")
    if est > 1: print(f"ATENÇÃO: texto não coube ({est}px). Encurte o título ou o texto."); sys.exit(2)
    print("ok", saida)

if __name__ == "__main__":
    n = json.load(open(sys.argv[1], encoding="utf-8"))
    ed = n.get("edicao")
    if not ed:
        m = re.search(r"\d{4}-\d{2}-\d{2}-(\d{2})", os.path.abspath(sys.argv[1]))
        ed = int(m.group(1)) if m else 1
    asyncio.run(render(n, sys.argv[2], int(ed)))
