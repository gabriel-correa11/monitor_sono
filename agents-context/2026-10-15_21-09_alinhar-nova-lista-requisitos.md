# Alinhar repositório à nova lista de requisitos

- **Data e hora:** 2026-10-15 21:09
- **Pedido por:** gestor do projeto
- **Ferramenta:** Claude Code
- **Requisitos relacionados:** RF01–RF15, RNF01–RNF12, RN01–RN10

## Pedido e contexto
O escopo do projeto mudou para "estudo de caso" e a lista de requisitos foi substituída inteiramente:
RF01–RF15, RNF01–RNF12, RN01–RN10. O áudio foi eliminado (RNF01, RN09). Novos módulos de classificação
foram adicionados (RF09, RF10, RF11). O banco foi reescrito com tabelas separadas para comportamentos
e estados (RNF07). O pedido foi: alinhar todo o repositório à nova lista.

## O que foi feito

### Criado
- `src/monitor_sono/classificacao/__init__.py` — módulo de classificação (RF09, RF10, RF11)
- `src/monitor_sono/classificacao/comportamentos.py` — classificar comportamentos (RF09, RN01–RN07)
- `src/monitor_sono/classificacao/estados.py` — estimar estados (RF10, RN02, RN03, RN07, RN10)
- `src/monitor_sono/classificacao/periodos.py` — identificar períodos (RF11, RN03–RN05)
- `src/monitor_sono/deteccao/presenca.py` — detectar presença (RF03)
- `src/monitor_sono/deteccao/rosto.py` — detectar rosto (RF04)
- `src/monitor_sono/deteccao/olhos.py` — estado dos olhos (RF05, RN06)
- `src/monitor_sono/deteccao/cabeca.py` — movimento da cabeça (RF06)
- `src/monitor_sono/deteccao/visibilidade.py` — visibilidade insuficiente (RF15, RN07)
- `docs/requisitos.md` — transcrição da lista oficial de requisitos

### Alterado
- `src/monitor_sono/config.py` — COMPORTAMENTOS frozenset (7 tipos), AVISO_NAO_DIAGNOSTICO (RNF12)
- `src/monitor_sono/registro/banco.py` — 3 tabelas (sessoes, comportamentos, estados), FK CASCADE, excluir_sessao()
- `src/monitor_sono/sessao/__init__.py` — removido parâmetro origem de iniciar_sessao()
- `src/monitor_sono/captura/__init__.py` — docstring sem áudio
- `src/monitor_sono/captura/video.py` — capturar_quadros() para câmera em tempo real (RF02)
- `src/monitor_sono/deteccao/__init__.py` — docstring com novos requisitos
- `src/monitor_sono/deteccao/movimento.py` — RF05→RF07, duas funções (corporal e posição)
- `src/monitor_sono/registro/__init__.py` — docstring atualizada
- `src/monitor_sono/dashboard/__init__.py` — docstring atualizada
- `src/monitor_sono/dashboard/app.py` — seções RF13, RF14, RF15, RNF07, RNF12
- `src/monitor_sono/__init__.py` — docstring sem áudio, cita RNF12
- `src/monitor_sono/__main__.py` — removido subcomando sessoes, removida referência a origem
- `pyproject.toml` — removido librosa
- `requirements.txt` — removido librosa
- `tests/test_registro.py` — 4 testes: sessao_e_comportamento, registrar_estado, rejeita_invalido, excluir_sessao
- `AGENTS.md` — escopo, módulos, restrições, contexto técnico atualizados
- `README.md` — escopo, estrutura, tecnologias, pendências atualizados
- `docs/rastreabilidade.md` — reescrita completa com RF01–RF15, RNF01–RNF12, RN01–RN10

### Excluído
- `src/monitor_sono/captura/audio.py` — áudio removido do escopo (RNF01, RN09)
- `src/monitor_sono/deteccao/som.py` — áudio removido do escopo (RNF01, RN09)

## Decisões e motivos
- Tabelas separadas para `comportamentos` e `estados`: atende RNF07 (distinguir observações de estimativas).
- Campo `origem` removido de `sessoes`: sem importação de gravações, a sessão é sempre ao vivo.
- Estados comportamentais (vigília, possível sono, indeterminado) não entram em config até a equipe confirmar.
- Todos os novos arquivos de detecção e classificação lançam NotImplementedError, sem implementação.
- A lista de COMPORTAMENTOS no config valida apenas tipos de observação (RF05–RF07, RF11, RF15), não estados estimados.

## Verificação
- `pytest`: 4 testes passaram (test_sessao_e_comportamento, test_registrar_estado, test_rejeita_comportamento_invalido, test_excluir_sessao).
- Busca por resíduos (audio, librosa, som.py, TIPOS_EVENTO, registrar_evento, eventos_da_sessao, origem): zero ocorrências no código-fonte.

## Pendências
- Limiares e critérios de classificação (RF09, RN01–RN05): equipe decide.
- Lista confirmada de estados comportamentais válidos (RF10, RN07): pesquisadores decidem.
- Módulo pipeline que liga captura → detecção → classificação → registro: equipe decide.
- Controle de acesso e termo de consentimento (RNF06, RNF08): pesquisadores e gestão.
- Verificar se docs/requisitos.md confere exatamente com o documento oficial — foi reconstruído a partir das referências no código.
