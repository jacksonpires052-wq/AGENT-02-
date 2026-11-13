"""Story de notícia (1080x1920 JPG), sem foto: arte do tema + nome e CRECI do Jackson.
Uso: python3 agente03/story.py noticia.json saida.jpg

noticia.json:
{
  "tema": "desconto",            # desconto, juros, poupanca, lancamentos, distrato, alerta,
                                 # casa_popular, praia, mapa, grafico_sobe, grafico_desce
  "numero": "13%",               # o dado em destaque
  "numero_legenda": "é o desconto médio na compra",
  "titulo": "Comprador está conseguindo mais desconto",
  "texto": "Frase curta explicando o que muda para quem quer comprar.",
  "fonte": "FipeZap Raio-X, 3º tri de 2026 (via Portas)",
  "data": "13/11"
}
"""
import json, sys, html, asyncio, os

CORES = {  # fundo do quadro da arte, cor de destaque
    "desconto": ("#0F7B5F", "#2EE6A6"),
    "juros": ("#8A1C2B", "#FF5A6E"),
    "poupanca": ("#8A5A00", "#FFC233"),
    "lancamentos": ("#1D3F9E", "#5B8CFF"),
    "distrato": ("#7A2E00", "#FF8A3D"),
    "alerta": ("#6B1F7A", "#E07BFF"),
    "casa_popular": ("#0B6E78", "#3FE0F0"),
    "praia": ("#0A5C8A", "#FFD45C"),
    "mapa": ("#24622A", "#7BE36A"),
    "grafico_sobe": ("#1D5E3A", "#4CE38A"),
    "grafico_desce": ("#7E1D1D", "#FF6B6B"),
}

CASA = '''<g transform="translate({x},{y}) scale({s})">
  <rect x="-110" y="-10" width="220" height="170" rx="10" fill="#F4F1EA"/>
  <path d="M-140 0 L0 -120 L140 0 Z" fill="{a}"/>
  <rect x="-30" y="70" width="60" height="90" rx="6" fill="{b}"/>
  <rect x="-90" y="30" width="45" height="45" rx="5" fill="#BFD4FF"/>
  <rect x="45" y="30" width="45" height="45" rx="5" fill="#BFD4FF"/>
</g>'''

def casa(x, y, s, a, b):
    return CASA.format(x=x, y=y, s=s, a=a, b=b)

