# Agente 03: stories diários (desde 24/11/2026: 5 notícias + 5 lançamentos, intercalados)

Pedido do Jackson em 13/11: as notícias do mercado imobiliário saem **apenas como story**, **sem a foto dele**, com nome e CRECI 323400. Os Reels de notícia foram desligados. Este doc vale no lugar das regras antigas de agente-03.md, que ficam como histórico.

Pedido de 23/11: metade dos stories passa a ser lançamento de Sorocaba, intercalado com as notícias.

## Horários (Brasília)
- Notícias (números ímpares 01, 03, 05, 07, 09): 07h07, 10h07, 12h37, 16h07, 19h37.
- Lançamentos (números pares 02, 04, 06, 08, 10, pastas `stories/AAAA-MM-DD-NN-emp-<slug>`): 08h37, 11h37, 14h07, 18h07, 21h07.

## Stories de lançamento (desde 23/11)
- Base: `lancamentos/dados.json` com 14 lançamentos até R$ 350 mil achados no apto.vc em 23/11 (Reserva Painá e São Conrado com preço do site do Jackson). Campo "usado" guarda o dia em que saiu. Fotos oficiais do condomínio em `lancamentos/fotos/<slug>.jpg`.
- As fotos vieram pelo navegador embutido do app no computador do Jackson: a página do apto.vc desenha a foto num canvas e devolve em base64 (o container não acessa api.apto.vc e o Chrome bloqueia download múltiplo).
- Visual: `agente03/story_empreendimento_motion.py` (MP4 8 s, sem áudio, e story.jpg). Foto em tela cheia com zoom lento, nome, bairro e zona, bloco LOCALIZAÇÃO (rua, bairro, cidade e até 3 "Perto de", só quando o apto.vc informa), chips de dormitórios e metragem, linha neon verde que se desenha em cima do preço "a partir de", botão "Simule comigo: me chama no direct", nota de valores de referência, nome e CRECI.
- O Jackson pediu para TIRAR a renda (23/11). Parcela também não entra sem fonte. Zona e pontos próximos só com fonte, nunca chutados.
- Preços diferentes entre apto.vc e o site do Jackson: Villa Creta (311 x 266 mil), Reserva Lobato (316 x 308 mil), Morada Boa Vista (302 x 290 mil). Usado o apto.vc.
- Ritmo: 2 em 23/11, 5 em 24/11, 5 em 25/11 e os 2 últimos em 26/11. Antes de acabar, perguntar ao Jackson se recomeça a lista ou busca lançamentos novos.

## Como funciona
- **Produção:** às 5h41, um lembrete nesta conversa (send_later) faz os stories do dia e sobe tudo em `stories/AAAA-MM-DD-NN-assunto/` (story.mp4, story.jpg, noticia.json e o arquivo vazio `fila`). Cada rodada já agenda a do dia seguinte. A produção roda aqui porque as tarefas agendadas novas não conseguiam gravar no GitHub (erro 403 desde 11/11).
- **Disparo:** o relógio (`relogio.yml`) dispara o workflow `stories.yml` em cada horário. O `agente03/stories.js` publica o story mais antigo da fila (ordem do nome da pasta) pela API do Instagram: tenta o story.mp4 (vídeo) e, se o Instagram recusar, publica o story.jpg. Grava `publicado.json` (com "tipo": vídeo ou imagem) e loga "STORY POSTADO: pasta | link | tipo". Para encaixar um story no meio do dia, use um nome que ordene entre os outros (ex.: `2026-11-23-07b-...`). Para tirar da fila, apague o arquivo `fila`.
- **Fiscal:** 10 minutos antes de cada horário, o relógio confere se tem story pronto na fila. Se não tiver, abre um aviso "Fiscal ..." no GitHub.
- **Conferência:** 4 minutos depois de cada horário, um lembrete nesta conversa confere se o story saiu, corrige se precisar e manda o link pro Jackson aqui. Às 21h11 sai o placar do dia. Se o stories.yml não rodou no horário, a conferência dispara na mão (`gh workflow run stories.yml --ref main`) e religa o relógio.
- Cópia deste doc fica em `docs-projeto/agente-03-stories.md` no repositório: edite lá com sed/python e suba com project_write (local_path), sem redigitar tudo.

