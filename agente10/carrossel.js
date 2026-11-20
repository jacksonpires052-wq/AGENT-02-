// Posta UM carrossel no feed: carrosseis/<pasta>/ com 01.jpg..NN.jpg e legenda.txt.
// Uso: PASTA=<nome da pasta> node agente10/carrossel.js   (sem PASTA: o mais antigo sem publicado.json)
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const VERSAO = 'v26.0';
const CONTA = '17841477285975541';
const REPO = 'jacksonpires052-wq/AGENT-02-';
const TOKEN = process.env.IG_TOKEN;
const BASE = path.join(__dirname, '..', 'carrosseis');
const esperar = ms => new Promise(r => setTimeout(r, ms));

async function ig(metodo, rota, params = {}) {
  const corpo = new URLSearchParams({ ...params, access_token: TOKEN });
  const url = `https://graph.facebook.com/${VERSAO}${rota}`;
  const r = await fetch(metodo === 'GET' ? `${url}?${corpo}` : url, { method: metodo, body: metodo === 'GET' ? undefined : corpo });
  const j = await r.json().catch(() => ({}));
  if (!r.ok || j.error) throw new Error(`Instagram: ${(j.error && (j.error.error_user_msg || j.error.message)) || r.status}`);
  return j;
}
function resumo(t) { console.log(t); if (process.env.GITHUB_STEP_SUMMARY) fs.appendFileSync(process.env.GITHUB_STEP_SUMMARY, t + '\n'); }
async function pronto(id) {
  for (let t = 0; t < 60; t++) {
    const s = await ig('GET', `/${id}`, { fields: 'status_code,status' });
    if (s.status_code === 'FINISHED') return;
    if (s.status_code === 'ERROR' || s.status_code === 'EXPIRED') throw new Error(`Instagram recusou: ${s.status || s.status_code}`);
    await esperar(3000);
  }
  throw new Error('Instagram demorou demais para processar');
}

async function main() {
  if (!TOKEN) throw new Error('Falta o segredo IG_TOKEN');
  const pub = d => fs.existsSync(path.join(BASE, d, 'publicado.json'));
  const d = process.env.PASTA || fs.readdirSync(BASE).sort().find(x => !pub(x));
  if (!d) return resumo('Nenhum carrossel esperando.');
  if (pub(d)) return resumo(`${d} já foi publicado. Nada feito.`);
  const dir = path.join(BASE, d);
  const imgs = fs.readdirSync(dir).filter(f => /^\d+\.jpg$/.test(f)).sort();
  if (imgs.length < 2 || imgs.length > 10) throw new Error(`${d}: precisa de 2 a 10 imagens (tem ${imgs.length})`);
  const legenda = fs.readFileSync(path.join(dir, 'legenda.txt'), 'utf8').trim();
  const raw = f => `https://raw.githubusercontent.com/${REPO}/main/carrosseis/${encodeURIComponent(d)}/${f}`;

  const filhos = [];
  for (const f of imgs) {
    const c = await ig('POST', `/${CONTA}/media`, { image_url: raw(f), is_carousel_item: 'true' });
    await pronto(c.id); filhos.push(c.id);
  }
  const car = await ig('POST', `/${CONTA}/media`, { media_type: 'CAROUSEL', children: filhos.join(','), caption: legenda });
  await pronto(car.id);
  const p = await ig('POST', `/${CONTA}/media_publish`, { creation_id: car.id });
  let link = '';
  try { link = (await ig('GET', `/${p.id}`, { fields: 'permalink' })).permalink; } catch {}
  resumo(`CARROSSEL POSTADO: ${d} | ${link || p.id}`);
  fs.writeFileSync(path.join(dir, 'publicado.json'), JSON.stringify({ id: p.id, link, data: new Date().toISOString() }, null, 1));

  if (process.env.GITHUB_ACTIONS) {
    const sh = cmd => execSync(cmd, { stdio: 'inherit' });
    sh('git config user.name "Agente 10" && git config user.email "agente10@users.noreply.github.com"');
    sh(`git add carrosseis && git commit -q -m "carrossel postado ${d}"`);
    for (let i = 1; i <= 8; i++) {
      try { sh('git pull -q --rebase origin main && git push -q'); return; } catch { execSync(`sleep ${i * 5}`); }
    }
    throw new Error('Carrossel postado, mas não consegui gravar o registro no GitHub (risco de repetir).');
  }
}
main().catch(e => { resumo(`ERRO: ${e.message}`); process.exit(1); });
