from flask import Flask, jsonify, send_file
from flask_cors import CORS

# Graphics
import seaborn as sns
sns.set_style('darkgrid')

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

# Data model
import datamodel

data = datamodel.DataModel()

datamodel.updater(data) # Call to update

# Setting api
app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'message': 'COVID19 Cuba Data API',
    })

@app.route('/summary', methods=['GET'])
def resume():
    increment = data.diagnosticados[-1] - data.diagnosticados[-2]

    if increment > 0:
        increment = '+{}'.format(str(increment))
    else:
        increment = str(increment)

    return jsonify({
        'Diagnosticados': data.total_diagnosticados,
        'DiagnosticadosDay': str(data.diagnosticados[-1]) + ' ({})'.format(increment),
        'Activos': data.total_activos,
        'Recuperados': data.total_recuperados,
        'Recuperacion': round(data.total_recuperados * 100 / data.total_activos, 1),
        'Evacuados': data.total_evacuados,
        'Muertes': data.total_muertes,
        'Ingresados': data.total_ingresados,
        'Mortalidad': round(data.total_muertes * 100 / data.total_diagnosticados, 1),
        'Updated': data.fecha
    })

@app.route('/summary_graph1', methods=['GET'])
def summary_graph1():
    fig = Figure(figsize=(9, 6))

    ax = fig.add_subplot(1, 1, 1)

    total = data.total_diagnosticados + data.total_recuperados + data.total_evacuados + data.total_muertes

    wedges, _, _  = ax.pie([data.total_diagnosticados, data.total_recuperados, data.total_evacuados, data.total_muertes], autopct='%1.1f%%', startangle=90, wedgeprops=dict(width=0.95))
    ax.legend(wedges, [
        'Diagnosticados ' + str(round(data.total_diagnosticados/total*100, 1)) + '%',
        'Recuperados ' + str(round(data.total_recuperados/total*100, 1)) + '%', 
        'Evacuados ' + str(round(data.total_evacuados/total*100, 1)) + '%', 
        'Fallecidos ' + str(round(data.total_muertes/total*100, 1)) + '%',
    ], loc='lower center', bbox_to_anchor=(0.9,0,0.5,1))

    ax.set_title('Resumen', fontsize=20)

    FigureCanvasAgg(fig).print_png('summary1.png')

    return send_file(
        'summary1.png'
    )

@app.route('/summary_graph2', methods=['GET'])
def summary_graph2():
    fig = Figure(figsize=(9, 6))

    ax = fig.add_subplot(1, 1, 1)

    total = data.total_ingresados + data.total_activos

    wedges, _, _  = ax.pie([data.total_ingresados, data.total_activos], autopct='%1.1f%%', startangle=90, wedgeprops=dict(width=0.95))
    ax.legend(wedges, [
        'Ingresados ' + str(round(data.total_ingresados/total*100, 1)) + '%', 
        'Activos ' + str(round(data.total_activos/total*100, 1)) + '%',
    ], loc='lower center', bbox_to_anchor=(0.9,0,0.5,1))

    ax.set_title('Activos | Ingresados', fontsize=20)

    FigureCanvasAgg(fig).print_png('summary2.png')

    return send_file(
        'summary2.png'
    )


import base64

@app.route('/evolution', methods=['GET'])
def evolution():
    fig = Figure(figsize=(12, 7))

    ax = fig.add_subplot(1, 1, 1)

    xss = [str(i) for i in range(1,len(data.diagnosticados_acc)+1)]
    xs = range(0,len(data.diagnosticados_acc))

    ax.plot(xss, data.diagnosticados_acc, 'o-', label='Casos acumulados')
    ax.plot(xss, data.diagnosticados, 'o-', label='Casos en el día')

    for x, y in zip(xs, data.diagnosticados_acc):
        label = "{}".format(y)

        ax.annotate(label,
                     (x,y),
                      textcoords='offset points',
                      xytext=(0,10),
                      ha='center')

    for x, y in zip(xs, data.diagnosticados):
        label = "{}".format(y)

        ax.annotate(label,
                     (x,y),
                      textcoords='offset points',
                      xytext=(0,-17),
                      ha='center')

    ax.set_title('Evolución de casos por días', fontsize=20)
    fig.legend(frameon=True, fontsize=12)

    FigureCanvasAgg(fig).print_png('evolution.png')

    return send_file(
        'evolution.png'
    )

