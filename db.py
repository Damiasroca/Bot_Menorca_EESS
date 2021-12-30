import pandas as pd
import numpy as np
import mysql.connector as msql
from mysql.connector import Error

def database():
    estacions_data = pd.read_csv(r'/path/to/json_processing/combinat_per_importar.csvdata.csv')
    estacions_data_null = estacions_data.replace({np.nan: None})
    estacions_data.head()
    try:
        conn = msql.connect(host='localhost', user='user',  
                        password='YOUR_PASS')
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS menorca")
            print("menorca database creada")
    except Error as e:
        print("Error conectant a  MySQL", e)
    
    try:
        conn = msql.connect(host='localhost', 
                           database='menorca', user='user', 
                           password='YOUR_PASS')
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            print("Conectat a : ", record)
            cursor.execute('DROP TABLE IF EXISTS benzineres')
            print('Creant taula....')
            cursor.execute("""CREATE TABLE benzineres (ID SMALLINT, `C.P.` FLOAT,
                            `Dirección` VARCHAR(150), Horario VARCHAR(50), Latitud CHAR(11),
                            Localidad VARCHAR(30), `Longitud (WGS840)` CHAR(11), Margen CHAR(1), Municipio VARCHAR(35),
                            `Precio Biodiesel`FLOAT, `Precio Bioetanol` FLOAT, `Precio Gas Natural Comprimido` FLOAT,
                            `Precio Gas Natural Licuado` FLOAT, `Precio Gases Licuados del petróleo` CHAR(20),
                            `Precio Gasoleo A` CHAR(5), `Precio Gasoleo B` CHAR(5), `Precio Gasoleo Premium` CHAR(5),
                            `Precio Gasolina 95 E10` FLOAT, `Precio Gasolina 95 E5` CHAR(5), `Precio Gasolina 95 E5 Premium` FLOAT,
                            `Precio Gasolina 98 E10` FLOAT, `Precio Gasolina 98 E5` FLOAT, `Precio Hidrogeno` FLOAT, Provincia CHAR(25),
                            `Remisión` CHAR(2), `Rótulo` VARCHAR(20), `Tipo Venta` CHAR(1), `% BioEtanol` CHAR(10), `% Éster metílico` CHAR(10),
                            IDEESS FLOAT, IDMunicipio FLOAT, IDProvincia FLOAT, IDCCAA FLOAT)""")
            print("Creada taula benzineres....")
            for i,row in estacions_data_null.iterrows():
                sql = "INSERT INTO menorca.benzineres VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql, tuple(row))
                print("Insertat")
                conn.commit()
    except Error as e:
        print("Error conectant MySQL", e)
