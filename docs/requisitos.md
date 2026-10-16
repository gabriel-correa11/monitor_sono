# Levantamento de Requisitos — Sistema de Monitoramento do Sono

Transcrição fiel do documento oficial "Levantamento de Requisitos", elaborado pelos pesquisadores para o
escopo de estudo de caso. Esta é a lista vigente de requisitos do projeto. Não altere este arquivo sem uma
nova versão aprovada pela gestão.


## 1. Requisitos funcionais (RF)

| Código | Requisito funcional | Prioridade |
|---|---|---|
| RF01 | O sistema deverá permitir iniciar e encerrar uma sessão de monitoramento do sono. | Alta |
| RF02 | O sistema deverá capturar imagens ou quadros de vídeo em tempo real utilizando exclusivamente uma câmera. | Alta |
| RF03 | O sistema deverá identificar a presença de uma pessoa na área monitorada. | Alta |
| RF04 | O sistema deverá detectar a região facial do indivíduo, quando visível. | Alta |
| RF05 | O sistema deverá identificar se os olhos estão abertos, fechados ou se não é possível determinar seu estado. | Alta |
| RF06 | O sistema deverá detectar movimentos da cabeça durante o monitoramento. | Média |
| RF07 | O sistema deverá identificar movimentos corporais observáveis, como mudanças de posição e movimentações de braços e pernas. | Alta |
| RF08 | O sistema deverá registrar os movimentos identificados com seus respectivos horários. | Alta |
| RF09 | O sistema deverá classificar os comportamentos identificados conforme critérios previamente estabelecidos. | Alta |
| RF10 | O sistema deverá estimar estados de sono a partir das características visuais detectadas. | Alta |
| RF11 | O sistema deverá identificar períodos de movimentação e de ausência de movimentação observável. | Alta |
| RF12 | O sistema deverá armazenar os resultados das classificações realizadas durante cada sessão. | Alta |
| RF13 | O sistema deverá apresentar um histórico cronológico dos comportamentos e estados estimados durante o monitoramento. | Média |
| RF14 | O sistema deverá gerar um relatório contendo a duração da sessão, os movimentos detectados e os estados estimados. | Média |
| RF15 | O sistema deverá sinalizar quando a câmera não conseguir observar adequadamente o indivíduo. | Alta |

## 2. Requisitos não funcionais (RNF)

| Código | Requisito não funcional | Categoria |
|---|---|---|
| RNF01 | O sistema deverá utilizar exclusivamente uma câmera para coletar informações sobre o indivíduo. | Restrição tecnológica |
| RNF02 | O sistema deverá processar imagens automaticamente por meio de técnicas de visão computacional. | Tecnologia |
| RNF03 | O sistema deverá funcionar sem exigir interação constante do usuário durante o monitoramento. | Usabilidade |
| RNF04 | O sistema deverá registrar os horários dos eventos detectados com precisão de, no mínimo, um segundo. | Precisão temporal |
| RNF05 | O sistema deverá preservar a integridade dos registros gerados durante as sessões. | Confiabilidade |
| RNF06 | O sistema deverá proteger as imagens e os dados pessoais coletados contra acessos não autorizados. | Segurança |
| RNF07 | O sistema deverá apresentar os resultados de maneira compreensível, distinguindo observações visuais de estados estimados. | Usabilidade |
| RNF08 | O sistema deverá permitir monitoramento contínuo durante o período de uma sessão, desde que haja recursos computacionais disponíveis. | Desempenho |
| RNF09 | O sistema deverá registrar situações em que não seja possível realizar uma classificação confiável. | Confiabilidade |
| RNF10 | O sistema deverá permitir a exclusão dos dados armazenados de uma sessão. | Privacidade |
| RNF11 | O sistema deverá obter autorização para o tratamento das imagens e respeitar os princípios aplicáveis da LGPD. | Privacidade |
| RNF12 | O sistema deverá informar que os resultados representam estimativas comportamentais e não diagnósticos clínicos. | Transparência |

## 3. Regras de negócio (RN)

| Código | Regra de negócio |
|---|---|
| RN01 | A identificação de olhos abertos por um período contínuo poderá ser utilizada como evidência de vigília. |
| RN02 | A identificação de olhos fechados por um período contínuo poderá ser utilizada como evidência de possível sono, desde que considerada em conjunto com outros comportamentos. |
| RN03 | A ausência prolongada de movimentos corporais poderá contribuir para a classificação de possível sono, mas não será suficiente isoladamente. |
| RN04 | Movimentos corporais frequentes deverão ser registrados como períodos de maior atividade motora. |
| RN05 | Mudanças bruscas de posição deverão ser registradas como eventos de movimentação corporal. |
| RN06 | Quando os olhos não estiverem visíveis, o sistema não deverá classificá-los automaticamente como fechados. |
| RN07 | Quando não houver informações visuais suficientes, o estado deverá ser classificado como indeterminado. |
| RN08 | Todas as classificações deverão estar associadas a um horário ou intervalo de tempo. |
| RN09 | As classificações deverão ser baseadas exclusivamente nas informações visuais capturadas pela câmera. |
| RN10 | O sistema não deverá apresentar estimativas comportamentais como identificação clínica dos estágios do sono. |

## 4. Classificação dos comportamentos e estados

**Comportamentos identificáveis**

| Comportamento | Identificação pela câmera |
|---|---|
| Olhos abertos | Detecção da abertura ocular |
| Olhos fechados | Detecção do fechamento ocular |
| Movimento da cabeça | Alteração da posição ou orientação da cabeça |
| Movimento corporal | Deslocamento de partes visíveis do corpo |
| Mudança de posição | Alteração significativa da postura corporal |
| Ausência de movimento | Nenhuma movimentação relevante identificada no intervalo |
| Visibilidade insuficiente | Rosto ou corpo fora do enquadramento ou obstruído |

## Observação sobre a transcrição

O título da seção 4 do documento original é "Classificação dos comportamentos e estados", mas o documento
traz apenas a tabela de comportamentos. A lista de estados não consta no original e está registrada como
pendência em `docs/rastreabilidade.md`.