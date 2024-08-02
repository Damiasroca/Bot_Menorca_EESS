import json

arxius=['/municipis_modificats/alaior.json', '/municipis_modificats/ciutadella.json', '/municipis_modificats/escastell.json', '/municipis_modificats/ferreries.json', '/municipis_modificats/mao.json', '/municipis_modificats/merdal.json', '/municipis_modificats/santlluis.json']


def alaior():
    def un():
        with open('/json_processing/b.json', 'w', encoding="utf8") as dest_file:
            with open('/municipis_original/alaior.json', 'r', encoding="utf8") as source_file:
                for line in source_file:
                    element = json.loads(line.strip())
                    if 'Fecha' in element:
                        del element['Fecha']
                    dest_file.write(json.dumps(element, ensure_ascii=False))

    def dos():
        with open('/json_processing/c.json', 'w', encoding="utf8") as dest_file:
            with open('/json_processing/b.json', 'r', encoding="utf8") as source_file:
                for line in source_file:
                    element = json.loads(line.strip())
                    if 'Nota' in element:
                        del element['Nota']
                    dest_file.write(json.dumps(element, ensure_ascii=False))

    def quatre():
        with open('/json_processing/e.json', 'w', encoding="utf8") as dest_file:
            with open('/json_processing/c.json', 'r', encoding="utf8") as source_file:
                for line in source_file:
                    element = json.loads(line.strip())
                    if 'ResultadoConsulta' in element:
                        del element['ResultadoConsulta']
                    dest_file.write(json.dumps(element, ensure_ascii=False))

    def cinc():
        with open('/municipis_modificats/alaior.json', 'w', encoding="utf8") as n:
            with open('/json_processing/e.json', 'r', encoding="utf8") as f:
                data=json.load(f)
                data1=str(data)
                data2=data1.replace("{'ListaEESSPrecio': ","")
                data3=data2[:-1]
                data4=str(data3)
                data5=data4.replace("'", '"')
                print(data5)
                n.write(data5)
    un()
    dos()
    quatre()
    cinc()

def ciutadella():
    def un():
        with open('/json_processing/b.json', 'w', encoding="utf8") as dest_file:
            with open('/municipis_original/ciutadella.json', 'r', encoding="utf8") as source_file:
                for line in source_file:
                    element = json.loads(line.strip())
                    if 'Fecha' in element:
                        del element['Fecha']
                    dest_file.write(json.dumps(element, ensure_ascii=False))

    def dos():
        with open('/json_processing/c.json', 'w', encoding="utf8") as dest_file:
            with open('/json_processing/b.json', 'r', encoding="utf8") as source_file:
                for line in source_file:
                    element = json.loads(line.strip())
                    if 'Nota' in element:
                        del element['Nota']
                    dest_file.write(json.dumps(element, ensure_ascii=False))

    def quatre():
        with open('/json_processing/e.json', 'w', encoding="utf8") as dest_file:
            with open('/json_processing/c.json', 'r', encoding="utf8") as source_file:
                for line in source_file:
                    element = json.loads(line.strip())
                    if 'ResultadoConsulta' in element:
                        del element['ResultadoConsulta']
                    dest_file.write(json.dumps(element, ensure_ascii=False))

    def cinc():
        with open('/municipis_modificats/ciutadella.json', 'w', encoding="utf8") as n:
            with open('/json_processing/e.json', 'r', encoding="utf8") as f:
                data=json.load(f)
                data1=str(data)
                data2=data1.replace("{'ListaEESSPrecio': ","")
                data3=data2[:-1]
                data4=str(data3)
                data5=data4.replace("'", '"')
                print(data5)
                n.write(data5)
    un()
    dos()
    quatre()
    cinc()

