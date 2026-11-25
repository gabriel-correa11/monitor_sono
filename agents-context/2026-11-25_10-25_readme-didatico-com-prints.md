# README didático com prints do dashboard

- **Data e hora:** 2026-11-25 10:25
- **Pedido por:** gabriel correa
- **Ferramenta:** Claude Code
- **Requisitos relacionados:** RF13, RF14, RNF12

## Pedido e contexto
Reescrever o `README.md` "para que uma pessoa leiga, que nunca programou, entenda em poucos minutos o que o
software faz, o que ele não faz e como usar", com "frases curtas, sem jargão", sem comentar o próprio estilo
nem o leitor. O README deve ter três prints do dashboard com uma sessão de exemplo, com dados inventados,
nunca com o banco real nem com as gravações. O trabalho foi na branch `ajustes-finais`, e o commit foi
aprovado por quem pediu ("pode fazer o commit").

## O que foi feito
- **Prints:**
  - sessão de exemplo inventada (20/11, 22:30 a 06:30) gravada com `registro/banco.py` num banco temporário
    no scratchpad, fora do repositório;
  - dashboard rodado com `config.CAMINHO_BANCO` trocado para esse banco;
  - prints tirados com o Edge sem tela pelo Playwright, que ficou num ambiente temporário fora do projeto;
  - barra do Streamlit escondida e branco em volta cortado;
  - banco, scripts e ambiente temporários apagados depois.
- **Alterado:** `docs/imagens/dashboard-resumo.png` — título, aviso, escolha da sessão e resumo (substitui o
  arquivo que já existia).
- **Alterado:** `docs/imagens/dashboard-linha-do-tempo.png` — faixas Observado e Estimado (substitui o
  arquivo que já existia).
- **Alterado:** `docs/imagens/dashboard-estados-relatorio.png` — estados estimados com o tempo não confiável,
  avisos da câmera e botão do relatório (substitui o arquivo que já existia).
- **Alterado:** `README.md` — reescrito nesta ordem:
  1. o que é;
  2. aviso de não diagnóstico;
  3. o que faz, com exemplos;
  4. o que não faz;
  5. como funciona;
  6. o que aparece na tela, com os três prints;
  7. como usar (`iniciar.bat` primeiro, depois o passo a passo pelo terminal e os problemas comuns, sem
     mudança nos comandos);
  8. privacidade;
  9. glossário;
  10. seção para quem vai mexer no código (regra dos requisitos, links para `docs/` e `AGENTS.md`,
      estrutura de pastas, tecnologias e testes).
- **Criado:** `agents-context/2026-11-25_10-25_readme-didatico-com-prints.md` — este registro
- **Excluído:** nada no repositório

## Decisões e motivos
- Cada afirmação do README foi conferida no código: `config.py`, `classificacao/estados.py`, `pipeline.py`,
  `dashboard/app.py`, `__main__.py` e `iniciar.bat`.
- "Vídeos e resultados não vão para a internet", em vez de "nada vai para a internet": rodado pelo terminal,
  o Streamlit pode enviar estatísticas anônimas de uso.
- O CSV "abre em programas de planilha", sem citar o Excel: o arquivo é separado por vírgulas, e o Excel em
  português pode não separar as colunas sozinho.
- A árvore de pastas ganhou `captura/carimbo.py` e `docs/imagens/`, que existiam e faltavam.

## Verificação
- Cada print foi conferido visualmente; o recorte do resumo também foi conferido pixel a pixel.
- `git status`: só `README.md`, `docs/imagens/` e este registro. Nenhum código, teste ou outro documento
  foi alterado. O `pytest` não foi rodado, porque não houve mudança de código.

## Pendências
- Revisão e merge do PR `ajustes-finais`, por outro analista.
