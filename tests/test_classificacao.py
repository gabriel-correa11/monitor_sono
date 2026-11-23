"""Testes da classificação (RF09, RF10, RF11) e das regras de negócio, com detecções inventadas."""

from monitor_sono import config
from monitor_sono.classificacao import comportamentos, estados, periodos
from monitor_sono.tipos import DeteccaoMovimento, EstadoOlhos, Intervalo, Visibilidade


def mov(segundo: float, movimento: bool = False, posicao: bool = False, luz: bool = False) -> DeteccaoMovimento:
    return DeteccaoMovimento(segundo, 0.0, movimento, posicao, luz)


def vis(segundo: float, adequada: bool = True) -> Visibilidade:
    return Visibilidade(segundo, adequada, "ok" if adequada else "escura")


def parado(inicio: int, fim: int) -> list[DeteccaoMovimento]:
    return [mov(s) for s in range(inicio, fim + 1)]


# --- RF11: períodos ------------------------------------------------------------------------------------

def test_movimentos_proximos_formam_um_periodo():
    dets = parado(0, 9) + [mov(10, True), mov(12, True), mov(14, True)] + parado(15, 20)
    tipos = periodos.identificar_periodos(dets, [])
    movs = [p for p in tipos if p.tipo == "movimento_corporal"]
    assert movs == [Intervalo("movimento_corporal", 10, 14)]


def test_ausencia_curta_nao_e_registrada():
    dets = parado(0, int(config.AUSENCIA_MINIMA_S) - 10) + [mov(100, True)]
    assert not [p for p in periodos.identificar_periodos(dets, []) if p.tipo == "ausencia_movimento"]


def test_ausencia_longa_e_registrada():
    fim = int(config.AUSENCIA_MINIMA_S) + 30
    dets = parado(0, fim) + [mov(fim + 1, True)]
    aus = [p for p in periodos.identificar_periodos(dets, []) if p.tipo == "ausencia_movimento"]
    assert aus == [Intervalo("ausencia_movimento", 0, fim)]


def test_sem_informacao_interrompe_ausencia():
    # RN07: trecho escuro no meio não pode ser contado como "parado".
    meio = int(config.AUSENCIA_MINIMA_S)
    dets = parado(0, 2 * meio)
    visib = [vis(s, adequada=(s != meio)) for s in range(0, 2 * meio + 1)]
    aus = [p for p in periodos.identificar_periodos(dets, visib) if p.tipo == "ausencia_movimento"]
    assert all(not (p.inicio <= meio <= p.fim) for p in aus)


# --- RF09: comportamentos ------------------------------------------------------------------------------

def test_mudanca_brusca_vira_evento_de_mudanca_de_posicao():
    # RN05
    dets = parado(0, 5) + [mov(6, True, posicao=True)] + parado(7, 10)
    c = comportamentos.classificar_comportamentos(dets, [])
    assert Intervalo("mudanca_posicao", 6, 6) in c


def test_movimentos_frequentes_viram_maior_atividade():
    # RN04
    n = config.MOVIMENTOS_FREQUENTES
    dets = [mov(s, True) for s in range(0, n + 5)]
    c = comportamentos.classificar_comportamentos(dets, [])
    assert any(i.tipo == "maior_atividade_motora" for i in c)


def test_movimentos_esparsos_nao_sao_maior_atividade():
    janela = int(config.JANELA_ATIVIDADE_S)
    dets = [mov(s, True) for s in range(0, 10 * janela, janela)]
    c = comportamentos.classificar_comportamentos(dets, [])
    assert not any(i.tipo == "maior_atividade_motora" for i in c)


def test_visibilidade_insuficiente_vira_comportamento():
    c = comportamentos.classificar_comportamentos([], [vis(1, False), vis(2, False), vis(3)])
    assert Intervalo("visibilidade_insuficiente", 1, 2) in c


def test_todos_os_tipos_estao_no_escopo():
    dets = [mov(s, True, posicao=(s == 3)) for s in range(0, 30)] + parado(31, 200)
    olhos = [EstadoOlhos(s, "abertos") for s in range(0, 10)]
    c = comportamentos.classificar_comportamentos(dets, [vis(5, False)], olhos)
    assert {i.tipo for i in c} <= config.COMPORTAMENTOS


# --- RF10: estados -------------------------------------------------------------------------------------

def test_sem_olhos_tudo_e_indeterminado():
    # RN06 e RN07: sem detecção ocular, nem a ausência prolongada de movimento vira possível sono (RN03).
    aus = [Intervalo("ausencia_movimento", 0, 3600)]
    e = estados.estimar_estados([], aus, 0, 3600)
    assert e == [estados.EstadoEstimado("indeterminado", 0, 3600, False)]


def test_olhos_abertos_por_periodo_continuo_e_vigilia():
    # RN01
    t = int(config.PERIODO_CONTINUO_OLHOS_S) + 10
    olhos = [EstadoOlhos(s, "abertos") for s in range(0, t + 1)]
    e = estados.estimar_estados(olhos, [], 0, t)
    assert e[0].estado == "vigilia" and e[0].confiavel


def test_olhos_fechados_sozinhos_nao_bastam():
    # RN02: olhos fechados sem ausência prolongada de movimento não viram possível sono.
    t = int(config.PERIODO_CONTINUO_OLHOS_S) + 10
    olhos = [EstadoOlhos(s, "fechados") for s in range(0, t + 1)]
    e = estados.estimar_estados(olhos, [], 0, t)
    assert all(x.estado == "indeterminado" for x in e)


def test_olhos_fechados_e_ausencia_prolongada_viram_possivel_sono():
    # RN02 + RN03
    t = int(config.AUSENCIA_PROLONGADA_S) + 60
    olhos = [EstadoOlhos(s, "fechados") for s in range(0, t + 1)]
    aus = [Intervalo("ausencia_movimento", 0, t)]
    e = estados.estimar_estados(olhos, aus, 0, t)
    assert any(x.estado == "possivel_sono" and x.confiavel for x in e)


def test_olhos_nao_visiveis_nao_contam_como_fechados():
    # RN06
    t = int(config.AUSENCIA_PROLONGADA_S) + 60
    olhos = [EstadoOlhos(s, "indeterminado") for s in range(0, t + 1)]
    aus = [Intervalo("ausencia_movimento", 0, t)]
    e = estados.estimar_estados(olhos, aus, 0, t)
    assert all(x.estado == "indeterminado" and not x.confiavel for x in e)


def test_estados_cobrem_a_sessao_inteira():
    # RN08: todo trecho da sessão tem um estado associado a um intervalo.
    t = int(config.PERIODO_CONTINUO_OLHOS_S) + 10
    olhos = [EstadoOlhos(s, "abertos") for s in range(100, 100 + t + 1)]
    e = estados.estimar_estados(olhos, [], 0, 1000)
    assert e[0].inicio == 0 and e[-1].fim == 1000
    assert all(a.fim == b.inicio for a, b in zip(e, e[1:]))
    assert {x.estado for x in e} <= set(config.ESTADOS)
