// AGENTE 02 - posta imoveis da AE Patrimonio no Instagram do Jackson Pires
// Uso:
//   node agente02.js            -> faixa da hora atual, monta e POSTA
//   node agente02.js --teste    -> monta as imagens e a legenda, NAO posta
//   node agente02.js --faixa 2  -> forca a faixa (1 a 4)
//   node agente02.js --checar   -> confere se os acessos do Instagram e do GitHub funcionam
const fs = require('fs');
const path = require('path');
const { capa, capaSeta, foto } = require('./capa');
const { fachadaPrimeiro } = require('./fachada');

const DIR = __dirname;
const CONFIG = path.join(DIR, 'config.json');
const ESTADO = path.join(DIR, 'dados', 'estado.json');
const POSTADOS = path.join(DIR, 'dados', 'postados.json');
const LOG = path.join(DIR, 'dados', 'agente02.log');
const POSTS = path.join(DIR, 'posts');
const AE = 'https://aepatrimonio.com.br';
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0 Safari/537.36';

const args = process.argv.slice(2);
const TESTE_MANUAL = args.includes('--teste');
let TESTE = TESTE_MANUAL;
const CHECAR = args.includes('--checar');
const faixaArg = args.includes('--faixa') ? parseInt(args[args.indexOf('--faixa') + 1], 10) : null;

fs.mkdirSync(path.join(DIR, 'dados'), { recursive: true });
fs.mkdirSync(POSTS, { recursive: true });

function log(...m) {
  const linha = `[${new Date().toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' })}] ${m.join(' ')}`;
  console.log(linha);
  fs.appendFileSync(LOG, linha + '\n');
}
const lerJson = (f, padrao) => { try { return JSON.parse(fs.readFileSync(f, 'utf8')); } catch { return padrao; } };
const salvarJson = (f, o) => fs.writeFileSync(f, JSON.stringify(o, null, 2));
const esperar = ms => new Promise(r => setTimeout(r, ms));
const _fetch = global.fetch;
global.fetch = async (url, op) => {
  for (let t = 1; ; t++) {
    try { return await _fetch(url, op); }
    catch (e) {
      const host = (() => { try { return new URL(url).host; } catch { return String(url).slice(0, 40); } })();
      const causa = e.cause ? (e.cause.code || e.cause.message || String(e.cause)) : e.message;
      if (t >= 3) throw new Error(`sem conexão com ${host} (${causa})`);
      log(`Falha de rede com ${host} (${causa}), tentando de novo...`); await esperar(3000 * t);
    }
  }
};

const NUVEM = !!process.env.GITHUB_ACTIONS;
const cfg = lerJson(CONFIG, null) || lerJson(path.join(DIR, 'config.nuvem.json'), null);
if (cfg && process.env.IG_TOKEN) cfg.instagram.token = process.env.IG_TOKEN.trim();
const REPO = process.env.GITHUB_REPOSITORY || (cfg && cfg.github ? `${cfg.github.usuario}/${cfg.github.repositorio}` : '');
const RAMO = process.env.GITHUB_REF_NAME || 'main';
const linkPublico = (cod, n) => `https://raw.githubusercontent.com/${REPO}/${RAMO}/posts/${cod}/${n}`;
function saida(k, v) { if (process.env.GITHUB_OUTPUT) fs.appendFileSync(process.env.GITHUB_OUTPUT, `${k}=${v}\n`); }
function resumo(t) { if (process.env.GITHUB_STEP_SUMMARY) fs.appendFileSync(process.env.GITHUB_STEP_SUMMARY, t + '\n'); }
if (!cfg) { log('ERRO: config.json nao encontrado. Copie config.exemplo.json para config.json e preencha.'); process.exit(1); }
const estado = lerJson(ESTADO, {});
const postados = lerJson(POSTADOS, []);

