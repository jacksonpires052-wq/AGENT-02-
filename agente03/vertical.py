"""Gera story (1080x1920 JPG) e Reels (1080x1920 MP4) a partir dos slides do carrossel.
Uso: python3 vertical.py pasta_saida "Texto do topo do story"
"""
import sys, os, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AZUL = (63, 95, 217)
W, H = 1080, 1920
FONTE = "/usr/share/fonts/truetype/inter/InterDisplay-Bold.ttf"


def fonte(tam):
    for f in [FONTE, "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"]:
        if os.path.exists(f):
            return ImageFont.truetype(f, tam)
    import glob
    c = glob.glob("/usr/share/fonts/**/InterDisplay-Bold.*", recursive=True) or glob.glob("/usr/share/fonts/**/Inter*Bold*", recursive=True)
    return ImageFont.truetype(c[0], tam)


def fundo():
    bg = Image.new("RGB", (W, H), AZUL)
    d = ImageDraw.Draw(bg)
    for y in range(0, H, 6):  # meio-tom
        for x in range(0, W, 6):
            d.ellipse((x, y, x + 2, y + 2), fill=(52, 82, 196))
    return bg


def cola(bg, slide, escala, y):
    w, h = int(1080 * escala), int(1350 * escala)
    s = slide.resize((w, h), Image.LANCZOS)
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w, h), 34, fill=255)
    sombra = Image.new("RGBA", (w + 80, h + 80), (0, 0, 0, 0))
    ImageDraw.Draw(sombra).rounded_rectangle((40, 50, w + 40, h + 50), 34, fill=(0, 0, 0, 110))
    sombra = sombra.filter(ImageFilter.GaussianBlur(22))
    x = (W - w) // 2
    bg.paste(sombra, (x - 40, y - 40), sombra)
    bg.paste(s, (x, y), m)


def texto_centro(bg, txt, y, tam, cor=(255, 255, 255), faixa=None):
    d = ImageDraw.Draw(bg)
    f = fonte(tam)
    for i, linha in enumerate(txt.split("\n")):
        bw = d.textlength(linha, font=f)
        x = (W - bw) / 2
        yy = y + i * int(tam * 1.12)
        if faixa:
            d.rectangle((x - 18, yy - 4, x + bw + 18, yy + tam * 1.1), fill=faixa)
        d.text((x, yy), linha, font=f, fill=cor)


def story(out, topo):
    bg = fundo()
    cola(bg, Image.open(os.path.join(out, "slide01.jpg")), 0.86, 390)
    texto_centro(bg, topo, 150, 66, cor=AZUL, faixa=(255, 255, 255))
    texto_centro(bg, "Toca aqui e vê o post completo", 1640, 40)
    texto_centro(bg, "@CORRETOR.JACKSONPIRES  |  CRECI 323400", 1790, 26)
    bg.save(os.path.join(out, "story.jpg"), quality=93)


def reels(out, topo, seg=2.32, fade=0.4):
    quadros = []
    for i in range(1, 6):
        bg = fundo()
        cola(bg, Image.open(os.path.join(out, f"slide{i:02d}.jpg")), 0.94, 400)
        texto_centro(bg, topo, 140, 62, cor=AZUL, faixa=(255, 255, 255))
        texto_centro(bg, "@CORRETOR.JACKSONPIRES  |  CRECI 323400", 1790, 26)
        p = os.path.join(out, f"_reel{i}.png"); bg.save(p); quadros.append(p)
    fps, n = 30, int(seg * 30)
    entradas, filtros = [], []
    for i, p in enumerate(quadros):
        entradas += ["-loop", "1", "-t", str(seg), "-i", p]
        filtros.append(f"[{i}:v]scale=1188:2112,zoompan=z='min(zoom+0.0009,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={fps},setsar=1,format=yuv420p[v{i}]")
    ant, off = "v0", seg - fade
    for i in range(1, len(quadros)):
        filtros.append(f"[{ant}][v{i}]xfade=transition=slideleft:duration={fade}:offset={off:.2f}[x{i}]")
        ant, off = f"x{i}", off + seg - fade
    total = seg * len(quadros) - fade * (len(quadros) - 1)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", *entradas, "-f", "lavfi", "-t", f"{total:.2f}", "-i", "anullsrc=r=44100:cl=stereo",
           "-filter_complex", ";".join(filtros), "-map", f"[{ant}]", "-map", f"{len(quadros)}:a",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest",
           "-movflags", "+faststart", os.path.join(out, "reels.mp4")]
    subprocess.run(cmd, check=True)
    for p in quadros: os.remove(p)


if __name__ == "__main__":
    out, topo = sys.argv[1], sys.argv[2].replace("\\n", "\n")
    story(out, topo)
    reels(out, topo)
    print("ok")
