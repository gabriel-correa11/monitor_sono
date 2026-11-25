# Limpeza do repositório

- **Data e hora:** 2026-11-24 17:58
- **Pedido por:** gabriel correa
- **Ferramenta:** Claude Code
- **Requisitos relacionados:** nenhum

## Pedido e contexto
"preciso que vc limpe esse repo, eu tirei a secao 8 de pendencias, acho inutil e subi pra algumas coisas,
veja voce". Os PRs #1 a #4 já estavam mergeados na `main`, e quem pediu removeu a seção 8 (Pendências)
do `README.md` direto no GitHub (commit `892e2af`).

## O que foi feito
- `main` local atualizada com `git pull --ff-only` (estava 20 commits atrás).
- Conferido que os itens da seção 8 removida continuam em "Decisões pendentes" do
  `docs/rastreabilidade.md`. Nada se perdeu.
- **Alterado:** `AGENTS.md` — a regra "Decidir pendências listadas no `README.md`" passou a apontar para
  "Decisões pendentes" do `docs/rastreabilidade.md`, porque o README não tem mais essa seção.
- **Criado:** `agents-context/2026-11-24_17-58_limpeza-do-repositorio.md` — este registro
- **Excluído:** nada. A exclusão das branches já mergeadas e das pastas geradas (`build/`,
  `.pytest_cache/`, `__pycache__/`) foi bloqueada pela permissão do Claude Code e ficou para quem pediu
  confirmar.

## Decisões e motivos
- `dados/`, `.idea/`, `.claude/`, `.venv/` e `src/monitor_sono.egg-info/` não foram tocados: guardam o
  banco, configurações pessoais e a instalação editável.
- Nenhum commit, branch ou push: o pedido não citou commit, e a `main` não recebe commit direto.

## Verificação
Só documentação alterada; `pytest` não foi rodado.

## Pendências
- Apagar as branches mergeadas (locais: `correcoes-dashboard-pipeline`, `finalizacao`,
  `organizacao-repositorio`, `rf13-iniciar-bat-readme`; no GitHub: `correcoes-dashboard-pipeline`,
  `finalizacao`, `rf02-captura-video`, `rf13-iniciar-bat-readme`), se quem pediu confirmar.
- Levar para a `main`, por PR, a mudança do `AGENTS.md`, este registro e o registro solto
  `2026-11-23_16-22_commit-push-conexoes-readme.md`.
