import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

df = pd.read_csv('spotify-2023.csv', encoding='ISO-8859-1')


df['artist(s)_name'] = df['artist(s)_name'].str.encode(
    'utf-8', errors='ignore').str.decode('utf-8')

valor_anomalo = 'BPM110KeyAModeMajorDanceability53Valence75Energy69Acousticness7Instrumentalness0Liveness17Speechiness3'

# Removendo a linha que contém o valor anômalo na coluna 'streams'
df = df[df['streams'] != valor_anomalo]


def treat_data(df):
    numeric_columns = ['streams', 'in_deezer_playlists', 'in_shazam_charts']
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df['key'] = df['key'].fillna('Unknown')

    percentage_columns = ['danceability_%', 'valence_%', 'energy_%', 'acousticness_%',
                          'instrumentalness_%', 'liveness_%', 'speechiness_%']
    for col in percentage_columns:
        df[col] = df[col] / 100
        df = df.rename(columns={col: col.replace('_%', '')})

    df['release_date'] = pd.to_datetime(
        df[['released_year', 'released_month', 'released_day']].astype(str).agg('-'.join, axis=1))

    df = df.dropna()

    return df


# Aplicando o tratamento
df = treat_data(df)

###################################################

st.title('Análise de popularidade de artistas')

st.sidebar.header('Controles - Análise de popularidade de artistas')

# Slider para selecionar o número de artistas top
num_artistas = st.sidebar.slider('Número de artistas top', 5, 50, 10)

ordem_invertida = st.sidebar.checkbox(
    'Mostrar artistas mais populares primeiro', value=True)

tipo_stream = st.sidebar.radio('Tipo de streams', ['Total', 'Médio'])

if tipo_stream == 'Total':
    df_grouped = df.groupby('artist(s)_name')['streams'].sum().reset_index()
else:
    df_grouped = df.groupby('artist(s)_name')['streams'].mean().reset_index()

df_sorted = df_grouped.sort_values(
    'streams', ascending=not ordem_invertida).head(num_artistas)

fig = px.bar(df_sorted,
             x='streams',
             y='artist(s)_name',
             orientation='h',
             title=f'Top {num_artistas} Artistas por Número de Streams {tipo_stream}s',
             labels={'streams': 'Número de Streams', 'artist(s)_name': 'Artista'})

fig.update_layout(yaxis={'categoryorder': 'total ascending'})

st.plotly_chart(fig)

# Adicionar algumas estatísticas
st.write('Estatísticas:')
st.write(
    f"Total de streams para estes artistas: {df_sorted['streams'].sum():,}")
st.write(f"Média de streams por artista: {df_sorted['streams'].mean():,.2f}")

############################################

st.title('Impacto da Presença em Playlists nos Streams por Plataforma')

fig = go.Figure()

platforms = ['spotify', 'apple', 'deezer']
colors = ['blue', 'red', 'green']

for platform, color in zip(platforms, colors):
    fig.add_trace(go.Scatter(
        x=df[f'in_{platform}_playlists'],
        y=df['streams'],
        mode='markers',
        name=platform.capitalize(),
        marker=dict(color=color, opacity=0.3),
    ))

    x = df[f'in_{platform}_playlists']
    y = df['streams']
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    fig.add_trace(go.Scatter(
        x=x,
        y=p(x),
        mode='lines',
        name=f'{platform.capitalize()} (Regressão)',
        line=dict(color=color)
    ))

fig.update_layout(
    title='Impacto da Presença em Playlists nos Streams por Plataforma',
    xaxis_title='Número de Playlists',
    yaxis_title='Número de Streams',
    legend_title='Plataforma',
    height=600,
    width=900
)

st.plotly_chart(fig)

##########################################################

st.title('Análise temporal de streams e playlists')

st.sidebar.header('Controles - Análise temporal de streams e playlists')

# Checkbox para escolher entre análise anual ou mensal
analysis_type = st.sidebar.radio(
    "Escolha o tipo de análise:", ('Anual', 'Mensal'))


def create_plot(data, x_col, title, x_title, x_tickvals=None, x_ticktext=None):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(x=data[x_col], y=data['streams'], name="Streams"),
        secondary_y=False,
    )

    for platform in ['spotify', 'apple', 'deezer']:
        fig.add_trace(
            go.Scatter(
                x=data[x_col], y=data[f'in_{platform}_playlists'], name=f"{platform.capitalize()} Playlists"),
            secondary_y=True,
        )

    fig.update_layout(
        title_text=title,
        xaxis_title=x_title,
    )

    if x_tickvals and x_ticktext:
        fig.update_xaxes(tickmode='array', tickvals=x_tickvals,
                         ticktext=x_ticktext)

    fig.update_yaxes(title_text="Média de Streams", secondary_y=False)
    fig.update_yaxes(
        title_text="Média de Presença em Playlists", secondary_y=True)

    return fig


if analysis_type == 'Anual':
    yearly_data = df.groupby(df['release_date'].dt.year).agg({
        'streams': 'mean',
        'in_spotify_playlists': 'mean',
        'in_apple_playlists': 'mean',
        'in_deezer_playlists': 'mean'
    }).reset_index()

    fig = create_plot(yearly_data, 'release_date',
                      "Tendência Anual: Streams e Presença em Playlists", "Ano de Lançamento")
    st.plotly_chart(fig)

    st.write("Correlação entre ano de lançamento e streams:",
             df['released_year'].corr(df['streams']))

