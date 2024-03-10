import dash
from dash import dcc, html, Input, Output
from dash.exceptions import PreventUpdate
import numpy as np

# Define la aplicación Dash
app = dash.Dash(__name__)

# Define el diseño del tablero
app.layout = html.Div([
    html.H1("Predicción de Productividad"),
    html.Div([
        html.Label('Targeted Productivity:'),
        dcc.Input(id='targeted-productivity', type='number', value=0, step=0.1),
        dcc.Slider(
            id='targeted-productivity-slider',
            min=0,
            max=1,
            step=0.1,
            value=0,
            marks={i/10: str(i/10) for i in range(0, 11)}
        )
    ]),
    html.Div([
        html.Label('SMV:'),
        dcc.Input(id='smv', type='number', value=0),
        dcc.Slider(
            id='smv-slider',
            min=0,
            max=100,
            step=1,
            value=0,
            marks={i: str(i) for i in range(0, 101, 10)}
        )
    ]),
    html.Div([
        html.Label('Idle Men:'),
        dcc.Input(id='idle-men', type='number', value=0),
        dcc.Slider(
            id='idle-men-slider',
            min=0,
            max=100,
            step=1,
            value=0,
            marks={i: str(i) for i in range(0, 101, 10)}
        )
    ]),
    dcc.Graph(id='prediction-interval-graph'),
    html.Div(id='output-data-upload'),
])

# Función para realizar predicciones
def predict_productivity(targeted_productivity, smv, idle_men):
    # Aquí podrías incluir el cálculo de la predicción y el error estándar
    # Por simplicidad, asumiremos un error estándar de 0.1 para este ejemplo
    predicted_productivity = 0.734 + 0.065 * targeted_productivity - 0.006 * smv - 0.023 * idle_men
    standard_error = 0.1  # Esto sería el error estándar que necesitas estimar correctamente

    return predicted_productivity, standard_error

# Callback para realizar predicciones y mostrar los resultados
@app.callback(Output('output-data-upload', 'children'),
              [Input('targeted-productivity', 'value'),
               Input('smv', 'value'),
               Input('idle-men', 'value')])
def update_output(targeted_productivity, smv, idle_men):
    if targeted_productivity is None or smv is None or idle_men is None:
        raise PreventUpdate

    # Validar que targeted_productivity no sea mayor que 1
    if targeted_productivity > 1:
        return html.Div([
            html.H5('Error'),
            html.Label('No es permitido ingresar un valor mayor a 1 en Targeted Productivity.')
        ])

    # Realizar predicciones solo si targeted_productivity es menor o igual a 1
    predicted_productivity, standard_error = predict_productivity(targeted_productivity, smv, idle_men)

    # Crear el resultado de la predicción
    prediction_result = html.Div([
        html.H5('Resultados de Predicción'),
        html.Label(f'Productividad Predicha: {round(predicted_productivity*100,2)}%'),
        html.Br(),
        html.Label(f'Intervalo de Confianza (95%): [{round((predicted_productivity - 1.96 * standard_error)*100,2)}%,{round((predicted_productivity + 1.96 * standard_error)*100,2)}%]')
    ])

    return prediction_result

# Callback para actualizar la gráfica
@app.callback(Output('prediction-interval-graph', 'figure'),
              [Input('targeted-productivity', 'value'),
               Input('smv', 'value'),
               Input('idle-men', 'value')])
def update_graph(targeted_productivity, smv, idle_men):
    if targeted_productivity is None or smv is None or idle_men is None:
        raise PreventUpdate

    # Realizar predicciones
    predicted_productivity, standard_error = predict_productivity(targeted_productivity, smv, idle_men)

    # Crear datos para la gráfica
    x_values = np.linspace(0, 1, 100)
    y_values = 0.734 + 0.065 * x_values - 0.006 * smv - 0.023 * idle_men
    lower_bound = y_values - 1.96 * standard_error
    upper_bound = y_values + 1.96 * standard_error

    # Crear la figura de la gráfica
    fig = {
        'data': [
            {'x': x_values, 'y': y_values, 'type': 'scatter', 'mode': 'lines', 'name': 'Prediction'},
            {'x': np.concatenate((x_values, x_values[::-1])), 
             'y': np.concatenate((upper_bound, lower_bound[::-1])), 
             'type': 'scatter', 'mode': 'lines', 'name': 'Confidence Interval', 'fill': 'toself'}
        ],
        'layout': {
            'title': 'Predicción de Productividad con Intervalo de Confianza',
            'xaxis': {'title': 'Targeted Productivity'},
            'yaxis': {'title': 'Predicted Productivity'},
            'margin': {'l': 40, 'b': 40, 't': 40, 'r': 40},
            'hovermode': 'closest'
        }
    }

    return fig

# Callbacks para actualizar los valores de las cajas de texto cuando se cambian los sliders
@app.callback(
    Output('targeted-productivity', 'value'),
    [Input('targeted-productivity-slider', 'value')]
)
def update_targeted_productivity(value):
    return value

@app.callback(
    Output('smv', 'value'),
    [Input('smv-slider', 'value')]
)
def update_smv(value):
    return value


@app.callback(
    Output('idle-men', 'value'),
    [Input('idle-men-slider', 'value')]
)
def update_idle_men(value):
    return value

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)