// ---------------------------------------------------------------- site da AE
let cookies = {};
function guardarCookies(r) {
  const lista = typeof r.headers.getSetCookie === 'function' ? r.headers.getSetCookie() : (r.headers.get('set-cookie') || '').split(/,(?=\s*\w+=)/);
  for (const c of lista) { const [kv] = c.split(';'); const i = kv.indexOf('='); if (i > 0) cookies[kv.slice(0, i).trim()] = kv.slice(i + 1).trim(); }
}
async function pegar(url, tipo = 'text') {
  for (let t = 1; t <= 3; t++) {
    try {
      const r = await fetch(url, { headers: { 'User-Agent': UA, 'Accept-Language': 'pt-BR,pt;q=0.9', Cookie: Object.entries(cookies).map(([k, v]) => `${k}=${v}`).join('; ') }, redirect: 'manual' });
      guardarCookies(r);
      if (r.status >= 300 && r.status < 400 && r.headers.get('location')) return pegar(new URL(r.headers.get('location'), url).href, tipo);
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return tipo === 'buffer' ? Buffer.from(await r.arrayBuffer()) : await r.text();
    } catch (e) { if (t === 3) throw e; await esperar(2000 * t); }
  }
}

async function buscar(faixa, pagina) {
  const base = `${AE}/venda/residencial_comercial/${cfg.cidade}/`;
  const q = `?finalidade=venda&dormitorios[]=${faixa.quartos}&valorvenda=${faixa.min},${faixa.max}&ordenar=${cfg.ordem || 'relevancia'}&pagina=${pagina}`;
  let h = await pegar(base + q);
  if (h.length < 2000) { // o site guarda o filtro e manda pra pagina limpa
    const destino = (h.match(/location\.assign\('([^']+)'/) || [])[1] || base;
    h = await pegar(destino);
  }
  const vistos = new Set(); const lista = [];
  for (const m of h.matchAll(/\/imovel\/(\d+)\/[a-z0-9\-]+\//g)) {
    if (!vistos.has(m[1])) { vistos.add(m[1]); lista.push({ codigo: m[1], url: AE + m[0] }); }
  }
  const total = parseInt(((h.match(/Encontramos\s*([\d\.]+)/) || [])[1] || '0').replace(/\./g, ''), 10);
  return { lista, total };
}

const entidades = s => s.replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&quot;/g, '"').replace(/&#0?39;/g, "'")
  .replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&#(\d+);/g, (m, n) => String.fromCharCode(+n));
const semTags = s => entidades(s.replace(/<(script|style|svg|noscript)[\s\S]*?<\/\1>/gi, ' ').replace(/<br\s*\/?>/gi, '\n').replace(/<[^>]+>/g, '\n'))
  .split('\n').map(l => l.replace(/\s+/g, ' ').trim()).filter(Boolean).join('\n');
const num = s => parseFloat(String(s).replace(/\./g, '').replace(',', '.'));
const tituloCaso = s => s.toLowerCase().replace(/(^|\s|-)(\S)/g, (m, a, b) => a + b.toUpperCase())
  .replace(/\b(De|Da|Do|Das|Dos|E|Em)\b/g, w => w.toLowerCase()).replace(/^./, c => c.toUpperCase());

async function lerImovel(item) {
  const h = await pegar(item.url);
  const i = h.indexOf('<h1');
  if (i < 0) throw new Error('pagina sem titulo');
  const topo = h.slice(i, i + 4000);
  const titulo = semTags((topo.match(/<h1[^>]*>([\s\S]*?)<\/h1>/) || [])[1] || '');
  const condo = semTags((topo.match(/<\/h1>\s*<h3[^>]*>([\s\S]*?)<\/h3>/) || [])[1] || '');
  const local = semTags((topo.match(/<\/h[13]>\s*<p[^>]*>([\s\S]*?)<\/p>/) || [])[1] || '').replace(/\n/g, ' ');
  const [bairro, cidadeUf] = local.split(/\s+-\s+/);
  const cidade = (cidadeUf || 'Sorocaba').replace(/\s*\/\s*\w+$/, '').trim();

  let texto = semTags(h);
  const ini = texto.indexOf(titulo.split('\n')[0]);
  texto = texto.slice(ini >= 0 ? ini : 0);
  const fim = texto.search(/INDICADOS PARA VOC|RECEBER CONTATO POR/);
  const main = fim > 0 ? texto.slice(0, fim) : texto.slice(0, 6000);

  const preco = num((main.match(/Venda\s*R\$\s*([\d\.]+,\d\d)/) || [])[1] || 'NaN');
  const condominio = num((main.match(/Condom[ií]nio\s*R\$\s*([\d\.]+,\d\d)/) || [])[1] || 'NaN');
  const pegaN = re => { const m = main.match(re); return m ? parseInt(m[1], 10) : 0; };
  const quartos = pegaN(/\n(\d+)\nQuartos?\n/i) || pegaN(/(\d+)\s*Quartos?/i);
  const suites = pegaN(/\n(\d+)\nSu[ií]tes?\n/i);
  const banheiros = pegaN(/\n(\d+)\nBanheiros?\n/i);
  const vagas = pegaN(/\n(\d+)\nVagas?\n/i);
  const am = main.match(/([\d\.,]+)\s*m\s*²?\s*\n?\s*2?\s*\n?\s*(Privativos|Totais|Constru[ií]dos|[ÚU]teis|Terreno)/i);
  const area = am ? Math.round(num(am[1])) : 0;
  const areaTipo = am ? am[2].toLowerCase() : '';
  const descIni = main.search(/Privativos|Totais|Constru[ií]dos|Vagas?\n/i);
  const descricao = main.slice(descIni > 0 ? descIni : 0).split(/Quer saber|\+ DETALHES|RECEBER CONTATO/)[0];

  const fotos = [];
  for (const m of h.matchAll(new RegExp(`https://[^"'\\s)]+/${item.codigo}/[^"'\\s)]+\\.(?:webp|jpe?g|png)`, 'gi'))) if (!fotos.includes(m[0])) fotos.push(m[0]);

  const tipo = tituloCaso((titulo.match(/^([^\d]+?)\s+\d/) || [, titulo.split(' ')[0]])[1]);
  return {
    codigo: item.codigo, url: item.url, titulo, tipo,
    condo: condo ? tituloCaso(condo) : '', bairro: tituloCaso(bairro || ''), cidade: tituloCaso(cidade),
    preco, condominio, quartos, suites, banheiros, vagas, area, areaTipo, descricao, fotos
  };
}

// ---------------------------------------------------------------- textos
function precoCurto(v) {
  if (v >= 1e6) return 'R$ ' + (v / 1e6).toFixed(2).replace(/\.?0+$/, '').replace('.', ',') + (v >= 2e6 ? ' milhões' : ' milhão');
  return 'R$ ' + (v / 1000).toFixed(1).replace(/\.0$/, '').replace('.', ',') + ' mil';
}
const real = v => 'R$ ' + Math.round(v).toLocaleString('pt-BR');
const plural = (n, s, p) => `${n} ${n === 1 ? s : p}`;
const LAZER = [['piscina', 'piscina'], ['salão de festas|salao de festas', 'salão de festas'], ['playground', 'playground'], ['churrasqueira', 'churrasqueira'],
  ['academia|fitness', 'academia'], ['\\bquadras?\\b(?! ?metros)', 'quadra'], ['\\bpet\\b|pet place', 'espaço pet'], ['gourmet', 'espaço gourmet'], ['brinquedoteca', 'brinquedoteca'], ['portaria 24', 'portaria 24h']];

function legenda(im) {
  const d = im.descricao.toLowerCase();
  const lazer = LAZER.filter(([re]) => new RegExp(re).test(d)).map(([, n]) => n).slice(0, 4);
  const tipoMin = im.tipo.toLowerCase();
  const apelido = /apartamento/.test(tipoMin) ? 'Apê' : im.tipo;
  const fem = /^(casa|cobertura|chácara|chacara|kitnet|sala|loja|área|area)/.test(tipoMin);
  const num = fem ? 'numa' : 'num', esse = fem ? 'essa' : 'esse';
  const ganchos = [
    `${apelido} de ${plural(im.quartos, 'quarto', 'quartos')} em ${im.cidade} por ${precoCurto(im.preco)} 🏡`,
    `${precoCurto(im.preco)} ${num} ${tipoMin} de ${plural(im.quartos, 'quarto', 'quartos')} em ${im.cidade} 🔑`,
    `Olha ${esse} ${tipoMin} de ${plural(im.quartos, 'quarto', 'quartos')} por ${precoCurto(im.preco)} 👀`
  ];
  const g = ganchos[(postados.length) % ganchos.length];
  const onde = im.condo && im.condo.toLowerCase() !== im.bairro.toLowerCase() ? `Fica no ${im.condo}, no bairro ${im.bairro}` : `Fica no bairro ${im.bairro}`;
  const extra = /cadeira de rodas|cadeirante|acessibilidade/.test(d) ? ', e foi feito pensando em quem usa cadeira de rodas.' : '.';
  const itens = [];
  if (im.area) itens.push(`✅ ${im.area} m² ${/priv/.test(im.areaTipo) ? 'privativos' : /terreno/.test(im.areaTipo) ? 'de terreno' : 'no total'}`);
  const comodos = [plural(im.quartos, 'quarto', 'quartos')];
  if (im.suites) comodos.push(plural(im.suites, 'suíte', 'suítes'));
  if (im.banheiros) comodos.push(plural(im.banheiros, 'banheiro', 'banheiros'));
  if (im.vagas) comodos.push(plural(im.vagas, 'vaga', 'vagas'));
  itens.push('✅ ' + comodos.join(', ').replace(/, ([^,]+)$/, ' e $1'));
  if (lazer.length) itens.push('✅ ' + (lazer.join(', ').replace(/, ([^,]+)$/, ' e $1')).replace(/^./, c => c.toUpperCase()));
  if (im.condominio > 0) itens.push(`✅ Condomínio de ${real(im.condominio)}`);
  const tagTipo = '#' + (/apartamento/.test(tipoMin) ? 'apartamento' : /casa/.test(tipoMin) ? 'casa' : tipoMin.replace(/\W/g, '')) + 'sorocaba';
  const tagBairro = '#' + im.bairro.normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-zA-Z0-9]/g, '').toLowerCase();
  const tags = ['#imoveissorocaba', tagTipo, '#sorocaba', tagBairro, '#corretordeimoveis'].filter((t, i, a) => t.length > 2 && a.indexOf(t) === i).slice(0, 5);
  return [
    g, '', onde + extra, '', ...itens, '',
    `💰 ${real(im.preco)}`, `📌 Código ${im.codigo}`, '',
    'Quer visitar ou simular o financiamento? Me chama no direct que eu te ajudo.', '',
    `${cfg.corretor} | Corretor | CRECI ${cfg.creci}`, '', tags.join(' ')
  ].join('\n');
}

