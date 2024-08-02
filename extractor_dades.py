import mysql.connector as msql
from mysql.connector import Error

#Per estacions de servei
def estacions_servei_extraccio_benzina_ascendent():
    try:
        conn = msql.connect(host='localhost', user='USER',  
                        password='PASSWORD')
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("""SELECT Localidad, `Rótulo`, `Precio Gasolina 95 E5`, `Precio Gasoleo A`, `Dirección`, Latitud, `Longitud (WGS84)`
                            FROM menorca.benzineres WHERE `Precio Gasolina 95 E5` IS NOT NULL ORDER BY `Precio Gasolina 95 E5` ASC""")
            records = cursor.fetchall()
            return records

    except Error as e:
        print("Error conectant a  MySQL", e)

def estacions_servei_extraccio_benzina_descendent():
    try:
        conn = msql.connect(host='localhost', user='USER',  
                        password='PASSWORD')
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("""SELECT Localidad, `Rótulo`, `Precio Gasolina 95 E5`, `Precio Gasoleo A`, `Dirección`, Latitud, `Longitud (WGS84)`
                            FROM menorca.benzineres WHERE `Precio Gasolina 95 E5` IS NOT NULL ORDER BY `Precio Gasolina 95 E5` DESC""")
            records = cursor.fetchall()
            return records

    except Error as e:
        print("Error conectant a  MySQL", e)

def estacions_servei_extraccio_diesel_A_ascendent():
    try:
        conn = msql.connect(host='localhost', user='USER',  
                        password='PASSWORD')
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("""SELECT Localidad, `Rótulo`, `Precio Gasoleo A`, `Dirección`, Latitud, `Longitud (WGS84)`
                            FROM menorca.benzineres WHERE `Precio Gasoleo A` IS NOT NULL ORDER BY `Precio Gasoleo A` ASC""")
            records = cursor.fetchall()
            return records

    except Error as e:
        print("Error conectant a  MySQL", e)

#Per carburants
def carburants_extraccio_diesel_A_ascendent():
    try:
        conn = msql.connect(host='localhost', user='USER',  
                        password='PASSWORD')
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("""SELECT Localidad, `Rótulo`, `Precio Gasoleo A`, `Dirección`, Latitud, `Longitud (WGS84)` 
                            FROM menorca.benzineres WHERE `Precio Gasolina 95 E5` IS NOT NULL ORDER BY `Precio Gasoleo A` ASC""")
            records = cursor.fetchall()
            return records

    except Error as e:
        print("Error conectant a  MySQL", e)
    
def carburants_extraccio_diesel_B_ascendent():
    try:
        conn = msql.connect(host='localhost', user='USER',  
                        password='PASSWORD')
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("""SELECT Localidad, `Rótulo`, `Precio Gasoleo B`, `Dirección`, Latitud, `Longitud (WGS84)`
                            FROM menorca.benzineres WHERE `Precio Gasoleo B` IS NOT NULL ORDER BY `Precio Gasoleo B` ASC""")
            records = cursor.fetchall()
            return records

    except Error as e:
        print("Error conectant a  MySQL", e)

def carburants_extraccio_diesel_premium_ascendent():
    try:
        conn = msql.connect(host='localhost', user='USER',  
                        password='PASSWORD')
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("""SELECT Localidad, `Rótulo`, `Precio Gasoleo Premium`, `Dirección`, Latitud, `Longitud (WGS84)`
                            FROM menorca.benzineres WHERE `Precio Gasoleo Premium` IS NOT NULL ORDER BY `Precio Gasoleo Premium` ASC""")
            records = cursor.fetchall()
            return records

    except Error as e:
        print("Error conectant a  MySQL", e)

def carburants_extraccio_GLP_ascendent():
    try:
        conn = msql.connect(host='localhost', user='USER',  
                        password='PASSWORD')
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("""SELECT Localidad, `Rótulo`, `Precio Gases Licuados del petróleo`, `Dirección`, Latitud, `Longitud (WGS84)` 
                            FROM menorca.benzineres WHERE `Precio Gases Licuados del petróleo` IS NOT NULL ORDER BY `Precio Gases Licuados del petróleo` ASC""")
            records = cursor.fetchall()
            return records

    except Error as e:
        print("Error conectant a  MySQL", e)

