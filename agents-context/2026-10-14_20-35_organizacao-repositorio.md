# Organização do repositório: regras para IA, agents-context e privacidade

- **Data e hora:** 2026-10-14 20:35
- **Pedido por:** Analista (responsável pelo repositório)
- **Ferramenta:** Claude Code
- **Requisitos relacionados:** nenhum (tarefa de infraestrutura)

## Pedido e contexto

Organizar o repositório para a entrega aos analistas. O gestor alterou o escopo do projeto para um
estudo de caso e a lista de requisitos está sendo refeita. O AGENTS.md deveria se tornar o arquivo
único de regras para IA, sem depender de CLAUDE.md. Foram pedidos:

- Substituir AGENTS.md e .gitignore pelo novo conteúdo.
- Remover CLAUDE.md do projeto (arquivo e referências).
- Criar a pasta `agents-context/` com README.
- Atualizar o README: nota de escopo, AGENTS.md e agents-context na árvore, tabela de partes, remoção de datas.

## O que foi feito

- **Alterado:** `AGENTS.md` — substituído pelo novo conteúdo; regra adicionada na seção 3 proibindo a
  criação de `CLAUDE.md` ou `CLAUDE.local.md` (se existirem, o Claude Code os leria no lugar do AGENTS.md)
- **Alterado:** `.gitignore` — reescrito com privacidade expandida (mais formatos de vídeo/áudio, pastas
  de dados extras); duas correções aplicadas após revisão (ver abaixo)
- **Excluído:** `CLAUDE.md` — removido do disco (nunca foi rastreado no git; estava no .gitignore desde
  o início, então `git rm` não era aplicável)
- **Criado:** `agents-context/README.md` — explica a pasta e referencia a seção 4 do AGENTS.md
- **Alterado:** `README.md` — nota de escopo após aviso de não diagnóstico; `AGENTS.md` e
  `agents-context/` adicionados à árvore de estrutura; tabela de partes por pasta; datas de prazo e
  coluna "Próxima entrega" removidas da seção de analistas e da situação atual

## Decisões e motivos

- **AGENTS.md independente, sem CLAUDE.md:** o CLAUDE.md seria o único arquivo lido automaticamente
  pelo Claude Code, e os outros analistas que usassem outros assistentes (Copilot, Cursor) não o
  veriam. O AGENTS.md como arquivo único garante que todos os assistentes sigam as mesmas regras.
- **Correção 1 — CLAUDE.md e CLAUDE.local.md fora do .gitignore:** a primeira versão do .gitignore
  incluía essas linhas como "linha de defesa extra". Revertido a pedido: com o ignore ativo, um arquivo
  criado por engano não aparece no `git status` nem no Pull Request, passando despercebido. Sem o
  ignore, ele aparece na revisão e pode ser detectado e removido antes do merge.
- **Correção 2 — verificação no disco:** confirmado que `CLAUDE.md` e `CLAUDE.local.md` não existem
  no disco (nem rastreados nem locais).

## Verificação

- `pytest`: 2 passaram
- `git ls-files --deleted`: vazio (nenhum arquivo rastreado foi removido)
- Busca por segredos (`rtsp://` com credenciais, tokens, senhas): nenhum encontrado
- `CLAUDE.md` e `CLAUDE.local.md` no disco: nenhum encontrado

## Pendências

- Pull Request para revisão por outro analista antes do merge na `main`.
- Após aprovação do novo escopo pelos pesquisadores, atualizar `docs/rastreabilidade.md` e a seção 1
  do `AGENTS.md` com a nova lista de requisitos.
