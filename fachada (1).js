// Agente 02 - acha a foto da ENTRADA/FACHADA do imovel pela imagem (sem IA, de graca)
// Pontua ceu azul no topo da foto e verde (jardim/arvores). Foto de dentro quase nao tem nada disso.
const { createCanvas, loadImage } = require('@napi-rs/canvas');

async function notaFachada(buf) {
  const img = await loadImage(buf);
  const W = 48, H = 60;
  const c = createCanvas(W, H); const x = c.getContext('2d');
  x.drawImage(img, 0, 0, W, H);
  const d = x.getImageData(0, 0, W, H).data;
  let ceu = 0, nCeu = 0, verde = 0, n = 0;
  for (let yy = 0; yy < H; yy++) for (let xx = 0; xx < W; xx++) {
    const i = (yy * W + xx) * 4, r = d[i], g = d[i + 1], b = d[i + 2];
    n++;
    if (g > r + 12 && g > b + 8 && g > 60) verde++;
    if (yy < H * 0.28) { nCeu++; if (b > 120 && b - r > 45 && b - g > 8 && (b - Math.min(r, g)) / b > 0.3) ceu++; }
  }
  return ceu / nCeu + 0.5 * (verde / n);
}

// devolve a lista com a melhor foto de fachada na frente
async function fachadaPrimeiro(urls, baixar, max = 20) {
  const notas = [];
  for (const [i, u] of urls.slice(0, max).entries()) {
    try { notas.push({ u, i, nota: await notaFachada(await baixar(u)) + (i === 0 ? 0.03 : 0) - i * 0.002 }); } catch { }
  }
  if (!notas.length) return urls;
  notas.sort((a, b) => b.nota - a.nota);
  const melhor = notas[0];
  if (melhor.nota < 0.05) return urls; // nenhuma parece de fora: mantem a ordem do site
  return [melhor.u, ...urls.filter(u => u !== melhor.u)];
}

module.exports = { notaFachada, fachadaPrimeiro };
