# Análise de Dados do Spotify 2023

Este projeto é uma aplicação Streamlit que realiza uma análise abrangente dos dados do Spotify para o ano de 2023. A aplicação oferece visualizações interativas e insights sobre popularidade de artistas, impacto de playlists, tendências temporais, características musicais e comparações entre artistas solo e colaborativos.


### Base de dados
Link da base:https://www.kaggle.com/datasets/nelgiriyewithana/top-spotify-songs-2023 
- Colunas:
* **track_name**: Nome da música
* **artist(s)_name**: Nome do(s) artista(s) da música
* **artist_count**: Número de artistas que contribuíram para a música
* **released_year**: Ano em que a música foi lançada
* **released_month**: Mês em que a música foi lançada
* **released_day**: Dia do mês em que a música foi lançada
* **in_spotify_playlists**: Número de playlists do Spotify em que a música está incluída
* **in_spotify_charts**: Presença e posição da música nas paradas do Spotify
* **streams**: Número total de reproduções no Spotify
* **in_apple_playlists**: Número de playlists do Apple Music em que a música está incluída
* **in_apple_charts**: Presença e posição da música nas paradas do Apple Music
* **in_deezer_playlists**: Número de playlists do Deezer em que a música está incluída
* **in_deezer_charts**: Presença e posição da música nas paradas do Deezer
* **in_shazam_charts**: Presença e posição da música nas paradas do Shazam
* **bpm**: Batidas por minuto, uma medida do tempo da música
* **key**: Tonalidade da música
* **mode**: Modo da música (maior ou menor)
* **danceability_%**: Porcentagem que indica o quão adequada a música é para dançar
* **valence_%**: Positividade do conteúdo musical da música
* **energy_%**: Nível percebido de energia da música
* **acousticness_%**: Quantidade de som acústico na música
* **instrumentalness_%**: Quantidade de conteúdo instrumental na música
* **liveness_%**: Presença de elementos de performance ao vivo
* **speechiness_%**: Quantidade de palavras faladas na música








## Tratamento de Dados

O tratamento de dados é uma etapa crucial neste projeto. Aqui estão os principais passos:

1. **Encoding dos nomes dos artistas:**
   ```python
   df['artist(s)_name'] = df['artist(s)_name'].str.encode('utf-8', errors='ignore').str.decode('utf-8')
   ```
   Garante a correta codificação dos nomes dos artistas em UTF-8.

2. **Remoção de valores anômalos:**
   ```python
   df = df[df['streams'] != valor_anomalo]
   ```
   Remove uma linha específica com valor anômalo na coluna 'streams'.

3. **Conversão de colunas para tipo numérico:**
   ```python
   numeric_columns = ['streams', 'in_deezer_playlists', 'in_shazam_charts']
   for col in numeric_columns:
       df[col] = pd.to_numeric(df[col], errors='coerce')
   ```
   Assegura que colunas específicas sejam tratadas como números.

4. **Tratamento de valores ausentes:**
   ```python
   df['key'] = df['key'].fillna('Unknown')
   ```
   Preenche valores ausentes na coluna 'key'.

5. **Normalização de colunas de porcentagem:**
   ```python
   percentage_columns = ['danceability_%', 'valence_%', 'energy_%', 'acousticness_%',
                         'instrumentalness_%', 'liveness_%', 'speechiness_%']
   for col in percentage_columns:
       df[col] = df[col] / 100
       df = df.rename(columns={col: col.replace('_%', '')})
   ```
   Converte porcentagens para escala de 0 a 1 e renomeia as colunas.

6. **Criação de coluna de data de lançamento:**
   ```python
   df['release_date'] = pd.to_datetime(df[['released_year', 'released_month', 'released_day']].astype(str).agg('-'.join, axis=1))
   ```
   Combina ano, mês e dia em uma única coluna de data.

7. **Remoção de linhas com valores ausentes:**
   ```python
   df = df.dropna()
   ```
   Elimina linhas com valores ausentes após todos os tratamentos.

## Funcionalidades

A aplicação inclui várias análises interativas:

1. **Análise de popularidade de artistas:** Visualiza os artistas mais populares com base no número de streams.

2. **Impacto da presença em playlists nos streams:** Analisa a relação entre a presença em playlists e o número de streams.

3. **Análise temporal de streams e playlists:** Examina tendências anuais e mensais de streams e presença em playlists.

4. **Análise de características musicais e presença nos charts:** Explora como diferentes características musicais afetam a presença em charts.

5. **Comparação entre artistas solo e colaborativos:** Compara o desempenho de artistas solo versus colaborações.

6. **Correlações entre características musicais e streams:** Visualiza correlações entre diferentes atributos musicais e popularidade.


  
