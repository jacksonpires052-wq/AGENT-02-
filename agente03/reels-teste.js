// Agente 03: publica como REELS TESTE (trial reels) cada pasta nova em reels/<id>/
// Cada pasta tem: reels.mp4, legenda.txt e, se quiser, capa.jpg.
// Depois de postar, grava reels/<id>/publicado.json pra nunca repetir.
const fs = require('fs');
const path = require('path');

const VERSAO = 'v26.0';
const CONTA = '17841477285975541';
const REPO = 'jacksonpires052-wq/AGENT-02-';
const RAMO = process.env.RAMO || 'main';
const TOKEN = process.env.IG_TOKEN;
const ESTRATEGIA = process.env.ESTRATEGIA || 'SS_PERFORMANCE'; // ou MANUAL
const PASTA = path.join(__dirname, '..', 'reels');

const esperar = ms => new Promise(r => setTimeout(r, ms));

async function ig(metodo, rota, params = {}) {
  const corpo = new URLSearchParams({ ...params, access_token: TOKEN });
  const base = `https://graph.facebook.com/${VERSAO}${rota}`;
  const r = await fetch(metodo === 'GET' ? `${base}?${corpo}` : base, { method: metodo, body: metodo === 'GET' ? undefined : corpo });
  const j = await r.json().catch(() => ({}));
  if (!r.ok || j.error) throw new Error(`Instagram: ${(j.error && (j.error.error_user_msg || j.error.message)) || r.status}`);
  return j;
}

async function aguardar(id) {
  for (let t = 0; t < 72; t++) { // ate 6 minutos
    const s = await ig('GET', `/${id}`, { fields: 'status_code,status' });
    if (s.status_code === 'FINISHED') return;
    if (s.status_code === 'ERROR' || s.status_code === 'EXPIRED') throw new Error(`Instagram recusou o video: ${s.status || s.status_code}`);
    await esperar(5000);
  }
  throw new Error('Instagram demorou demais pra processar o video');
}

async function main() {
  if (!TOKEN) throw new Error('Falta o segredo IG_TOKEN');
  if (!fs.existsSync(PASTA)) return console.log('Sem pasta reels/');
  const pendentes = fs.readdirSync(PASTA)
    .filter(d => fs.existsSync(path.join(PASTA, d, 'reels.mp4')) && !fs.existsSync(path.join(PASTA, d, 'publicado.json')))
    .sort();
  if (!pendentes.length) return console.log('Nenhum Reels teste pendente');
  let falhas = 0;
  for (const d of pendentes) {
    try {
      const raw = n => `https://raw.githubusercontent.com/${REPO}/${RAMO}/reels/${encodeURIComponent(d)}/${n}`;
      const legenda = fs.existsSync(path.join(PASTA, d, 'legenda.txt')) ? fs.readFileSync(path.join(PASTA, d, 'legenda.txt'), 'utf8') : '';
      const params = { media_type: 'REELS', video_url: raw('reels.mp4'), caption: legenda, trial_params: JSON.stringify({ graduation_strategy: ESTRATEGIA }) };
      if (fs.existsSync(path.join(PASTA, d, 'capa.jpg'))) params.cover_url = raw('capa.jpg');
      console.log(`Mandando ${d} pro Instagram como Reels teste (${ESTRATEGIA})...`);
      const c = await ig('POST', `/${CONTA}/media`, params);
      await aguardar(c.id);
      const pub = await ig('POST', `/${CONTA}/media_publish`, { creation_id: c.id });
      let link = '';
      try { link = (await ig('GET', `/${pub.id}`, { fields: 'permalink' })).permalink; } catch {}
      fs.writeFileSync(path.join(PASTA, d, 'publicado.json'), JSON.stringify({ id: pub.id, link, data: new Date().toISOString(), estrategia: ESTRATEGIA }, null, 2));
      console.log(`POSTADO como teste: ${link || pub.id}`);
      if (process.env.GITHUB_STEP_SUMMARY) fs.appendFileSync(process.env.GITHUB_STEP_SUMMARY, `- ✅ ${d}: ${link || pub.id}\n`);
    } catch (e) {
      falhas++;
      console.log(`ERRO em ${d}: ${e.message}`);
      if (process.env.GITHUB_STEP_SUMMARY) fs.appendFileSync(process.env.GITHUB_STEP_SUMMARY, `- ❌ ${d}: ${e.message}\n`);
    }
  }
  if (falhas) process.exitCode = 1;
}
main();
