"""Reels de LEITURA (retenção): texto grande, uma ideia por tela, palavra-chave em destaque,
barra de progresso no topo e final que volta para o começo (loop). 1080x1920, 30 fps, sem áudio
(a música, se quiser, entra no app na hora de postar).
Uso: python3 agente04/reel_leitura.py roteiro.json saida.mp4
roteiro.json: {"cenas":[{"dur":3,"linhas":["texto", ...],"destaque":["palavra",...],"chips":[...],"tabela":[[r,v],...]}], "cor":"#FFC93C"}
Na linha, use *trecho* para marcar destaque.
"""
import json, sys, os, asyncio, subprocess, tempfile, shutil, html, re, base64
AQUI = os.path.dirname(os.path.abspath(__file__))
F3 = os.path.join(AQUI, "..", "agente03", "fontes")
def fonte(nome, arq, peso):
    b = base64.b64encode(open(os.path.join(F3, arq), "rb").read()).decode()
    return f"@font-face{{font-family:'{nome}';font-weight:{peso};src:url(data:font/woff2;base64,{b}) format('woff2')}}"
FONTES = "".join([fonte("Brico", f"bricolage-grotesque-latin-{p}-normal.woff2", p) for p in (600, 800)] +
                 [fonte("DM", f"dm-sans-latin-{p}-normal.woff2", p) for p in (500, 700)])
FPS = 30
PALETA = ["#FFC93C", "#7CC4FF", "#FF8A65", "#5FD3B0", "#B79CFF"]

def linha_html(l, i):
    partes = re.split(r"(\*[^*]+\*)", l)
    out = []
    for p in partes:
        if not p: continue
        if p.startswith("*"):
            t = p[1:-1]
            pedacos = [t] if len(t) <= 14 else t.split()
            out += [f'<span class="w"><span class="hl nw">{html.escape(x)}</span></span>' for x in pedacos]
        else:
            out += [f'<span class="w">{html.escape(w)}</span>' for w in p.split()]
    h = re.sub(r' (<span class="w">[.,!?:;]</span>)', r'\1', " ".join(out))
    return f'<div class="ln" data-i="{i}">{h}</div>'

def cena_html(c, k):
    corpo = "".join(linha_html(l, i) for i, l in enumerate(c.get("linhas", [])))
    if c.get("chips"):
        corpo += '<div class="chips">' + "".join(f'<div class="chip" data-i="{len(c["linhas"]) + j}">{html.escape(x)}</div>' for j, x in enumerate(c["chips"])) + "</div>"
    if c.get("tabela"):
        base = len(c.get("linhas", []))
        corpo += '<div class="tab">' + "".join(
            f'<div class="row" data-i="{base + j}"><span>{html.escape(a)}</span><b>{html.escape(b)}</b></div>' for j, (a, b) in enumerate(c["tabela"])) + "</div>"
    if c.get("cta"):
        corpo += f'<div class="cta" data-i="99">{html.escape(c["cta"])}</div>'
    fundo = f'<div class="fundo" id="f{k}">{html.escape(c["fundo"])}</div>' if c.get("fundo") else ""
    cor = PALETA[k % len(PALETA)] if not c.get("cor") else c["cor"]
    return f'{fundo}<section class="cena" id="c{k}" style="--cor:{cor}">{corpo}</section>'

