# Conferência de requisitos e correção de IDs trocados

- **Data e hora:** 2026-10-15 21:36
- **Pedido por:** gestor do projeto
- **Ferramenta:** Claude Code
- **Requisitos relacionados:** RN01, RN07, RNF05, RNF08, RNF11

## Pedido e contexto
Após o alinhamento à nova lista de requisitos, o gestor substituiu manualmente `docs/requisitos.md` pela
transcrição fiel do documento oficial e pediu uma conferência completa: cruzar cada referência no código
contra o oficial, corrigir o que estiver errado e registrar a conferência.

## O que foi feito

### Correção de RNF05, RNF08 e RNF11 (registro anterior `2026-10-15_21-09`)
A lista oficial de requisitos se perdeu na compactação automática do contexto do Claude Code. Ao
reconstruir o `docs/requisitos.md` a partir de fragmentos no histórico, três RNFs foram atribuídos aos
IDs errados (permutação circular):

| ID | Minha versão (errada) | Oficial (correta) |
|---|---|---|
| RNF05 | Monitoramento contínuo (Desempenho) | Preservar integridade dos registros (Confiabilidade) |
| RNF08 | Autorização LGPD (Privacidade) | Monitoramento contínuo (Desempenho) |
| RNF11 | Preservar integridade (Confiabilidade) | Autorização LGPD (Privacidade) |

Corrigido em `docs/rastreabilidade.md` (6 edições) e `README.md` (2 edições). O código (`banco.py`,
`registro/__init__.py`) já citava RNF05 para integridade — correto por coincidência, sem alteração.

### Ajuste de RN01 e RN07 nas docstrings
- **Alterado:** `src/monitor_sono/classificacao/comportamentos.py` — removido RN01 da docstring
  (vigília é sobre estado, não classificação de comportamento). Ficou `RN02–RN08`.
- **Alterado:** `src/monitor_sono/classificacao/estados.py` — acrescentado RN01 na docstring.
  Ficou `RN01, RN02, RN03, RN07, RN10`. RN07 já estava presente.
- **Alterado:** `docs/rastreabilidade.md` — RN01: removido `classificacao/comportamentos.py`,
  ficou apenas `classificacao/estados.py`.

### Confirmação dos RNFs sem código
Confirmado que RNF01, RNF02, RNF03, RNF06, RNF08 e RNF11 constam na rastreabilidade com situação e
o que falta, mesmo sem implementação direta no código.

## Decisões e motivos
- RN01 ("olhos abertos → vigília") é uma regra de estimativa de estado, não de classificação de
  comportamento. A vigília é um estado estimado (RF10), não um comportamento observável.
- RN07 já estava em `estados.py` e `visibilidade.py`. Nenhuma alteração necessária.

## Verificação
- `pytest`: 4 testes passaram.
- Conferência completa de RF01–RF15, RNF01–RNF12 e RN01–RN10 contra o documento oficial: sem
  inconsistências remanescentes.

## Pendências
Nenhuma.
