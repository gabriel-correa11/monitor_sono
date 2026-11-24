"""RF13, RF14, RF15, RNF07, RNF10, RNF12 — Dashboard Streamlit.

Rodar com: streamlit run src/monitor_sono/dashboard/app.py
Lê os dados só pelo módulo registro; não abre o banco diretamente nem roda a câmera.
"""

from datetime import datetime, timedelta

import altair as alt
import pandas as pd
import streamlit as st

from monitor_sono import config
from monitor_sono.registro import banco

NOMES = {
    "movimento_corporal": "Movimento corporal",
    "mudanca_posicao": "Mudança de posição",
    "ausencia_movimento": "Sem movimento",
    "maior_atividade_motora": "Maior atividade motora",
    "visibilidade_insuficiente": "Câmera sem visão",
    "olhos_abertos": "Olhos abertos",
    "olhos_fechados": "Olhos fechados",
    "movimento_cabeca": "Movimento da cabeça",
    "vigilia": "Acordado (estimado)",
    "possivel_sono": "Possível sono (estimado)",
    "indeterminado": "Indeterminado",
}


def _tabela(linhas, coluna_tipo: str) -> pd.DataFrame:
    df = pd.DataFrame([dict(l) for l in linhas])
    if df.empty:
        return df
    df["inicio"] = pd.to_datetime(df["inicio"])
    df["fim"] = pd.to_datetime(df["fim"]).fillna(df["inicio"])
    # Eventos instantâneos ganham 1 minuto de largura só para aparecer na linha do tempo.
    df["fim_grafico"] = df[["fim"]].max(axis=1).where(df["fim"] > df["inicio"], df["inicio"] + timedelta(minutes=1))
    df["nome"] = df[coluna_tipo].map(NOMES).fillna(df[coluna_tipo])
    df["duracao_min"] = (df["fim"] - df["inicio"]).dt.total_seconds() / 60
    return df


st.set_page_config(page_title="Monitor de Sono", layout="wide")
st.title("Monitor de Sono")
st.warning(config.AVISO_NAO_DIAGNOSTICO)  # RNF12

sessoes = banco.listar_sessoes()
if not sessoes:
    st.info("Nenhuma sessão gravada. Analise uma gravação com: python -m monitor_sono analisar <arquivo> --autorizado")
    st.stop()

rotulos = {s["id"]: f"Sessão {s['id']} — {s['inicio'].replace('T', ' ')}" for s in sessoes}
sessao_id = st.selectbox("Sessão", list(rotulos), format_func=rotulos.get)
sessao = next(s for s in sessoes if s["id"] == sessao_id)

comp = _tabela(banco.comportamentos_da_sessao(sessao_id), "tipo")
est = _tabela(banco.estados_da_sessao(sessao_id), "estado")

inicio = datetime.fromisoformat(sessao["inicio"])
fim = datetime.fromisoformat(sessao["fim"]) if sessao["fim"] else inicio
duracao_min = (fim - inicio).total_seconds() / 60


def _contar(tipo: str) -> int:
    return int((comp["tipo"] == tipo).sum()) if not comp.empty else 0


def _minutos(tipo: str) -> float:
    return float(comp.loc[comp["tipo"] == tipo, "duracao_min"].sum()) if not comp.empty else 0.0


# --- RF14: relatório ---------------------------------------------------------------------------------
st.header("Resumo da sessão")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Duração", f"{duracao_min / 60:.0f} h {duracao_min % 60:.0f} min")
c2.metric("Períodos de movimento", _contar("movimento_corporal"))
c3.metric("Mudanças de posição", _contar("mudanca_posicao"))
c4.metric("Tempo sem movimento", f"{_minutos('ausencia_movimento'):.0f} min")

# --- RF13 e RNF07: histórico cronológico, observado separado do estimado --------------------------------
st.header("Linha do tempo")
st.caption(
    "**Observado** é o que a câmera registrou. **Estimado** é a conclusão do sistema a partir do que foi "
    "observado. Estimativas não são diagnóstico."
)