#Per Municipis
def extraccio_MAO_ascendent():
    try:
        conn = msql.connect(host='localhost', user='USER',  
                        password='PASSWORD')
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("""SELECT Localidad, `Rótulo`, `Precio Gasolina 95 E5`, `Precio Gasoleo A`, `Dirección`, Latitud, `Longitud (WGS84)` 
                            FROM menorca.benzineres WHERE Localidad IS NOT NULL AND Localidad = 'MAO' ORDER BY `Precio Gasolina 95 E5` ASC""")
            records = cursor.fetchall()
            return records

    except Error as e:
        print("Error conectant a  MySQL", e)

def extraccio_CIUTADELLA_ascendent():
    try:
        conn = msql.connect(host='localhost', user='USER',  
                        password='PASSWORD')
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("""SELECT Localidad, `Rótulo`, `Precio Gasolina 95 E5`, `Precio Gasoleo A`, `Dirección`, Latitud, `Longitud (WGS84)`
                            FROM menorca.benzineres WHERE Localidad IS NOT NULL AND Localidad = 'CIUTADELLA DE MENORCA' ORDER BY `Precio Gasolina 95 E5` ASC""")
            records = cursor.fetchall()
            return records

    except Error as e:
        print("Error conectant a  MySQL", e)

def extraccio_MERDAL_ascendent():
    try:
        conn = msql.connect(host='localhost', user='USER',  
                        password='PASSWORD')
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("""SELECT Localidad, `Rótulo`, `Precio Gasolina 95 E5`, `Precio Gasoleo A`, `Dirección`, Latitud, `Longitud (WGS84)`
                            FROM menorca.benzineres WHERE Localidad IS NOT NULL AND Localidad = 'MERCADAL (ES)' ORDER BY `Precio Gasolina 95 E5` ASC""")
            records = cursor.fetchall()
            return records

    except Error as e:
        print("Error conectant a  MySQL", e)

def extraccio_ALAIOR_ascendent():
    try:
        conn = msql.connect(host='localhost', user='USER',  
                        password='PASSWORD')
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("""SELECT Localidad, `Rótulo`, `Precio Gasolina 95 E5`, `Precio Gasoleo A`, `Dirección`, Latitud, `Longitud (WGS84)`
                            FROM menorca.benzineres WHERE Localidad IS NOT NULL AND Localidad = 'ALAIOR' ORDER BY `Precio Gasolina 95 E5` ASC""")
            records = cursor.fetchall()
            return records

    except Error as e:
        print("Error conectant a  MySQL", e)

def extraccio_FERRERIES_ascendent():
    try:
        conn = msql.connect(host='localhost', user='USER',  
                        password='PASSWORD')
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("""SELECT Localidad, `Rótulo`, `Precio Gasolina 95 E5`, `Precio Gasoleo A`, `Dirección`, Latitud, `Longitud (WGS84)` 
                            FROM menorca.benzineres WHERE Localidad IS NOT NULL AND Localidad = 'FERRERIES' ORDER BY `Precio Gasolina 95 E5` ASC""")
            records = cursor.fetchall()
            return records

    except Error as e:
        print("Error conectant a  MySQL", e)

def extraccio_ESCASTELL_ascendent():
    try:
        conn = msql.connect(host='localhost', user='USER',  
                        password='PASSWORD')
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("""SELECT Localidad, `Rótulo`, `Precio Gasolina 95 E5`, `Precio Gasoleo A`, `Dirección`, Latitud, `Longitud (WGS84)`
                            FROM menorca.benzineres WHERE Localidad IS NOT NULL AND Localidad = 'SON VILAR' ORDER BY `Precio Gasolina 95 E5` ASC""")
            records = cursor.fetchall()
            return records

    except Error as e:
        print("Error conectant a  MySQL", e)

def extraccio_SANTLLUIS_ascendent():
    try:
        conn = msql.connect(host='localhost', user='USER',  
                        password='PASSWORD')
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("""SELECT Localidad, `Rótulo`, `Precio Gasolina 95 E5`, `Precio Gasoleo A`, `Dirección`, Latitud, `Longitud (WGS84)` 
                            FROM menorca.benzineres WHERE Localidad IS NOT NULL AND Localidad = 'SANT LLUIS' ORDER BY `Precio Gasolina 95 E5` ASC""")
            records = cursor.fetchall()
            return records

    except Error as e:
        print("Error conectant a  MySQL", e)

def extraccio_FORNELLS_ascendent():
    try:
        conn = msql.connect(host='localhost', user='USER',  
                        password='PASSWORD')
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("""SELECT `Rótulo`, `Dirección`, `Precio Gasolina 95 E5`, `Precio Gasoleo A`, Latitud, `Longitud (WGS84)` 
                            FROM menorca.benzineres WHERE Localidad IS NOT NULL AND Localidad = 'MERCADAL (ES)' AND `Rótulo`= 'GALP' ORDER BY `Precio Gasolina 95 E5` ASC""")
            records = cursor.fetchall()
            return records

    except Error as e:
        print("Error conectant a  MySQL", e)