def pagina(r):
    cor = r.get("cor", "#FFC93C")
    cenas = "".join(cena_html(c, k) for k, c in enumerate(r["cenas"]))
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>{FONTES}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;background:#12121F;color:#fff;font-family:DM;overflow:hidden;position:relative}}
.bar{{position:absolute;top:150px;left:80px;right:80px;height:10px;background:#ffffff22;border-radius:10px;overflow:hidden}}
.bar i{{display:block;height:100%;width:0;background:{cor};border-radius:10px}}
.tag{{position:absolute;top:200px;left:80px;font:700 30px DM;letter-spacing:4px;color:{cor}}}
.cena{{position:absolute;left:80px;right:80px;top:330px;bottom:420px;display:flex;flex-direction:column;justify-content:center;opacity:0}}
.ln{{font:800 92px/1.08 Brico;letter-spacing:-2px;margin:10px 0}}
.ln.peq{{font-size:60px}}
.w{{display:inline-block;opacity:0}}
.blob{{position:absolute;width:760px;height:760px;border-radius:50%;filter:blur(120px);opacity:.35}}
.hl{{background:linear-gradient(var(--cor),var(--cor)) no-repeat left/calc(var(--p,0)*100%) 100%;color:calc(var(--p));padding:0 14px;border-radius:14px;box-decoration-break:clone;-webkit-box-decoration-break:clone;transition:none}}
.hl.nw{{white-space:nowrap}}
.hl.on{{color:#12121F}}
.fundo{{position:absolute;right:-40px;top:520px;font:800 900px/1 Brico;color:transparent;-webkit-text-stroke:4px #ffffff14;opacity:0}}
.chips{{display:flex;gap:24px;margin-top:40px}}
.chip{{width:170px;height:170px;border-radius:40px;border:5px solid var(--cor);display:flex;align-items:center;justify-content:center;font:800 90px Brico;color:var(--cor);opacity:0;transform:scale(0)}}
.tab{{margin-top:40px;border-top:4px solid #fff}}
.row{{display:flex;justify-content:space-between;align-items:baseline;padding:34px 0;border-bottom:2px solid #ffffff30;opacity:0;transform:translateX(-60px)}}
.row span{{font:500 46px DM;color:#C9C9DA}}.row b{{font:800 70px Brico;color:var(--cor)}}
.cta{{margin-top:60px;align-self:flex-start;font:800 110px Brico;color:#12121F;background:var(--cor);padding:20px 44px;border-radius:30px;opacity:0;transform:scale(.5) rotate(-4deg)}}
.rod{{position:absolute;left:80px;right:80px;bottom:300px;font:500 28px DM;color:#9A9AB5;white-space:nowrap}}
.rod b{{color:#fff;font:700 32px DM}}
</style></head><body>
<div class="blob" id="b1"></div><div class="blob" id="b2"></div><div class="bar"><i id="bar"></i></div><div class="tag" id="tag"></div>
{cenas}
<div class="rod"><b>Jackson Pires</b> · Corretor de imóveis | CRECI 323400 · Sorocaba e região</div>
<script>
const PAL={json.dumps(PALETA)};
const R={json.dumps([{"dur": c["dur"], "tag": c.get("tag", "")} for c in r["cenas"]])};
const TOT=R.reduce((a,c)=>a+c.dur,0);
const ease=x=>1-Math.pow(1-Math.min(Math.max(x,0),1),3);
const back=x=>{{x=Math.min(Math.max(x,0),1);const c1=1.7,c3=c1+1;return 1+c3*Math.pow(x-1,3)+c1*Math.pow(x-1,2)}};
window.quadro=function(t){{
  document.getElementById('bar').style.width=(100*t/TOT)+'%';
  let ini=0;
  R.forEach((c,k)=>{{
    const el=document.getElementById('c'+k), lt=t-ini, fim=c.dur;
    const vis=lt>=0&&lt<fim;
    const entra=ease(lt/0.35), sai=lt>fim-0.3?ease((lt-(fim-0.3))/0.3):0;
    el.style.opacity=vis?Math.min(entra,1-sai):0;
    el.style.transform='translateY('+(120*(1-entra)-160*sai)+'px) scale('+(0.96+0.04*entra)+')';
    if(vis){{const cor=PAL[k%PAL.length];['b1','b2'].forEach((id,j)=>{{const b=document.getElementById(id);b.style.background=cor;
      b.style.left=(j?500:-300)+Math.sin(t*0.6+j*2)*160+'px';b.style.top=(j?1200:200)+Math.cos(t*0.5+j)*180+'px';}});}}
    const f=document.getElementById('f'+k); if(f){{f.style.opacity=vis?Math.min(lt*3,1):0;f.style.transform='translateY('+(-30*lt)+'px)';}}
    if(vis) document.getElementById('tag').textContent=c.tag;
    let acc=0.3;
    el.querySelectorAll('[data-i]').forEach(e=>{{
      let d=acc;
      if(e.classList.contains('chip')||e.classList.contains('cta')){{acc+=e.classList.contains('cta')?0.4:0.16;const p=(lt-d)/0.45,b=back(p);
        e.style.opacity=Math.min(Math.max(p*2,0),1);e.style.transform='scale('+Math.max(b,0)+')'+(e.classList.contains('cta')?' rotate(-3deg)':'');}}
      else if(e.classList.contains('row')){{acc+=0.4;const p=(lt-d)/0.45;e.style.opacity=ease(p);e.style.transform='translateX('+(-60*(1-ease(p)))+'px)';
        const b=e.querySelector('b'); if(!b.dataset.v) b.dataset.v=b.textContent;
        const v=b.dataset.v, m=v.match(/[0-9][0-9.,]*/);
        if(m){{const dec=(m[0].split(',')[1]||'').length, alvo=parseFloat(m[0].replace(/\./g,'').replace(',','.')), x=alvo*ease((lt-d)/0.8);
          b.textContent=v.replace(m[0], x.toLocaleString('pt-BR',{{minimumFractionDigits:dec,maximumFractionDigits:dec}}));}}}}
      else {{const ws=e.querySelectorAll('.w'); acc+=ws.length*0.08+0.3;
        ws.forEach((w,j)=>{{const q=(lt-d-j*0.08)/0.3;w.style.opacity=ease(q);w.style.transform='translateY('+(36*(1-ease(q)))+'px) rotate('+(4*(1-ease(q)))+'deg)';}});
        const q=ease((lt-d-ws.length*0.08)/0.35); e.querySelectorAll('.hl').forEach(h=>{{h.style.setProperty('--p',q);h.classList.toggle('on',q>0.5);}});}}
    }});
    ini+=c.dur;
  }});
}};
window.TOTAL=TOT;
</script></body></html>'''

async def gerar(r, pasta):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(channel="chrome")
        pg = await b.new_page(viewport={"width": 1080, "height": 1920})
        await pg.set_content(pagina(r)); await pg.wait_for_timeout(500)
        tot = await pg.evaluate("TOTAL")
        for i in range(int(tot * FPS)):
            await pg.evaluate(f"quadro({i / FPS})")
            await pg.screenshot(path=os.path.join(pasta, f"q{i:04d}.jpg"), type="jpeg", quality=90)
        await b.close()

def main():
    r = json.load(open(sys.argv[1], encoding="utf-8")); saida = sys.argv[2]
    tmp = tempfile.mkdtemp()
    asyncio.run(gerar(r, tmp))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(tmp, "q%04d.jpg"),
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-an",
                    "-movflags", "+faststart", saida], check=True)
    shutil.copy(os.path.join(tmp, sorted(os.listdir(tmp))[int(FPS * r["cenas"][0]["dur"]) - 5]), saida.replace(".mp4", "-capa.jpg"))
    shutil.rmtree(tmp); print("ok", saida)

if __name__ == "__main__":
    main()
