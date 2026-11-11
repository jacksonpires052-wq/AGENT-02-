// Agente 03: publica sozinho cada kit novo em reels/<id>/
// Arquivos da pasta: reels.mp4, capa.jpg, legenda.txt, slide01..05.jpg, story.jpg
// Publica 4 coisas: Reels teste, Reels normal, carrossel no feed e story.
// Guarda o que ja saiu em reels/<id>/publicado.json (nunca repete, e tenta de novo so o que falhou).
const fs = require('fs');
const path = require('path');

const VERSAO = 'v26.0';
const CONTA = '17841477285975541';
const REPO = 'jacksonpires052-wq/AGENT-02-';
const RAMO = process.env.RAMO || 'main';
const TOKEN = process.env.IG_TOKEN;
const ESTRATEGIA = process.env.ESTRATEGIA || 'SS_PERFORMANCE';
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
  for (let t = 0; t < 72; t++) {
    const s = await ig('GET', `/${id}`, { fields: 'status_code,status' });
    if (s.status_code === 'FINISHED') return;
    if (s.status_code === 'ERROR' || s.status_code === 'EXPIRED') throw new Error(`Instagram recusou: ${s.status || s.status_code}`);
    await esperar(5000);
  }
  throw new Error('Instagram demorou demais pra processar');
}

async function publicarContainer(id) {
  await aguardar(id);
  const pub = await ig('POST', `/${CONTA}/media_publish`, { creation_id: id });
  let link = '';
  try { link = (await ig('GET', `/${pub.id}`, { fields: 'permalink' })).permalink; } catch {}
  return { id: pub.id, link, data: new Date().toISOString() };
}

function resumo(t) { console.log(t); if (process.env.GITHUB_STEP_SUMMARY) fs.appendFileSync(process.env.GITHUB_STEP_SUMMARY, t + '\n'); }

async function main() {
  if (!TOKEN) throw new Error('Falta o segredo IG_TOKEN');
  if (!fs.existsSync(PASTA)) return console.log('Sem pasta reels/');
  let falhas = 0;
  for (const d of fs.readdirSync(PASTA).sort()) {
    const dir = path.join(PASTA, d);
    if (!fs.existsSync(path.join(dir, 'reels.mp4'))) continue;
    const arqPub = path.join(dir, 'publicado.json');
    let pub = fs.existsSync(arqPub) ? JSON.parse(fs.readFileSync(arqPub, 'utf8')) : {};
    if (pub.id && !pub.teste) pub = { teste: pub }; // formato antigo
    const raw = n => `https://raw.githubusercontent.com/${REPO}/${RAMO}/reels/${encodeURIComponent(d)}/${n}`;
    const tem = n => fs.existsSync(path.join(dir, n));
    const legenda = tem('legenda.txt') ? fs.readFileSync(path.join(dir, 'legenda.txt'), 'utf8') : '';
    const salvar = () => {
      fs.writeFileSync(arqPub, JSON.stringify(pub, null, 2));
      if (process.env.GITHUB_ACTIONS) {
        const { execSync } = require('child_process');
        const sh = c => execSync(c, { stdio: 'inherit' });
        try {
          sh('git config user.name "Agente 03" && git config user.email "agente03@users.noreply.github.com"');
          sh(`git add "${arqPub}" && git commit -q -m "registro ${d}"`);
          for (let i = 1; i <= 8; i++) {
            try { sh('git pull -q --rebase origin main && git push -q'); return; }
            catch { execSync(`sleep ${i * 5}`); }
          }
          throw new Error('nao consegui gravar o registro no GitHub');
        } catch (e) { throw new Error('PARANDO pra nao duplicar: ' + e.message); }
      }
    };

    const tarefas = [
      ['teste', 'Reels teste', true, async () => {
        const p = { media_type: 'REELS', video_url: raw('reels.mp4'), caption: legenda, trial_params: JSON.stringify({ graduation_strategy: ESTRATEGIA }) };
        if (tem('capa.jpg')) p.cover_url = raw('capa.jpg');
        return publicarContainer((await ig('POST', `/${CONTA}/media`, p)).id);
      }],
      ['carrossel', 'Carrossel no feed', [1, 2, 3, 4, 5].every(i => tem(`slide0${i}.jpg`)), async () => {
        const filhos = [];
        for (let i = 1; i <= 5; i++) filhos.push((await ig('POST', `/${CONTA}/media`, { image_url: raw(`slide0${i}.jpg`), is_carousel_item: 'true' })).id);
        for (const f of filhos) await aguardar(f);
        return publicarContainer((await ig('POST', `/${CONTA}/media`, { media_type: 'CAROUSEL', children: filhos.join(','), caption: legenda })).id);
      }],
      ['story', 'Story', tem('story.jpg'), async () =>
        publicarContainer((await ig('POST', `/${CONTA}/media`, { media_type: 'STORIES', image_url: raw('story.jpg') })).id)],
      ['reels', 'Reels normal', tem('normal') || tem('slide01.jpg'), async () => {
        const p = { media_type: 'REELS', video_url: raw('reels.mp4'), caption: legenda, share_to_feed: 'true' };
        if (tem('capa.jpg')) p.cover_url = raw('capa.jpg');
        return publicarContainer((await ig('POST', `/${CONTA}/media`, p)).id);
      }]
    ];

    for (const [chave, nome, ativo, fazer] of tarefas) {
      if (!ativo || pub[chave]) continue;
      try {
        console.log(`${d}: postando ${nome}...`);
        pub[chave] = await fazer();
        salvar();
        resumo(`- ✅ ${d} | ${nome}: ${pub[chave].link || pub[chave].id}`);
        console.log(`POSTADO ${nome}: ${pub[chave].link || pub[chave].id}`);
      } catch (e) {
        if (String(e.message).startsWith('PARANDO')) { resumo(`- 🛑 ${e.message}`); process.exit(1); }
        falhas++;
        resumo(`- ❌ ${d} | ${nome}: ${e.message}`);
      }
    }
  }
  if (falhas) process.exitCode = 1;
}
main();
