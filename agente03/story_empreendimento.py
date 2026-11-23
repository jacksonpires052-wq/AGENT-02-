# Story de empreendimento (lançamento) com foto real, linha neon sobre o preço e renda compatível.
# Uso: python3 agente03/story_empreendimento.py dados.json saida.jpg [foto.jpg]
# dados.json: {"nome","bairro","m2","preco","dorms","renda"(opcional),"numero","total","data_ref"}
import base64, json, sys, os
from playwright.sync_api import sync_playwright

AQUI = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(AQUI, "fontes") + "/"

def _font(fam, w, f):
    b = base64.b64encode(open(F + f, "rb").read()).decode()
    return f"@font-face{{font-family:'{fam}';font-weight:{w};src:url(data:font/woff2;base64,{b}) format('woff2')}}"

FONTS = "".join([_font("Bri", 400, "bricolage-grotesque-latin-400-normal.woff2"),
                 _font("Bri", 800, "bricolage-grotesque-latin-800-normal.woff2"),
                 _font("DM", 500, "dm-sans-latin-500-normal.woff2"),
                 _font("DM", 700, "dm-sans-latin-700-normal.woff2")])
NEON = "#39FFB0"

def html(d, foto=None):
    if foto:
        b = base64.b64encode(open(foto, "rb").read()).decode()
        fundo = f"background:#0B1020 url(data:image/jpeg;base64,{b}) center/cover no-repeat;"
    else:
        fundo = "background:radial-gradient(120% 70% at 80% 10%,#1E3A5F 0%,#0B1020 60%);"
    nome = d["nome"]
    tam = 104 if len(nome) <= 16 else (88 if len(nome) <= 22 else 76)
    renda = ""
    if d.get("parcela"):
        renda += f'<div class="renda"><span>PARCELAS A PARTIR DE</span><b>{d["parcela"]}</b></div>'
    if d.get("renda"):
        renda += f'<div class="renda"><span>RENDA COMPATÍVEL A PARTIR DE</span><b>{d["renda"]}</b></div>'
    nota = f'Valores de referência de {d.get("data_ref","23/11/2026")}, sujeitos a alteração pela construtora.'
    if d.get("renda"):
        nota = f'Preço de {d.get("data_ref","23/11/2026")}. Renda estimada com 80% financiado em 35 anos, juros de 7% ao ano e parcela de até 30% da renda. Sujeito a análise de crédito.'
    local = ""
    if d.get("rua"):
        perto = "".join(f'<span class="pt">Perto de {p}</span>' for p in d.get("perto", [])[:3])
        local = f'<div class="local"><div class="lt">LOCALIZAÇÃO</div><div class="rua">{d["rua"]}, {d["bairro"]}, Sorocaba</div>' + (f'<div class="pts">{perto}</div>' if perto else "") + '</div>'
    num = f'<div class="num">{d["numero"]:02d}/{d["total"]}</div>' if d.get("numero") else ""
    return f"""<html><head><style>{FONTS}
*{{margin:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;{fundo}font-family:DM;color:#fff;position:relative;overflow:hidden}}
.sh{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(6,10,22,.55) 0%,rgba(6,10,22,0) 22%,rgba(6,10,22,0) 38%,rgba(6,10,22,.78) 55%,rgba(6,10,22,.96) 70%,#060A16 100%)}}
.top{{position:absolute;top:230px;left:72px;right:72px;display:flex;justify-content:space-between;align-items:center}}
.pill{{background:rgba(255,255,255,.14);backdrop-filter:blur(10px);border:2px solid rgba(255,255,255,.35);font-weight:700;font-size:28px;letter-spacing:3px;padding:14px 28px;border-radius:40px}}
.num{{font-family:Bri;font-weight:800;font-size:30px;opacity:.85}}
.box{{position:absolute;left:72px;right:72px;bottom:450px}}
h1{{font-family:Bri;font-weight:800;font-size:{tam}px;line-height:.98;letter-spacing:-2px}}
.bairro{{margin-top:22px;font-size:38px;font-weight:500;opacity:.9}}
.bairro i{{display:inline-block;width:16px;height:16px;border-radius:50%;background:{NEON};box-shadow:0 0 14px {NEON};margin-right:14px;vertical-align:middle}}
.chips{{display:flex;gap:16px;margin-top:26px}}
.local{{margin-top:28px;border-left:5px solid {NEON};padding:6px 0 6px 24px}}
.lt{{font-size:22px;font-weight:700;letter-spacing:3px;color:{NEON}}}
.rua{{font-size:32px;font-weight:500;margin-top:6px;line-height:1.25}}
.pts{{display:flex;flex-wrap:wrap;gap:10px;margin-top:14px}}
.pt{{background:rgba(255,255,255,.14);border-radius:20px;padding:8px 18px;font-size:24px;font-weight:700}}
.chip{{border:2px solid rgba(255,255,255,.45);border-radius:30px;padding:12px 26px;font-weight:700;font-size:30px}}
.neon{{margin-top:44px;height:8px;border-radius:8px;background:{NEON};box-shadow:0 0 12px {NEON},0 0 34px {NEON},0 0 70px rgba(57,255,176,.6)}}
.preco{{margin-top:26px}}
.preco span{{font-size:28px;font-weight:700;letter-spacing:3px;color:{NEON}}}
.preco b{{display:block;font-family:Bri;font-weight:800;font-size:132px;line-height:1.02;letter-spacing:-3px}}
.renda{{margin-top:22px;display:flex;justify-content:space-between;align-items:center;background:rgba(57,255,176,.12);border:2px solid rgba(57,255,176,.55);border-radius:24px;padding:20px 28px}}
.renda span{{font-size:24px;font-weight:700;letter-spacing:2px;color:{NEON};max-width:560px}}
.renda b{{font-family:Bri;font-weight:800;font-size:52px}}
.cta{{position:absolute;top:1500px;left:72px;right:72px;background:{NEON};color:#06121A;border-radius:34px;padding:26px;font-size:36px;font-weight:700;text-align:center}}
.nota{{position:absolute;top:1612px;left:72px;right:72px;font-size:21px;opacity:.6;text-align:center}}
.foot{{position:absolute;top:1684px;left:72px;right:72px;display:flex;justify-content:space-between;align-items:center;border-top:2px solid rgba(255,255,255,.2);padding-top:22px}}
.foot b{{font-family:Bri;font-weight:800;font-size:32px;display:block}} .foot span{{font-size:22px;opacity:.8}}
.sel{{border:2px solid {NEON};color:{NEON};border-radius:30px;padding:10px 20px;font-weight:700;font-size:20px;letter-spacing:2px}}
</style></head><body><div class="sh"></div>
<div class="top"><div class="pill">LANÇAMENTO EM SOROCABA</div>{num}</div>
<div class="box"><h1>{nome}</h1><div class="bairro"><i></i>{d["bairro"]}{(" · " + d["zona"]) if d.get("zona") else ""}</div>
{local}<div class="chips"><div class="chip">{d.get("dorms","2 dormitórios")}</div><div class="chip">{d["m2"]}</div></div>
<div class="neon"></div><div class="preco"><span>A PARTIR DE</span><b>{d["preco"]}</b></div>{renda}</div>
<div class="cta">Simule comigo: me chama no direct</div>
<div class="nota">{nota}</div>
<div class="foot"><div><b>Jackson Pires</b><span>Corretor de imóveis | CRECI 323400</span></div><div class="sel">SOROCABA E REGIÃO</div></div>
</body></html>"""

def gerar(d, saida, foto=None, page=None):
    def run(pg):
        pg.set_content(html(d, foto)); pg.wait_for_timeout(200)
        pg.screenshot(path=saida, type="jpeg", quality=92)
    if page: return run(page)
    with sync_playwright() as p:
        br = p.chromium.launch(); pg = br.new_page(viewport={"width": 1080, "height": 1920}); run(pg); br.close()

if __name__ == "__main__":
    d = json.load(open(sys.argv[1]))
    gerar(d, sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
