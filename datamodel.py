import mdb

from collections import defaultdict
import config

class DataModel:
    def update(self, data):
        self.__dict__ = data

### START UPDATE FUNCTION

def updater(datamodel: DataModel):
    info = {}

    # Getting DATA
    data = mdb.getdata()

    # Cantidad diagnosticados por dia
    diagnosticados = []

    for k in range(1, len(data['casos']['dias'].keys())+1):
        try: 
            diagnosticados.append(len(data['casos']['dias'][str(k)]['diagnosticados']))
        except: 
            diagnosticados.append(0)

    info['diagnosticados'] = diagnosticados

    # Diagnosticados acumulados
    diagnosticados_acc = []

    for i, _ in enumerate(diagnosticados):
        diagnosticados_acc.append(sum(diagnosticados[:i+1]))

    info['diagnosticados_acc'] = diagnosticados_acc

    # Cantidad recuperados por dia
    recuperados = []

    for k in range(1, len(data['casos']['dias'].keys())+1):
        try: 
            recuperados.append(data['casos']['dias'][str(k)]['recuperados_numero'])
        except: 
            recuperados.append(0)

    info['recuperados'] = recuperados

    # Cantidad evacuados por dia
    evacuados = []

    for k in range(1, len(data['casos']['dias'].keys())+1):
        try: 
            evacuados.append(data['casos']['dias'][str(k)]['evacuados_numero'])
        except: 
            evacuados.append(0)

    info['evacuados'] = evacuados

    # Muertes
    muertes = []

    for k in range(1, len(data['casos']['dias'].keys())+1):
        try: 
            muertes.append(data['casos']['dias'][str(k)]['muertes_numero'])
        except: 
            muertes.append(0)

    info['muertes'] = muertes

    # Fallecidos acumulados
    muertes_acc = []

    for i, _ in enumerate(muertes):
        muertes_acc.append(sum(muertes[:i+1]))

    info['muertes_acc'] = muertes_acc

    # Total diagnosticados
    total_diagnosticados = sum(diagnosticados)
    info['total_diagnosticados'] = total_diagnosticados

    # Total recuperados
    total_recuperados = sum(recuperados)
    info['total_recuperados'] = total_recuperados

    # Total evacuados
    total_evacuados = sum(evacuados)
    info['total_evacuados'] = total_evacuados

    # Total muertes
    total_muertes = sum(muertes)
    info['total_muertes'] = total_muertes

    # Total activos
    total_activos = total_diagnosticados - (total_recuperados + total_evacuados + total_muertes)
    info['total_activos'] = total_activos

    # Fecha
    last_day = [k for k in data['casos']['dias'].keys()][-1]
    fecha = data['casos']['dias'][last_day]['fecha']
    info['fecha'] = fecha

    # Ingresados
    total_ingresados = data['casos']['dias'][last_day]['sujetos_riesgo']
    info['total_ingresados'] = total_ingresados

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

    info['sex_labels'] = sex_labels
    info['hombres'] = hombres
    info['mujeres'] = mujeres
    info['non_sex'] = non_sex

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

    info['modos_labels'] = modos_labels
    info['modos_values'] = modos_values

    # Casos extranjeros
    paises = defaultdict(int)

    for k in range(1, len(data['casos']['dias'].keys())+1):
        try:
            for caso in data['casos']['dias'][str(k)]['diagnosticados']:
                if caso['pais'] != 'cu':
                    paises[caso['pais']] += 1
        except:
            pass

    info['paises'] = paises

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

    info['cubanos'] = cubanos
    info['extranjeros'] = extranjeros

    # Distribución por grupos etarios
    edades = {'0-4': 0, '5-9': 0, '10-18': 0, '19-40': 0, '41-60': 0, '61-80': 0, '+81': 0, 'Desconocido': 0}

    for k in range(1, len(data['casos']['dias'].keys())+1):
        try:
            for caso in data['casos']['dias'][str(k)]['diagnosticados']:
                try:
                    edad = int(caso['edad'])
                except TypeError:
                    edades['Desconocido'] += 1
                    continue
            
                if edad <= 4 :
                    edades['0-4'] += 1
                elif edad >= 5 and edad <= 9:
                    edades['5-9'] += 1
                elif edad >= 10 and edad <= 18:
                    edades['10-18'] += 1
                elif edad >= 19 and edad <= 40:
                    edades['19-40'] += 1
                elif edad >= 41 and edad <= 60:
                    edades['41-60'] += 1
                elif edad >= 60 and edad <= 80:
                    edades['60-80'] += 1
                else:
                    edades['+81'] += 1
        except:
            pass

    info['edades'] = edades

    # Test realizados y acumulados
    cant_tests = []

    for k in range(12, len(data['casos']['dias'].keys())+1):
        cant_tests.append(data['casos']['dias'][str(k)]['tests_total'])

    info['cant_tests'] = cant_tests

    prop_test_vs_detected = []
    detected_acc = []

    for i, c in enumerate(cant_tests):
        detected_acc.append(sum(diagnosticados[:11+i]))
        prop_test_vs_detected.append(round(detected_acc[-1] / c, 2)*100)

    info['prop_test_vs_detected'] = prop_test_vs_detected
    info['detected_acc'] = detected_acc

    # Casos detectados por provincias
    locations = defaultdict(int)

    for k in range(1, len(data['casos']['dias'].keys())+1):
        try:
            for caso in data['casos']['dias'][str(k)]['diagnosticados']:
                locations[caso['provincia_detección']] += 1
        except:
            pass

    locations = sorted(dict(locations).items(), key=lambda kv: kv[1])

    info['locations'] = locations

    # Casos detectados por municipios
    mlocations = defaultdict(int)

    for k in range(1, len(data['casos']['dias'].keys())+1):
        try:
            for caso in data['casos']['dias'][str(k)]['diagnosticados']:
                mun = caso['municipio_detección']
                prov = caso['provincia_detección']
            
                mkey = mun + '\n' + '('+prov+')'

                mlocations[mkey] += 1
        except:
            pass
   
    mlocations = sorted(dict(mlocations).items(), key=lambda kv: kv[1])

    municipios_top10 = mlocations[-10:]

    info['mlocations'] = mlocations
    info['municipios_top10'] = municipios_top10

    # cantidad de días
    info['cant_days'] = len(data['casos']['dias'].keys())

    datamodel.update(info)

### END UPDATE FUNCTION