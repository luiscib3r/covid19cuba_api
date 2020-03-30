from flask import Flask, jsonify, send_file
from flask_cors import CORS

# Graphics
import seaborn as sns
sns.set_style('darkgrid')

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

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
        'Updated': fecha
    })

import base64

@app.route('/evolution', methods=['GET'])
def evolution():
    fig = Figure(figsize=(10, 6))

    ax = fig.add_subplot(1, 1, 1)

    ax.plot([str(i) for i in range(1,len(diagnosticados)+1)], diagnosticados_acc, label='Casos acumulados')
    ax.plot([str(i) for i in range(1,len(diagnosticados)+1)], diagnosticados, label='Casos en el día')

    ax.set_title('Evolución de casos por días', fontsize=20)
    fig.legend(frameon=True, fontsize=12)

    FigureCanvasAgg(fig).print_png('evolution.png')

    return send_file(
        'evolution.png'
    )

if __name__ == '__main__':
    app.run(debug=True)