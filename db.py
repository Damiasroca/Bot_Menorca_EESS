import pandas as pd
import numpy as np
import mysql.connector as msql
from mysql.connector import Error
import datetime

def backup_current_data():
    """Backup current data to historical_prices table before updating"""
    try:
        conn = msql.connect(host='localhost', database='menorca', user='USER', password='PASSWORD')
        if conn.is_connected():
            cursor = conn.cursor()
            
            # Create historical_prices table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS historical_prices (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    date DATE NOT NULL,
                    rotulo VARCHAR(255),
                    localidad VARCHAR(255),
                    direccion VARCHAR(255),
                    latitud DECIMAL(10, 8),
                    longitud_wgs84 DECIMAL(11, 8),
                    precio_gasolina_95_e5 DECIMAL(5, 3),
                    precio_gasoleo_a DECIMAL(5, 3),
                    precio_gasoleo_b DECIMAL(5, 3),
                    precio_gasoleo_premium DECIMAL(5, 3),
                    precio_gases_licuados_del_petroleo DECIMAL(5, 3),
                    INDEX idx_date (date),
                    INDEX idx_localidad (localidad),
                    INDEX idx_rotulo (rotulo)
                )
            """)
            
            # Check if we already have data for today
            today = datetime.date.today()
            cursor.execute("SELECT COUNT(*) FROM historical_prices WHERE date = %s", (today,))
            count = cursor.fetchone()[0]
            
            if count == 0:
                # Backup current data to historical table
                backup_query = """
                INSERT INTO historical_prices 
                (date, rotulo, localidad, direccion, latitud, longitud_wgs84, 
                 precio_gasolina_95_e5, precio_gasoleo_a, precio_gasoleo_b, 
                 precio_gasoleo_premium, precio_gases_licuados_del_petroleo)
                SELECT %s, `Rótulo`, Localidad, `Dirección`, 
                       CAST(REPLACE(Latitud, ',', '.') AS DECIMAL(10,8)),
                       CAST(REPLACE(`Longitud (WGS84)`, ',', '.') AS DECIMAL(11,8)),
                       CAST(REPLACE(`Precio Gasolina 95 E5`, ',', '.') AS DECIMAL(5,3)),
                       CAST(REPLACE(`Precio Gasoleo A`, ',', '.') AS DECIMAL(5,3)),
                       CAST(REPLACE(`Precio Gasoleo B`, ',', '.') AS DECIMAL(5,3)),
                       CAST(REPLACE(`Precio Gasoleo Premium`, ',', '.') AS DECIMAL(5,3)),
                       CAST(REPLACE(`Precio Gases licuados del petróleo`, ',', '.') AS DECIMAL(5,3))
                FROM benzineres 
                WHERE `Precio Gasolina 95 E5` IS NOT NULL 
                   OR `Precio Gasoleo A` IS NOT NULL
                """
                
                try:
                    cursor.execute(backup_query, (today,))
                    conn.commit()
                    print(f"Historical data backed up for {today}")
                except Error as e:
                    print(f"Note: Could not backup historical data (table might not exist yet): {e}")
            else:
                print(f"Historical data for {today} already exists")
                
    except Error as e:
        print(f"Error during historical backup: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def database():
    # First, backup current data for historical charts
    backup_current_data()
    
    estacions_data = pd.read_csv(r'/json_processing/combinat_per_importar.csvdata.csv')
    
    # Replace NaN values with None
    estacions_data_null = estacions_data.replace({np.nan: None})
    print("First few rows of the data:")
    print(estacions_data_null.head())
    print("Data types of the DataFrame columns:")
    print(estacions_data_null.dtypes)  # Print data types

    # Explicitly convert columns to the correct data types
    numeric_columns = [
        'C.P.', 'Precio Biodiesel', 'Precio Bioetanol', 'Precio Gas Natural Comprimido',
        'Precio Gas Natural Licuado', 'Precio Gasolina 95 E10', 'Precio Gasolina 95 E5 Premium',
        'Precio Gasolina 98 E10', 'Precio Gasolina 98 E5', 'Precio Hidrogeno', 'IDEESS', 'IDMunicipio',
        'IDProvincia', 'IDCCAA'
    ]
    
    for column in numeric_columns:
        estacions_data_null[column] = pd.to_numeric(estacions_data_null[column], errors='coerce')

    try:
        conn = msql.connect(host='localhost', user='USER', password='PASSWORD')
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS menorca")
            print("menorca database created")
    except Error as e:
        print("Error connecting to MySQL during database creation:", e)
    
    try:
        conn = msql.connect(host='localhost', database='menorca', user='USER', password='PASSWORD')
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            print("Connected to database: ", record)
            
            # Instead of dropping, truncate to preserve structure but clear data
            cursor.execute('DROP TABLE IF EXISTS benzineres')
            print('Creating table...')
            cursor.execute("""
                CREATE TABLE benzineres (
                    ID SMALLINT NOT NULL, 
                    `C.P.` FLOAT,
                    `Dirección` VARCHAR(150), 
                    Horario VARCHAR(50), 
                    Latitud CHAR(11),
                    Localidad VARCHAR(30), 
                    `Longitud (WGS84)` CHAR(11), 
                    Margen CHAR(1), 
                    Municipio VARCHAR(35),
                    `Precio Biodiesel` FLOAT, 
                    `Precio Bioetanol` FLOAT, 
                    `Precio Gas Natural Comprimido` FLOAT,
                    `Precio Gas Natural Licuado` FLOAT, 
                    `Precio Gases licuados del petróleo` CHAR(20),
                    `Precio Gasoleo A` CHAR(10),  
                    `Precio Gasoleo B` CHAR(10),  
                    `Precio Gasoleo Premium` CHAR(10),  
                    `Precio Gasolina 95 E10` FLOAT, 
                    `Precio Gasolina 95 E5` CHAR(10),  
                    `Precio Gasolina 95 E5 Premium` FLOAT,
                    `Precio Gasolina 98 E10` FLOAT, 
                    `Precio Gasolina 98 E5` FLOAT, 
                    `Precio Hidrogeno` FLOAT, 
                    Provincia CHAR(25),
                    `Remisión` CHAR(2), 
                    `Rótulo` VARCHAR(20), 
                    `Tipo Venta` CHAR(1), 
                    `% BioEtanol` CHAR(10), 
                    `% Éster metílico` CHAR(10),
                    IDEESS FLOAT, 
                    IDMunicipio FLOAT, 
                    IDProvincia FLOAT, 
                    IDCCAA FLOAT,
                    PRIMARY KEY (ID)
                )
            """)
            print("Table benzineres created...")

            for i, row in estacions_data_null.iterrows():
                if row['ID'] is None:
                    print(f"Skipping row {i} with null ID")
                    continue  # Skip rows with null ID
                
                # Convert NaN or 'nan' to None in the values tuple
                values = tuple(None if pd.isna(x) else x for x in [
                    row['ID'], row['C.P.'], row['Dirección'], row['Horario'], row['Latitud'],
                    row['Localidad'], row['Longitud (WGS84)'], row['Margen'], row['Municipio'],
                    row['Precio Biodiesel'], row['Precio Bioetanol'], row['Precio Gas Natural Comprimido'],
                    row['Precio Gas Natural Licuado'], row['Precio Gases licuados del petróleo'],
                    row['Precio Gasoleo A'], row['Precio Gasoleo B'], row['Precio Gasoleo Premium'],
                    row['Precio Gasolina 95 E10'], row['Precio Gasolina 95 E5'], row['Precio Gasolina 95 E5 Premium'],
                    row['Precio Gasolina 98 E10'], row['Precio Gasolina 98 E5'], row['Precio Hidrogeno'],
                    row['Provincia'], row['Remisión'], row['Rótulo'], row['Tipo Venta'],
                    row['% BioEtanol'], row['% Éster metílico'], row['IDEESS'], row['IDMunicipio'],
                    row['IDProvincia'], row['IDCCAA']
                ])
                
                sql = """
                    INSERT INTO menorca.benzineres 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                try:
                    cursor.execute(sql, values)
                    conn.commit()
                    print("Inserted row with ID:", row['ID'])
                except Error as e:
                    print(f"Error inserting row {i} with ID {row['ID']}: {e}")

            print(f"✅ Data update completed. Historical data preserved for chart generation.")

    except Error as e:
        print("Error connecting MySQL during table creation or data insertion:", e)

if __name__ == "__main__":
    database()
