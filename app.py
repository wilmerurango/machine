import streamlit as st
import warnings
import holidays
import numpy as np
import pandas as pd
import seaborn as sns
import plotly.express as px
import requests
sns.set_style("darkgrid")


@st.cache(allow_output_mutation=True)
def import_transform_data():
    Loggedin = pd.read_csv(
        "C:/Users/Wilmer/Documents/DIPLOMADO/AnalisisDeDatos/env/project_unicor/Grupo1_HernandezMorenoUrangoAlvarezDurango/mdl_informes_2022_1_user_loggedin.csv", sep=";")

    Loggedin["timecreated"] = pd.to_datetime(
        Loggedin["timecreated_unix"], unit="s")

    Variables = np.array(["eventname", "component", "action", "target", "objecttable", "crud", "edulevel",
                          "courseid", "relateduserid", "origin", "realuserid", "cur_id", "cur_idnumber",
                          "cur_shortname", "cur_fullname", "cur_category", "cur_startdate", "cur_enddate",
                          "prog_id", "prog_idnumber", "fac_idnumber", "fac_facultad", "id", "userid", "other",
                          "timecreated_unix", "ip", "usr_id", "usr_idnumber"])
    Loggedin.drop(columns=Variables, inplace=True)
    # reindexar el dataframe
    Loggedin.index = Loggedin.timecreated

    Loggedin = Loggedin.replace({'prog_programa': {'Departamento De Geografía Y Medio Ambien': 'Dpto de GeografIa y Medio Ambiente',
                                                   'BIOLOGÍA': 'Biología', 'QUÍMICA': 'Química',
                                                   'LIC EN CIENCIAS NATURALES Y EDU AMBIENTA': 'Lic en Ciencias Naturales y Edu Ambienta',
                                                   'INGENIERÍA INDUSTRIAL': 'Ingeniería Industrial',
                                                   'Adminis. en Finanzas y Negocios Internac': 'Administración en Finanzas y Negocios Internacionales'}})

    loggedin_day = Loggedin.usr_username.resample('H').count()[19:-5]

    warnings.filterwarnings('ignore')

    df = pd.concat([loggedin_day], axis=1)

    df['dayofweek'] = df.index.dayofweek  # Dia de la semana
    # Mes (Numero de meses contados en 30 dias)
    df['monthh'] = (df.index.day_of_year-80)//30+1
    df['weekk'] = df.index.weekofyear-11  # Numero de la semana del semestre
    df['hourr'] = df.index.hour  # Hora del dia
    df['court'] = (df.index.day_of_year-80)//46 + \
        1  # corte academico en el semestre
    df['dayofsemester'] = df.index.day_of_year-80  # Dia en el semestre
    df['dayofmonth'] = df['dayofsemester'] - \
        30*(df['monthh']-1)  # Dia en el mes
    df['dayofcuort'] = df['dayofsemester'] - \
        46*(df['court']-1)  # Dia en el corte
    df['serie'] = df.index.date
    co_holidays = holidays.CO()  # Dias festuvos
    df['holidayss'] = np.where(df['serie'].isin(
        co_holidays), '1', '0')  # 1 si es festivo
    df = df.rename(
        columns={'usr_username': 'loggedin'}
    )

    return df


@st.cache(allow_output_mutation=True)
def grafico_barra(data, x='serie', y='loggedin', title='Número de Logueos de Cintia en Función del Tiempo'):

    fig = px.bar(
        data,
        x=x,
        y=y,
        color_discrete_sequence=['Blue'],
        title=title
    )

    fig.update_layout(yaxis_title='Cantidad de Logues', xaxis_title='Fecha')
    # fig.update_layout({'plot_bgcolor':'rgba(0,0,0,0)','paper_bgcolor':'rgba(0,0,0,0)' })

    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(step='day', stepmode='backward', label='1 dia', count=1),
                dict(step='day', stepmode='backward',
                     label='1 semana', count=7),
                dict(step='month', stepmode='backward', label='1 mes', count=1),
                dict(step='month', stepmode='backward', label='3 mes', count=3),
                dict(step='all', label='Todos')
            ])
        ),
    )

    fig.update_xaxes(dtick='M1', ticklabelmode='period',
                     tickformat='%d %b\n%Y')

    return fig


@st.cache(allow_output_mutation=True)
def request_api(dia, mes, anio, hora):
    request_data = [
        {
            'dia': dia,
            'mes': mes,
            'anio': anio,
            'hora': hora
        }
    ]

    data_cleaned = str(request_data).replace("'", '"')
    url_api = "http://127.0.0.1:8000/predic"

    pred = requests.post(url=url_api, data=data_cleaned).text

    pred_df = pd.read_json(pred)

    return pred_df


df = import_transform_data()
fig = grafico_barra(df)


col1, col2 = st.columns([1, 4])
col1.markdown("""
**DESCRIPCION**

Estos son los graficos de los datos

""")
col2.plotly_chart(fig, use_container_width=True)


st.sidebar.header('MENU DE PREDICCIÓN')
st.sidebar.markdown('Por favor Diligenciar fecha y hora')

hora = st.sidebar.number_input(label='Hora', max_value=24, min_value=0)
dia = st.sidebar.number_input(label='Día', max_value=31, min_value=1)
mes = st.sidebar.number_input(label='Mes', max_value=31, min_value=1)
anio = st.sidebar.number_input(label='Año mayor a 2022', min_value=2022,value=2022)

btn_predecir = st.sidebar.button(label='PREDECIR LOGUEOS')

if btn_predecir:
    prediccion = request_api(dia, mes, anio, hora)
    st.metric(value=f'{prediccion["employee_left"][0]}', label='Cantidad de loguesos Pronosticados en la fecha indicada')

st.sidebar.header('MENU DE TENDENCIA')