def escastell():
    def un():
        with open('/json_processing/b.json', 'w', encoding="utf8") as dest_file:
            with open('/municipis_original/escastell.json', 'r', encoding="utf8") as source_file:
                for line in source_file:
                    element = json.loads(line.strip())
                    if 'Fecha' in element:
                        del element['Fecha']
                    dest_file.write(json.dumps(element, ensure_ascii=False))

    def dos():
        with open('/json_processing/c.json', 'w', encoding="utf8") as dest_file:
            with open('/json_processing/b.json', 'r', encoding="utf8") as source_file:
                for line in source_file:
                    element = json.loads(line.strip())
                    if 'Nota' in element:
                        del element['Nota']
                    dest_file.write(json.dumps(element, ensure_ascii=False))

    def quatre():
        with open('/json_processing/e.json', 'w', encoding="utf8") as dest_file:
            with open('/json_processing/c.json', 'r', encoding="utf8") as source_file:
                for line in source_file:
                    element = json.loads(line.strip())
                    if 'ResultadoConsulta' in element:
                        del element['ResultadoConsulta']
                    dest_file.write(json.dumps(element, ensure_ascii=False))

    def cinc():
        with open('/municipis_modificats/escastell.json', 'w', encoding="utf8") as n:
            with open('/json_processing/e.json', 'r', encoding="utf8") as f:
                data=json.load(f)
                data1=str(data)
                data2=data1.replace("{'ListaEESSPrecio': ","")
                data3=data2[:-1]
                data4=str(data3)
                data5=data4.replace("'", '"')
                print(data5)
                n.write(data5)
    un()
    dos()
    quatre()
    cinc()

def ferreries():
    def un():
        with open('/json_processing/b.json', 'w', encoding="utf8") as dest_file:
            with open('/municipis_original/ferreries.json', 'r', encoding="utf8") as source_file:
                for line in source_file:
                    element = json.loads(line.strip())
                    if 'Fecha' in element:
                        del element['Fecha']
                    dest_file.write(json.dumps(element, ensure_ascii=False))

    def dos():
        with open('/json_processing/c.json', 'w', encoding="utf8") as dest_file:
            with open('/json_processing/b.json', 'r', encoding="utf8") as source_file:
                for line in source_file:
                    element = json.loads(line.strip())
                    if 'Nota' in element:
                        del element['Nota']
                    dest_file.write(json.dumps(element, ensure_ascii=False))

    def quatre():
        with open('/json_processing/e.json', 'w', encoding="utf8") as dest_file:
            with open('/json_processing/c.json', 'r', encoding="utf8") as source_file:
                for line in source_file:
                    element = json.loads(line.strip())
                    if 'ResultadoConsulta' in element:
                        del element['ResultadoConsulta']
                    dest_file.write(json.dumps(element, ensure_ascii=False))

    def cinc():
        with open('/municipis_modificats/ferreries.json', 'w', encoding="utf8") as n:
            with open('/json_processing/e.json', 'r', encoding="utf8") as f:
                data=json.load(f)
                data1=str(data)
                data2=data1.replace("{'ListaEESSPrecio': ","")
                data3=data2[:-1]
                data4=str(data3)
                data5=data4.replace("'", '"')
                print(data5)
                n.write(data5)
    un()
    dos()
    quatre()
    cinc()

def mao():
    def un():
        with open('/json_processing/b.json', 'w', encoding="utf8") as dest_file:
            with open('/municipis_original/mao.json', 'r', encoding="utf8") as source_file:
                for line in source_file:
                    element = json.loads(line.strip())
                    if 'Fecha' in element:
                        del element['Fecha']
                    dest_file.write(json.dumps(element, ensure_ascii=False))

    def dos():
        with open('/json_processing/c.json', 'w', encoding="utf8") as dest_file:
            with open('/json_processing/b.json', 'r', encoding="utf8") as source_file:
                for line in source_file:
                    element = json.loads(line.strip())
                    if 'Nota' in element:
                        del element['Nota']
                    dest_file.write(json.dumps(element, ensure_ascii=False))

    def quatre():
        with open('/json_processing/e.json', 'w', encoding="utf8") as dest_file:
            with open('/json_processing/c.json', 'r', encoding="utf8") as source_file:
                for line in source_file:
                    element = json.loads(line.strip())
                    if 'ResultadoConsulta' in element:
                        del element['ResultadoConsulta']
                    dest_file.write(json.dumps(element, ensure_ascii=False))

    def cinc():
        with open('/municipis_modificats/mao.json', 'w', encoding="utf8") as n:
            with open('/json_processing/e.json', 'r', encoding="utf8") as f:
                data=json.load(f)
                data1=str(data)
                data2=data1.replace("{'ListaEESSPrecio': ","")
                data3=data2[:-1]
                data4=str(data3)
                data5=data4.replace("'", '"')
                print(data5)
                n.write(data5)
    un()
    dos()
    quatre()
    cinc()

