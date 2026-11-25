# Limpeza das branches já juntadas na main

- **Data e hora:** 2026-11-25 09:40
- **Pedido por:** gabriel correa
- **Ferramenta:** Claude Code
- **Requisitos relacionados:** nenhum

## Pedido e contexto
Parte 4 da tarefa "ajustes finais": apagar as branches já juntadas na `main`, mas só depois de conferir
com `git merge-base --is-ancestor origin/<branch> origin/main` e com a aprovação de quem pediu
("aprovado").

## O que foi feito
- `git checkout main` e `git fetch --prune`.
- Conferência: `finalizacao`, `rf02-captura-video`, `correcoes-dashboard-pipeline` e
  `rf13-iniciar-bat-readme` estavam inteiras na `origin/main`.
- **Excluído no GitHub** (`git push origin --delete`): `finalizacao`, `rf02-captura-video`,
  `correcoes-dashboard-pipeline`, `rf13-iniciar-bat-readme`. Motivo: já juntadas na `main` pelos PRs #1
  a #4.
- **Excluído localmente** (`git branch -d`): `finalizacao`, `correcoes-dashboard-pipeline`,
  `rf13-iniciar-bat-readme`. A `rf02-captura-video` não tinha cópia local.
- **Criado:** `agents-context/2026-11-25_09-40_limpeza-branches-juntadas.md` — este registro

## Decisões e motivos
- `main` e `ajustes-finais` não foram tocadas.
- Só `-d`, nunca `-D`.
- A branch local `organizacao-repositorio` ficou, porque não estava na lista. A cópia dela no GitHub já
  não existia, e o commit dela já está na `main`.

## Verificação
`git branch -a` depois da limpeza: `ajustes-finais`, `main`, `organizacao-repositorio` (local) e
`origin/ajustes-finais`, `origin/main`.

## Pendências
- Decidir se a branch local `organizacao-repositorio` deve ser apagada.
- Decidir o que fazer com o `git stash` da tarefa anterior (`AGENTS.md` com "Decisões pendentes" e os
  registros `2026-11-23_16-22_commit-push-conexoes-readme.md` e `2026-11-24_17-58_limpeza-do-repositorio.md`).
