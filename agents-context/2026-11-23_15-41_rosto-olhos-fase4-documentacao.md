# Rosto e olhos — fase 4: documentação e descrição do PR

- **Data e hora:** 2026-11-23 15:41
- **Pedido por:** gabriel correa
- **Ferramenta:** Claude Code
- **Requisitos relacionados:** RF03, RF04, RF05, RF06, RF09, RF10, RF15, RNF02, RN01, RN02, RN06

## Pedido e contexto
Seguir para a fase 4 com os resultados da fase 3 como estão, sem ajustar parâmetros. Pedidos: usar os
números da fase 3 como oficiais na tabela do estudo de caso; registrar em uma linha que os números de
movimento mudaram porque a análise anterior foi feita em partes, em outro ambiente e com OpenCV 5;
acrescentar linhas de rosto e olhos; registrar a conclusão do estudo de caso e os prováveis motivos;
trabalho futuro (contraste dos rostos, regra de olhos fechados com gabarito, câmera mais perto); RF03 a
RF06 implementados e RF10 Parcial; escrever a descrição do PR fora do repositório; parar antes do push.

## O que foi feito
- **Alterado:** `docs/rastreabilidade.md` — versão 3.1. RF03 a RF06: arquivo, funções, Implementado e testes.
  RF09 e RF15 de Parcial para Implementado. RF10 continua Parcial, com o motivo. RNF02 sem pendência. RN01,
  RN02 e RN06 atualizados. Observações de RF03 a RF06, com a limitação do reinício do acompanhamento dos
  olhos (ajuste 2 da aprovação da fase 1). A decisão pendente do detector de rosto foi resolvida (OpenCV 4.x)
  e trocada pela decisão sobre a regra de olhos fechados. Resumo: 14 RF implementados e 1 parcial. Linha 3.1
  no histórico.
- **Alterado:** `docs/material-documentacao.md` — tabela do estudo de caso com os números da fase 3 e as
  linhas de rosto, rostos aproveitáveis, olhos determinados e movimentos da cabeça; nota sobre a mudança dos
  números de movimento; leitura dos resultados com a conclusão do estudo de caso; parâmetros novos; limitações
  e trabalho futuro. Ajustes pequenos fora dessas seções, porque o texto ficaria errado: número de testes (36
  para 67) e um parágrafo sobre RF03 a RF06 em "Como o sistema funciona".
- **Criado (fora do repositório):** `pr-descricao.md` na pasta pai do projeto — descrição do Pull Request.
- **Criado:** `agents-context/2026-11-23_15-41_rosto-olhos-fase4-documentacao.md` — este registro
- **Excluído:** nada

## Decisões e motivos
- As linhas "Segundos com movimento" e "Trocas de iluminação" saíram da tabela: esses números não são
  gravados no banco e não foram medidos nesta análise. Isso ficou escrito numa nota abaixo da tabela.
- O bullet sobre as trocas de iluminação da gravação 2 saiu da leitura dos resultados, porque se baseava
  nesses números da análise anterior.
- Os números de movimento que faltavam no resumo da fase 3 (maior ausência, ausências de 5 min ou mais,
  minutos de maior atividade) foram somados das sessões no banco, pelo módulo `registro`, só como números
  agregados.

## Verificação
`pytest`: 67 passaram. Conferido que os documentos não têm o caminho das gravações.

## Pendências
- Push e abertura do PR, quando quem pediu autorizar.
