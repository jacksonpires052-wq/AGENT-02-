// Agente 02 - monta a capa e as fotos do post (1080x1350, JPG)
const path = require('path');
const { createCanvas, loadImage, GlobalFonts } = require('@napi-rs/canvas');

const F = path.join(__dirname, 'fonts');
GlobalFonts.registerFromPath(path.join(F, 'Lora-Medium.ttf'), 'LoraAG');
GlobalFonts.registerFromPath(path.join(F, 'Inter-Medium.otf'), 'InterAG');
GlobalFonts.registerFromPath(path.join(F, 'Inter-ExtraBold.otf'), 'InterAGX');

const W = 1080, H = 1350, FH = 727;
const COR = { azul: '#1e5bd8', texto: '#121a2b', cinza: '#6b6f76', linha: '#e3e5e8', verde: '#25e36f', amarelo: '#ffd400' };

function cover(x, img, X, Y, w, h) {
  const s = Math.max(w / img.width, h / img.height);
  const iw = img.width * s, ih = img.height * s;
  x.save(); x.beginPath(); x.rect(X, Y, w, h); x.clip();
  x.drawImage(img, X + (w - iw) / 2, Y + (h - ih) / 2, iw, ih);
  x.restore();
}

// texto com espacamento entre letras (desenha letra por letra)
function espacado(x, t, px, cor, sp, X, Y, alinhar) {
  x.font = `${px}px InterAG`; x.fillStyle = cor; x.textAlign = 'left'; x.textBaseline = 'alphabetic';
  const letras = [...t];
  const larg = letras.reduce((a, c) => a + x.measureText(c).width + sp, 0) - sp;
  let cx = alinhar === 'right' ? X - larg : X;
  for (const c of letras) { x.fillText(c, cx, Y); cx += x.measureText(c).width + sp; }
}

function caber(x, t, fonte, max, tamanho, minimo) {
  let px = tamanho;
  while (px > minimo) { x.font = `${px}px ${fonte}`; if (x.measureText(t).width <= max) break; px -= 2; }
  return px;
}

async function capa(d) {
  const c = createCanvas(W, H); const x = c.getContext('2d');
  x.fillStyle = '#fff'; x.fillRect(0, 0, W, H);
  cover(x, await loadImage(d.foto), 0, 0, W, FH);

  // tracejado amarelo
  x.save(); x.strokeStyle = 'rgba(255,214,0,0.9)'; x.lineWidth = 2; x.setLineDash([8, 7]);
  x.beginPath(); x.moveTo(0, FH - 97); x.lineTo(W, FH - 97); x.stroke(); x.restore();

  // selo A VENDA
  const bx = 760, by = 300, bw = 297, bh = 83;
  x.save(); x.fillStyle = 'rgba(52,78,62,0.78)';
  x.beginPath(); x.roundRect(bx, by, bw, bh, 8); x.fill();
  x.font = '58px InterAGX'; x.textAlign = 'center'; x.textBaseline = 'middle';
  x.shadowColor = 'rgba(40,255,120,0.9)'; x.shadowBlur = 14;
  x.fillStyle = COR.verde; x.fillText('À VENDA', bx + bw / 2, by + bh / 2 + 2);
  x.restore();
  x.fillStyle = COR.amarelo; x.fillRect(780, by + bh + 6, 260, 5);

  // ficha
  espacado(x, d.categoria.toUpperCase(), 16, COR.cinza, 6, 60, 792);
  const px = caber(x, d.nome, 'LoraAG', 700, 60, 36);
  x.font = `${px}px LoraAG`; x.fillStyle = COR.texto; x.textAlign = 'left'; x.fillText(d.nome, 58, 853);
  espacado(x, d.bairro.toUpperCase(), 17, COR.cinza, 4, 1020, d.cidade ? 827 : 840, 'right');
  if (d.cidade) espacado(x, d.cidade.toUpperCase(), 17, COR.cinza, 4, 1020, 853, 'right');

  x.fillStyle = COR.linha;
  x.fillRect(60, 900, 960, 2); x.fillRect(60, 1042, 960, 2);
  x.fillRect(380, 900, 2, 144); x.fillRect(700, 900, 2, 144);
  const cols = [60, 416, 736];
  d.stats.slice(0, 3).forEach((st, i) => {
    x.font = '58px InterAGX'; x.fillStyle = COR.texto; x.textAlign = 'left';
    x.fillText(String(st.v), cols[i], 978);
    espacado(x, st.l.toUpperCase(), 16, COR.cinza, 5, cols[i], 1013);
  });

  // preco
  espacado(x, 'VALOR', 16, COR.cinza, 6, 60, 1084);
  x.font = '50px InterAGX'; x.fillStyle = COR.azul; x.textAlign = 'left'; x.fillText(d.preco, 58, 1132);
  if (d.precoObs) espacado(x, d.precoObs.toUpperCase(), 16, COR.cinza, 4, 1020, 1126, 'right');

  // rodape
  x.fillStyle = COR.linha; x.fillRect(60, 1150, 960, 2);
  x.fillStyle = COR.azul; x.fillRect(60, 1188, 5, 78);
  x.font = '37px InterAGX'; x.fillStyle = COR.texto; x.textAlign = 'left';
  x.fillText(d.corretor, 88, 1227);
  espacado(x, 'CORRETOR · CRECI ' + d.creci, 18, COR.cinza, 5, 88, 1259);
  espacado(x, 'ARRASTA', 18, COR.texto, 6, 962, 1233, 'right');
  x.strokeStyle = COR.azul; x.lineWidth = 2.5; x.beginPath();
  x.moveTo(990, 1233); x.lineTo(1012, 1233); x.moveTo(1004, 1226); x.lineTo(1012, 1233); x.lineTo(1004, 1240); x.stroke();

  return c.encode('jpeg', 93);
}

async function foto(buf) {
  const c = createCanvas(W, H); const x = c.getContext('2d');
  cover(x, await loadImage(buf), 0, 0, W, H);
  return c.encode('jpeg', 92);
}

module.exports = { capa, foto };
