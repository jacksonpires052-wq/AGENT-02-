// Agente 06 - Analista de Resultados
// Puxa os números do @corretor.jacksonpires pela API oficial, guarda o histórico
// e escreve o relatório do dia com sugestões de ajuste.
// Uso: node metricas.js            (roda tudo)
//      node metricas.js --dias 14  (quantos dias de posts reler, padrão 14)

const fs = require('fs');
const path = require('path');

const DIR = __dirname;
const PASTA = path.join(DIR, 'dados', 'metricas');
fs.mkdirSync(PASTA, { recursive: true });
const ler = (f, p) => { try { return JSON.parse(fs.readFileSync(f, 'utf8')); } catch { return p; } };
const salvar = (f, o) => fs.writeFileSync(f, JSON.stringify(o, null, 2));

const cfg = ler(path.join(DIR, 'config.json'), null) || ler(path.join(DIR, 'config.nuvem.json'), {});
const IGC = cfg.instagram || {};
const TOKEN = process.env.IG_TOKEN || IGC.token;
const UNIF = (IGC.tipo || 'unificado') !== 'instagram';
const BASE = `https://graph.${UNIF ? 'facebook' : 'instagram'}.com/${IGC.versao || 'v26.0'}`;
const CONTA = IGC.id;
const argDias = process.argv.indexOf('--dias');
const DIAS_RELER = argDias > 0 ? Number(process.argv[argDias + 1]) : 14;

const FAIXAS = (cfg.faixas || []).map((f, i) => ({ n: i + 1, ...f }));
const postados = ler(path.join(DIR, 'dados', 'postados.json'), []);
const porPost = Object.fromEntries(postados.map(p => [String(p.post), p]));

// ---------------------------------------------------------------- datas em Brasília
const fmt = new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Sao_Paulo', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', hour12: false });
function brt(d) {
  const p = Object.fromEntries(fmt.formatToParts(new Date(d)).map(x => [x.type, x.value]));
  return { dia: `${p.year}-${p.month}-${p.day}`, hora: Number(p.hour) % 24 };
}
const HOJE = brt(Date.now()).dia;
const somaDias = (dia, n) => { const d = new Date(dia + 'T12:00:00-03:00'); d.setUTCDate(d.getUTCDate() + n); return brt(d).dia; };
const ONTEM = somaDias(HOJE, -1);

// ---------------------------------------------------------------- API
async function api(rota, params = {}) {
  const q = new URLSearchParams({ ...params, access_token: TOKEN });
  const r = await fetch(`${BASE}${rota}?${q}`);
  const j = await r.json().catch(() => ({}));
  if (!r.ok || j.error) throw new Error((j.error && j.error.message) || `HTTP ${r.status}`);
  return j;
}
// Pede várias métricas de uma vez; se a API recusar, tenta uma por uma e pula as que não existem.
let ERRO_INSIGHTS = null;
async function insights(rota, metricas, extra = {}) {
  const ler1 = j => Object.fromEntries((j.data || []).map(m => [m.name, m.total_value ? m.total_value.value : (m.values && m.values.length ? m.values[m.values.length - 1].value : null)]));
  try { return ler1(await api(rota, { metric: metricas.join(','), ...extra })); }
  catch {
    const out = {};
    for (const m of metricas) { try { Object.assign(out, ler1(await api(rota, { metric: m, ...extra }))); } catch (e) { ERRO_INSIGHTS = ERRO_INSIGHTS || e.message; } }
    return out;
  }
}

