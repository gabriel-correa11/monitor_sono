# Horário real de início das gravações do estudo de caso

- **Data e hora:** 2026-11-23 14:46
- **Pedido por:** Gabriel Correa (analista)
- **Ferramenta:** Claude
- **Requisitos relacionados:** RF08, RNF04, RN08

## Pedido e contexto
As sessões do estudo de caso tinham sido gravadas com o horário da análise, porque o início real das gravações
não era conhecido. O Gabriel informou a data e hora que a câmera grava na imagem, no início de cada vídeo. A IA não
leu essa informação dos quadros: o Gabriel conferiu no player e mandou só o recorte com o horário.

## O que foi feito
- **Alterado (fora do git):** `dados/monitor_sono.db` — as duas sessões foram regravadas com o início real
  (Sono 1: 09/11/2026 03:22:48; Sono 2: 10/11/2026 04:23:21), usando as detecções já calculadas, sem processar os
  vídeos de novo.
- **Alterado:** `docs/material-documentacao.md` — horário de início na tabela de resultados; removida a limitação
  sobre o horário.
- **Alterado:** `docs/rastreabilidade.md` — removida a decisão pendente sobre o horário de início.
- **Excluído:** nada.

## Decisões e motivos
- Assumido que a primeira imagem enviada é o início do Sono 1 e a segunda o do Sono 2, pela ordem e pelas datas.

## Verificação
Sessões no banco: Sono 1 de 03:22:48 a 06:01:39 (09/11); Sono 2 de 04:23:21 a 08:15:49 (10/11).

## Pendências
- Conferir o horário do fim de cada vídeo na câmera com o fim calculado (06:01:39 e 08:15:49).
