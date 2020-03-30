from flask import Flask, jsonify
from flask_cors import CORS

# Graphics
import seaborn as sns
import matplotlib.pyplot as plt # Graphics
sns.set_style('darkgrid')

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

if __name__ == '__main__':
    app.run(debug=True)