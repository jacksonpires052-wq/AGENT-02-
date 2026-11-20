"""Versão ANIMADA do story (Boletim ou Leve). Gera story.mp4 (1080x1920, 30 fps, 8 s, com trilha) e story.jpg (quadro final).
Uso: python3 agente03/story_motion.py noticia.json pasta_saida [leve|boletim]
O stories.js publica o story.mp4 quando existe e cai para o story.jpg se o vídeo falhar.
"""
import json, sys, os, re, asyncio, subprocess, shutil, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import story, story_leve

AQUI = os.path.dirname(os.path.abspath(__file__))
TRILHA = os.path.join(AQUI, "trilha-noticia.mp3")
FPS, DUR = 30, 8.0

ANIM_LEVE = """
@keyframes entra{from{transform:translateY(160px) rotate(-6deg);opacity:0}to{transform:translateY(0) rotate(-1.2deg);opacity:1}}
@keyframes pop{0%{transform:scale(0) rotate(-14deg)}60%{transform:scale(1.15) rotate(2deg)}80%{transform:scale(.95) rotate(-4deg)}100%{transform:scale(1) rotate(-3deg)}}
@keyframes sobe{from{transform:translateY(60px);opacity:0}to{transform:translateY(0);opacity:1}}
@keyframes sobe2{from{transform:translateY(80px) rotate(4deg);opacity:0}to{transform:translateY(0) rotate(1deg);opacity:1}}
@keyframes gira{from{transform:rotate(0)}to{transform:rotate(360deg)}}
@keyframes pulso{0%,100%{transform:scale(1)}50%{transform:scale(1.08)}}
@keyframes bolha{0%,100%{transform:translate(0,0)}50%{transform:translate(-40px,40px)}}
.card{animation:entra .7s cubic-bezier(.2,1.4,.4,1) .2s both}
.num{animation:pop .8s cubic-bezier(.2,1.5,.4,1) .7s both}
.leg{animation:sobe .5s ease-out 1.3s both}
.tit{animation:sobe .5s ease-out 1.6s both}
.muda{animation:sobe2 .6s cubic-bezier(.2,1.3,.4,1) 2.2s both}
.fonte{animation:sobe .4s ease-out 2.8s both}
.rod{animation:sobe .5s ease-out 3s both}
.est{animation:gira 8s linear infinite}
.b1{animation:bolha 8s ease-in-out infinite}
.pts i.on:last-of-type,.pts i.on{animation:pulso 1.2s ease-in-out infinite}
"""
ANIM_BOLETIM = """
@keyframes sobe{from{transform:translateY(50px);opacity:0}to{transform:translateY(0);opacity:1}}
@keyframes risco{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes zoom{from{transform:scale(.6);opacity:0;filter:blur(12px)}to{transform:scale(1);opacity:1;filter:blur(0)}}
@keyframes luz{0%,100%{opacity:.6}50%{opacity:1}}
.linha{transform-origin:left;animation:risco .8s ease-out .2s both}
.cab,.ed{animation:sobe .5s ease-out .1s both}
.cat{animation:sobe .5s ease-out .6s both}
.num{transform-origin:left;animation:zoom .7s cubic-bezier(.2,1.2,.4,1) .9s both}
.leg{animation:sobe .5s ease-out 1.5s both}
.tit{animation:sobe .5s ease-out 1.8s both}
.box{animation:sobe .6s ease-out 2.3s both}
.fonte,.rod{animation:sobe .5s ease-out 2.9s both}
.luz{animation:luz 4s ease-in-out infinite}
"""

def html_e_css(n, ed, modelo):
    if modelo == "leve":
        return story_leve.pagina(n, ed), ANIM_LEVE
    return story.pagina(n, ed), ANIM_BOLETIM

async def quadros(n, ed, modelo, pasta):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(channel="chrome")
        pg = await b.new_page(viewport={"width": 1080, "height": 1920})
        h, css = html_e_css(n, ed, modelo)
        await pg.set_content(h); await pg.wait_for_timeout(600)
        est = int(await pg.evaluate("document.body.dataset.estouro"))
        # animação só entra depois de medir o texto (o layout final é o mesmo do JPG)
        await pg.add_style_tag(content=css); await pg.wait_for_timeout(100)
        total = int(FPS * DUR)
        for i in range(total):
            t = i * 1000 / FPS
            await pg.evaluate(f"document.getAnimations().forEach(a=>{{a.pause();a.currentTime={t}}})")
            await pg.screenshot(path=os.path.join(pasta, f"q{i:04d}.jpg"), type="jpeg", quality=90)
        await b.close()
    return est

def main():
    n = json.load(open(sys.argv[1], encoding="utf-8"))
    saida = sys.argv[2]; modelo = sys.argv[3] if len(sys.argv) > 3 else "leve"
    m = re.search(r"\d{4}-\d{2}-\d{2}-(\d{2})", os.path.abspath(sys.argv[1]))
    ed = int(n.get("edicao") or (m.group(1) if m else 1))
    tmp = tempfile.mkdtemp()
    est = asyncio.run(quadros(n, ed, modelo, tmp))
    if est > 1: print(f"ATENÇÃO: texto não coube ({est}px)"); sys.exit(2)
    os.makedirs(saida, exist_ok=True)
    mp4 = os.path.join(saida, "story.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(tmp, "q%04d.jpg"),
                    "-i", TRILHA, "-filter_complex", f"[1:a]afade=t=in:d=0.5,afade=t=out:st={DUR-1}:d=1,volume=0.8[a]",
                    "-map", "0:v", "-map", "[a]", "-t", str(DUR), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                    "-pix_fmt", "yuv420p", "-profile:v", "high", "-r", str(FPS), "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
                    "-movflags", "+faststart", mp4], check=True)
    ult = sorted(os.listdir(tmp))[-1]
    from PIL import Image
    Image.open(os.path.join(tmp, ult)).convert("RGB").save(os.path.join(saida, "story.jpg"), quality=93)
    shutil.rmtree(tmp)
    print("ok", mp4)

if __name__ == "__main__":
    main()
