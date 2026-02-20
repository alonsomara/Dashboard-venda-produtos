import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output

df = pd.read_csv('ecommerce_estatistica.csv')

# Criar gráficos
def cria_graficos(df):

    # Histograma - Distribuição do preço
    fig1 = px.histogram(
        df,
        x='Preço',
        nbins=30,
        title='Distribuição do Preço dos Produtos'
    )

    # Dispersão - Preço x Quantidade Vendida
    fig2 = px.scatter(
        df,
        x='Preço',
        y='Qtd_Vendidos_Cod',
        title='Preço x Quantidade Vendida'
    )

    # Mapa de Calor - Correlação
    base_corr = df[['Preço', 'Qtd_Vendidos_Cod', 'N_Avaliações_MinMax']].dropna()
    if base_corr.shape[0] >= 2:
        corr = base_corr.corr()
        fig3 = px.imshow(corr, text_auto=True, title='Mapa de Calor - Correlação')
    else:
        fig3 = px.imshow(
            [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            text_auto=True,
            title='Mapa de Calor - (sem informações suficientes)'
        )

    # Gráfico de Barras - Temporada
    temp = df['Temporada_Cod'].value_counts().reset_index()
    temp.columns = ['Temporada', 'Quantidade']

    fig4 = px.bar(
        temp,
        x='Temporada',
        y='Quantidade',
        title='Quantidade por Temporada'
    )

    # Pizza - Marca Keeper por Gênero
    keeper = df[df['Marca'].astype(str).str.lower() == 'keeper'].copy()
    if keeper.empty:
        fig5 = px.pie(
            values=[1],
            names=['Sem dados (Keeper)'],
            title='Distribuição da Marca Keeper por Gênero'
        )
    else:
        keeper_gen = keeper['Gênero'].fillna('Sem gênero').value_counts().reset_index()
        keeper_gen.columns = ['Gênero', 'Quantidade']

        fig5 = px.pie(
            keeper_gen,
            names='Gênero',
            values='Quantidade',
            title='Distribuição da Marca Keeper por Gênero'
        )

    # Densidade - Preço
    fig6 = px.density_heatmap(
        df,
        x='Preço',
        y='Qtd_Vendidos_Cod',
        nbinsx=30,
        nbinsy=30
    )

    fig6.update_layout(
        template='plotly_white',
        height=450,
        title='Densidade: Preço x Quantidade Vendida'
    )

    fig6.update_traces(opacity=0.85, colorscale="Blues")

    # Regressão - Preço x Quantidade Vendida
    fig7 = px.scatter(
        df,
        x='Preço',
        y='Qtd_Vendidos_Cod',
        trendline='ols',
        title='Regressão: Preço x Quantidade Vendida'
    )

    for fig in (fig1, fig2, fig3, fig4, fig5, fig6, fig7):
        fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))

    return fig1, fig2, fig3, fig4, fig5, fig6, fig7


# Criar app
app = Dash(__name__)

marcas = sorted(df['Marca'].dropna().astype(str).unique())
temps = sorted(df['Temporada_Cod'].dropna().unique())

preco_min = float(df['Preço'].min())
preco_max = float(df['Preço'].max())

app.layout = html.Div([
    html.H1("Dashboard - Análise de Venda de Produtos"),

    # Filtros
    html.Div([
        html.Div([
            html.Label("Marca"),
            dcc.Dropdown(
                id="filtro-marca",
                options=[{"label": m, "value": m} for m in marcas],
                value=[],
                multi=True,
                placeholder="Selecione marcas (vazio = todas)"
            ),
        ], style={"width": "33%", "display": "inline-block", "paddingRight": "10px"}),

        html.Div([
            html.Label("Temporada"),
            dcc.Dropdown(
                id="filtro-temporada",
                options=[{"label": str(t), "value": t} for t in temps],
                value=[],
                multi=True,
                placeholder="Selecione temporadas (vazio = todas)"
            ),
        ], style={"width": "33%", "display": "inline-block", "paddingRight": "10px"}),

        html.Div([
            html.Label("Faixa de Preço"),
            dcc.RangeSlider(
                id="filtro-preco",
                min=preco_min,
                max=preco_max,
                value=[preco_min, preco_max],
                allowCross=False,
                tooltip={"placement": "bottom", "always_visible": False},
            ),
        ], style={"width": "33%", "display": "inline-block"}),
    ], style={"marginBottom": "15px"}),

    # Gráficos com id
    dcc.Graph(id="graf1"),
    dcc.Graph(id="graf2"),
    dcc.Graph(id="graf3"),
    dcc.Graph(id="graf4"),
    dcc.Graph(id="graf5"),
    dcc.Graph(id="graf6"),
    dcc.Graph(id="graf7"),
])

# Callback
@app.callback(
    Output("graf1", "figure"),
    Output("graf2", "figure"),
    Output("graf3", "figure"),
    Output("graf4", "figure"),
    Output("graf5", "figure"),
    Output("graf6", "figure"),
    Output("graf7", "figure"),
    Input("filtro-marca", "value"),
    Input("filtro-temporada", "value"),
    Input("filtro-preco", "value"),
)
def atualizar(marcas_sel, temps_sel, faixa_preco):

    if not marcas_sel:
        marcas_sel = marcas
    if not temps_sel:
        temps_sel = temps

    pmin, pmax = faixa_preco

    dff = df[
        (df["Marca"].astype(str).isin([str(m) for m in marcas_sel])) &
        (df["Temporada_Cod"].isin(temps_sel)) &
        (df["Preço"].between(pmin, pmax))
    ].copy()

    return cria_graficos(dff)


# Executar app
if __name__ == '__main__':
    app.run(debug=True)