else:
    monthly_data = df.groupby(df['release_date'].dt.month).agg({
        'streams': 'mean',
        'in_spotify_playlists': 'mean',
        'in_apple_playlists': 'mean',
        'in_deezer_playlists': 'mean'
    }).reset_index()

    months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
              'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    fig = create_plot(monthly_data, 'release_date', "Sazonalidade Mensal: Streams e Presença em Playlists",
                      "Mês de Lançamento", x_tickvals=list(range(1, 13)), x_ticktext=months)
    st.plotly_chart(fig)

    monthly_corr = df.groupby(df['release_date'].dt.month)[
        'streams'].mean().corr(pd.Series(range(1, 13)))
    st.write("Correlação entre mês de lançamento e streams:", monthly_corr)

##########################################

st.title('Análise de características musicais e presença nos charts')

st.sidebar.header('Controles - Análise de características musicais e presença nos charts')

# Seleção da característica musical
feature_options = ['danceability', 'energy', 'acousticness', 'instrumentalness', 'liveness', 'speechiness', 'valence']
selected_feature = st.sidebar.selectbox('Escolha a característica musical:', feature_options)

def create_categories(df, feature):
    return pd.cut(df[feature], 
                  bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
                  labels=['Muito Baixa', 'Baixa', 'Média', 'Alta', 'Muito Alta'])

df['feature_category'] = create_categories(df, selected_feature)

# Calcular médias por categoria
feature_stats = df.groupby('feature_category').agg({
    'in_spotify_charts': 'mean',
    'in_apple_charts': 'mean',
    'in_deezer_charts': 'mean',
    'in_shazam_charts': 'mean',
    'streams': 'mean'
}).reset_index()

fig = go.Figure()

for chart in ['in_spotify_charts', 'in_apple_charts', 'in_deezer_charts', 'in_shazam_charts']:
    fig.add_trace(go.Bar(
        x=feature_stats['feature_category'],
        y=feature_stats[chart],
        name=chart.replace('in_', '').replace('_charts', '').capitalize()
    ))

fig.update_layout(
    title=f'Presença nos Charts por Categoria de {selected_feature.replace("_%", "")}',
    xaxis_title=f'Categoria de {selected_feature.replace("_%", "")}',
    yaxis_title='Média de Presença nos Charts',
    barmode='group'
)

st.plotly_chart(fig)

# Adicionar estatísticas
st.subheader('Estatísticas por Categoria')
st.write(feature_stats)

#################################################

st.title('Análise comparativa: artistas solo vs. colaborativos')

df['is_collaborative'] = df['artist_count'] > 1

# Calcular médias para métricas de sucesso
success_metrics = ['streams', 'in_spotify_playlists', 'in_apple_playlists', 'in_deezer_playlists']
avg_metrics = df.groupby('is_collaborative')[success_metrics].mean().reset_index()

fig = make_subplots(rows=2, cols=2, subplot_titles=("Streams", "Spotify Playlists", "Apple Music Playlists", "Deezer Playlists"))

for i, metric in enumerate(success_metrics):
    row = i // 2 + 1
    col = i % 2 + 1
    
    fig.add_trace(
        go.Bar(x=['Solo', 'Collaborative'], 
               y=avg_metrics[metric],
               text=avg_metrics[metric].round(0),
               textposition='auto',
               name=metric),
        row=row, col=col
    )

fig.update_layout(height=700, width=800, title_text="Comparação de Métricas de Sucesso: Artistas Solo vs. Colaborativos")
fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

st.plotly_chart(fig)

# Calcular e mostrar percentuais de aumento/diminuição
st.subheader('Impacto Percentual das Colaborações')
for metric in success_metrics:
    solo_value = avg_metrics.loc[avg_metrics['is_collaborative'] == False, metric].values[0]
    collab_value = avg_metrics.loc[avg_metrics['is_collaborative'] == True, metric].values[0]
    percent_change = ((collab_value - solo_value) / solo_value) * 100
    st.write(f"{metric}: {percent_change:.2f}% {'aumento' if percent_change > 0 else 'diminuição'} para colaborações")

##########################################################

st.title('Correlações entre características musicais e streams')

st.sidebar.header('Controles - Correlações entre características musicais e streams')

# Seleção de características
all_features = ['danceability', 'valence', 'energy', 'acousticness', 'streams']
selected_features = st.sidebar.multiselect(
    'Escolha as características para análise:',
    all_features,
    default=all_features
)

# Calcular a matriz de correlação
correlation_matrix = df[selected_features].corr()

fig = go.Figure(data=go.Heatmap(
                    z=correlation_matrix.values,
                    x=correlation_matrix.columns,
                    y=correlation_matrix.columns,
                    hoverongaps = False,
                    texttemplate="%{z:.2f}",
                    colorscale='RdBu'))

fig.update_layout(
    title='Mapa de Calor de Correlações',
    xaxis_title='Características',
    yaxis_title='Características'
)

st.plotly_chart(fig)

# Gráfico de dispersão
st.subheader('Gráfico de Dispersão')
x_axis = st.selectbox('Escolha a característica para o eixo X:', selected_features)
y_axis = st.selectbox('Escolha a característica para o eixo Y:', 
                      [feat for feat in selected_features if feat != x_axis], 
                      index=1)

fig_scatter = go.Figure(data=go.Scatter(
    x=df[x_axis],
    y=df[y_axis],
    mode='markers',
    marker=dict(
        size=5,
        color=df['streams'],
        colorscale='Viridis',
        showscale=True
    ),
    text=df['track_name'] + ' - ' + df['artist(s)_name'],
    hoverinfo='text'
))

fig_scatter.update_layout(
    title=f'{x_axis.capitalize()} vs {y_axis.capitalize()}',
    xaxis_title=x_axis.capitalize(),
    yaxis_title=y_axis.capitalize(),
    coloraxis_colorbar=dict(title="Streams")
)

st.plotly_chart(fig_scatter)