## Visual das notícias (desde 20/11): animadas, sem música
Pedidos do Jackson em 20/11: "intercala com layout mais animado e descontraído", "coloque motions" e "deixe sem música". Desde 24/11 as notícias ficam nos números ímpares, então saem no layout **Boletim**.
- **Leve** (`agente03/story_leve.py`) segue disponível: fundo colorido, cartão creme com borda preta, número em destaque inclinado, bloco "E PARA VOCÊ?", fontes Bricolage Grotesque e DM Sans (em `agente03/fontes`).
- Animados com `agente03/story_motion.py noticia.json pasta boletim|leve`: MP4 de 8 s, 30 fps, sem áudio (a trilha só volta com MUSICA=1). Cada um leva uns 30 a 50 s. Rodar no máximo 2 em paralelo e em background: em 22/11, com 5 em paralelo e limite de tempo, 4 foram cortados no meio e precisaram ser refeitos. Sempre conferir se cada pasta tem story.mp4 de 8 s e story.jpg.

## Modelo Boletim (agente03/story.py, desde 14/11 às 17h37)
Aprovado pelo Jackson em 14/11 ("Ficou melhor. Manda nesse formato a partir de agora"). Pedido: layout moderno e sério, de notícia, mostrando organização.
- Fundo azul quase preto com grade sutil, só branco e um dourado (#E0B252) de destaque. Sem desenho.
- Cabeçalho "BOLETIM.IMOBILIÁRIO" e a data (ex.: 14 NOV 2026), linha branca embaixo.
- "NOTÍCIA 04 DE 10" com barrinha de 10 segmentos (o número vem da pasta AAAA-MM-DD-NN).
- Editoria em dourado (ALUGUEL, LANÇAMENTOS, CONSTRUÇÃO, MCMV...). Sai de palavras do título e da legenda; se precisar, forçar com o campo "categoria" no noticia.json.
- Número grande, legenda com filete dourado, título em serifa (Lora), bloco "O QUE ISSO MUDA PARA VOCÊ" com o texto.
- Rodapé: FONTE, depois "Jackson Pires / Corretor de imóveis | CRECI 323400" e selo dourado "SOROCABA E REGIÃO".
- Tudo fica fora das áreas que o Instagram cobre. O script sai com erro 2 se o texto não couber.

## Modelos interativos (prontos, esperando o ok do Jackson)
`agente03/story_modelos.py`: Pergunta (A, B, C) e Resposta, Mito ou Verdade (pergunta e resposta), Conta Rápida e Fala Comigo (palavra RENDA no direct). Proposta: 2 por dia postados pelo Jackson com música em alta séria (sem piada). Ainda sem confirmação.

## Regras de texto
- Norma culta, "juros" sempre no plural, sem travessão.
- Só fato com número e fonte, de preferência das últimas 72 h. Conferir o ano do dado (muita página traz números de 2025).
- Nunca repetir notícia já usada (veja stories/*/noticia.json).
- Nunca escrever comparação, superlativo ou conselho que a fonte não sustenta. Exemplo: com a Selic alta, a poupança rende uns 8% ao ano, então "aluguel rende mais que a poupança" estaria errado.
- Na fonte, citar só o veículo onde a notícia foi realmente lida.
- Quando der, incluir 1 notícia de Sorocaba e região. A pesquisa CRECISP Sorocaba mais nova achada (em 18/11) é a de junho de 2026 (vendas +7,42%, locações +1,97%), já usada em 18/11. Procurar a de julho em diante.
- No máximo 2 notícias de resultado de construtora, 3 da mesma pesquisa e 3 de aluguel no mesmo dia.
- Cuidado com "3º maior mercado do país": Curitiba (Ademi-PR) e Fortaleza (Sinduscon-CE) usam o título com métricas diferentes. Só repetir citando quem disse.

## Tarefas antigas pausadas em 13/11
"Agente de Notícias" (Reels, 5 rodadas), "Fiscal dos agentes (antes dos picos)" e "Conferência do Agente de Notícias". As três seguiam a agenda antiga de Reels e falhavam no push.

## Histórico
- 13/11/2026: formato criado. Os 10 stories do dia entraram na fila às 8h50. Como os horários das 7h07 e 8h37 já tinham passado, os 2 primeiros foram postados às 8h50: desconto médio de 13% (FipeZap) https://www.instagram.com/stories/corretor.jacksonpires/4029472613814756259 e bancos subindo os juros (Bradesco 15% + TR) https://www.instagram.com/stories/corretor.jacksonpires/4029472996418484343. Os outros 8 saíram de 10h07 a 21h07: poupança -R$ 7,58 bi, MCMV 75,6% dos lançamentos em SP, distratos +65,5%, Cury R$ 42 mi de provisão, MCMV 2,7 mi de moradias, temporada no Rio +98%, interior paulista +81% e crédito +25% em 2026. Placar: 10 de 10, nenhuma falha.
- 14/11/2026, 5h43: os 10 stories do dia entraram na fila. Temas:
  - MCMV é 7 em 10 vendas em SP (Secovi)
  - estoque de MCMV em SP +65% (Secovi)
  - imóvel sobe 5,61% no ano, acima da inflação (FipeZap)
  - aluguel +8% no ano (FipeZap)
  - aluguel rende 6,13% ao ano (FipeZap)
  - custo da construção +6,75% em 12 meses (INCC-M/FGV)
  - 355 mil imóveis novos, 9,5 meses de estoque (CBIC)
  - Recife +83% em lançamentos (Brain/Ademi-PE)
  - 44,6% das cidades sem Plano Diretor (IBGE)
  - Campo Grande lidera a alta do aluguel com 16,91% (FipeZap)
  Antes de postar, 3 textos foram corrigidos por afirmarem mais do que a fonte dizia. De 7h07 a 16h07 saíram 7 de 7 no visual antigo. Às 17h37 o Jackson aprovou o layout Boletim, e os stories 08, 09 e 10 (18h07, 19h37 e 21h07) foram refeitos nele. Placar: 10 de 10, nenhuma falha.
- 15/11/2026, 5h44: os 10 stories do dia entraram na fila, todos no layout Boletim. Temas:
  - Selic mantida em 13,75% (Copom, 04/11)
  - IGP-M de 5,24% em 12 meses, reajuste do aluguel de novembro (FGV)
  - FGTS aprova R$ 144,5 bi para habitação em 2027 (Conselho Curador)
  - imóvel financiado +12,58% em 12 meses, IPCA 4,58% (IGMI-R/Abecip)
  - m² na planta em Sorocaba: R$ 7.539 (apto.vc)
  - Vitória lidera a valorização em 2026 com 12,27% (FipeZap)
  - verba do MCMV para a classe média cai para R$ 10 bi a partir de 2028 (Conselho Curador do FGTS)
  - reforma tributária: corte de R$ 240 mil de aluguel por ano para IBS e CBS (LC 214/2025)
  - hipoteca de 30 anos nos EUA em 7,18% (Freddie Mac)
  - imóvel novo na China -2,8% em 12 meses (NBS)
  Placar: 10 de 10, nenhuma falha.
- 16/11/2026, 5h44: os 10 stories do dia entraram na fila. Temas:
  - Focus: mercado espera Selic de 13,75% no fim de 2026 (antes 13,50%)
  - MRV bate recorde de vendas: R$ 3,04 bi no 3T26 (+29,6%)
  - vendas da Cyrela caem 14% no 3T26
  - MCMV é 58% dos lançamentos e vendas no interior e litoral de SP (Secovi, 1º semestre)
  - locações no ABC +40,16% em setembro (CRECISP)
  - construção abre 9.468 vagas em setembro (Novo Caged)
  - lucro da Cury +30,5% no 3T26 (R$ 369,6 mi)
  - inadimplência das famílias em 5,8% em julho, a maior desde 2011 (BC)
  - casas em Portugal +16,5% em 12 meses (INE, 2º tri)
  - Caixa Seguridade tem lucro recorde de R$ 1,18 bi no 3T26
  Placar: 10 de 10. O das 14h07 saiu 5 min atrasado (relógio travou com execução em "queued" no GitHub; postado na mão às 14h12 e relógio religado). Os outros 9 no horário.
- 17/11/2026, 5h43: os 10 stories do dia entraram na fila. Temas:
  - só 9% compraram imóvel no 3º tri; intenção de compra cai para 35% (Raio-X FipeZap)
  - m² médio anunciado no Brasil: R$ 10.065 em outubro (FipeZap)
  - em SP, imóvel sobe 3% no ano até outubro, abaixo da inflação (FipeZap)
  - 73% acham imóvel caro, contra 67% um ano antes (Raio-X FipeZap)
  - aluguel comercial +11,18% em 12 meses (FipeZap Comercial)
  - valorização esperada cai de 2,5% para 1,9% (Raio-X FipeZap)
  - só 16% das obras usam sistema industrializado (FGV)
  - MCMV Rural: 716 moradias autorizadas (Portaria MCID 1.449)
  - EUA: venda de casas usadas a 3,75 mi/ano, a menor desde 2010 (NAR, outubro)
  - EUA: compradores de primeiro imóvel são 29% das vendas (NAR, outubro)
  Placar: 10 de 10, todos no horário.
- 18/11/2026, 5h43: os 10 stories do dia entraram na fila. Temas:
  - Caixa estuda subir os juros; tem 68,2% do crédito imobiliário (coletiva de 13/11)
  - condomínio em Salvador +6,6%, Nazaré de R$ 409 para R$ 646 (Loft)
  - IVAR: aluguel negociado +4,47% em 12 meses, -0,01% em outubro (FGV)
  - periferia de SP: Parelheiros +26,2%; preços sobem em 95 de 114 bairros (Loft, 3T26)
  - Sorocaba e região: vendas de usados +7,42% em junho (CRECISP)
  - inadimplência no aluguel cai para 5,84% em outubro (Loft)
  - carteira imobiliária da Caixa: R$ 1,043 trilhão em setembro, +15,5%
  - aluguel em BH +13,29% em 12 meses, m² R$ 48,27 (FipeZap)
  - Reino Unido: casas +0,5% em 12 meses, menor ritmo desde jan/2024 (Nationwide)
  - Austrália: casas -1,2% em outubro, 6,7% abaixo do recorde de março (Cotality)
  Placar: 10 de 10, todos no horário, nenhuma falha.
- 19/11/2026, 5h44: os 10 stories do dia entraram na fila. Temas:
  - BH: vendas de apartamentos -1,5% e m² +12,4% de jan a set (Secovi-MG, via Diário do Comércio)
  - aluguel em SP +5,53% de jan a out, IPCA 4,10% (FipeZap, via Portas)
  - 56% dos executivos vão priorizar reduzir dívidas em 2027 (GRI Institute, via Portas)
  - incorporadoras da bolsa já têm mais de 50% do VGV residencial de SP, antes uns 30% (via Portas)
  - Black November no Rio: Cury com desconto de até R$ 80 mil (Portas)
  - Fortaleza e região: R$ 7,08 bi em vendas até setembro, 13.172 unidades (Sinduscon-CE, via Portas)
  - Eztec financia até 50% das próprias vendas, antes 20% a 30% (via Portas)
  - EUA: vendas pendentes -4,7% em outubro, -16,7% em 12 meses (NAR, via Diário do Grande ABC)
  - Lisboa: vendas de casas -12,9% de jan a set (Confidencial Imobiliário, via Renascença)
  - EUA: preço mediano -0,9% em 12 meses (Redfin, via Mortgage Professional America)
  Sem pesquisa nova de Sorocaba encontrada nesse dia. Placar: 10 de 10, todos no horário, nenhuma falha.
- 20/11/2026, 5h42: os 10 stories do dia entraram na fila. Temas:
  - MCMV é 77% das vendas de imóveis novos em SP em setembro, 8.266 unidades (Secovi-SP, via Portas)
  - Faixa 3 do MCMV: juros até 8,16%, renda até R$ 9,6 mil, imóvel até R$ 400 mil; Faixa 4 até R$ 13 mil e R$ 600 mil (via Portas)
  - Rio: vendas de novos +18,9% no 3T, 5.522 unidades, m² R$ 13.340 (Ademi-RJ/Brain, via Diário do Rio)
  - 60,4% das empresas da construção com dificuldade de contratar; CBIC projeta +1,2% em 2026 (via Portas)
  - Even reduz de 800 para 300 corretores e foca no luxo (Portas)
  - loja na Paulista: R$ 516,20/m² pedido, Oscar Freire R$ 472,60 (Cushman & Wakefield, via Portas)
  - Nordeste tem 5 das 10 cidades com mais demanda no segmento econômico; Fortaleza lidera (IDI/CBIC, via Portas)
  - EUA: hipoteca de 30 anos em 7,11%, 4ª semana de queda (Freddie Mac, 12/11)
  - Reino Unido: preço pedido -1,8% em novembro, £ 364.270 (Rightmove, via The Negotiator)
  - Canadá: vendas -10,6% em outubro, 37.827 (CREA, via Investment Executive)
  Sem pesquisa nova de Sorocaba encontrada nesse dia. No meio do dia entraram os layouts intercalados e a animação: 01 a 05 saíram em imagem; 06 a 10 em vídeo animado (sem música), nenhum caiu para imagem. Placar: 10 de 10, todos no horário.
- 21/11/2026, 5h47: os 10 stories do dia entraram na fila, os primeiros feitos já animados e intercalados. Temas:
  - R$ 38 bi em imóveis novos prontos sem comprador, 30.085 unidades (Portas)
  - Baixada Santista: m² de novos R$ 12.560, média do estado R$ 9.875; lidera fora da Grande SP (Portas)
  - EUA: parcela mediana da casa US$ 2.723, menor em quase 2 meses (Redfin, via PR Newswire)
  - Vale do Taquari (RS): 3.585 apartamentos lançados, estoque de 906 para 874 (Sinduscom VT, via Grupo A Hora)
  - EUA: início de obras +2,8% em 12 meses em outubro, puxado por prédios (Census, via Real Estate News)
  - Espanha: +12,2% em 12 meses no 2º tri, 49º trimestre seguido de alta (INE, via thinkSPAIN)
  - vendas de novos +5,4% no 1º semestre; CBIC divulga o 3º tri em 23/11 (CBIC)
  - França: preço das casas -0,8% no 2º tri; Alemanha +0,6% (Eurostat, via Euronews)
  - Holanda: +7,8% no 3º tri mesmo com juros maiores (ING Think)
  - aluguel: Porto Alegre +0,57% e Rio +0,45% no mês (FipeZap, via Portas)
  Antes de subir, 2 textos foram corrigidos (tirado um conselho sem fonte no 01 e ajustado o "mais caro do estado" no 02). Sem pesquisa nova de Sorocaba. Placar: 10 de 10, todos no horário e todos em vídeo.
- 22/11/2026, 5h46: os 10 stories do dia entraram na fila, animados e intercalados. Temas:
  - Curitiba: cerca de 12 mil imóveis vendidos em 12 meses até setembro, R$ 9 bi; 3º maior mercado do país (Ademi-PR, via RIC)
  - Curitiba: 1 imóvel acima de R$ 5 mi vendido a cada 3 dias; compactos 55,4% dos lançamentos no 2º tri (Ademi-PR, via RIC)
  - Grande Recife: R$ 2,25 bi em vendas no 3º tri, unidades -9,8% e valor +12,3%, 4.427 imóveis (Brain/Ademi-PE, via Folha de Pernambuco)
  - Grande Recife: vendas do MCMV +138% no 3º tri, de 616 para 1.463 (Brain/Ademi-PE, via Movimento Econômico)
  - Rio: VGV -6,7% no 3º tri, de R$ 3,811 bi para R$ 3,557 bi; MCMV -17,5% (Ademi-RJ, via Diário do Rio)
  - União Europeia: custo de construir casa nova +0,9% no 3º tri, índice 129,8 (Eurostat, via IndexBox)
  - EUA: mais de 2 vendedores para cada comprador de condomínio; 21% dos anúncios com redução de preço (Redfin, via Mortgage Professional America)
  - EUA: mediana passa de US$ 400 mil; +1,7% em 12 meses em setembro (Cotality)
  - Lisboa: preço +0,1% no 3º tri, menor alta desde 2021; vendas -12,9% (Confidencial Imobiliário, via Dinheiro Vivo)
  - Rio: 413 ruas com imóveis dentro dos novos limites do MCMV (Portas)
  Sem pesquisa nova de Sorocaba. Às 7h saiu o carrossel "Juntos pode dar" (https://www.instagram.com/p/DgCixF-D6Q0/). Placar: 10 de 10, todos no horário e todos em vídeo.
- 23/11/2026, 5h44: os 10 stories do dia entraram na fila, animados e intercalados (renderizados 2 por vez, sem falha). Temas:
  - Fortaleza: R$ 2,04 bi em vendas no 3º tri, 3.543 unidades (+32,2% sobre o 2º tri); Região Metropolitana -2,6% (Sinduscon-CE, via O Povo)
  - Goiânia: 7.219 imóveis vendidos no 1º semestre, +42%; 4º lugar no país (O Hoje)
  - EUA: índice NAHB das construtoras cai para 25 em novembro, o menor desde abril de 2012 (via Real Estate News)
  - 52% querem comprar imóvel, só 11% compraram em 12 meses, 2º tri (Brain, via Band)
  - Fortaleza: m² médio de apartamento R$ 12.402 no 3º tri; 5.393 lançamentos, +2% (Movimento Econômico)
  - 5 capitais do Nordeste: 11.827 imóveis vendidos no 2º tri, +24,4% (CBIC)
  - Pesquisa Nacional de Bens: busca por CPF ou CNPJ em 3,6 mil cartórios de registro de imóveis (ONR, via Agência Brasil)
  - Goiânia: m² R$ 11.681 em junho, +7,4% no ano; Marista perto de R$ 14 mil (Ademi-GO, via Jornal Opção)
  - EUA: previsão de que 2026 tenha a menor venda de casas usadas desde 1995 (TheStreet), NÃO publicada
  - Curitiba: aluguel de 3 quartos +13,67% em 12 meses, até julho (Índice QuintoAndar Imovelweb), NÃO publicada
  À tarde o Jackson pediu a sequência nova com lançamentos. Os stories 09 e 10 saíram da fila e entraram 2 lançamentos animados: Residencial Imperatriz às 18h07 (https://www.instagram.com/stories/corretor.jacksonpires/4037000994642801748) e Lyon Residencial às 21h07 (https://www.instagram.com/stories/corretor.jacksonpires/4037091575972702089); a notícia de Goiânia foi às 19h37. O carrossel "Dia da chave" falhou às 7h (o Instagram cancelou por demora no download das imagens) e ficou esperando o Jackson dizer quando tentar de novo. Sem pesquisa nova de Sorocaba. Placar: 10 de 10 no horário e em vídeo (8 notícias e 2 lançamentos).
- 24/11/2026, 5h44: primeiro dia completo no formato novo, 5 notícias e 5 lançamentos intercalados, todos animados. Notícias:
  - 108,4 mil imóveis novos vendidos no 3º tri, +2,7%; lançamentos 119,7 mil, +1% (CBIC e Brain, via Diário do Grande ABC)
  - MCMV com 58,6% dos lançamentos, recorde da série; 70.129 lançados (+28,2%) e 56.812 vendidos (+21,6%) (CBIC e Brain, via CNN Brasil)
  - aluguel +9,01% em 12 meses, IPCA 4,63%; 2 quartos +10,20% (FipeZap, via Gazeta do Povo)
  - estoque recorde de 382,3 mil imóveis novos, cerca de 10,2 meses de vendas (CBIC e Brain, via Revista Construa)
  - 67% das compras até setembro tiveram desconto, contra 65% um ano antes (Raio-X FipeZap, via Revista Oeste)
  Lançamentos: Moove Residence (R$ 232 mil), Vista Horto (R$ 248 mil), Residencial Caribe (R$ 295 mil), Zafira Residencial (R$ 264 mil) e Parque das Margaridas (R$ 280 mil). Sem pesquisa nova de Sorocaba. Carrossel das 7h: "Subsídio" (https://www.instagram.com/p/DgHsWqej4bk/). Placar: 10 de 10, todos no horário; 9 em vídeo e 1 em imagem (o Moove Residence das 08h37: o Instagram deu erro passageiro no vídeo e o sistema publicou o story.jpg). Último: Parque das Margaridas, https://www.instagram.com/stories/corretor.jacksonpires/4037816353624290363
- 25/11/2026, 5h44: 5 notícias e 5 lançamentos intercalados, todos animados. Notícias:
  - 31% já desistiram de comprar imóvel; 24% citam dívidas (Loft, Índice de Confiança, via Portas)
  - 78% das regiões metropolitanas dos EUA com alta de preço no 3º tri; 21% caíram (NAR, via ConsumerAffairs)
  - IFIX caiu 1,29% na segunda (23), 44,98 pontos (Mercado Hoje)
  - 70% de quem quer comprar é para morar; 54% primeiro imóvel (Loft, via Portas)
  - m² em Portugal a € 3.249; Vila Real, Guarda e Beja com as maiores altas (idealista)
  Lançamentos: Jardins Ipanema (R$ 290 mil), Morada Boa Vista (R$ 302 mil), Villa Creta (R$ 311 mil), Reserva Lobato (R$ 316 mil) e Gama Harmony (R$ 321 mil). Carrossel das 7h: "Perguntas na planta". Perguntado ao Jackson se a lista recomeça ou se busco lançamentos novos depois de 26/11. Placar: 10 de 10, todos no horário e todos em vídeo. Carrossel: https://www.instagram.com/p/DgKRMu9Dnf2/. Último: Gama Harmony, https://www.instagram.com/stories/corretor.jacksonpires/4038541628930515377
- 26/11/2026, 5h46: 8 notícias e os 2 últimos lançamentos da lista (o Jackson não respondeu se recomeça ou busca novos, então 06, 08 e 10 viraram notícia). Notícias:
  - Recife lidera a valorização: +20,69% em 12 meses até setembro (Abecip e FGV Ibre, IGMI-R, via Movimento Econômico)
  - EUA: casas +2,1% em 12 meses até agosto, inflação 3,4%; 15º mês de queda real (S&P Cotality Case-Shiller)
  - inadimplência do crédito imobiliário em torno de 1% (Abecip, via CBIC)
  - EUA: casas novas vendidas a 676 mil/ano em setembro (Census, via HousingWire)
  - imóveis +6,94% de janeiro a setembro; 12,58% em 12 meses, IPCA 4,58% (IGMI-R, via Movimento Econômico)
  - crédito imobiliário de R$ 180,9 bi no 1º semestre, +23% (Abecip, via O Povo)
  - Rio: aluguel de 1 quarto +18,40% em 12 meses até julho, m² R$ 67,89 (Índice QuintoAndar Imovelweb)
  - 21% pretendem comprar ou alugar; 22% são proprietários (Loft, via Portas)
  Poucas notícias novas nas últimas 72 h: 4 são de julho a setembro. Título do 05 trocado antes de subir ("Quem financia paga em dia" afirmava mais que a fonte). Lançamentos: Reserva Painá (R$ 280 mil) e Residencial São Conrado (R$ 259 mil). Lista de lançamentos acabou. Carrossel das 7h: "Quanto ganhar" (https://www.instagram.com/p/DgM2ALAF0j8/). Placar: 10 de 10, todos no horário e todos em vídeo. Último: https://www.instagram.com/stories/corretor.jacksonpires/4039265922488651794