function escolherFotos(lista) {
  const resto = lista.slice(1);
  const pos = [0.15, 0.5, 0.85].map(p => Math.min(resto.length - 1, Math.round(p * (resto.length - 1))));
  const sel = [...new Set(pos)].map(i => resto[i]);
  for (const f of resto) { if (sel.length >= 3) break; if (!sel.includes(f)) sel.push(f); }
  return [lista[0], ...sel.slice(0, 3)];
}

// ---------------------------------------------------------------- GitHub
async function gh(metodo, rota, corpo) {
  const r = await fetch('https://api.github.com' + rota, {
    method: metodo,
    headers: { Authorization: `Bearer ${cfg.github.token}`, 'User-Agent': 'agente02', Accept: 'application/vnd.github+json', 'Content-Type': 'application/json' },
    body: corpo ? JSON.stringify(corpo) : undefined
  });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(`GitHub ${r.status}: ${j.message || ''}`);
  return j;
}
async function subirGithub(caminho, buf) {
  const { usuario, repositorio } = cfg.github;
  let sha;
  try { sha = (await gh('GET', `/repos/${usuario}/${repositorio}/contents/${caminho}`)).sha; } catch {}
  const j = await gh('PUT', `/repos/${usuario}/${repositorio}/contents/${caminho}`, { message: 'post ' + caminho, content: buf.toString('base64'), sha });
  return j.content.download_url;
}