#Per distribuidora
def extraccio_distribuidora_AUTONET():
    try:
        conn = msql.connect(host='localhost', user='USER',  
                        password='PASSWORD')
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("""SELECT `Rótulo`, Localidad, Latitud, `Longitud (WGS84)`, `Dirección`
                            FROM menorca.benzineres WHERE `Rótulo` IS NOT NULL AND `Rótulo` = 'AUTONETOIL' ORDER BY Localidad ASC""")
            records = cursor.fetchall()
            return records

    except Error as e:
        print("Error conectant a  MySQL", e)

def extraccio_distribuidora_BP():
    try:
        conn = msql.connect(host='localhost', user='USER',  
                        password='PASSWORD')
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("""SELECT `Rótulo`, Localidad, Latitud, `Longitud (WGS84)`, `Dirección`
                            FROM menorca.benzineres WHERE `Rótulo` IS NOT NULL AND `Rótulo` = 'BP' ORDER BY Localidad ASC""")
            records = cursor.fetchall()
            return records

    except Error as e:
        print("Error conectant a  MySQL", e)

def extraccio_distribuidora_CARB_LOWCOST():
    try:
        conn = msql.connect(host='localhost', user='USER',  
                        password='PASSWORD')
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("""SELECT `Rótulo`, Localidad, Latitud, `Longitud (WGS84)`, `Dirección`
                            FROM menorca.benzineres WHERE `Rótulo` IS NOT NULL AND `Rótulo` = 'CARBURANTS LOW COST' ORDER BY Localidad ASC""")
            records = cursor.fetchall()
            return records

    except Error as e:
        print("Error conectant a  MySQL", e)

def extraccio_distribuidora_CEPSA():
    try:
        conn = msql.connect(host='localhost', user='USER',  
                        password='PASSWORD')
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("""SELECT `Rótulo`, Localidad, Latitud, `Longitud (WGS84)`, `Dirección`
                            FROM menorca.benzineres WHERE `Rótulo` IS NOT NULL AND `Rótulo` = 'CEPSA' ORDER BY Localidad ASC""")
            records = cursor.fetchall()
            return records

    except Error as e:
        print("Error conectant a  MySQL", e)

def extraccio_distribuidora_EROSKI():
    try:
        conn = msql.connect(host='localhost', user='USER',  
                        password='PASSWORD')
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("""SELECT `Rótulo`, Localidad, Latitud, `Longitud (WGS84)`, `Dirección`
                            FROM menorca.benzineres WHERE `Rótulo` IS NOT NULL AND `Rótulo` = 'EROSKI' ORDER BY Localidad ASC""")
            records = cursor.fetchall()
            return records

    except Error as e:
        print("Error conectant a  MySQL", e)

def extraccio_distribuidora_GALP():
    try:
        conn = msql.connect(host='localhost', user='USER',  
                        password='PASSWORD')
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("""SELECT `Rótulo`, Localidad, Latitud, `Longitud (WGS84)`, `Dirección`
                            FROM menorca.benzineres WHERE `Rótulo` IS NOT NULL AND `Rótulo` = 'GALP' ORDER BY Localidad ASC""")
            records = cursor.fetchall()
            return records

    except Error as e:
        print("Error conectant a  MySQL", e)

def extraccio_distribuidora_GMOIL():
    try:
        conn = msql.connect(host='localhost', user='USER',  
                        password='PASSWORD')
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("""SELECT `Rótulo`, Localidad, Latitud, `Longitud (WGS84)`, `Dirección`
                            FROM menorca.benzineres WHERE `Rótulo` IS NOT NULL AND `Rótulo` = 'GMOIL' ORDER BY Localidad ASC""")
            records = cursor.fetchall()
            return records

    except Error as e:
        print("Error conectant a  MySQL", e)

def extraccio_distribuidora_REPSOL():
    try:
        conn = msql.connect(host='localhost', user='USER',  
                        password='PASSWORD')
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("""SELECT `Rótulo`, Localidad, Latitud, `Longitud (WGS84)`, `Dirección`
                            FROM menorca.benzineres WHERE `Rótulo` IS NOT NULL AND `Rótulo` = 'REPSOL' ORDER BY Localidad ASC""")
            records = cursor.fetchall()
            return records

    except Error as e:
        print("Error conectant a  MySQL", e)


    

