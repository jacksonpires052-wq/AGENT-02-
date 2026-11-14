"""Story de notícia, layout BOLETIM (sério e organizado). 1080x1920 JPG.
Uso: python3 agente03/story.py noticia.json saida.jpg
Mesmos campos do story.py. Opcional: "categoria" (ex.: "ALUGUEL") e "edicao" (ex.: 4).
Se "edicao" faltar, pega do nome da pasta (2026-11-14-04-...).
"""
import json, sys, html, asyncio, os, re

CAT = {"desconto": "COMPRA E VENDA", "juros": "JUROS E CRÉDITO", "poupanca": "POUPANÇA",
       "lancamentos": "LANÇAMENTOS", "distrato": "DISTRATOS", "alerta": "ALERTA DE MERCADO",
       "casa_popular": "MINHA CASA, MINHA VIDA", "praia": "LITORAL", "mapa": "REGIÃO",
       "grafico_sobe": "INDICADOR EM ALTA", "grafico_desce": "INDICADOR EM QUEDA"}
PALAVRAS = [("aluguel", "ALUGUEL"), ("mcmv", "MINHA CASA, MINHA VIDA"), ("minha casa", "MINHA CASA, MINHA VIDA"),
            ("juros", "JUROS E CRÉDITO"), ("selic", "JUROS E CRÉDITO"), ("financiamento", "CRÉDITO IMOBILIÁRIO"),
            ("fgts", "FGTS"), ("lançamento", "LANÇAMENTOS"), ("plano diretor", "PLANEJAMENTO URBANO"), ("plano", "PLANEJAMENTO URBANO"), ("constru", "CONSTRUÇÃO"), ("sorocaba", "SOROCABA E REGIÃO")]
MESES = "JAN FEV MAR ABR MAI JUN JUL AGO SET OUT NOV DEZ".split()

def categoria(n):
    if n.get("categoria"): return n["categoria"].upper()
    t = (n.get("titulo", "") + " " + n.get("numero_legenda", "")).lower()
    for k, v in PALAVRAS:
        if k in t: return v
    return CAT.get(n.get("tema"), "MERCADO IMOBILIÁRIO")

def data_fmt(d):
    p = re.findall(r"\d+", d or "")
    if len(p) >= 2:
        ano = p[2] if len(p) > 2 else "2026"
        return f"{int(p[0]):02d} {MESES[int(p[1])-1]} {ano}"
    return d or ""