@app.route('/evolution_fallecidos', methods=['GET'])
def evolution_fallecidos():
    fig = Figure(figsize=(12, 7))

    ax = fig.add_subplot(1, 1, 1)

    xss = [str(i) for i in range(1,len(data.muertes_acc)+1)]
    xs = range(0,len(data.muertes_acc))

    ax.plot(xss, data.muertes_acc, 'o-',label='Casos acumulados')
    ax.plot(xss, data.muertes, 'o-',label='Casos en el día')

    for x, y in zip(xs, data.muertes_acc):
        label = "{}".format(y)

        ax.annotate(label,
                     (x,y),
                      textcoords='offset points',
                      xytext=(0,10),
                      ha='center')

    for x, y in zip(xs, data.muertes):
        label = "{}".format(y)

        ax.annotate(label,
                     (x,y),
                      textcoords='offset points',
                      xytext=(0,-15),
                      ha='center')

    ax.set_title('Evolución de casos por días (Fallecidos)', fontsize=15)
    fig.legend(frameon=True, fontsize=12)

    FigureCanvasAgg(fig).print_png('fallecidos.png')

    return send_file(
        'fallecidos.png'
    )

@app.route('/evolution_text', methods=['GET'])
def evolution_text():
    return jsonify({
        'diagnosticados': data.diagnosticados,
        'diagnosticados_acc': data.diagnosticados_acc,
        'fallecidos': data.muertes,
        'fallecidos_acc': data.muertes_acc
    })

@app.route('/sexo', methods=['GET'])
def sexo():

    fig = Figure(figsize=(8, 6))

    ax = fig.add_subplot(1, 1, 1)

    wedges, _, _  = ax.pie([data.mujeres, data.hombres, data.non_sex], autopct='%1.1f%%', startangle=90, wedgeprops=dict(width=0.95))

    ax.set_title('Casos por sexo', fontsize=20)
    ax.legend(wedges, data.sex_labels, loc='lower center', bbox_to_anchor=(0.9,0,0.5,0.5))

    FigureCanvasAgg(fig).print_png('sexo.png')

    return send_file(
        'sexo.png'
    )

@app.route('/sexo_text', methods=['GET'])
def sexo_text():
    return jsonify({
        'mujeres': data.mujeres,
        'hombres': data.hombres,
        'no determinado': data.non_sex
    })

@app.route('/modo', methods=['GET'])
def modo():

    fig = Figure(figsize=(8, 6))

    ax = fig.add_subplot(1, 1, 1)

    wedges, _, _  = ax.pie(data.modos_values, autopct='%1.1f%%', startangle=90, wedgeprops=dict(width=0.95))

    ax.set_title('Casos por modo de contagio', fontsize=20)
    ax.legend(wedges, data.modos_labels, loc='lower center', bbox_to_anchor=(0.9,0,0.5,0.5))

    FigureCanvasAgg(fig).print_png('modo.png')

    return send_file(
        'modo.png'
    )

@app.route('/modo_text', methods=['GET'])
def modo_text():
    
    return jsonify({
        'labels': data.modos_labels,
        'values': data.modos_values,
    })

@app.route('/casos_extranjeros', methods=['GET'])
def casos_extranjeros():
    fig = Figure(figsize=(8, 6))

    ax = fig.add_subplot(1, 1, 1)

    ax.bar([str(k) for k in data.paises.keys()], [v for v in data.paises.values()])

    ax.set_title('Distribución por nacionalidad casos extranjeros', fontsize=20)

    FigureCanvasAgg(fig).print_png('paises.png')

    return send_file(
        'paises.png'
    )

@app.route('/casos_extranjeros_text', methods=['GET'])
def casos_extranjeros_text():
    return jsonify(dict(data.paises))

@app.route('/nacionalidad', methods=['GET'])
def nacionalidad():
    fig = Figure(figsize=(8, 6))

    ax = fig.add_subplot(1, 1, 1)

    wedges, _, _  = ax.pie([data.cubanos, data.extranjeros], autopct='%1.1f%%', startangle=90, wedgeprops=dict(width=0.95))
    ax.legend(wedges, ['Cubanos', 'Extranjeros'], loc='lower center', bbox_to_anchor=(0.9,0,0.5,1))

    ax.set_title('Casos por nacionalidad', fontsize=20)

    FigureCanvasAgg(fig).print_png('nacionalidad.png')

    return send_file(
        'nacionalidad.png'
    )

