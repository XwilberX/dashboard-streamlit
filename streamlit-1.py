import streamlit as st
import pandas as pd
import numpy as np
from scipy import  stats
import plotly.express as px
import plotly.figure_factory as ff
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
import pygal


###### funciones
def trim_mean_10(x):
    return stats.trim_mean(x, 0.1)

def percentile(n):
    def percentile_(x):
        return x.quantile(n)
    return percentile_

################

# configuracion de la pagina
st.set_page_config(
    page_title="Calidad del aire de la ZMVM",
    page_icon="icon.jpg",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.set_option('deprecation.showPyplotGlobalUse', False)
# @st.cache(show_spinner=False)

# READ DATA --------------------------------------------------------------------
# @st.cache(allow_output_mutation=True)
# def get_data():
df = pd.read_csv('BaseDatos_2016_2020.csv')
df = df.drop('Unnamed: 0', 1)

data  = df

data['date'] = pd.to_datetime(data['date'])

data['year'] = data['date'].dt.year

# data = get_data()

particulas = data.columns.values.tolist()

zonas = data['zone']
zonas = zonas.drop_duplicates()
zonas = zonas.values.tolist()

estaciones = data['id_station']
estaciones = estaciones.drop_duplicates()
estaciones = estaciones.values.tolist()

years = data['year']
years = years.drop_duplicates()
years = years.values.tolist()

with st.sidebar:
    st.title("Calidad del aire de la ZMVM")
    
    st.subheader("Seleccina zonas o estaciones:")

    modo = st.radio("Selecciona el modo de visualizacion",('Zonas', 'Estaciones'))

    if modo == 'Zonas':
        st.subheader("Seleccina una ZONA:")
        zona = st.selectbox("Zonas", zonas)
    elif modo == 'Estaciones':
        st.subheader("Seleccina una ESTACION:")
        estacion = st.selectbox("Estaciones", estaciones)

    st.subheader("Seleccina una particula:")

    particula = st.selectbox("Particulas", particulas[2:7])

    

    st.subheader("Seleccina un año:")

    year = st.selectbox("Años", years)

data = data.query('year==@year')

# "Boxplot del año " + str(year)

# ROW 1 ------------------------------------------------------------------------

row1_1, row1_2= st.beta_columns(2)

with row1_1:
    row1_1.subheader("Boxplot del año " + str(year))
    ax = sns.boxplot(x=particula, y='zone', data=data, palette='colorblind', hue='zone');
    ax.set(xlabel='Concentración ($\mu g/m^3$)', ylabel='Zona');
    ax.set_title('Boxplot por zona del año {} de {}'.format(year, particula), fontsize=15, fontweight='bold');

    st.pyplot()

with  row1_2:
    row1_2.subheader("KDE del año " + str(year))
    
    ax = sns.kdeplot(data=data, x=particula, hue='zone',fill=True, palette='Paired_r');
    ax.set(xlabel='Concentración ($\mu g/m^3$)', ylabel='Densidad');
    ax.set_title('Gráfica de densidad de $@particula$, por Zona', fontsize='15', fontweight='bold');

    st.pyplot()

# ROW 2 ------------------------------------------------------------------------

row2_1, row2_2= st.beta_columns(2)

with row2_1:
    row2_1.subheader("aun nose")

    sns.set(style='darkgrid')
    ax = sns.displot(data=data, x=particula, hue='zone', palette='Paired_r', multiple='stack');
    ax.set(xlabel='Concentración ($\mu g/m^3$)', ylabel='Frecuencia');
    plt.title('Histograma de distribución de ${}$, por Zona del {}'.format(particula, year), fontsize=15, fontweight='bold');

    st.pyplot()

# st.area_chart(data, use_container_width = False, width = 800)

if modo == 'Zonas':
    estimado = data.groupby('zone')[particula].agg(
                    media='mean',
                    mediana='median',
                    media_truncada=trim_mean_10,
                    desv_estandar='std',
                    minimo='min',
                    percentile_25=percentile(0.25),
                    percentile_50=percentile(0.5),
                    percentile_75=percentile(0.75),
                    maximo='max',
                    rango=np.ptp, # max - min
                    IQR=stats.iqr
                )
elif modo == 'Estaciones':
    estimado = data.groupby('id_station')[particula].agg(
                    media='mean',
                    mediana='median',
                    media_truncada=trim_mean_10,
                    desv_estandar='std',
                    minimo='min',
                    percentile_25=percentile(0.25),
                    percentile_50=percentile(0.5),
                    percentile_75=percentile(0.75),
                    maximo='max',
                    rango=np.ptp, # max - min
                    IQR=stats.iqr
                )

st.table(estimado.head(25))