// ---------------------------------------------------------------- coleta
async function coletar() {
  const conta = await api(`/${CONTA}`, { fields: 'username,followers_count,media_count' });

  // posts dos últimos DIAS_RELER dias
  const limite = Date.now() - DIAS_RELER * 864e5;
  let midias = [], url = `/${CONTA}/media`, params = { fields: 'id,media_type,media_product_type,timestamp,permalink,caption', limit: 50 };
  for (let pag = 0; pag < 10; pag++) {
    const j = await api(url, params);
    midias.push(...(j.data || []));
    const ultimo = j.data && j.data[j.data.length - 1];
    if (!j.paging || !j.paging.cursors || !j.paging.next || !ultimo || new Date(ultimo.timestamp) < limite) break;
    params = { ...params, after: j.paging.cursors.after };
  }
  midias = midias.filter(m => new Date(m.timestamp) >= limite);

  const banco = ler(path.join(PASTA, 'midias.json'), {});
  for (const m of midias) {
    const reel = m.media_product_type === 'REELS';
    const lista = ['reach', 'views', 'likes', 'comments', 'shares', 'saved', 'total_interactions'];
    if (reel) lista.push('ig_reels_avg_watch_time', 'ig_reels_video_view_total_time');
    const num = await insights(`/${m.id}/insights`, lista);
    const p = porPost[m.id];
    const { dia, hora } = brt(m.timestamp);
    const faixa = p ? (FAIXAS.find(f => p.preco >= f.min && p.preco <= f.max) || {}).n || null : null;
    banco[m.id] = {
      id: m.id, dia, hora, quando: m.timestamp, tipo: reel ? 'reels' : (m.media_type === 'CAROUSEL_ALBUM' ? 'carrossel' : 'post'),
      origem: p ? 'Agente 02' : 'outros', codigo: p ? p.codigo : null, faixa, preco: p ? p.preco : null,
      titulo: p ? p.titulo : (m.caption || '').split('\n')[0].slice(0, 80), link: m.permalink,
      ...num, atualizado: new Date().toISOString()
    };
  }
  salvar(path.join(PASTA, 'midias.json'), banco);

  // conta: ontem e hoje (dia fechado de ontem é o que vale)
  const dias = ler(path.join(PASTA, 'dias.json'), {});
  for (const dia of [ONTEM, HOJE]) {
    const since = Math.floor(new Date(dia + 'T00:00:00-03:00') / 1000);
    const until = Math.min(since + 86400, Math.floor(Date.now() / 1000));
    if (until <= since) continue;
    const num = await insights(`/${CONTA}/insights`, ['reach', 'views', 'accounts_engaged', 'total_interactions', 'profile_links_taps'],
      { period: 'day', metric_type: 'total_value', since, until });
    try {
      const j = await api(`/${CONTA}/insights`, { metric: 'follows_and_unfollows', period: 'day', metric_type: 'total_value', breakdown: 'follow_type', since, until });
      const res = (((j.data || [])[0] || {}).total_value || {}).breakdowns;
      const linhas = (res && res[0] && res[0].results) || [];
      const fu = { follows: 0, unfollows: 0 };
      for (const r of linhas) { const t = String((r.dimension_values || [])[0] || ''); if (/NON|UNFOLLOW/i.test(t)) fu.unfollows += n0(r.value); else fu.follows += n0(r.value); }
      if (linhas.length) num.follows_and_unfollows = fu;
    } catch {}
    dias[dia] = { ...(dias[dia] || {}), ...num, ...(dia === HOJE ? { seguidores: conta.followers_count } : {}) };
  }
  salvar(path.join(PASTA, 'dias.json'), dias);
  return { conta, banco, dias };
}

// ---------------------------------------------------------------- análise
const media = a => a.length ? a.reduce((s, x) => s + x, 0) / a.length : 0;
const n0 = x => Number(x) || 0;
const pct = (a, b) => b ? Math.round((a / b - 1) * 100) : 0;
const int = x => Math.round(n0(x)).toLocaleString('pt-BR');

