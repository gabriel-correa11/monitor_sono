# Verificar merges pendentes

- **Data e hora:** 2026-11-23 14:05
- **Pedido por:** gabriel correa
- **Ferramenta:** Claude Code
- **Requisitos relacionados:** nenhum

## Pedido e contexto
"ve se tem alguma merge pendente" — conferir se há merge em andamento, pull requests abertos
ou branches ainda não mescladas na `main`.

## O que foi feito
- **Criado:** `agents-context/2026-11-23_14-05_verificar-merges-pendentes.md` — este registro
- **Alterado:** nada
- **Excluído:** nada

Comandos só de leitura: `git status`, `git fetch --all --prune`, `git branch -a -vv`,
`git branch -a --no-merged origin/main`, `git branch -a --merged origin/main`, `gh pr list --state open`.

## Decisões e motivos
- Não foi feito `git pull` nem apagada nenhuma branch, porque não foi pedido.

## Verificação
- Nenhum merge em andamento (sem `.git/MERGE_HEAD`); árvore de trabalho limpa.
- Nenhum pull request aberto.
- Nenhuma branch, local ou remota, fora da `origin/main`.
- O PR #1 (`rf02-captura-video`, commit `b425da8`) já foi mesclado na `origin/main` (`1c53d89`).
- A `main` local está 2 commits atrás da `origin/main`.

## Pendências
- Atualizar a `main` local com `git pull` (decisão de quem pediu).
- Branch remota `origin/rf02-captura-video` já mesclada e branch local `organizacao-repositorio`
  (remota apagada) podem ser removidas, se a equipe quiser.