def merdal():
    def un():
        with open('/json_processing/b.json', 'w', encoding="utf8") as dest_file:
            with open('/municipis_original/merdal.json', 'r', encoding="utf8") as source_file:
                for line in source_file:
                    element = json.loads(line.strip())
                    if 'Fecha' in element:
                        del element['Fecha']
                    dest_file.write(json.dumps(element, ensure_ascii=False))

    def dos():
        with open('/json_processing/c.json', 'w', encoding="utf8") as dest_file:
            with open('/json_processing/b.json', 'r', encoding="utf8") as source_file:
                for line in source_file:
                    element = json.loads(line.strip())
                    if 'Nota' in element:
                        del element['Nota']
                    dest_file.write(json.dumps(element, ensure_ascii=False))

    def quatre():
        with open('/json_processing/e.json', 'w', encoding="utf8") as dest_file:
            with open('/json_processing/c.json', 'r', encoding="utf8") as source_file:
                for line in source_file:
                    element = json.loads(line.strip())
                    if 'ResultadoConsulta' in element:
                        del element['ResultadoConsulta']
                    dest_file.write(json.dumps(element, ensure_ascii=False))

    def cinc():
        with open('/municipis_modificats/merdal.json', 'w', encoding="utf8") as n:
            with open('/json_processing/e.json', 'r', encoding="utf8") as f:
                data=json.load(f)
                data1=str(data)
                data2=data1.replace("{'ListaEESSPrecio': ","")
                data3=data2[:-1]
                data4=str(data3)
                data5=data4.replace("'", '"')
                print(data5)
                n.write(data5)
    un()
    dos()
    quatre()
    cinc()

def santlluis():
    def un():
        with open('/json_processing/b.json', 'w', encoding="utf8") as dest_file:
            with open('/municipis_original/santlluis.json', 'r', encoding="utf8") as source_file:
                for line in source_file:
                    element = json.loads(line.strip())
                    if 'Fecha' in element:
                        del element['Fecha']
                    dest_file.write(json.dumps(element, ensure_ascii=False))

    def dos():
        with open('/json_processing/c.json', 'w', encoding="utf8") as dest_file:
            with open('/json_processing/b.json', 'r', encoding="utf8") as source_file:
                for line in source_file:
                    element = json.loads(line.strip())
                    if 'Nota' in element:
                        del element['Nota']
                    dest_file.write(json.dumps(element, ensure_ascii=False))

    def quatre():
        with open('/json_processing/e.json', 'w', encoding="utf8") as dest_file:
            with open('/json_processing/c.json', 'r', encoding="utf8") as source_file:
                for line in source_file:
                    element = json.loads(line.strip())
                    if 'ResultadoConsulta' in element:
                        del element['ResultadoConsulta']
                    dest_file.write(json.dumps(element, ensure_ascii=False))

    def cinc():
        with open('/municipis_modificats/santlluis.json', 'w', encoding="utf8") as n:
            with open('/json_processing/e.json', 'r', encoding="utf8") as f:
                data=json.load(f)
                data1=str(data)
                data2=data1.replace("{'ListaEESSPrecio': ","")
                data3=data2[:-1]
                data4=str(data3)
                data5=data4.replace("'", '"')
                print(data5)
                n.write(data5)
    un()
    dos()
    quatre()
    cinc()

def combina_json(nom_arxiu):
    result = list()
    for i in nom_arxiu:
        with open(i, 'r') as infile:
            result.extend(json.load(infile))

    with open('/json_processing/combinat.json', 'w') as output_file:
        json.dump(result, output_file, ensure_ascii=False)

def principal():
    alaior()
    ciutadella()
    escastell()
    ferreries()
    mao()
    merdal()
    santlluis()
    combina_json(arxius)
    


principal()

