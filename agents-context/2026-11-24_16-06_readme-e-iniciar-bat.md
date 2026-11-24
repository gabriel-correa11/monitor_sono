# Como rodar explicado no README e iniciar.bat com clique duplo

- **Data e hora:** 2026-11-24 16:06
- **Pedido por:** dono do repositório
- **Ferramenta:** Claude Code
- **Requisitos relacionados:** RF01, RF13, RF14, RNF11

## Pedido e contexto
"i need to fix the readme, its a college work make portuguese-br include how to run explained, or make a
script just click and runs". O README já estava em português, mas a parte de como rodar era só uma lista de
comandos, difícil para quem não usa terminal.

## O que foi feito
- **Criado:** `iniciar.bat` — menu do Windows com clique duplo: na primeira vez cria o `.venv` e instala o
  projeto; depois abre o dashboard, analisa gravações (escolhidas numa janela ou arrastadas para cima do
  arquivo) ou roda os testes. Antes de analisar, pergunta pelo termo de consentimento (RNF11).
- **Criado:** `.gitattributes` — mantém o `.bat` com fim de linha do Windows (CRLF), sem o qual o `cmd`
  pode errar os rótulos do script.
- **Alterado:** `README.md` — seção 6 reescrita: as duas etapas do uso, o jeito com o `iniciar.bat`, o passo
  a passo pelo terminal com o que cada comando faz, e uma tabela de problemas comuns. A estrutura do
  projeto lista os dois arquivos novos.
- **Excluído:** nada.

## Decisões e motivos
- Um único `.bat` com menu, em vez de vários scripts, para a pasta do projeto continuar simples.
- O menu usa `choice` (aperta o número, sem Enter) em vez de `set /p`, que entra em laço sem fim se a
  entrada acabar.
- O dashboard sobe com `--server.headless true`, que evita a pergunta de e-mail do Streamlit na primeira
  execução; o navegador é aberto pelo próprio script.
- Sem dependência nova: o `pytest` só é instalado quando a pessoa escolhe rodar os testes.

## Verificação
Numa cópia limpa do projeto (sem `.venv` e sem `dados/`):
- primeira execução: criou o `.venv` e instalou o projeto;
- opção 3: `pytest` instalado e 97 testes passaram;
- arrastar dois vídeos sintéticos (nomes com espaço): duas sessões gravadas;
- opção 2 com a janela de escolha trocada por um arquivo fixo: sessão gravada; o comando da janela foi
  conferido sem abri-la;
- comando do dashboard: o servidor sobe e responde em `/_stcore/health`.

As perguntas do `choice` e a janela de escolha de arquivo foram trocadas por respostas fixas no teste,
porque precisam de teclado e mouse.

## Pendências
- Testar com teclado e mouse: o menu, a janela de escolha e a abertura automática do navegador.