def _linha_do_tempo(df: pd.DataFrame, cor: str) -> alt.Chart:
    altura = 34 * max(df["nome"].nunique(), 1) + 40
    return (
        alt.Chart(df)
        .mark_bar(color=cor, height=16)
        .encode(
            x=alt.X("inicio:T", title="Horário", axis=alt.Axis(format="%H:%M"),
                    scale=alt.Scale(domain=[inicio.isoformat(), fim.isoformat()])),
            x2="fim_grafico:T",
            y=alt.Y("nome:N", title=None, axis=alt.Axis(labelLimit=260)),
            tooltip=[
                alt.Tooltip("nome:N", title="O quê"),
                alt.Tooltip("inicio:T", title="Início", format="%H:%M:%S"),
                alt.Tooltip("fim:T", title="Fim", format="%H:%M:%S"),
            ],
        )
        .properties(height=altura)
    )


if not comp.empty:
    st.subheader("Observado")
    st.altair_chart(_linha_do_tempo(comp, "#3B6EA8"), width="stretch")
if not est.empty:
    st.subheader("Estimado")
    st.altair_chart(_linha_do_tempo(est, "#9A9A9A"), width="stretch")

# --- Estados estimados ------------------------------------------------------------------------------
st.header("Estados estimados")
if not est.empty:
    tempo = est.groupby("nome")["duracao_min"].sum()
    total = tempo.sum() or 1
    st.dataframe(
        pd.DataFrame({"Minutos": tempo.round(0), "% do tempo": (100 * tempo / total).round(0)}).rename_axis("Estado"),
        width="stretch",
    )
    if (est["estado"] == "indeterminado").all():
        st.info(
            "Todo o tempo ficou **indeterminado**. Nesta versão o sistema ainda não detecta os olhos (RF05), "
            "e pelas regras RN02, RN03 e RN06 a falta de movimento sozinha não basta para estimar sono."
        )

# --- RF15: avisos de visibilidade ---------------------------------------------------------------------
st.header("Avisos: câmera sem visão adequada")
avisos = comp[comp["tipo"] == "visibilidade_insuficiente"] if not comp.empty else comp
if avisos.empty:
    st.success("A câmera observou a cena durante toda a sessão.")
else:
    st.dataframe(
        avisos[["inicio", "fim", "duracao_min"]].rename(
            columns={"inicio": "Início", "fim": "Fim", "duracao_min": "Duração (min)"}
        ),
        width="stretch",
        hide_index=True,
    )

# --- RF14: relatório para baixar ----------------------------------------------------------------------
st.header("Relatório")
relatorio = pd.concat(
    [
        comp.assign(categoria="Observado")[["categoria", "nome", "inicio", "fim"]] if not comp.empty else None,
        est.assign(categoria="Estimado")[["categoria", "nome", "inicio", "fim"]] if not est.empty else None,
    ],
    ignore_index=True,
)
relatorio.columns = ["Categoria", "Comportamento ou estado", "Início", "Fim"]
st.download_button(
    "Baixar relatório (CSV)",
    data=("# " + config.AVISO_NAO_DIAGNOSTICO + "\n" + relatorio.to_csv(index=False)).encode("utf-8-sig"),
    file_name=f"relatorio_sessao_{sessao_id}.csv",
    mime="text/csv",
)

# --- RNF10: exclusão dos dados da sessão --------------------------------------------------------------
with st.expander("Excluir os dados desta sessão"):
    st.write("Apaga a sessão e todos os comportamentos e estados registrados nela. Não pode ser desfeito.")
    confirmar = st.checkbox("Confirmo que quero excluir esta sessão")
    if st.button("Excluir sessão", type="primary", disabled=not confirmar):
        banco.excluir_sessao(sessao_id)
        st.success("Sessão excluída.")
        st.rerun()