// ---------------------------------------------------------------- Instagram
// login unificado (token de usuario do sistema, nao vence) usa graph.facebook.com
// login do Instagram (apps antigos) usa graph.instagram.com
const UNIFICADO = () => (cfg.instagram.tipo || 'unificado') !== 'instagram';
const IG = () => `https://graph.${UNIFICADO() ? 'facebook' : 'instagram'}.com/${cfg.instagram.versao || 'v26.0'}`;
const token = () => estado.token || cfg.instagram.token;
async function contaInstagram() {
  if (cfg.instagram.id) return { id: cfg.instagram.id, username: cfg.instagram.usuario || '' };
  if (!UNIFICADO()) { const eu = await ig('GET', '/me', { fields: 'user_id,username' }); return { id: eu.user_id || eu.id, username: eu.username }; }
  const tentativas = [
    async () => (await ig('GET', '/me/accounts', { fields: 'instagram_business_account{id,username}' })).data.map(p => p.instagram_business_account).filter(Boolean),
    async () => { const ne = (await ig('GET', '/me', { fields: 'business' })).business; if (!ne) return []; return (await ig('GET', `/${ne.id}/owned_instagram_accounts`, { fields: 'id,username' })).data; },
    async () => (await ig('GET', '/me/instagram_accounts', { fields: 'id,username' })).data
  ];
  for (const t of tentativas) { try { const l = await t(); if (l && l.length) { const c = l.find(a => a.username === cfg.instagram.usuario) || l[0]; return c; } } catch {} }
  throw new Error('Não achei a conta do Instagram ligada a esse token. Coloque o ID da conta em "instagram.id" no config.json.');
}
async function ig(metodo, rota, params = {}) {
  const corpo = new URLSearchParams({ ...params, access_token: token() });
  const url = metodo === 'GET' ? `${IG()}${rota}?${corpo}` : `${IG()}${rota}`;
  const r = await fetch(url, { method: metodo, body: metodo === 'GET' ? undefined : corpo });
  const j = await r.json().catch(() => ({}));
  if (!r.ok || j.error) throw new Error(`Instagram: ${(j.error && (j.error.error_user_msg || j.error.message)) || r.status}`);
  return j;
}
async function renovarToken() {
  if (UNIFICADO()) return; // token de usuario do sistema nao vence
  const ultima = estado.tokenRenovadoEm ? new Date(estado.tokenRenovadoEm) : null;
  if (ultima && (Date.now() - ultima) < 20 * 864e5) return;
  try {
    const r = await fetch(`https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token=${encodeURIComponent(token())}`);
    const j = await r.json();
    if (j.access_token) { estado.token = j.access_token; estado.tokenRenovadoEm = new Date().toISOString(); salvarJson(ESTADO, estado); log('Acesso do Instagram renovado por mais', Math.round(j.expires_in / 864e2) + ' dias'); }
    else log('Aviso: nao deu pra renovar o acesso agora:', JSON.stringify(j.error || j));
  } catch (e) { log('Aviso: falha ao renovar acesso:', e.message); }
}
async function publicar(urls, texto) {
  const eu = await contaInstagram();
  const id = eu.id;
  const filhos = [];
  for (const u of urls) filhos.push((await ig('POST', `/${id}/media`, { image_url: u, is_carousel_item: 'true' })).id);
  for (const f of filhos) await aguardar(f);
  const carrossel = (await ig('POST', `/${id}/media`, { media_type: 'CAROUSEL', children: filhos.join(','), caption: texto })).id;
  await aguardar(carrossel);
  const pub = await ig('POST', `/${id}/media_publish`, { creation_id: carrossel });
  let link = '';
  try { link = (await ig('GET', `/${pub.id}`, { fields: 'permalink' })).permalink; } catch {}
  return { id: pub.id, link, usuario: eu.username };
}
async function aguardar(container) {
  for (let t = 0; t < 30; t++) {
    const s = await ig('GET', `/${container}`, { fields: 'status_code' });
    if (s.status_code === 'FINISHED') return;
    if (s.status_code === 'ERROR' || s.status_code === 'EXPIRED') throw new Error('Instagram recusou a mídia (' + s.status_code + ')');
    await esperar(3000);
  }
  throw new Error('Instagram demorou demais pra processar');
}

