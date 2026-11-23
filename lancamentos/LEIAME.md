# Lançamentos de Sorocaba (stories intercalados com as notícias)

Pedido do Jackson em 23/11/2026: 5 stories de empreendimento por dia, intercalados com 5 notícias.
Ímpares (07h07, 10h07, 12h37, 16h07, 19h37) = notícia. Pares (08h37, 11h37, 14h07, 18h07, 21h07) = empreendimento.

- dados.json: 14 lançamentos até R$ 350 mil (fonte apto.vc em 23/11; Reserva Painá e São Conrado pelo site do Jackson).
  Campo "usado" recebe a data em que o story saiu. Campo "renda" só é preenchido com valor passado pelo Jackson.
- fotos/<slug>.jpg: foto oficial do condomínio (baixada pelo Chrome do Jackson; o container não acessa api.apto.vc).
- Gerar: python3 agente03/story_empreendimento.py dados_item.json story.jpg [fotos/<slug>.jpg]
