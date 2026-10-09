
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard dos Clubes",
    page_icon="⚽",
    layout="wide"
)

# Estilo visual
st.markdown("""
<style>
.stApp {
    background-color: #0e1117;
}
[data-testid="stMetric"] {
    background-color: #1c2333;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #303849;
}
</style>
""", unsafe_allow_html=True)

# Título
st.title("⚽ Dashboard dos Clubes")
st.caption("Painel de análise de dados do futebol")

# Carregar dados
arquivo = st.file_uploader(
    "📂 Envie sua tabela Tabela_Clubes.csv",
    type=["csv"]
)

if arquivo is None:
    st.info("Envie o arquivo CSV para visualizar o dashboard.")
    st.stop()

df = pd.read_csv(arquivo)

# Remover coluna de índice
df = df.loc[:, ~df.columns.str.startswith("Unnamed")]

# Converter colunas numéricas
colunas_numericas = [
    "Ano", "Pos.", "Vitorias", "Derrotas", "Empates",
    "Saldo", "Qtd_Jogadores", "Estrangeiros",
    "Valor_total", "Media_Valor"
]

for coluna in colunas_numericas:
    if coluna in df.columns:
        df[coluna] = pd.to_numeric(df[coluna], errors="coerce")

if "Idade_Media" in df.columns:
    df["Idade_Media"] = pd.to_numeric(
        df["Idade_Media"].astype(str).str.replace(",", "."),
        errors="coerce"
    )

if "Clubes" not in df.columns or "Ano" not in df.columns:
    st.error("A tabela precisa ter as colunas Clubes e Ano.")
    st.stop()

# Filtros laterais
st.sidebar.title("🎛️ Filtros")

anos = sorted(df["Ano"].dropna().unique())
anos_selecionados = st.sidebar.multiselect(
    "Temporada",
    anos,
    default=anos
)

clubes = sorted(df["Clubes"].dropna().unique())
clubes_selecionados = st.sidebar.multiselect(
    "Clubes",
    clubes,
    default=clubes
)

dados = df[
    df["Ano"].isin(anos_selecionados)
    & df["Clubes"].isin(clubes_selecionados)
].copy()

if dados.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
    st.stop()

# Indicadores principais
st.subheader("📊 Indicadores gerais")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Clubes", dados["Clubes"].nunique())
c2.metric("Registros", len(dados))

if "Vitorias" in dados.columns:
    c3.metric("Vitórias", int(dados["Vitorias"].sum()))

if "Saldo" in dados.columns:
    c4.metric("Saldo de gols", int(dados["Saldo"].sum()))

st.divider()

# Gráficos
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Ranking de vitórias")

    if "Vitorias" in dados.columns:
        ranking = (
            dados.groupby("Clubes")["Vitorias"]
            .sum()
            .nlargest(10)
            .reset_index()
        )

        fig1 = px.bar(
            ranking.sort_values("Vitorias"),
            x="Vitorias",
            y="Clubes",
            orientation="h",
            text="Vitorias",
            title="Top 10 clubes"
        )

        fig1.update_layout(
            template="plotly_dark",
            yaxis_title="",
            xaxis_title="Vitórias"
        )

        st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("💰 Valor dos elencos")

    if "Valor_total" in dados.columns:
        valores = (
            dados.groupby("Clubes")["Valor_total"]
            .mean()
            .nlargest(10)
            .reset_index()
        )

        fig2 = px.bar(
            valores,
            x="Clubes",
            y="Valor_total",
            title="Top 10 por valor do elenco"
        )

        fig2.update_layout(
            template="plotly_dark",
            xaxis_title="Clube",
            yaxis_title="Valor total"
        )

        st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.subheader("📈 Posição por temporada")

    if "Pos." in dados.columns:
        posicoes = dados.groupby(
            "Ano", as_index=False
        )["Pos."].mean()

        fig3 = px.line(
            posicoes,
            x="Ano",
            y="Pos.",
            markers=True,
            title="Evolução da posição média"
        )

        fig3.update_layout(template="plotly_dark")
        fig3.update_yaxes(autorange="reversed")

        st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("⚖️ Resultados")

    colunas = [
        c for c in ["Vitorias", "Empates", "Derrotas"]
        if c in dados.columns
    ]

    if colunas:
        resultados = (
            dados[colunas]
            .sum()
            .rename_axis("Resultado")
            .reset_index(name="Quantidade")
        )

        fig4 = px.pie(
            resultados,
            names="Resultado",
            values="Quantidade",
            hole=0.45,
            title="Vitórias, empates e derrotas"
        )

        fig4.update_layout(template="plotly_dark")
        st.plotly_chart(fig4, use_container_width=True)

# Perfil dos elencos
st.subheader("👥 Perfil dos elencos")

a, b, c = st.columns(3)

if "Qtd_Jogadores" in dados.columns:
    a.metric(
        "Média de jogadores",
        round(dados["Qtd_Jogadores"].mean(), 1)
    )

if "Idade_Media" in dados.columns:
    b.metric(
        "Idade média",
        round(dados["Idade_Media"].mean(), 1)
    )

if "Estrangeiros" in dados.columns:
    c.metric(
        "Média de estrangeiros",
        round(dados["Estrangeiros"].mean(), 1)
    )

# Tabela
st.divider()
st.subheader("🔎 Consultar dados")

pesquisa = st.text_input("Pesquisar clube")

tabela = dados.copy()

if pesquisa:
    tabela = tabela[
        tabela["Clubes"].astype(str).str.contains(
            pesquisa,
            case=False,
            na=False
        )
    ]

st.dataframe(
    tabela,
    use_container_width=True,
    hide_index=True
)

# Exportação
st.download_button(
    "📥 Exportar tabela filtrada",
    data=tabela.to_csv(index=False).encode("utf-8-sig"),
    file_name="clubes_filtrados.csv",
    mime="text/csv"
)

st.caption("Dashboard desenvolvido com Python, Pandas, Plotly e Streamlit.")
