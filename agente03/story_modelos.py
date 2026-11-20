"""Modelos extras de story (mesma família do Boletim). 1080x1920 JPG.
Uso: python3 agente03/story_modelos.py card.json saida.jpg
Campo "modelo": pergunta | resposta | mito | conta | direct
Campos por modelo:
  pergunta: pergunta, opcoes [A,B,C], chamada, fonte_dica (opcional)
  resposta: pergunta, opcoes, certa (índice 0..2), explicacao, fonte
  mito:     afirmacao, chamada  (story 1)  |  com "veredito" (MITO/VERDADE) + explicacao + fonte (story 2)
  conta:    titulo, linhas [[rótulo, valor], ...], resultado [rótulo, valor], nota, fonte
  direct:   gancho, palavra, texto
Comum: data (DD/MM/AAAA)
"""
import json, sys, html, asyncio, os, re

MESES = "JAN FEV MAR ABR MAI JUN JUL AGO SET OUT NOV DEZ".split()
def data_fmt(d):
    p = re.findall(r"\d+", d or "")
    return f"{int(p[0]):02d} {MESES[int(p[1])-1]} {p[2] if len(p) > 2 else '2026'}" if len(p) >= 2 else ""
E = lambda s: html.escape(str(s))

CSS = """*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1920px;background:#0A0F1C;color:#F3F5F9;font-family:Inter;position:relative;overflow:hidden}
.grade{position:absolute;inset:0;background-image:linear-gradient(#ffffff08 1px,transparent 1px),linear-gradient(90deg,#ffffff08 1px,transparent 1px);background-size:90px 90px}
.luz{position:absolute;inset:0;background:radial-gradient(900px 700px at 100% 0%,#1B3A7A55,transparent 70%)}
.wrap{position:absolute;top:230px;left:90px;right:90px;bottom:240px;display:flex;flex-direction:column}
.cab{display:flex;justify-content:space-between;align-items:flex-end}
.marca{font:800 40px 'Inter Display';letter-spacing:6px}.marca em{font-style:normal;color:#E0B252}
.dt{font:600 28px Inter;color:#8C98AE;letter-spacing:3px}
.linha{height:2px;background:#F3F5F9;margin-top:22px}
.tag{margin-top:90px;align-self:flex-start;font:800 30px Inter;letter-spacing:6px;color:#0A0F1C;background:#E0B252;padding:14px 22px}
.big{margin-top:44px;font:700 76px/1.12 Lora}
.op{margin-top:22px;display:flex;align-items:center;gap:28px;border:2px solid #2A3550;padding:26px 30px;font:600 46px Inter}
.op b{width:74px;height:74px;flex:none;display:flex;align-items:center;justify-content:center;border:2px solid #E0B252;color:#E0B252;font:800 40px Inter}
.op.ok{border-color:#E0B252;background:#E0B25218}.op.ok b{background:#E0B252;color:#0A0F1C}
.op.no{opacity:.35}
.cta{margin-top:46px;font:500 38px/1.35 Inter;color:#B7C1D3;padding-left:24px;border-left:4px solid #E0B252}
.cta strong{color:#F3F5F9}
.txt{margin-top:40px;font:400 38px/1.42 Inter;color:#D5DBE6}
.ver{margin-top:60px;font:800 200px/1 'Inter Display';letter-spacing:-6px;color:#E0B252}
.risc{margin-top:40px;font:500 40px/1.3 Lora;color:#7F8BA3;text-decoration:line-through;text-decoration-color:#E0B252}
.tab{margin-top:56px;border-top:2px solid #F3F5F9}
.tab div{display:flex;justify-content:space-between;padding:30px 0;border-bottom:1px solid #2A3550;font:500 40px Inter;color:#B7C1D3}
.tab div span:last-child{font:700 44px 'Inter Display';color:#F3F5F9}
.tab div.res{border-bottom:none;border-top:2px solid #E0B252;margin-top:-1px;color:#E0B252}
.tab div.res span:last-child{font:800 64px 'Inter Display';color:#E0B252}
.pal{margin-top:50px;align-self:flex-start;font:800 120px/1 'Inter Display';letter-spacing:4px;color:#0A0F1C;background:#E0B252;padding:24px 40px}
.seta{margin-top:40px;font:600 34px Inter;color:#8C98AE;letter-spacing:3px}
.esp{flex:1}
.fonte{font:500 24px/1.35 Inter;color:#7F8BA3;padding:20px 0;border-top:1px solid #2A3550}
.fonte b{color:#B7C1D3;letter-spacing:3px;font-weight:700;margin-right:12px}
.rod{display:flex;align-items:center;justify-content:space-between;padding-top:24px;border-top:2px solid #F3F5F9}
.rod b{font:700 36px 'Inter Display';display:block}.rod small{font:500 26px Inter;color:#8C98AE}
.selo{font:700 22px Inter;letter-spacing:3px;color:#0A0F1C;background:#E0B252;padding:12px 18px}"""