@app.route('/nacionalidad_text', methods=['GET'])
def nacionalidad_text():
    return jsonify({
        'Cubanos': data.cubanos,
        'Extranjeros': data.extranjeros,
    })

@app.route('/edad', methods=['GET'])
def edad():
    fig = Figure(figsize=(8, 6))

    ax = fig.add_subplot(1, 1, 1)

    ax.bar([str(k) for k in data.edades.keys()], [v for v in data.edades.values()])

    for x, y in enumerate(data.edades.values()):
        label = "{}".format(y)

        ax.annotate(label,
                     (x,y),
                      textcoords='offset points',
                      xytext=(0,4),
                      ha='center')

    ax.set_title('Distribución por rangos etarios', fontsize=20)

    FigureCanvasAgg(fig).print_png('edades.png')

    return send_file(
        'edades.png'
    )

@app.route('/edad_text', methods=['GET'])
def edad_text():
    return jsonify(data.edades)

@app.route('/test', methods=['GET'])
def test():
    fig = Figure(figsize=(15, 6))

    (ax1, ax2) = fig.subplots(1, 2)

    # Test realizados
    xss = [str(k) for k in range(12, data.cant_days+1)]
    xs = range(0, data.cant_days+1 - 12)

    ax1.bar(xss, data.cant_tests)
    ax1.bar(xss, data.detected_acc)

    for x, y in zip(xs, data.cant_tests):
        label = "{}".format(y)

        ax1.annotate(label,
                     (x,y),
                      textcoords='offset points',
                      xytext=(0,4),
                      ha='center')

    ax1.set_title('Tests acumulados por día')

    # Proporción entre casos confirmados y test realizados
    ax2.bar([str(k) for k in range(12, data.cant_days+1)], data.prop_test_vs_detected) 

    ax2.set_title('Proporción detectados/tests realizados')

    FigureCanvasAgg(fig).print_png('tests.png')

    return send_file(
        'tests.png'
    )

@app.route('/test_text', methods=['GET'])
def test_text():
    return jsonify({
        'cant_tests': data.cant_tests,
        'detected_acc': data.detected_acc,
        'prop': data.prop_test_vs_detected,
    })

@app.route('/provincias', methods=['GET'])
def provincia():
    fig = Figure(figsize=(15, 6))

    ax = fig.add_subplot(1, 1, 1)

    ax.barh([str(l[0]) for l in data.locations], [l[1] for l in data.locations], color='orange')

    
    for i, v in enumerate(data.locations):
        label = "{} ({}%)".format(v[1], round(v[1]*100/data.total_diagnosticados, 2))

        ax.annotate(label,
                     (v[1],i),
                      textcoords='offset points',
                      xytext=(2,-3),
                      ha='left')    

    ax.set_title('Casos detectados por provincias',fontsize = 20)

    FigureCanvasAgg(fig).print_png('provincias.png')

    return send_file(
        'provincias.png'
    )

@app.route('/municipios', methods=['GET'])
def municipio():
    fig = Figure(figsize=(15, 6))

    ax = fig.add_subplot(1, 1, 1)

    ax.barh([str(l[0]) for l in data.municipios_top10], [l[1] for l in data.municipios_top10], color='orange')

    for i, v in enumerate(data.municipios_top10):
        label = "{} ({}%)".format(v[1], round(v[1]*100/data.total_diagnosticados, 2))

        ax.annotate(label,
                     (v[1],i),
                      textcoords='offset points',
                      xytext=(2,-3),
                      ha='left') 

    ax.set_title('Casos detectados por municipios (Top 10)',fontsize = 20)

    FigureCanvasAgg(fig).print_png('municipios.png')

    return send_file(
        'municipios.png'
    )

@app.route('/provincias_text', methods=['GET'])
def provincia_text():
    return jsonify({
        'provincias': data.locations,
    })

@app.route('/municipios_text', methods=['GET'])
def municipio_text():
    return jsonify({
        'municipios': data.mlocations,
    })

@app.route('/reload', methods=['GET'])
def reload():
    datamodel.updater(data)

    return jsonify({
        'message': 'Updated Data'
    })

if __name__ == '__main__':
    app.run(debug=True)