// ---------------------------------------------------------------- principal
async function checar() {
  let ok = true;
  try { const eu = await contaInstagram(); log('Instagram OK, conta @' + (eu.username || eu.id), '(ID ' + eu.id + ')'); } catch (e) { ok = false; log('Instagram com problema:', e.message); }
  try { const r = await gh('GET', `/repos/${cfg.github.usuario}/${cfg.github.repositorio}`); log('GitHub OK, repositório', r.full_name, r.private ? '(PRIVADO, precisa ser público!)' : '(público)'); if (r.private) ok = false; } catch (e) { ok = false; log('GitHub com problema:', e.message); }
  try { const { total } = await buscar(cfg.faixas[0], 1); log('Site da AE OK,', total, 'imóveis na faixa 1'); } catch (e) { ok = false; log('Site da AE com problema:', e.message); }
  process.exit(ok ? 0 : 1);
}

// publica um post que ja foi montado (pelo --teste) e aprovado
async function publicarPronto() {
  let codigo = args[args.indexOf('--publicar') + 1];
  const ja = new Set(postados.map(p => p.codigo));
  if (!codigo || codigo.startsWith('--')) {
    const pastas = fs.readdirSync(POSTS).filter(d => fs.existsSync(path.join(POSTS, d, `${d}-legenda.txt`)) && !ja.has(d))
      .sort((a, b) => fs.statSync(path.join(POSTS, b)).mtimeMs - fs.statSync(path.join(POSTS, a)).mtimeMs);
    codigo = pastas[0];
  }
  if (!codigo) { log('Nenhum post montado esperando aprovação. Rode o testar.bat primeiro.'); return; }
  if (ja.has(codigo)) { log(`O imóvel ${codigo} já foi postado. Nada feito.`); return; }
  const pasta = path.join(POSTS, codigo);
  const nomes = fs.readdirSync(pasta).filter(f => /\.jpg$/i.test(f)).sort();
  const texto = fs.readFileSync(path.join(pasta, `${codigo}-legenda.txt`), 'utf8');
  const dados = lerJson(path.join(pasta, `${codigo}-dados.json`), {});
  log(`Publicando o post aprovado do imóvel ${codigo} (${nomes.length} imagens)`);
  await renovarToken();
  const urls = [];
  if (NUVEM) { for (const n of nomes) urls.push(linkPublico(codigo, n)); }
  else for (const n of nomes) { urls.push(await subirGithub(`posts/${codigo}/${n}`, fs.readFileSync(path.join(pasta, n)))); log('Subiu', n); }
  log('Imagens no ar no GitHub. Mandando pro Instagram...');
  await esperar(5000);
  const res = await publicar(urls, texto);
  postados.push({ codigo, data: new Date().toISOString(), preco: dados.preco, titulo: dados.titulo, post: res.id, link: res.link });
  salvarJson(POSTADOS, postados);
  log(`POSTADO em @${res.usuario || cfg.instagram.usuario}: ${res.link || res.id}`);
  resumo(`## ✅ Postado\n${res.link || res.id}`);
}