def arte(tema, fundo, dest):
    c = []
    if tema == "desconto":
        c.append(casa(380, 380, 1.25, dest, fundo))
        c.append(f'''<g transform="translate(640,230) rotate(18)">
          <path d="M-90 -60 H60 L110 0 L60 60 H-90 Z" fill="#FFFFFF"/>
          <circle cx="62" cy="0" r="14" fill="{fundo}"/>
          <text x="-20" y="22" font-size="70" font-weight="800" text-anchor="middle" fill="{fundo}" font-family="Poppins">%</text></g>''')
    elif tema == "juros":
        c.append(f'''<g transform="translate(330,330)">
          <path d="M-170 -40 L0 -140 L170 -40 Z" fill="#F4F1EA"/>
          <rect x="-150" y="-30" width="300" height="24" fill="#F4F1EA"/>
          {''.join(f'<rect x="{-130 + i*75}" y="0" width="34" height="150" fill="#F4F1EA"/>' for i in range(4))}
          <rect x="-170" y="160" width="340" height="30" rx="6" fill="#F4F1EA"/></g>''')
        c.append(f'''<g transform="translate(640,300)"><path d="M-120 140 L-40 60 L20 100 L120 -40" stroke="{dest}" stroke-width="30" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M70 -60 L140 -60 L140 10 Z" fill="{dest}"/></g>''')
    elif tema == "poupanca":
        c.append(f'''<g transform="translate(400,350)">
          <ellipse cx="0" cy="0" rx="190" ry="150" fill="#FFB3C7"/>
          <ellipse cx="190" cy="-10" rx="45" ry="55" fill="#FF9BB4"/>
          <circle cx="198" cy="-20" r="8" fill="#7A2E44"/><circle cx="198" cy="5" r="8" fill="#7A2E44"/>
          <circle cx="90" cy="-60" r="14" fill="#3B2030"/>
          <path d="M-60 -150 L-20 -110 L-90 -100 Z" fill="#FF9BB4"/>
          <rect x="-70" y="-160" width="110" height="20" rx="10" fill="#7A2E44"/>
          <rect x="-150" y="120" width="40" height="70" rx="12" fill="#FF9BB4"/><rect x="80" y="120" width="40" height="70" rx="12" fill="#FF9BB4"/></g>''')
        for i, (cx, cy) in enumerate([(660, 470), (720, 520), (620, 540)]):
            c.append(f'<g><circle cx="{cx}" cy="{cy}" r="46" fill="{dest}"/><circle cx="{cx}" cy="{cy}" r="32" fill="none" stroke="#B88400" stroke-width="6"/></g>')
        c.append(f'<path d="M640 200 L640 330 M590 280 L640 330 L690 280" stroke="#FFFFFF" stroke-width="22" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    elif tema == "lancamentos":
        for i, (x, h) in enumerate([(170, 330), (310, 430), (450, 280), (590, 380)]):
            c.append(f'<rect x="{x}" y="{560-h}" width="120" height="{h}" rx="8" fill="{"#F4F1EA" if i % 2 == 0 else dest}"/>')
            for r in range(int(h / 60) - 1):
                c.append(f'<rect x="{x+22}" y="{560-h+30+r*60}" width="28" height="28" rx="4" fill="{fundo}" opacity=".55"/><rect x="{x+70}" y="{560-h+30+r*60}" width="28" height="28" rx="4" fill="{fundo}" opacity=".55"/>')
        c.append(f'<g transform="translate(740,160)"><rect x="-6" y="0" width="12" height="400" fill="#FFFFFF"/><rect x="-6" y="0" width="160" height="14" fill="#FFFFFF"/><rect x="120" y="14" width="6" height="90" fill="#FFFFFF"/><rect x="100" y="104" width="46" height="36" rx="4" fill="{dest}"/></g>')
    elif tema == "distrato":
        c.append(f'''<g transform="translate(420,350) rotate(-6)">
          <path d="M-160 -200 H40 L20 -100 L50 0 L10 100 L40 200 H-160 Z" fill="#F4F1EA"/>
          {''.join(f'<rect x="-130" y="{-160 + i*55}" width="140" height="16" rx="8" fill="#C9C2B4"/>' for i in range(6))}</g>''')
        c.append(f'''<g transform="translate(560,370) rotate(10)">
          <path d="M20 -200 H180 V200 H30 L60 100 L20 0 L50 -100 Z" fill="#E9E3D6"/>
          {''.join(f'<rect x="70" y="{-160 + i*55}" width="90" height="16" rx="8" fill="#C9C2B4"/>' for i in range(6))}</g>''')
        c.append(f'<circle cx="760" cy="170" r="70" fill="{dest}"/><path d="M730 140 L790 200 M790 140 L730 200" stroke="#FFFFFF" stroke-width="18" stroke-linecap="round"/>')
    elif tema == "alerta":
        c.append(casa(330, 380, 1.15, "#F4F1EA", fundo))
        c.append(f'''<g transform="translate(640,330)"><path d="M0 -190 L170 120 H-170 Z" fill="{dest}" stroke="#FFFFFF" stroke-width="16" stroke-linejoin="round"/>
          <rect x="-16" y="-80" width="32" height="120" rx="16" fill="#FFFFFF"/><circle cx="0" cy="85" r="20" fill="#FFFFFF"/></g>''')
    elif tema == "casa_popular":
        for i, x in enumerate([200, 450, 700]):
            c.append(casa(x, 400 + (30 if i == 1 else 0), 0.95, dest if i == 1 else "#F4F1EA", fundo))
        c.append(f'<g transform="translate(450,150)"><path d="M0 60 C-60 0 -90 -40 -50 -70 C-20 -90 0 -60 0 -45 C0 -60 20 -90 50 -70 C90 -40 60 0 0 60 Z" fill="#FF6B8A"/></g>')
    elif tema == "praia":
        c.append(f'<circle cx="700" cy="170" r="90" fill="{dest}"/>')
        c.append('<path d="M0 470 Q200 430 450 470 T900 470 V620 H0 Z" fill="#F2D59B"/>')
        c.append('<path d="M0 420 Q150 390 300 420 T600 420 T900 420 V480 H0 Z" fill="#3FA9E0" opacity=".85"/>')
        c.append(f'''<g transform="translate(300,300)"><rect x="-130" y="-110" width="260" height="220" rx="12" fill="#F4F1EA"/>
          {''.join(f'<rect x="{-100 + (i%3)*75}" y="{-85 + (i//3)*70}" width="50" height="45" rx="5" fill="#BFD4FF"/>' for i in range(6))}</g>''')
        c.append(f'<g transform="translate(600,380)"><rect x="-6" y="-150" width="12" height="160" fill="#FFFFFF"/><path d="M-120 -150 Q0 -260 120 -150 Z" fill="{dest}"/></g>')
    elif tema == "mapa":
        c.append('<path d="M120 200 L330 140 L540 200 L760 140 V520 L540 580 L330 520 L120 580 Z" fill="#F4F1EA"/>')
        c.append('<path d="M330 140 V520 M540 200 V580" stroke="#C9C2B4" stroke-width="8"/>')
        c.append(f'<path d="M180 470 L330 400 L460 430 L640 260" stroke="{fundo}" stroke-width="14" fill="none" stroke-dasharray="26 18" stroke-linecap="round"/>')
        c.append(f'''<g transform="translate(640,250)"><path d="M0 0 C-80 -90 -80 -190 0 -190 C80 -190 80 -90 0 0 Z" fill="{dest}"/><circle cx="0" cy="-120" r="30" fill="#FFFFFF"/></g>''')
    else:  # grafico_sobe / grafico_desce
        sobe = tema != "grafico_desce"
        for i, h in enumerate([150, 220, 280, 360] if sobe else [360, 280, 220, 150]):
            c.append(f'<rect x="{190 + i*140}" y="{560-h}" width="100" height="{h}" rx="10" fill="{"#F4F1EA" if i < 3 else dest}"/>')
        d = "M180 400 L360 330 L500 260 L700 130" if sobe else "M180 150 L360 230 L500 300 L700 420"
        c.append(f'<path d="{d}" stroke="#FFFFFF" stroke-width="20" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    return "\n".join(c)


def pagina(n):
    fundo, dest = CORES.get(n.get("tema"), CORES["grafico_sobe"])
    e = lambda k: html.escape(n.get(k, ""))
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;background:#0D1626;font-family:Inter,sans-serif;color:#fff;overflow:hidden;position:relative}}
.grao{{position:absolute;inset:0;background:radial-gradient(circle at 20% 10%,{fundo}55,transparent 55%),radial-gradient(circle at 90% 90%,{fundo}40,transparent 50%)}}
.topo{{position:absolute;top:250px;left:90px;right:90px;display:flex;align-items:center;gap:22px}}
.selo{{background:#E3262F;color:#fff;font:800 34px Poppins;letter-spacing:2px;padding:14px 26px;border-radius:12px;display:flex;align-items:center;gap:14px}}
.selo i{{width:16px;height:16px;border-radius:50%;background:#fff;display:inline-block}}
.data{{font:600 34px Inter;color:#AFC0DA}}
.quadro{{position:absolute;top:340px;left:90px;width:900px;height:480px;border-radius:40px;background:linear-gradient(160deg,{fundo},{fundo}CC);overflow:hidden}}
.quadro svg{{position:absolute;inset:0}}
.col{{position:absolute;top:850px;left:90px;right:90px;display:flex;flex-direction:column}}
.num b{{display:block;font:800 140px/1 Poppins;color:{dest};letter-spacing:-4px;white-space:nowrap}}
.num span{{display:block;margin-top:10px;font:600 36px/1.2 Inter;color:#DCE5F2}}
.titulo{{margin-top:30px;font:800 62px/1.12 Poppins;letter-spacing:-1px}}
.texto{{margin-top:22px;font:500 36px/1.35 Inter;color:#C9D4E5}}
.fonte{{margin-top:20px;font:500 26px/1.3 Inter;color:#8094B2}}
.rodape{{position:absolute;bottom:250px;left:90px;right:90px;height:118px;background:#fff;border-radius:24px;display:flex;align-items:center;padding:0 34px;gap:22px;color:#0D1626}}
.rodape .ic{{width:70px;height:70px;border-radius:18px;background:{fundo};display:flex;align-items:center;justify-content:center}}
.rodape b{{font:800 38px Poppins;display:block}}
.rodape small{{font:600 27px Inter;color:#4A5A75}}
</style></head><body><div class="grao"></div>
<div class="topo"><div class="selo"><i></i>PLANTÃO IMOBILIÁRIO</div><div class="data">{e("data")}</div></div>
<div class="quadro"><svg viewBox="0 0 900 620" width="900" height="480" preserveAspectRatio="xMidYMid meet">
<circle cx="80" cy="560" r="160" fill="#ffffff" opacity=".06"/><circle cx="860" cy="60" r="200" fill="#ffffff" opacity=".06"/>
{arte(n.get("tema"), fundo, dest)}</svg></div>
<div class="col" id="c"><div class="num"><b id="n">{e("numero")}</b><span>{e("numero_legenda")}</span></div>
<div class="titulo" id="t">{e("titulo")}</div>
<div class="texto" id="x">{e("texto")}</div>
<div class="fonte" id="f">Fonte: {e("fonte")}</div></div>
<div class="rodape"><div class="ic"><svg width="44" height="44" viewBox="0 0 44 44"><path d="M4 20 L22 5 L40 20 V40 H4 Z" fill="#fff"/><rect x="17" y="27" width="10" height="13" fill="{fundo}"/></svg></div>
<div><b>Jackson Pires</b><small>Corretor de imóveis | CRECI 323400</small></div></div>
<script>
const c=document.getElementById('c'),t=document.getElementById('t'),n=document.getElementById('n');
let ns=140; while(n.scrollWidth>900 && ns>90){{ns-=6;n.style.fontSize=ns+'px'}}
let fs=62; while((850+c.offsetHeight>1530 || t.offsetHeight>3*fs*1.12+4) && fs>48){{fs-=2;t.style.fontSize=fs+'px'}}
document.body.dataset.fim=850+c.offsetHeight;
</script></body></html>'''


async def render(n, saida):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(channel="chrome")
        pg = await b.new_page(viewport={"width": 1080, "height": 1920})
        await pg.set_content(pagina(n))
        await pg.wait_for_timeout(300)
        fim = int(await pg.evaluate("document.body.dataset.fim"))
        tmp = saida + ".png"
        await pg.screenshot(path=tmp)
        await b.close()
    from PIL import Image
    Image.open(tmp).convert("RGB").save(saida, quality=92)
    os.remove(tmp)
    if fim > 1532:
        print(f"ATENÇÃO: o texto encosta no rodapé ({fim}px). Encurte o título ou o texto.")
        sys.exit(2)
    print("ok", saida)


if __name__ == "__main__":
    asyncio.run(render(json.load(open(sys.argv[1], encoding="utf-8")), sys.argv[2]))
