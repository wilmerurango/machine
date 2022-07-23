from pydantic import BaseModel as BM
from pydantic import Field
import joblib
import warnings
import holidays
import numpy as np
import pandas as pd

class InputModel(BM):
    """
    Este modelo define las entradas que debera ingresar el usuario
    """
    dia : int = Field(ge=1, le=31)
    mes : int = Field(ge=1, le=12)
    anio : int = Field(ge=2022)
    hora : int = Field(ge=0, le=24)

    class Config:
        scheme_extra = {
            "example": {

                'dia': 10,
                'mes': 9,
                'anio': 10,
                'hora': 10,
            }
        }


class OutputModel(BM):
    """
    Este modelo define las salidas que verá el usuario
    """
    cantidad_logueo: float = Field(
        ge=0.0, le=10000000000.0, description="Aqui se escribe la cantidad de logueos de salida en una fecha dada")

    class Config:
        scheme_extra = {
            "example": {
                "cantidad_logueo": 100.0,
            }
        }




class APIModelBackEnd:
    
    def __init__(self, dia,mes,anio,hora):
        self.dia= dia
        self.mes= mes
        self.anio= anio
        self.hora= hora

    def cargar_modelo(self, nombre_modelo: str = 'model2.pkl'):
        self.model = joblib.load(nombre_modelo)


    def preparar_datos_modelo(self):
        dia = self.dia
        mes = self.mes
        anio = self.anio
        hora = self.hora

        columas = ['dayofsemester', 'court', 'dayofcuort', 'monthh', 'dayofmonth', 'weekk','dayofweek', 'hourr', 'holidayss']

        warnings.filterwarnings('ignore')

        fecha_df = pd.DataFrame(columns=['fecha_hora'], data =[[str(dia)+'-'+str(mes)+'-'+str(anio)+' '+str(hora)+':00:00']])
        fecha_df['fecha_hora'] = pd.to_datetime(fecha_df['fecha_hora'])
        fecha_df.set_index('fecha_hora', inplace=True)

        fecha_df['dayofweek'] = fecha_df.index.dayofweek  # Dia de la semana
        # Mes (Numero de meses contados en 30 dias)
        fecha_df['monthh'] = (fecha_df.index.day_of_year-80)//30+1
        fecha_df['weekk'] = fecha_df.index.weekofyear-11  # Numero de la semana del semestre
        fecha_df['hourr'] = fecha_df.index.hour  # Hora del dia
        fecha_df['court'] = (fecha_df.index.day_of_year-80)//46+1  # corte academico en el semestre
        fecha_df['dayofsemester'] = fecha_df.index.day_of_year-80  # Dia en el semestre
        fecha_df['dayofmonth'] = fecha_df['dayofsemester'] - 30*(fecha_df['monthh']-1)  # Dia en el mes
        fecha_df['dayofcuort'] = fecha_df['dayofsemester'] - 46*(fecha_df['court']-1)  # Dia en el corte
        fecha_df['serie'] = fecha_df.index.date
        co_holidays = holidays.CO()  # Dias festuvos
        fecha_df['holidayss'] = np.where(fecha_df['serie'].isin(co_holidays), '1', '0')  # 1 si es festivo

        data_predic = pd.DataFrame(columns=columas, data=[ [ fecha_df[x][0] for x in columas] ])

        return data_predic
        

    def predecir(self):
        self.cargar_modelo()
        x = self.preparar_datos_modelo()
        predicccion = pd.DataFrame(self.model.predict(x)).rename(columns={0:'cantidad_logueo'})

        return predicccion
