// Agente 03 (desde 13/11/2026): as notícias saem SÓ como story.
// Cada disparo do relógio publica UM story da fila: stories/<AAAA-MM-DD-NN-assunto>/ com story.jpg e o arquivo vazio 'fila'.
// Sai sempre o mais antigo da fila (ordem do nome). Guarda o que saiu em publicado.json e nunca repete.
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const VERSAO = 'v26.0';
const CONTA = '17841477285975541';
const REPO = 'jacksonpires052-wq/AGENT-02-';
const TOKEN = process.env.IG_TOKEN;
const PASTA = path.join(__dirname, '..', 'stories');
const esperar = ms => new Promise(r => setTimeout(r, ms));

async function ig(metodo, rota, params = {}) {
  const corpo = new URLSearchParams({ ...params, access_token: TOKEN });
  const base = `https://graph.facebook.com/${VERSAO}${rota}`;
  const r = await fetch(metodo === 'GET' ? `${base}?${corpo}` : base, { method: metodo, body: metodo === 'GET' ? undefined : corpo });
  const j = await r.json().catch(() => ({}));
  if (!r.ok || j.error) throw new Error(`Instagram: ${(j.error && (j.error.error_user_msg || j.error.message)) || r.status}`);
  return j;
}

function resumo(t) { console.log(t); if (process.env.GITHUB_STEP_SUMMARY) fs.appendFileSync(process.env.GITHUB_STEP_SUMMARY, t + '\n'); }

async function main() {
  if (!TOKEN) throw new Error('Falta o segredo IG_TOKEN');
  if (!fs.existsSync(PASTA)) return resumo('Fila de stories vazia (sem pasta stories/).');
  const lerPub = d => { try { return JSON.parse(fs.readFileSync(path.join(PASTA, d, 'publicado.json'), 'utf8')); } catch { return {}; } };
  const fila = fs.readdirSync(PASTA).sort().filter(d =>
    fs.existsSync(path.join(PASTA, d, 'fila')) && fs.existsSync(path.join(PASTA, d, 'story.jpg')) && !lerPub(d).story);
  if (!fila.length) return resumo('Fila de stories vazia: nenhuma notícia esperando.');
  const d = fila[0];
  resumo(`Fila: ${fila.length} story(s). Publicando agora: ${d}`);

  const url = `https://raw.githubusercontent.com/${REPO}/main/stories/${encodeURIComponent(d)}/story.jpg`;
  const c = await ig('POST', `/${CONTA}/media`, { media_type: 'STORIES', image_url: url });
  for (let t = 0; t < 60; t++) {
    const s = await ig('GET', `/${c.id}`, { fields: 'status_code,status' });
    if (s.status_code === 'FINISHED') break;
    if (s.status_code === 'ERROR' || s.status_code === 'EXPIRED') throw new Error(`Instagram recusou: ${s.status || s.status_code}`);
    await esperar(3000);
  }
  const pub = await ig('POST', `/${CONTA}/media_publish`, { creation_id: c.id });
  let link = '';
  try { link = (await ig('GET', `/${pub.id}`, { fields: 'permalink' })).permalink; } catch {}
  const reg = { story: { id: pub.id, link, data: new Date().toISOString() } };
  fs.writeFileSync(path.join(PASTA, d, 'publicado.json'), JSON.stringify(reg, null, 2));
  resumo(`STORY POSTADO: ${d} | ${link || pub.id}`);

  if (process.env.GITHUB_ACTIONS) {
    const sh = cmd => execSync(cmd, { stdio: 'inherit' });
    sh('git config user.name "Agente 03" && git config user.email "agente03@users.noreply.github.com"');
    sh(`git add stories && git commit -q -m "story postado ${d}"`);
    for (let i = 1; i <= 8; i++) {
      try { sh('git pull -q --rebase origin main && git push -q'); return; } catch { execSync(`sleep ${i * 5}`); }
    }
    throw new Error('Story postado, mas não consegui gravar o registro no GitHub (risco de repetir).');
  }
}
main().catch(e => { resumo(`ERRO: ${e.message}`); process.exit(1); });
