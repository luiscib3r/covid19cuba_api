from flask import Flask, jsonify, send_file
from flask_cors import CORS

# Graphics
import seaborn as sns
sns.set_style('darkgrid')

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from collections import defaultdict

# Load data
import json
data = json.load(open('covid19-cuba.json'))

# Getting DATA

# Cantidad diagnosticados por dia
diagnosticados = []

for k in range(1, len(data['casos']['dias'].keys())+1):
    try: 
        diagnosticados.append(len(data['casos']['dias'][str(k)]['diagnosticados']))
    except: 
        diagnosticados.append(0)

# Diagnosticados acumulados
diagnosticados_acc = []

for i, _ in enumerate(diagnosticados):
    diagnosticados_acc.append(sum(diagnosticados[:i+1]))

# Cantidad recuperados por dia
recuperados = []

for k in range(1, len(data['casos']['dias'].keys())+1):
    try: 
        recuperados.append(data['casos']['dias'][str(k)]['recuperados_numero'])
    except: 
        recuperados.append(0)

# Cantidad evacuados por dia
evacuados = []

for k in range(1, len(data['casos']['dias'].keys())+1):
    try: 
        evacuados.append(data['casos']['dias'][str(k)]['evacuados_numero'])
    except: 
        evacuados.append(0)

# Muertes
muertes = []

for k in range(1, len(data['casos']['dias'].keys())+1):
    try: 
        muertes.append(data['casos']['dias'][str(k)]['muertes_numero'])
    except: 
        muertes.append(0)

# Total diagnosticados
total_diagnosticados = sum(diagnosticados)

# Total recuperados
total_recuperados = sum(recuperados)

# Total evacuados
total_evacuados = sum(evacuados)

# Total muertes
total_muertes = sum(muertes)

# Total activos
total_activos = total_diagnosticados - (total_recuperados + total_evacuados + total_muertes)

# Fecha
last_day = [k for k in data['casos']['dias'].keys()][-1]
fecha = data['casos']['dias'][last_day]['fecha']

# Ingresados
total_ingresados = data['casos']['dias'][last_day]['sujetos_riesgo']

# Casos por sexo
sex_labels = 'Mujeres', 'Hombres', 'No reportado'
hombres = 0
mujeres = 0
non_sex = 0

for k in range(1, len(data['casos']['dias'].keys())+1):
    try:
        for caso in data['casos']['dias'][str(k)]['diagnosticados']:
            if caso['sexo'] == 'hombre':
                hombres += 1
            elif caso['sexo'] == 'mujer':
                mujeres += 1
            else:
                non_sex += 1
    except:
        pass

# Modos de contagio
modos = defaultdict(int)

for k in range(1, len(data['casos']['dias'].keys())+1):
    try:
        for caso in data['casos']['dias'][str(k)]['diagnosticados']:
            modos[caso['contagio']] += 1
    except:
        pass

modos_labels = [str(k) for k in modos.keys()]
modos_values = [v for v in modos.values()]

# Casos extranjeros
paises = defaultdict(int)

for k in range(1, len(data['casos']['dias'].keys())+1):
    try:
        for caso in data['casos']['dias'][str(k)]['diagnosticados']:
            if caso['pais'] != 'cu':
                paises[caso['pais']] += 1
    except:
        pass

# Casos por nacionalidad
cubanos = 0
extranjeros = 0

for k in range(1, len(data['casos']['dias'].keys())+1):
    try:
        for caso in data['casos']['dias'][str(k)]['diagnosticados']:
            if caso['pais'] == 'cu':
                cubanos += 1
            else:
                extranjeros += 1
    except:
        pass

# Distribución por rangos etarios
edades = {'0-18': 0, '19-40': 0, '41-60': 0, '+60': 0}

for k in range(1, len(data['casos']['dias'].keys())+1):
    try:
        for caso in data['casos']['dias'][str(k)]['diagnosticados']:
            edad = caso['edad']
            
            if edad <= 18 :
                edades['0-18'] += 1
            elif edad >= 19 and edad <= 40:
                edades['19-40'] += 1
            elif edad >= 41 and edad <= 60:
                edades['41-60'] += 1
            else:
                edades['+60'] += 1
    except:
        pass

# Test realizados y acumulados
cant_tests = []

for k in range(12, len(data['casos']['dias'].keys())+1):
    cant_tests.append(data['casos']['dias'][str(k)]['tests_total'])

prop_test_vs_detected = []
detected_acc = []

for i, c in enumerate(cant_tests):
    detected_acc.append(sum(diagnosticados[:11+i]))
    prop_test_vs_detected.append(round(detected_acc[-1] / c, 2)*100)