def corpo(c):
    m = c["modelo"]
    if m in ("pergunta", "resposta"):
        certa = c.get("certa", -1) if m == "resposta" else -1
        ops = "".join(
            f'<div class="op {"ok" if i == certa else ("no" if certa >= 0 else "")}"><b>{"ABC"[i]}</b>{E(o)}</div>'
            for i, o in enumerate(c["opcoes"]))
        tag = "RESPOSTA" if m == "resposta" else "VOCÊ SABE?"
        fim = (f'<div class="txt">{E(c["explicacao"])}</div>' if m == "resposta"
               else f'<div class="cta">{c["chamada"]}</div>')
        return f'<div class="tag">{tag}</div><div class="big">{E(c["pergunta"])}</div>{ops}{fim}', c.get("fonte", "")
    if m == "mito":
        if c.get("veredito"):
            return (f'<div class="tag">MITO OU VERDADE?</div><div class="risc">{E(c["afirmacao"])}</div>'
                    f'<div class="ver">{E(c["veredito"])}</div><div class="txt">{E(c["explicacao"])}</div>'), c.get("fonte", "")
        return (f'<div class="tag">MITO OU VERDADE?</div><div class="big" style="font-size:84px">“{E(c["afirmacao"])}”</div>'
                f'<div class="cta">{c["chamada"]}</div>'), ""
    if m == "conta":
        ls = "".join(f'<div><span>{E(a)}</span><span>{E(b)}</span></div>' for a, b in c["linhas"])
        r = c["resultado"]
        return (f'<div class="tag">CONTA RÁPIDA</div><div class="big">{E(c["titulo"])}</div>'
                f'<div class="tab">{ls}<div class="res"><span>{E(r[0])}</span><span>{E(r[1])}</span></div></div>'
                f'<div class="txt" style="font-size:32px;color:#8C98AE">{E(c.get("nota",""))}</div>'), c.get("fonte", "")
    if m == "direct":
        return (f'<div class="tag">FALA COMIGO</div><div class="big" style="font-size:84px">{E(c["gancho"])}</div>'
                f'<div class="txt">{E(c["texto"])}</div><div class="pal">{E(c["palavra"])}</div>'
                f'<div class="seta">RESPONDE AQUI NO DIRECT ↓</div>'), ""
    raise SystemExit("modelo desconhecido: " + m)

def pagina(c):
    meio, fonte = corpo(c)
    f = f'<div class="fonte"><b>FONTE</b>{E(fonte)}</div>' if fonte else ""
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="grade"></div><div class="luz"></div><div class="wrap" id="w">
<div class="cab"><div class="marca">BOLETIM<em>.</em>IMOBILIÁRIO</div><div class="dt">{E(data_fmt(c.get("data")))}</div></div>
<div class="linha"></div>{meio}<div class="esp"></div>{f}
<div class="rod"><div><b>Jackson Pires</b><small>Corretor de imóveis | CRECI 323400</small></div><div class="selo">SOROCABA E REGIÃO</div></div>
</div><script>const w=document.getElementById('w');document.body.dataset.estouro=w.scrollHeight-w.clientHeight;</script></body></html>'''

async def render(c, saida):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(channel="chrome")
        pg = await b.new_page(viewport={"width": 1080, "height": 1920})
        await pg.set_content(pagina(c)); await pg.wait_for_timeout(400)
        est = int(await pg.evaluate("document.body.dataset.estouro"))
        await pg.screenshot(path=saida + ".png"); await b.close()
    from PIL import Image
    Image.open(saida + ".png").convert("RGB").save(saida, quality=93); os.remove(saida + ".png")
    if est > 1: print(f"ATENÇÃO: não coube ({est}px)"); sys.exit(2)
    print("ok", saida)

if __name__ == "__main__":
    asyncio.run(render(json.load(open(sys.argv[1], encoding="utf-8")), sys.argv[2]))