async function main() {
  if (CHECAR) return checar();
  if (args.includes('--publicar')) return publicarPronto();
  if (cfg.pedirAprovacao) TESTE = true; // monta e espera o ok do Jackson
  const agora = new Date(new Date().toLocaleString('en-US', { timeZone: 'America/Sao_Paulo' }));
  const hora = agora.getHours();
  if (!NUVEM && !TESTE_MANUAL && !faixaArg && (hora < cfg.horaInicio || hora > cfg.horaFim)) { log(`Fora do horário (${hora}h), nada a fazer.`); return; }
  const montados = fs.readdirSync(POSTS).filter(d => fs.statSync(path.join(POSTS, d)).isDirectory());
  const n = faixaArg || (NUVEM ? (montados.length % cfg.faixas.length) + 1
    : ((hora - cfg.horaInicio) % cfg.faixas.length + cfg.faixas.length) % cfg.faixas.length + 1);
  const faixa = cfg.faixas[n - 1];
  log(`Rodando faixa ${n}: ${faixa.quartos} quarto(s), ${real(faixa.min)} a ${real(faixa.max)}${TESTE ? ' (TESTE, sem postar)' : ''}`);

  const ja = new Set([...postados.map(p => p.codigo), ...(NUVEM ? montados : [])]);
  let escolhido = null;
  for (let pagina = 1; pagina <= (cfg.paginasMax || 15) && !escolhido; pagina++) {
    const { lista, total } = await buscar(faixa, pagina);
    if (pagina === 1) log(`Encontrados ${total} imóveis nessa faixa`);
    if (!lista.length) break;
    for (const item of lista) {
      if (ja.has(item.codigo)) continue;
      try {
        const im = await lerImovel(item);
        const motivo = !(im.preco >= faixa.min && im.preco <= faixa.max) ? 'preço fora da faixa'
          : im.quartos !== faixa.quartos ? 'quartos diferentes' : im.fotos.length < 4 ? 'poucas fotos' : !im.bairro ? 'sem bairro' : '';
        if (motivo) { ja.add(item.codigo); continue; }
        escolhido = im; break;
      } catch (e) { log('Pulei', item.codigo, e.message); }
    }
  }
  if (!escolhido) { log('Nenhum imóvel novo nessa faixa. Nada postado.'); return; }
  const im = escolhido;
  log(`Escolhido ${im.codigo}: ${im.titulo} | ${real(im.preco)} | ${im.fotos.length} fotos`);

  const pasta = path.join(POSTS, im.codigo); fs.mkdirSync(pasta, { recursive: true });
  // a foto da entrada/fachada sempre vai primeiro (capa)
  const cache = new Map();
  const baixar = async u => { if (!cache.has(u)) cache.set(u, await pegar(u, 'buffer')); return cache.get(u); };
  const ordem = await fachadaPrimeiro(im.fotos, baixar);
  if (ordem[0] !== im.fotos[0]) log('Fachada encontrada na foto', im.fotos.indexOf(ordem[0]) + 1, 'e colocada como capa');
  const sel = escolherFotos(ordem);
  const bufs = [];
  for (const u of sel) bufs.push(await baixar(u));
  const imagens = [(cfg.estiloCapa || 'seta') === 'seta' ? await capaSeta({ foto: bufs[0] }) : await capa({
    foto: bufs[0], categoria: `${im.tipo} · ${plural(im.quartos, 'quarto', 'quartos')}`,
    nome: im.condo || im.bairro, bairro: im.condo ? im.bairro : `${im.cidade} · SP`, cidade: im.condo ? `${im.cidade} · SP` : '',
    stats: [
      { v: im.area ? `${im.area} m²` : '-', l: /priv/.test(im.areaTipo) ? 'Área privativa' : /terreno/.test(im.areaTipo) ? 'Terreno' : 'Área total' },
      { v: `${im.quartos}`, l: im.suites ? `Dorm. · ${plural(im.suites, 'suíte', 'suítes')}` : (im.quartos === 1 ? 'Dormitório' : 'Dormitórios') },
      { v: im.vagas || '-', l: im.vagas === 1 ? 'Vaga' : 'Vagas' }
    ],
    preco: real(im.preco), precoObs: im.condominio > 0 ? `Condomínio ${real(im.condominio)}` : '',
    corretor: cfg.corretor, creci: cfg.creci
  })];
  for (const b of bufs.slice(1)) imagens.push(await foto(b));
  const nomes = imagens.map((_, i) => `${im.codigo}-${i + 1}${i === 0 ? '-capa' : ''}.jpg`);
  imagens.forEach((b, i) => fs.writeFileSync(path.join(pasta, nomes[i]), b));
  const texto = legenda(im);
  fs.writeFileSync(path.join(pasta, `${im.codigo}-legenda.txt`), texto);
  salvarJson(path.join(pasta, `${im.codigo}-dados.json`), { ...im, descricao: undefined, fotosUsadas: sel });
  log('Imagens e legenda salvas em', pasta);

  saida('codigo', im.codigo);
  resumo([`## 🏠 ${im.titulo}`, `**${real(im.preco)}** · código ${im.codigo} · [ver no site da AE](${im.url})`, '',
    nomes.map(nm => `<img src="${linkPublico(im.codigo, nm)}" width="220">`).join(' '), '',
    '### Legenda', '```', texto, '```', '', 'Pra postar, aprove o job **publicar**. Pra descartar, rejeite.'].join('\n'));
  if (TESTE) { log(`Post do imóvel ${im.codigo} MONTADO e esperando aprovação. Nada foi postado. Pra publicar: publicar.bat`); return; }

  await renovarToken();
  const urls = [];
  for (let i = 0; i < imagens.length; i++) urls.push(await subirGithub(`posts/${im.codigo}/${nomes[i]}`, imagens[i]));
  log('Imagens no ar no GitHub');
  await esperar(5000);
  const res = await publicar(urls, texto);
  postados.push({ codigo: im.codigo, data: new Date().toISOString(), faixa: n, preco: im.preco, titulo: im.titulo, post: res.id, link: res.link });
  salvarJson(POSTADOS, postados);
  log(`POSTADO em @${res.usuario}: ${res.link || res.id}`);
}

main().catch(e => { log('ERRO:', e.message + (e.cause ? ' | ' + (e.cause.code || e.cause.message) : '')); process.exit(1); });
