# Story de empreendimento ANIMADO (MP4 8 s, 30 fps, sem áudio) + story.jpg (último quadro).
# Uso: python3 agente03/story_empreendimento_motion.py dados.json pasta_saida [foto.jpg]
import asyncio, json, os, shutil, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from story_empreendimento import html, NEON
from playwright.async_api import async_playwright

FPS, DUR = 30, 8.0

ANIM = f"""
.bg{{position:absolute;inset:-2%;background-size:cover;background-position:center;animation:kb 8s linear both}}
@keyframes kb{{from{{transform:scale(1.02) translateY(0)}}to{{transform:scale(1.14) translateY(-1.5%)}}}}
@keyframes sobe{{from{{opacity:0;transform:translateY(46px)}}to{{opacity:1;transform:none}}}}
@keyframes desce{{from{{opacity:0;transform:translateY(-30px)}}to{{opacity:1;transform:none}}}}
@keyframes risca{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}
@keyframes brilho{{0%,100%{{box-shadow:0 0 12px {NEON},0 0 34px {NEON},0 0 70px rgba(57,255,176,.6)}}50%{{box-shadow:0 0 20px {NEON},0 0 60px {NEON},0 0 120px rgba(57,255,176,.85)}}}}
@keyframes pulsa{{0%,100%{{transform:scale(1)}}50%{{transform:scale(1.035)}}}}
@keyframes pop{{0%{{opacity:0;transform:scale(.85)}}70%{{opacity:1;transform:scale(1.04)}}100%{{opacity:1;transform:scale(1)}}}}
.top{{animation:desce .6s .1s cubic-bezier(.2,.8,.2,1) both}}
h1{{animation:sobe .8s .3s cubic-bezier(.2,.8,.2,1) both}}
.bairro{{animation:sobe .7s .6s cubic-bezier(.2,.8,.2,1) both}}
.local{{animation:sobe .7s .75s cubic-bezier(.2,.8,.2,1) both}}
.chips .chip:nth-child(1){{animation:pop .5s 1.0s both}} .chips .chip:nth-child(2){{animation:pop .5s 1.1s both}}
.neon{{transform-origin:left;animation:risca .7s 1.2s cubic-bezier(.6,0,.2,1) both,brilho 1.6s 1.9s ease-in-out infinite}}
.preco{{animation:sobe .7s 1.6s cubic-bezier(.2,.8,.2,1) both}}
.renda{{animation:sobe .7s 2.0s cubic-bezier(.2,.8,.2,1) both}}
.renda:nth-of-type(2){{animation-delay:2.2s}}
.cta{{animation:sobe .6s 2.5s cubic-bezier(.2,.8,.2,1) both,pulsa 1.4s 3.4s ease-in-out infinite}}
.nota,.foot{{animation:sobe .6s 2.8s both}}
"""

def html_motion(d, foto):
    h = html(d, None)
    bg = ""
    if foto:
        import base64
        b = base64.b64encode(open(foto, "rb").read()).decode()
        bg = f'<div class="bg" style="background-image:url(data:image/jpeg;base64,{b})"></div>'
    h = h.replace("</style>", ANIM + "</style>").replace('<div class="sh"></div>', bg + '<div class="sh"></div>', 1)
    return h

async def gravar(d, pasta, foto):
    os.makedirs(pasta, exist_ok=True)
    tmp = tempfile.mkdtemp()
    async with async_playwright() as p:
        br = await p.chromium.launch()
        pg = await br.new_page(viewport={"width": 1080, "height": 1920})
        await pg.set_content(html_motion(d, foto)); await pg.wait_for_timeout(300)
        total = int(FPS * DUR)
        for i in range(total):
            t = i * 1000 / FPS
            await pg.evaluate(f"document.getAnimations().forEach(a=>{{a.pause();a.currentTime={t}}})")
            await pg.screenshot(path=os.path.join(tmp, f"q{i:04d}.jpg"), type="jpeg", quality=90)
        await br.close()
    mp4 = os.path.join(pasta, "story.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(tmp, "q%04d.jpg"),
                    "-an", "-t", str(DUR), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                    "-profile:v", "high", "-r", str(FPS), "-movflags", "+faststart", mp4], check=True)
    shutil.copy(os.path.join(tmp, f"q{int(FPS*DUR)-1:04d}.jpg"), os.path.join(pasta, "story.jpg"))
    shutil.rmtree(tmp)

if __name__ == "__main__":
    d = json.load(open(sys.argv[1]))
    asyncio.run(gravar(d, sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None))
