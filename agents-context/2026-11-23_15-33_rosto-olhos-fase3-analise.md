# Rosto e olhos — fase 3: análise das gravações

- **Data e hora:** 2026-11-23 15:33
- **Pedido por:** gabriel correa
- **Ferramenta:** Claude Code
- **Requisitos relacionados:** RF03, RF04, RF05, RF06, RF10, RF15, RN06, RN07

## Pedido e contexto
Excluir as sessões antigas do banco, rodar o comando `analisar` sobre as duas gravações do estudo de
caso com os horários de início informados por quem pediu e mostrar só números agregados. Exceção
autorizada por quem pediu à regra da pasta restrita: rodar o comando do sistema localmente, sem abrir,
exibir, descrever, extrair ou salvar quadros e sem citar o caminho dos vídeos em arquivos do repositório.

## O que foi feito
- Sessões 1 e 2 (as análises anteriores, sem olhos) excluídas com `banco.excluir_sessao()`.
- O comando `python -m monitor_sono analisar <gravação> --inicio ... --autorizado` rodou sem alteração,
  chamado por um script temporário **fora do repositório**. O script só soma as saídas das detecções
  (quantidade de rostos, larguras em px, estado dos olhos), porque o `__main__.py` não mostra esses números
  e não está na lista de arquivos da tarefa. Nenhum quadro foi aberto, exibido ou salvo.
- Novas sessões gravadas no banco local `dados/` (fora do git).
- **Criado:** `agents-context/2026-11-23_15-33_rosto-olhos-fase3-analise.md` — este registro
- **Alterado:** nada no repositório
- **Excluído:** nada no repositório

## Resultados agregados

| | Gravação 1 | Gravação 2 |
|---|---|---|
| Quadros analisados | 9.485 | 13.948 |
| Com rosto | 402 (4,2%): 145 de frente, 257 de perfil | 1.372 (9,8%): 1.322 de frente, 50 de perfil |
| Largura do rosto (px originais), mediana | 154 | 151 |
| Rosto adequado para os olhos | 41 (0,4%) | 156 (1,1%) |
| Olhos abertos / fechados | 7 / 0 | 8 / 0 |
| Olhos determináveis | 7 (0,1%) | 8 (0,1%) |
| Estados | 100% indeterminado | 100% indeterminado |
| Movimentos da cabeça | 11 | 11 |
| Avisos de visibilidade | 0 | 0 |
| Tempo de processamento | 7,4 min | 10,3 min |

## Decisões e motivos
Nenhum parâmetro foi ajustado, conforme o pedido. As propostas foram apresentadas para aprovação.

## Verificação
Os dois comandos terminaram sem erro.

## Pendências
- Decidir ajustes de parâmetro ou de regra (aguardando quem pediu).
- Os números de movimento mudaram em relação à análise anterior (por exemplo, mudanças de posição na
  gravação 1: 236 antes, 347 agora), embora o movimento use a mesma redução para 320×240. Causa
  provável: troca do OpenCV 5.0 para 4.14 (decodificação do vídeo). Não foi investigado.
