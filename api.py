from classes import InputModel, OutputModel, APIModelBackEnd
from fastapi import FastAPI
from typing import List

app = FastAPI(title="API DE MACHINE LEARNING - predecir numero de logueos en una fecha", version="1.0")


@app.post("/predict", response_model=List[OutputModel])
async def predecir_probabilidad(inputs: List[InputModel]):
    respuestas = list()
    for Input in inputs:
        first_model = APIModelBackEnd(
            Input.dia, 
            Input.mes, 
            Input.anio,
            Input.hora
        )

        respuestas.append(first_model.predecir()[0])

    return respuestas