# Casos detectados por provincias
locations = defaultdict(int)

for k in range(1, len(data['casos']['dias'].keys())+1):
    try:
        for caso in data['casos']['dias'][str(k)]['diagnosticados']:
            locations[caso['provincia_detección']] += 1
    except:
        pass

locations = sorted(dict(locations).items(), key=lambda kv: kv[1])

# Casos detectados por municipios
mlocations = defaultdict(int)

for k in range(1, len(data['casos']['dias'].keys())+1):
    try:
        for caso in data['casos']['dias'][str(k)]['diagnosticados']:
            mlocations[caso['municipio_detección']] += 1
    except:
        pass
    
mlocations = sorted(dict(mlocations).items(), key=lambda kv: kv[1])

municipios_top10 = mlocations[-10:]

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
    return jsonify({
        'Diagnosticados': total_diagnosticados,
        'Activos': total_activos,
        'Recuperados': total_recuperados,
        'Evacuados': total_evacuados,
        'Muertes': total_muertes,
        'Ingresados': total_ingresados,
        'Updated': fecha
    })

@app.route('/summary_graph1', methods=['GET'])
def summary_graph1():
    fig = Figure(figsize=(9, 6))

    ax = fig.add_subplot(1, 1, 1)

    total = total_diagnosticados + total_recuperados + total_evacuados + total_muertes

    wedges, _, _  = ax.pie([total_diagnosticados, total_recuperados, total_evacuados, total_muertes], autopct='%1.1f%%', startangle=90, wedgeprops=dict(width=0.95))
    ax.legend(wedges, [
        'Diagnosticados ' + str(round(total_diagnosticados/total*100, 1)) + '%',
        'Recuperados ' + str(round(total_recuperados/total*100, 1)) + '%', 
        'Evacuados ' + str(round(total_evacuados/total*100, 1)) + '%', 
        'Fallecidos ' + str(round(total_muertes/total*100, 1)) + '%',
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

    total = total_ingresados + total_activos

    wedges, _, _  = ax.pie([total_ingresados, total_activos], autopct='%1.1f%%', startangle=90, wedgeprops=dict(width=0.95))
    ax.legend(wedges, [
        'Ingresados ' + str(round(total_ingresados/total*100, 1)) + '%', 
        'Activos ' + str(round(total_activos/total*100, 1)) + '%',
    ], loc='lower center', bbox_to_anchor=(0.9,0,0.5,1))

    ax.set_title('Activos | Ingresados', fontsize=20)

    FigureCanvasAgg(fig).print_png('summary2.png')

    return send_file(
        'summary2.png'
    )


import base64

@app.route('/evolution', methods=['GET'])
def evolution():
    fig = Figure(figsize=(10, 6))

    ax = fig.add_subplot(1, 1, 1)

    ax.plot([str(i) for i in range(1,len(diagnosticados_acc)+1)], diagnosticados_acc, label='Casos acumulados')
    ax.plot([str(i) for i in range(1,len(diagnosticados)+1)], diagnosticados, label='Casos en el día')

    ax.set_title('Evolución de casos por días', fontsize=20)
    fig.legend(frameon=True, fontsize=12)

    FigureCanvasAgg(fig).print_png('evolution.png')

    return send_file(
        'evolution.png'
    )

@app.route('/evolution_text', methods=['GET'])
def evolution_text():
    return jsonify({
        'diagnosticados': diagnosticados,
        'diagnosticados_acc': diagnosticados_acc,
    })

@app.route('/sexo', methods=['GET'])
def sexo():

    fig = Figure(figsize=(8, 6))

    ax = fig.add_subplot(1, 1, 1)

    wedges, _, _  = ax.pie([mujeres, hombres, non_sex], autopct='%1.1f%%', startangle=90, wedgeprops=dict(width=0.95))

    ax.set_title('Casos por sexo', fontsize=20)
    ax.legend(wedges, sex_labels, loc='lower center', bbox_to_anchor=(0.9,0,0.5,0.5))

    FigureCanvasAgg(fig).print_png('sexo.png')

    return send_file(
        'sexo.png'
    )

@app.route('/sexo_text', methods=['GET'])
def sexo_text():
    return jsonify({
        'mujeres': mujeres,
        'hombres': hombres,
        'no determinado': non_sex
    })

@app.route('/modo', methods=['GET'])
def modo():

    fig = Figure(figsize=(8, 6))

    ax = fig.add_subplot(1, 1, 1)

    wedges, _, _  = ax.pie(modos_values, autopct='%1.1f%%', startangle=90, wedgeprops=dict(width=0.95))

    ax.set_title('Casos por modo de contagio', fontsize=20)
    ax.legend(wedges, modos_labels, loc='lower center', bbox_to_anchor=(0.9,0,0.5,0.5))

    FigureCanvasAgg(fig).print_png('modo.png')

    return send_file(
        'modo.png'
    )

@app.route('/modo_text', methods=['GET'])
def modo_text():
    
    return jsonify({
        'labels': modos_labels,
        'values': modos_values,
    })

@app.route('/casos_extranjeros', methods=['GET'])
def casos_extranjeros():
    fig = Figure(figsize=(8, 6))

    ax = fig.add_subplot(1, 1, 1)

    ax.bar([str(k) for k in paises.keys()], [v for v in paises.values()])

    ax.set_title('Distribución por nacionalidad casos extranjeros', fontsize=20)

    FigureCanvasAgg(fig).print_png('paises.png')

    return send_file(
        'paises.png'
    )

@app.route('/casos_extranjeros_text', methods=['GET'])
def casos_extranjeros_text():
    return jsonify(dict(paises))

@app.route('/nacionalidad', methods=['GET'])
def nacionalidad():
    fig = Figure(figsize=(8, 6))

    ax = fig.add_subplot(1, 1, 1)

    wedges, _, _  = ax.pie([cubanos, extranjeros], autopct='%1.1f%%', startangle=90, wedgeprops=dict(width=0.95))
    ax.legend(wedges, ['Cubanos', 'Extranjeros'], loc='lower center', bbox_to_anchor=(0.9,0,0.5,1))

    ax.set_title('Casos por nacionalidad', fontsize=20)

    FigureCanvasAgg(fig).print_png('nacionalidad.png')

    return send_file(
        'nacionalidad.png'
    )

@app.route('/nacionalidad_text', methods=['GET'])
def nacionalidad_text():
    return jsonify({
        'Cubanos': cubanos,
        'Extranjeros': extranjeros,
    })

@app.route('/edad', methods=['GET'])
def edad():
    fig = Figure(figsize=(8, 6))

    ax = fig.add_subplot(1, 1, 1)

    ax.bar([str(k) for k in edades.keys()], [v for v in edades.values()])

    ax.set_title('Distribución por rangos etarios', fontsize=20)

    FigureCanvasAgg(fig).print_png('edades.png')

    return send_file(
        'edades.png'
    )

@app.route('/edad_text', methods=['GET'])
def edad_text():
    return jsonify(edades)

@app.route('/test', methods=['GET'])
def test():
    fig = Figure(figsize=(15, 6))

    (ax1, ax2) = fig.subplots(1, 2)

    # Test realizados
    ax1.bar([str(k) for k in range(12, len(data['casos']['dias'].keys())+1)], cant_tests)
    ax1.bar([str(k) for k in range(12, len(data['casos']['dias'].keys())+1)], detected_acc)

    ax1.set_title('Tests acumulados por día')

    # Proporción entre casos confirmados y test realizados
    ax2.bar([str(k) for k in range(12, len(data['casos']['dias'].keys())+1)], prop_test_vs_detected) 

    ax2.set_title('Proporción detectados/tests realizados')

    FigureCanvasAgg(fig).print_png('tests.png')

    return send_file(
        'tests.png'
    )

@app.route('/test_text', methods=['GET'])
def test_text():
    return jsonify({
        'cant_tests': cant_tests,
        'detected_acc': detected_acc,
        'prop': prop_test_vs_detected,
    })

@app.route('/provincias', methods=['GET'])
def provincia():
    fig = Figure(figsize=(15, 6))

    ax = fig.add_subplot(1, 1, 1)

    ax.barh([str(l[0]) for l in locations], [l[1] for l in locations], color='orange')

    ax.set_title('Casos detectados por provincias',fontsize = 20)

    FigureCanvasAgg(fig).print_png('provincias.png')

    return send_file(
        'provincias.png'
    )

@app.route('/municipios', methods=['GET'])
def municipio():
    fig = Figure(figsize=(15, 6))

    ax = fig.add_subplot(1, 1, 1)

    ax.barh([str(l[0]) for l in municipios_top10], [l[1] for l in municipios_top10], color='orange')

    ax.set_title('Casos detectados por municipios (Top 10)',fontsize = 20)

    FigureCanvasAgg(fig).print_png('municipios.png')

    return send_file(
        'municipios.png'
    )

@app.route('/provincias_text', methods=['GET'])
def provincia_text():
    return jsonify({
        'provincias': locations,
    })

@app.route('/municipios_text', methods=['GET'])
def municipio_text():
    return jsonify({
        'municipios': mlocations,
    })

if __name__ == '__main__':
    app.run(debug=True)