function analisar({ conta, banco, dias }) {
  const todos = Object.values(banco);
  const reels = todos.filter(m => m.tipo === 'reels');
  const doDia = d => reels.filter(m => m.dia === d);
  const ontem = doDia(ONTEM);
  const antes = reels.filter(m => m.dia < ONTEM && m.dia >= somaDias(ONTEM, -7));
  const semana = reels.filter(m => m.dia <= ONTEM && m.dia >= somaDias(ONTEM, -6));

  const alcOntem = media(ontem.map(m => n0(m.reach)));
  const alcAntes = media(antes.map(m => n0(m.reach)));
  const envios = l => { const r = l.reduce((s, m) => s + n0(m.reach), 0); return r ? l.reduce((s, m) => s + n0(m.shares), 0) / r * 1000 : 0; };
  const salvos = l => { const r = l.reduce((s, m) => s + n0(m.reach), 0); return r ? l.reduce((s, m) => s + n0(m.saved), 0) / r * 1000 : 0; };

  // histórico diário pra regra dos 3 dias
  const hist = ler(path.join(PASTA, 'historico.json'), {});
  hist[ONTEM] = { reels: ontem.length, alcanceMedio: Math.round(alcOntem), referencia: Math.round(alcAntes), enviosMil: +envios(ontem).toFixed(1) };
  salvar(path.join(PASTA, 'historico.json'), hist);

  const d = dias[ONTEM] || {}, dh = dias[HOJE] || {};
  const ganho = (dh.seguidores && d.seguidores) ? dh.seguidores - d.seguidores : null;

  // por faixa e por horário (7 dias)
  const grupo = (lista, chave) => {
    const g = {};
    for (const m of lista) { const k = m[chave]; if (k == null) continue; (g[k] = g[k] || []).push(m); }
    return Object.entries(g).map(([k, l]) => ({ k, qtd: l.length, alcance: media(l.map(m => n0(m.reach))), envios: envios(l) }));
  };
  const faixas = grupo(semana, 'faixa').sort((a, b) => a.k - b.k);
  const horas = grupo(semana, 'hora').sort((a, b) => b.alcance - a.alcance);

  // sugestões (o agente só sugere, quem decide é o Jackson)
  const sug = [];
  const semDados = ERRO_INSIGHTS && !reels.some(m => n0(m.reach) > 0);
  if (semDados) sug.push(`SEM DADOS: a API não liberou os números (${ERRO_INSIGHTS}). Falta a permissão de insights (instagram_manage_insights) no token. Nenhuma sugestão até isso ser resolvido.`);
  const ultimos3 = [0, 1, 2].map(i => hist[somaDias(ONTEM, -i)]).filter(Boolean);
  const caindo = ultimos3.length === 3 && ultimos3.every(h => h.referencia && h.alcanceMedio < h.referencia * 0.7);
  if (semDados) {}
  else if (caindo) sug.push('VERMELHO: há 3 dias o alcance por Reels está mais de 30% abaixo da média. O volume pode estar cansando o público. Sugestão: baixar de 25 pra 18 Reels por dia por uma semana e comparar.');
  else if (ontem.length && alcAntes && alcOntem >= alcAntes * 0.9) sug.push('VERDE: o alcance por Reels se segurou com o volume atual. Pode manter.');
  else if (ontem.length && alcAntes) sug.push(`AMARELO: alcance por Reels ${pct(alcOntem, alcAntes)}% em relação à semana. Ainda não é tendência, segue medindo.`);
  const mediaFaixas = media(faixas.map(f => f.alcance));
  if (!semDados) for (const f of faixas) if (f.qtd >= 5 && mediaFaixas && f.alcance < mediaFaixas * 0.6) sug.push(`A faixa ${f.k} está com alcance bem abaixo das outras. Sugestão: tirar 1 ou 2 Reels dela e passar pra faixa que mais rende.`);
  const fracas = horas.filter(h => h.qtd >= 3).slice(-2);
  if (!semDados && horas.length >= 6 && fracas.length) sug.push(`Horários mais fracos da semana: ${fracas.map(h => h.k + 'h').join(' e ')}. Sugestão: mover esses Reels pra ${horas.slice(0, 2).map(h => h.k + 'h').join(' ou ')}.`);
  const fu = d.follows_and_unfollows;
  if (fu && typeof fu === 'object' && fu.unfollows > fu.follows) sug.push('Mais gente deixou de seguir do que começou a seguir ontem. Ficar de olho: é o primeiro sinal de excesso.');
  if (!ontem.length) sug.push('Nenhum Reels medido ontem. Conferir se o Agente 02 rodou.');

  // ---------------------------------------------------------------- relatório
  const top = [...ontem].sort((a, b) => n0(b.reach) - n0(a.reach));
  const linha = m => `- ${m.hora}h · ${m.titulo || m.codigo || m.id} · alcance ${int(m.reach)} · views ${int(m.views)} · envios ${int(m.shares)} · salvos ${int(m.saved)}${m.ig_reels_avg_watch_time ? ` · assistiu ${(m.ig_reels_avg_watch_time / 1000).toFixed(1)} s` : ''} · ${m.link}`;
  const L = [];
  L.push(`# Relatório do Agente 06 · ${ONTEM.split('-').reverse().join('/')}`, '');
  L.push('## Conta');
  L.push(`- Seguidores agora: ${int(conta.followers_count)}${ganho != null ? ` (${ganho >= 0 ? '+' : ''}${ganho} no dia)` : ''}`);
  L.push(`- Alcance do perfil: ${int(d.reach)} · views: ${int(d.views)} · contas que interagiram: ${int(d.accounts_engaged)}`);
  L.push(`- Cliques no link da bio: ${int(d.profile_links_taps)}`);
  if (fu && typeof fu === 'object') L.push(`- Seguiram: ${int(fu.follows)} · deixaram de seguir: ${int(fu.unfollows)}`);
  L.push('', '## Reels de ontem');
  L.push(`- Publicados: ${ontem.length}`);
  L.push(`- Alcance médio por Reels: ${int(alcOntem)} (semana anterior: ${int(alcAntes)}, ${pct(alcOntem, alcAntes) >= 0 ? '+' : ''}${pct(alcOntem, alcAntes)}%)`);
  L.push(`- Envios a cada mil alcançados: ${envios(ontem).toFixed(1)} · salvos a cada mil: ${salvos(ontem).toFixed(1)}`);
  if (top.length) { L.push('', '**Os 3 melhores**', ...top.slice(0, 3).map(linha)); }
  if (top.length > 3) { L.push('', '**Os 3 mais fracos**', ...top.slice(-3).map(linha)); }
  if (faixas.length) { L.push('', '## Por faixa (7 dias)'); for (const f of faixas) { const fx = FAIXAS[f.k - 1] || {}; L.push(`- Faixa ${f.k} (${fx.quartos || '?'} quartos): ${f.qtd} Reels · alcance médio ${int(f.alcance)} · envios/mil ${f.envios.toFixed(1)}`); } }
  if (horas.length) { L.push('', '## Melhores horários (7 dias)'); for (const h of horas.slice(0, 5)) L.push(`- ${h.k}h: alcance médio ${int(h.alcance)} (${h.qtd} Reels)`); }
  L.push('', '## Sugestões de ajuste', ...(sug.length ? sug.map(s => '- ' + s) : ['- Nada a ajustar por enquanto.']));
  L.push('', '_O Agente 06 só sugere. Ajuste só entra com o ok do Jackson._');
  const texto = L.join('\n');
  fs.writeFileSync(path.join(PASTA, 'relatorio.md'), texto);
  fs.writeFileSync(path.join(PASTA, `relatorio-${ONTEM}.md`), texto);
  console.log(texto);
}

(async () => {
  if (!TOKEN) throw new Error('Falta o IG_TOKEN.');
  if (!CONTA) throw new Error('Falta o instagram.id no config.');
  analisar(await coletar());
  if (ERRO_INSIGHTS) console.error('Aviso da API de insights:', ERRO_INSIGHTS);
})().catch(e => { console.error('Erro no Agente 06:', e.message); process.exit(1); });