def pagina(n, edicao, total=10):
    e = lambda k: html.escape(str(n.get(k, "")))
    seg = "".join(f'<i class="{"on" if i < edicao else ""}{" cur" if i == edicao-1 else ""}"></i>' for i in range(total))
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;background:#0A0F1C;color:#F3F5F9;font-family:Inter;position:relative;overflow:hidden}}
.grade{{position:absolute;inset:0;background-image:linear-gradient(#ffffff08 1px,transparent 1px),linear-gradient(90deg,#ffffff08 1px,transparent 1px);background-size:90px 90px}}
.luz{{position:absolute;inset:0;background:radial-gradient(900px 700px at 100% 0%,#1B3A7A55,transparent 70%)}}
.wrap{{position:absolute;top:230px;left:90px;right:90px;bottom:240px;display:flex;flex-direction:column}}
.cab{{display:flex;justify-content:space-between;align-items:flex-end}}
.marca{{font:800 40px 'Inter Display';letter-spacing:6px}}
.marca em{{font-style:normal;color:#E0B252}}
.dt{{font:600 28px Inter;color:#8C98AE;letter-spacing:3px}}
.linha{{height:2px;background:#F3F5F9;margin-top:22px}}
.ed{{display:flex;justify-content:space-between;align-items:center;margin-top:20px;font:600 24px Inter;color:#8C98AE;letter-spacing:3px}}
.seg{{display:flex;gap:8px}}.seg i{{width:34px;height:8px;background:#26304A;display:block}}
.seg i.on{{background:#5E6B85}}.seg i.cur{{background:#E0B252}}
.cat{{margin-top:110px;display:flex;align-items:center;gap:18px;font:700 30px Inter;letter-spacing:5px;color:#E0B252}}
.cat:before{{content:"";width:46px;height:4px;background:#E0B252}}
.num{{margin-top:34px;font:700 230px/0.95 'Inter Display';letter-spacing:-8px;white-space:nowrap}}
.leg{{margin-top:18px;font:500 38px/1.25 Inter;color:#B7C1D3;padding-left:24px;border-left:4px solid #E0B252}}
.tit{{margin-top:70px;font:700 68px/1.12 Lora;letter-spacing:-0.5px}}
.box{{margin-top:50px;border-top:1px solid #2A3550;padding-top:30px}}
.box h4{{font:700 24px Inter;letter-spacing:4px;color:#8C98AE;margin-bottom:14px}}
.box p{{font:400 36px/1.4 Inter;color:#D5DBE6}}
.esp{{flex:1}}
.fonte{{font:500 24px/1.35 Inter;color:#7F8BA3;padding:20px 0;border-top:1px solid #2A3550}}
.fonte b{{color:#B7C1D3;letter-spacing:3px;font-weight:700;margin-right:12px}}
.rod{{display:flex;align-items:center;justify-content:space-between;padding-top:24px;border-top:2px solid #F3F5F9}}
.rod b{{font:700 36px 'Inter Display';display:block}}
.rod small{{font:500 26px Inter;color:#8C98AE}}
.selo{{font:700 22px Inter;letter-spacing:3px;color:#0A0F1C;background:#E0B252;padding:12px 18px}}
</style></head><body><div class="grade"></div><div class="luz"></div>
<div class="wrap" id="w">
 <div class="cab"><div class="marca">BOLETIM<em>.</em>IMOBILIÁRIO</div><div class="dt">{html.escape(data_fmt(n.get("data")))}</div></div>
 <div class="linha"></div>
 <div class="ed"><span>NOTÍCIA {edicao:02d} DE {total:02d}</span><div class="seg">{seg}</div></div>
 <div class="cat">{html.escape(categoria(n))}</div>
 <div class="num" id="n">{e("numero")}</div>
 <div class="leg">{e("numero_legenda")}</div>
 <div class="tit" id="t">{e("titulo")}</div>
 <div class="box"><h4>O QUE ISSO MUDA PARA VOCÊ</h4><p id="x">{e("texto")}</p></div>
 <div class="esp"></div>
 <div class="fonte"><b>FONTE</b>{e("fonte")}</div>
 <div class="rod"><div><b>Jackson Pires</b><small>Corretor de imóveis | CRECI 323400</small></div><div class="selo">SOROCABA E REGIÃO</div></div>
</div>
<script>
const w=document.getElementById('w'),n=document.getElementById('n'),t=document.getElementById('t');
let ns=230; while(n.scrollWidth>900 && ns>120){{ns-=8;n.style.fontSize=ns+'px'}}
let fs=68; while(w.scrollHeight>w.clientHeight+1 && fs>50){{fs-=2;t.style.fontSize=fs+'px'}}
document.body.dataset.estouro=w.scrollHeight-w.clientHeight;
</script></body></html>'''

async def render(n, saida, edicao):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(channel="chrome")
        pg = await b.new_page(viewport={"width": 1080, "height": 1920})
        await pg.set_content(pagina(n, edicao))
        await pg.wait_for_timeout(400)
        est = int(await pg.evaluate("document.body.dataset.estouro"))
        tmp = saida + ".png"
        await pg.screenshot(path=tmp)
        await b.close()
    from PIL import Image
    Image.open(tmp).convert("RGB").save(saida, quality=93)
    os.remove(tmp)
    if est > 1:
        print(f"ATENÇÃO: texto não coube ({est}px). Encurte o título ou o texto."); sys.exit(2)
    print("ok", saida)

if __name__ == "__main__":
    n = json.load(open(sys.argv[1], encoding="utf-8"))
    ed = n.get("edicao")
    if not ed:
        m = re.search(r"\d{4}-\d{2}-\d{2}-(\d{2})", os.path.abspath(sys.argv[1]))
        ed = int(m.group(1)) if m else 1
    asyncio.run(render(n, sys.argv[2], int(ed)))
