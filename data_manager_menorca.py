# Data Manager for Menorca Fuel Price Telegram Bot
# This module handles all data processing, database operations, and querying

import pandas as pd
import mysql.connector as msql
from sqlalchemy import create_engine
from mysql.connector import Error
import json
import glob
import os
import datetime
from geopy.distance import geodesic
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
import logging

import secret
from constants_menorca import FUEL_TYPES, MUNICIPALITIES

class MenorcaDataManager:
    """
    Data Manager following the exact architecture described in technical_description.txt
    Handles JSON data ingestion, database operations, and all data queries.
    """
    
    def __init__(self):
        self.db_config = {
            'host': secret.secret['db_host'],
            'user': secret.secret['db_user'],
            'password': secret.secret['db_password'],
            'database': secret.secret['db_name']
        }
        self.connection = None
        self.sqlalchemy_engine = None
        self.data = None  # In-memory pandas DataFrame cache
        self.last_update_time = None
        
        # Setup logging
        self.logger = logging.getLogger(__name__)

    def connect(self):
        """Establish database connection and create SQLAlchemy engine."""
        try:
            self.connection = msql.connect(**self.db_config)
            
            # Create SQLAlchemy engine for pandas operations
            connection_string = f"mysql+mysqlconnector://{self.db_config['user']}:{self.db_config['password']}@{self.db_config['host']}/{self.db_config['database']}"
            self.sqlalchemy_engine = create_engine(connection_string)
            
            self.logger.info("Connected to MySQL database")
            return True
        except Error as e:
            self.logger.error(f"Error connecting to MySQL: {e}")
            raise

    def _update_database_schema(self):
        """
        Update existing database schema to add new columns if needed.
        This handles database migrations for new features.
        """
        if not self.connection or not self.connection.is_connected():
            self.connect()
        
        cursor = self.connection.cursor()
        
        try:
            # Check if Precio_Gasolina_95_E5_Premium column exists
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'estaciones_servicio' 
                AND COLUMN_NAME = 'Precio_Gasolina_95_E5_Premium'
            """, (self.db_config['database'],))
            
            column_exists = cursor.fetchone()[0] > 0
            
            if not column_exists:
                self.logger.info("Adding Precio_Gasolina_95_E5_Premium column to estaciones_servicio table")
                cursor.execute("""
                    ALTER TABLE estaciones_servicio 
                    ADD COLUMN Precio_Gasolina_95_E5_Premium DECIMAL(5, 3) 
                    AFTER Precio_Gasolina_95_E5
                """)
                
                # Add index for the new column
                cursor.execute("""
                    ALTER TABLE estaciones_servicio 
                    ADD INDEX idx_gasolina_premium (Precio_Gasolina_95_E5_Premium)
                """)
                
                self.logger.info("Successfully added Precio_Gasolina_95_E5_Premium column")
            
            # Check if Horario column exists
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'estaciones_servicio' 
                AND COLUMN_NAME = 'Horario'
            """, (self.db_config['database'],))
            
            horario_exists = cursor.fetchone()[0] > 0
            
            if not horario_exists:
                self.logger.info("Adding Horario column to estaciones_servicio table")
                cursor.execute("""
                    ALTER TABLE estaciones_servicio 
                    ADD COLUMN Horario VARCHAR(255) 
                    AFTER Provincia
                """)
                
                self.logger.info("Successfully added Horario column")
            
            # Check if historical_prices table needs the column too
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'historical_prices' 
                AND COLUMN_NAME = 'precio_gasolina_95_e5_premium'
            """, (self.db_config['database'],))
            
            historical_column_exists = cursor.fetchone()[0] > 0
            
            if not historical_column_exists:
                self.logger.info("Adding precio_gasolina_95_e5_premium column to historical_prices table")
                cursor.execute("""
                    ALTER TABLE historical_prices 
                    ADD COLUMN precio_gasolina_95_e5_premium DECIMAL(5, 3) 
                    AFTER precio_gasolina_95_e5
                """)
                
                self.logger.info("Successfully added precio_gasolina_95_e5_premium column to historical_prices")
            
            # NEW: Check for IDMunicipio column in estaciones_servicio
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'estaciones_servicio' 
                AND COLUMN_NAME = 'IDMunicipio'
            """, (self.db_config['database'],))
            
            idmunicipio_exists = cursor.fetchone()[0] > 0

            if not idmunicipio_exists:
                self.logger.info("Adding IDMunicipio column to estaciones_servicio table")
                cursor.execute("""
                    ALTER TABLE estaciones_servicio 
                    ADD COLUMN IDMunicipio VARCHAR(10) 
                    AFTER Provincia
                """)
                cursor.execute("""
                    ALTER TABLE estaciones_servicio 
                    ADD INDEX idx_idmunicipio (IDMunicipio)
                """)
                self.logger.info("Successfully added IDMunicipio column")
            
            # NEW: Check if municipality column exists in user_subscriptions table
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'user_subscriptions' 
                AND COLUMN_NAME = 'municipality'
            """, (self.db_config['database'],))
            
            municipality_column_exists = cursor.fetchone()[0] > 0
            
            if not municipality_column_exists:
                self.logger.info("Adding municipality column to user_subscriptions table")
                cursor.execute("""
                    ALTER TABLE user_subscriptions 
                    ADD COLUMN municipality VARCHAR(255) 
                    AFTER price_threshold
                """)
                
                # Add index for the new column
                cursor.execute("""
                    ALTER TABLE user_subscriptions 
                    ADD INDEX idx_municipality (municipality)
                """)
                
                self.logger.info("Successfully added municipality column to user_subscriptions")
            
            # NEW: Check for IDMunicipio column in historical_prices
            cursor.execute("""
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = %s
                AND TABLE_NAME = 'historical_prices'
                AND COLUMN_NAME = 'IDMunicipio'
            """, (self.db_config['database'],))

            historical_idmunicipio_exists = cursor.fetchone()[0] > 0

            if not historical_idmunicipio_exists:
                self.logger.info("Adding IDMunicipio column to historical_prices table")
                cursor.execute("""
                    ALTER TABLE historical_prices 
                    ADD COLUMN IDMunicipio VARCHAR(10) 
                    AFTER localidad
                """)
                cursor.execute("""
                    ALTER TABLE historical_prices 
                    ADD INDEX idx_idmunicipio (IDMunicipio)
                """)
                self.logger.info("Successfully added IDMunicipio column to historical_prices")
            
            # NEW: Check if id_municipality column exists in user_subscriptions table
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'user_subscriptions' 
                AND COLUMN_NAME = 'id_municipality'
            """, (self.db_config['database'],))
            
            id_municipality_column_exists = cursor.fetchone()[0] > 0
            
            if not id_municipality_column_exists:
                self.logger.info("Adding id_municipality column to user_subscriptions table")
                cursor.execute("""
                    ALTER TABLE user_subscriptions 
                    ADD COLUMN id_municipality VARCHAR(50) 
                    AFTER municipality
                """)
                cursor.execute("""
                    ALTER TABLE user_subscriptions 
                    ADD INDEX idx_id_municipality (id_municipality)
                """)
                self.logger.info("Successfully added id_municipality column to user_subscriptions")
            
            self.connection.commit()
            self.logger.info("Database schema update completed successfully")
            
        except Error as e:
            self.logger.error(f"Error updating database schema: {e}")
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def create_database_and_tables(self):
        """
        Create the database schema matching the technical description.
        Creates the main estaciones_servicio table and supporting tables.
        """
        if not self.connection or not self.connection.is_connected():
            self.connect()
        
        cursor = self.connection.cursor()
        
        # Main stations table - matches the technical description structure
        estaciones_servicio_table = """
        CREATE TABLE IF NOT EXISTS estaciones_servicio (
            IDEESS VARCHAR(50) PRIMARY KEY,
            Rotulo VARCHAR(255),
            Direccion VARCHAR(500),
            Localidad VARCHAR(255),
            Provincia VARCHAR(255),
            IDMunicipio VARCHAR(10),
            Horario VARCHAR(255),
            Latitud DECIMAL(10, 8),
            Longitud_WGS84 DECIMAL(11, 8),
            Precio_Gasolina_95_E5 DECIMAL(5, 3),
            Precio_Gasolina_95_E5_Premium DECIMAL(5, 3),
            Precio_Gasoleo_A DECIMAL(5, 3),
            Precio_Gasoleo_B DECIMAL(5, 3),
            Precio_Gasoleo_Premium DECIMAL(5, 3),
            Precio_Gases_Licuados_del_petroleo DECIMAL(5, 3),
            Fecha_Actualizacion DATETIME,
            INDEX idx_localidad (Localidad),
            INDEX idx_idmunicipio (IDMunicipio),
            INDEX idx_rotulo (Rotulo),
            INDEX idx_gasolina (Precio_Gasolina_95_E5),
            INDEX idx_gasolina_premium (Precio_Gasolina_95_E5_Premium),
            INDEX idx_gasoleo_a (Precio_Gasoleo_A)
        )
        """
        
        # Historical prices table for chart generation
        historical_prices_table = """
        CREATE TABLE IF NOT EXISTS historical_prices (
            id INT AUTO_INCREMENT PRIMARY KEY,
            date DATE NOT NULL,
            rotulo VARCHAR(255),
            localidad VARCHAR(255),
            IDMunicipio VARCHAR(10),
            direccion VARCHAR(500),
            latitud DECIMAL(10, 8),
            longitud_wgs84 DECIMAL(11, 8),
            precio_gasolina_95_e5 DECIMAL(5, 3),
            precio_gasolina_95_e5_premium DECIMAL(5, 3),
            precio_gasoleo_a DECIMAL(5, 3),
            precio_gasoleo_b DECIMAL(5, 3),
            precio_gasoleo_premium DECIMAL(5, 3),
            precio_gases_licuados_del_petroleo DECIMAL(5, 3),
            INDEX idx_date (date),
            INDEX idx_localidad (localidad),
            INDEX idx_idmunicipio (IDMunicipio),
            INDEX idx_rotulo (rotulo)
        )
        """
        
        # User subscriptions for price alerts
        user_subscriptions_table = """
        CREATE TABLE IF NOT EXISTS user_subscriptions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id BIGINT NOT NULL,
            username VARCHAR(255),
            fuel_type VARCHAR(50) NOT NULL,
            price_threshold DECIMAL(5, 3) NOT NULL,
            municipality VARCHAR(255),
            id_municipality VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            INDEX idx_user_id (user_id),
            INDEX idx_fuel_type (fuel_type),
            INDEX idx_active (is_active),
            INDEX idx_municipality (municipality),
            INDEX idx_id_municipality (id_municipality)
        )
        """
        
        # User analytics table
        bot_users_table = """
        CREATE TABLE IF NOT EXISTS bot_users (
            user_id BIGINT PRIMARY KEY,
            username VARCHAR(255),
            first_name VARCHAR(255),
            last_name VARCHAR(255),
            language_code VARCHAR(10),
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            interaction_count INT DEFAULT 1,
            is_active BOOLEAN DEFAULT TRUE,
            INDEX idx_username (username),
            INDEX idx_last_seen (last_seen),
            INDEX idx_is_active (is_active)
        )
        """
        
        try:
            cursor.execute(estaciones_servicio_table)
            cursor.execute(historical_prices_table)
            cursor.execute(user_subscriptions_table)
            cursor.execute(bot_users_table)
            self.connection.commit()
            self.logger.info("Database schema created successfully")
            
            # Update existing schema if needed (add missing columns to existing tables)
            self._update_database_schema()
            
        except Error as e:
            self.logger.error(f"Error creating database schema: {e}")
            raise
        finally:
            cursor.close()

    def load_json_data(self):
        """
        Load fuel price data from JSON files following the exact pattern
        described in technical_description.txt.
        """
        if not self.connection or not self.connection.is_connected():
            self.connect()
        
        # Create database schema if needed
        self.create_database_and_tables()
        
        cursor = self.connection.cursor()
        
        # Clear existing data (as described in technical description)
        try:
            cursor.execute("DELETE FROM estaciones_servicio")
            self.logger.info("Cleared existing stations data")
        except Error as e:
            self.logger.error(f"Error clearing existing data: {e}")
            
        # Find all JSON files in municipis_original directory
        json_files = glob.glob("municipis_original/*.json")
        self.logger.info(f"Found {len(json_files)} JSON files to process")
        
        if not json_files:
            self.logger.warning("No JSON files found in municipis_original/ directory")
            return False
        
        # Process each JSON file
        for json_file in json_files:
            try:
                self.logger.info(f"Processing {json_file}")
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract station list (following technical description structure)
                if 'ListaEESSPrecio' not in data:
                    self.logger.warning(f"No ListaEESSPrecio found in {json_file}")
                    continue
                
                stations = data['ListaEESSPrecio']
                self.logger.info(f"Processing {len(stations)} stations from {json_file}")
                
                # Insert each station with upsert logic
                for station in stations:
                    self._insert_station(cursor, station)
                    
            except Exception as e:
                self.logger.error(f"Error processing {json_file}: {e}")
                continue
        
        # Commit all changes
        try:
            self.connection.commit()
            self.logger.info("Successfully loaded JSON data into database")
            
            # Store daily snapshot for historical tracking
            self.store_daily_snapshot()
            
            # Load data into memory cache
            self.load_data_from_db()
            
            return True
        except Error as e:
            self.logger.error(f"Error committing data: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()

    def _apply_data_corrections(self, station):
        """
        Apply known data corrections before inserting into database.
        This handles cases where the government data has incorrect municipality assignments.
        """
        
        direccion = station.get('Dirección', '').upper()
        rotulo = station.get('Rótulo', '').upper()
        localidad = station.get('Localidad', '').upper()
        ideess = station.get('IDEESS')
        
        # DEBUG: Log every station being processed
        self.logger.debug(f"Processing station IDEESS: {ideess}, Rotulo: {rotulo}")
        
        # Known corrections based on address patterns or specific stations
        # Fornells correction: The GALP station (IDEESS '2645') is officially in
        # 'Es Mercadal' but should be treated as 'Fornells' because FORNELLS INDEPENDENT!!.
        if station.get('IDEESS') == '2645':
            self.logger.info(f"🎯 FORNELLS CORRECTION TRIGGERED for station IDEESS: {ideess}")
            self.logger.info(f"Original data - IDMunicipio: {station.get('IDMunicipio')}, Localidad: {station.get('Localidad')}")
            
            station['IDMunicipio'] = '666'  # Use numeric ID for database compatibility
            station['Localidad'] = 'FORNELLS'  # Keep string for display
            
            self.logger.info(f"Corrected data - IDMunicipio: {station.get('IDMunicipio')}, Localidad: {station.get('Localidad')}")
            self.logger.info(f"✅ Data correction applied: Assigning station '2645' to Fornells (ID: 666).")
        else:
            # DEBUG: Log when the condition doesn't match for station 2645 specifically
            if ideess == '2645':
                self.logger.error(f"❌ FORNELLS CORRECTION FAILED - Condition did not match for station {ideess}")
                self.logger.error(f"station.get('IDEESS') = '{station.get('IDEESS')}' (type: {type(station.get('IDEESS'))})")
                self.logger.error(f"Expected: '2645' (type: {type('2645')})")
        
        return station

    def _insert_station(self, cursor, station):
        """Insert a single station with upsert logic as described in technical description."""
        # Apply data corrections before inserting
        station = self._apply_data_corrections(station)
        
        insert_query = """
        INSERT INTO estaciones_servicio 
        (IDEESS, Rotulo, Direccion, Localidad, Provincia, IDMunicipio, Horario, Latitud, Longitud_WGS84,
         Precio_Gasolina_95_E5, Precio_Gasolina_95_E5_Premium, Precio_Gasoleo_A, Precio_Gasoleo_B, 
         Precio_Gasoleo_Premium, Precio_Gases_Licuados_del_petroleo, Fecha_Actualizacion)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        Rotulo = VALUES(Rotulo),
        Direccion = VALUES(Direccion),
        Localidad = VALUES(Localidad),
        Provincia = VALUES(Provincia),
        IDMunicipio = VALUES(IDMunicipio),
        Horario = VALUES(Horario),
        Latitud = VALUES(Latitud),
        Longitud_WGS84 = VALUES(Longitud_WGS84),
        Precio_Gasolina_95_E5 = VALUES(Precio_Gasolina_95_E5),
        Precio_Gasolina_95_E5_Premium = VALUES(Precio_Gasolina_95_E5_Premium),
        Precio_Gasoleo_A = VALUES(Precio_Gasoleo_A),
        Precio_Gasoleo_B = VALUES(Precio_Gasoleo_B),
        Precio_Gasoleo_Premium = VALUES(Precio_Gasoleo_Premium),
        Precio_Gases_Licuados_del_petroleo = VALUES(Precio_Gases_Licuados_del_petroleo),
        Fecha_Actualizacion = VALUES(Fecha_Actualizacion)
        """
        
        try:
            cursor.execute(insert_query, (
                station.get('IDEESS', None),
                station.get('Rótulo', None),
                station.get('Dirección', None),
                station.get('Localidad', None),
                station.get('Provincia', None),
                station.get('IDMunicipio', None),
                station.get('Horario', None),
                self._convert_decimal(station.get('Latitud', None)),
                self._convert_decimal(station.get('Longitud (WGS84)', None)),
                self._convert_decimal(station.get('Precio Gasolina 95 E5', None)),
                self._convert_decimal(station.get('Precio Gasolina 95 E5 Premium', None)),
                self._convert_decimal(station.get('Precio Gasoleo A', None)),
                self._convert_decimal(station.get('Precio Gasoleo B', None)),
                self._convert_decimal(station.get('Precio Gasoleo Premium', None)),
                self._convert_decimal(station.get('Precio Gases licuados del petróleo', None)),
                datetime.datetime.now()
            ))
        except Error as e:
            self.logger.error(f"Error inserting station {station.get('IDEESS', 'Unknown')}: {e}")

    def _convert_decimal(self, value):
        """
        Convert comma-decimal to dot-decimal for MySQL.
        Handles the Spanish number format as described in technical description.
        """
        if value is None or value == '' or pd.isna(value):
            return None
        try:
            # Convert to string and replace comma with dot
            str_val = str(value).replace(',', '.')
            return float(str_val) if str_val else None
        except (ValueError, TypeError):
            return None

    def load_data_from_db(self):
        """Load data from database into pandas DataFrame for fast querying."""
        if not self.sqlalchemy_engine:
            self.connect()
        
        query = "SELECT * FROM estaciones_servicio"
        try:
            self.data = pd.read_sql(query, self.sqlalchemy_engine)
            self.logger.info(f"Loaded {len(self.data)} stations into memory cache")
            
            # Load update timestamp
            self._load_update_timestamp()
            
        except Exception as e:
            self.logger.error(f"Error loading data from database: {e}")
            self.data = pd.DataFrame()

    def _load_update_timestamp(self):
        """Load the last update timestamp."""
        try:
            timestamp_file = 'last_api_fetch.txt'
            if os.path.exists(timestamp_file):
                with open(timestamp_file, 'r') as f:
                    timestamp_str = f.read().strip()
                    self.last_update_time = datetime.datetime.strptime(timestamp_str, "%d/%m/%Y %H:%M:%S")
            else:
                self.last_update_time = datetime.datetime.now()
        except Exception as e:
            self.logger.error(f"Error loading update timestamp: {e}")
            self.last_update_time = datetime.datetime.now()

    def cleanup_historical_null_records(self):
        """Remove records with all NULL fuel prices from historical_prices table."""
        if not self.connection or not self.connection.is_connected():
            self.connect()
            
        cursor = self.connection.cursor()
        
        try:
            # Delete records where all fuel price columns are NULL
            delete_query = """
            DELETE FROM historical_prices 
            WHERE precio_gasolina_95_e5 IS NULL 
              AND precio_gasolina_95_e5_premium IS NULL
              AND precio_gasoleo_a IS NULL 
              AND precio_gasoleo_b IS NULL
              AND precio_gasoleo_premium IS NULL 
              AND precio_gases_licuados_del_petroleo IS NULL
            """
            
            cursor.execute(delete_query)
            deleted_count = cursor.rowcount
            self.connection.commit()
            
            self.logger.info(f"Cleaned up {deleted_count} NULL records from historical_prices")
            return deleted_count
            
        except Error as e:
            self.logger.error(f"Error cleaning up NULL records: {e}")
            self.connection.rollback()
            return 0
        finally:
            cursor.close()

    def store_daily_snapshot(self):
        """Store daily snapshot for historical price tracking."""
        if not self.connection or not self.connection.is_connected():
            self.connect()
            
        cursor = self.connection.cursor()
        today = datetime.date.today()
        
        # Check if we already have data for today
        check_query = "SELECT COUNT(*) FROM historical_prices WHERE date = %s"
        cursor.execute(check_query, (today,))
        count = cursor.fetchone()[0]
        
        if count > 0:
            self.logger.info(f"Historical data for {today} already exists")
            cursor.close()
            return
            
        # Insert today's data from main table - Only records with at least one fuel price
        insert_query = """
        INSERT INTO historical_prices 
        (date, rotulo, localidad, direccion, IDMunicipio, latitud, longitud_wgs84, 
         precio_gasolina_95_e5, precio_gasolina_95_e5_premium, precio_gasoleo_a, precio_gasoleo_b, 
         precio_gasoleo_premium, precio_gases_licuados_del_petroleo)
        SELECT %s, Rotulo, Localidad, Direccion, IDMunicipio, Latitud, Longitud_WGS84,
               Precio_Gasolina_95_E5, Precio_Gasolina_95_E5_Premium, Precio_Gasoleo_A, Precio_Gasoleo_B,
               Precio_Gasoleo_Premium, Precio_Gases_Licuados_del_petroleo
        FROM estaciones_servicio
        WHERE (Precio_Gasolina_95_E5 IS NOT NULL AND Precio_Gasolina_95_E5 > 0) 
           OR (Precio_Gasolina_95_E5_Premium IS NOT NULL AND Precio_Gasolina_95_E5_Premium > 0)
           OR (Precio_Gasoleo_A IS NOT NULL AND Precio_Gasoleo_A > 0) 
           OR (Precio_Gasoleo_B IS NOT NULL AND Precio_Gasoleo_B > 0)
           OR (Precio_Gasoleo_Premium IS NOT NULL AND Precio_Gasoleo_Premium > 0) 
           OR (Precio_Gases_Licuados_del_petroleo IS NOT NULL AND Precio_Gases_Licuados_del_petroleo > 0)
        """
        
        try:
            cursor.execute(insert_query, (today,))
            rows_inserted = cursor.rowcount
            self.connection.commit()
            self.logger.info(f"Daily snapshot stored for {today} - {rows_inserted} stations inserted")
        except Error as e:
            self.logger.error(f"Error storing daily snapshot: {e}")
            self.connection.rollback()
        finally:
            cursor.close()

    # ===============================
    # QUERY METHODS FOR BOT FUNCTIONALITY
    # ===============================

    def get_stations_by_fuel_ascending(self, fuel_type, limit=5):
        """Get cheapest stations for a specific fuel type."""
        if self.data is None or self.data.empty:
            self.load_data_from_db()
        
        if fuel_type not in FUEL_TYPES:
            return pd.DataFrame()
        
        column_name = FUEL_TYPES[fuel_type]['column'].title().replace('_', '_')
        
        # Filter valid prices and sort ascending
        filtered = self.data[
            self.data[column_name].notna() & 
            (self.data[column_name] > 0)
        ].sort_values(by=column_name, ascending=True)
        
        return filtered.head(limit)

    def get_stations_by_fuel_descending(self, fuel_type, limit=5):
        """Get most expensive stations for a specific fuel type."""
        if self.data is None or self.data.empty:
            self.load_data_from_db()
        
        if fuel_type not in FUEL_TYPES:
            return pd.DataFrame()
        
        column_name = FUEL_TYPES[fuel_type]['column'].title().replace('_', '_')
        
        # Filter valid prices and sort descending
        filtered = self.data[
            self.data[column_name].notna() & 
            (self.data[column_name] > 0)
        ].sort_values(by=column_name, ascending=False)
        
        return filtered.head(limit)

    def get_stations_by_municipality(self, id_municipality, limit=None):
        """Get all stations in a specific municipality by its ID."""
        if self.data is None or self.data.empty:
            self.load_data_from_db()
            if self.data is None or self.data.empty:
                self.logger.error("Data manager cache is still empty after trying to load.")
                return pd.DataFrame()

        if id_municipality not in MUNICIPALITIES:
            self.logger.warning(f"Invalid municipality ID provided: '{id_municipality}'")
            return pd.DataFrame()

        self.logger.debug(f"Querying for municipality ID: '{id_municipality}'")
        
        try:
            # Filter by the unique IDMunicipio
            filtered = self.data[self.data['IDMunicipio'] == id_municipality].copy()
            self.logger.info(f"Found {len(filtered)} stations for IDMunicipio '{id_municipality}'")
        except Exception as e:
            self.logger.error(f"Error filtering dataframe for IDMunicipio '{id_municipality}': {e}", exc_info=True)
            return pd.DataFrame()

        if limit:
            return filtered.head(limit)
        return filtered

    def find_stations_near_location(self, user_lat, user_lon, radius_km=10):
        """Find gas stations within radius of user location."""
        if self.data is None or self.data.empty:
            self.load_data_from_db()
        
        stations_in_radius = []
        user_location = (user_lat, user_lon)
        
        for _, station in self.data.iterrows():
            if pd.isna(station['Latitud']) or pd.isna(station['Longitud_WGS84']):
                continue
                
            station_location = (
                float(str(station['Latitud']).replace(',', '.')), 
                float(str(station['Longitud_WGS84']).replace(',', '.'))
            )
            
            distance = geodesic(user_location, station_location).kilometers
            
            if distance <= radius_km:
                station_data = station.to_dict()
                station_data['distance'] = round(distance, 2)
                stations_in_radius.append(station_data)
        
        # Sort by distance
        stations_in_radius.sort(key=lambda x: x['distance'])
        return stations_in_radius

    def get_last_update_time(self):
        """Get formatted last update time from the database."""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor()
            
            # Get the most recent update time from the database
            query = "SELECT MAX(Fecha_Actualizacion) FROM estaciones_servicio"
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            
            if result and result[0]:
                # Format the datetime to match Spanish format
                last_update = result[0]
                return last_update.strftime("%d/%m/%Y %H:%M:%S")
            else:
                # Fallback to current time if no data found
                return datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                
        except Exception as e:
            self.logger.error(f"Error getting last update time from database: {e}")
            
            # Fallback to file-based timestamp if database query fails
            try:
                timestamp_file = 'last_api_fetch.txt'
                if os.path.exists(timestamp_file):
                    with open(timestamp_file, 'r') as f:
                        timestamp_str = f.read().strip()
                        # Validate the timestamp format
                        datetime.datetime.strptime(timestamp_str, "%d/%m/%Y %H:%M:%S")
                        return timestamp_str
            except Exception as file_error:
                self.logger.error(f"Error reading timestamp file: {file_error}")
            
            # Final fallback to current time
            return datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # ===============================
    # HISTORICAL DATA AND CHARTS
    # ===============================

    def get_historical_data(self, fuel_type, days=30, id_municipality=None):
        """Get historical price data for chart generation."""
        if not self.connection or not self.connection.is_connected():
            self.connect()
            
        if fuel_type not in FUEL_TYPES:
            self.logger.error(f"Invalid fuel type: {fuel_type}")
            return pd.DataFrame()
            
        fuel_column = FUEL_TYPES[fuel_type]['column']
        start_date = datetime.date.today() - datetime.timedelta(days=days)
        
        query = f"""
        SELECT date, AVG({fuel_column}) as avg_price, 
               MIN({fuel_column}) as min_price, MAX({fuel_column}) as max_price,
               COUNT({fuel_column}) as station_count
        FROM historical_prices 
        WHERE date >= %s AND {fuel_column} IS NOT NULL AND {fuel_column} > 0
        """
        
        params = [start_date]
        
        if id_municipality and id_municipality in MUNICIPALITIES:
            query += " AND IDMunicipio = %s"
            params.append(id_municipality)
        
        query += " GROUP BY date ORDER BY date"
        
        # Debug logging
        self.logger.info(f"Historical data query for {fuel_type}:")
        self.logger.info(f"Fuel column: {fuel_column}")
        self.logger.info(f"Start date: {start_date}")
        self.logger.info(f"Municipality ID: {id_municipality}")
        self.logger.info(f"Query: {query}")
        self.logger.info(f"Params: {params}")
        
        try:
            result_df = pd.read_sql(query, self.connection, params=params)
            self.logger.info(f"Query returned {len(result_df)} rows")
            
            if not result_df.empty:
                self.logger.info("Sample results:")
                for _, row in result_df.head(3).iterrows():
                    self.logger.info(f"  {row['date']}: avg={row['avg_price']:.3f}, count={row['station_count']}")
            else:
                self.logger.warning("Query returned no results")
                
                # Additional debugging - check what data exists
                debug_query = f"""
                SELECT date, COUNT(*) as total_records, 
                       COUNT({fuel_column}) as fuel_records,
                       MIN({fuel_column}) as min_price,
                       MAX({fuel_column}) as max_price
                FROM historical_prices 
                WHERE date >= %s
                GROUP BY date ORDER BY date
                """
                debug_df = pd.read_sql(debug_query, self.connection, params=[start_date])
                self.logger.info(f"Debug query shows {len(debug_df)} dates with data:")
                for _, row in debug_df.iterrows():
                    self.logger.info(f"  {row['date']}: total={row['total_records']}, fuel={row['fuel_records']}, min={row['min_price']}, max={row['max_price']}")
            
            return result_df
        except Exception as e:
            self.logger.error(f"Error getting historical data: {e}")
            return pd.DataFrame()

    def generate_price_chart(self, fuel_type, days=30, id_municipality=None):
        """Generate a price chart and return it as bytes."""
        historical_data = self.get_historical_data(fuel_type, days, id_municipality)
        
        if historical_data.empty:
            self.logger.warning(f"No historical data available for chart generation: fuel={fuel_type}, days={days}, municipality={id_municipality}")
            return None
            
        self.logger.info(f"Generating chart with {len(historical_data)} data points")
            
        plt.style.use('default')
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Convert date column to datetime
        historical_data['date'] = pd.to_datetime(historical_data['date'])
        
        # Plot the data
        ax.plot(historical_data['date'], historical_data['avg_price'], 
                marker='o', linewidth=2, markersize=4, label='Preu mitjà')
        ax.fill_between(historical_data['date'], 
                       historical_data['min_price'], 
                       historical_data['max_price'], 
                       alpha=0.3, label='Rang min-max')
        
        # Formatting
        fuel_display_name = FUEL_TYPES[fuel_type]['display_name']
        title = f"Evolució preus - {fuel_display_name}"
        if id_municipality and id_municipality in MUNICIPALITIES:
            title += f" - {MUNICIPALITIES[id_municipality]['display_name']}"
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('Data')
        ax.set_ylabel('Preu (€/L)')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Format dates on x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, days//10)))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        # Add some stats to the title
        avg_stations = historical_data['station_count'].mean()
        title_with_stats = f"{title}\n(Mitjana {avg_stations:.0f} estacions per dia)"
        ax.set_title(title_with_stats, fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        # Convert to bytes
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close()
        
        self.logger.info(f"Chart generated successfully for {fuel_type}")
        return buf

    # ===============================
    # PRICE ALERTS MANAGEMENT
    # ===============================

    def create_price_alert(self, user_id, username, fuel_type, price_threshold, id_municipality=None):
        """Create a price alert for a user."""
        if not self.connection or not self.connection.is_connected():
            self.connect()
            
        cursor = self.connection.cursor()
        
        # Check if user already has this subscription using the new ID
        if id_municipality:
            check_query = """
            SELECT id FROM user_subscriptions 
            WHERE user_id = %s AND fuel_type = %s AND id_municipality = %s AND is_active = TRUE
            """
            cursor.execute(check_query, (user_id, fuel_type, id_municipality))
        else:
            check_query = """
            SELECT id FROM user_subscriptions 
            WHERE user_id = %s AND fuel_type = %s AND id_municipality IS NULL AND is_active = TRUE
            """
            cursor.execute(check_query, (user_id, fuel_type))
        
        existing = cursor.fetchone()
        
        try:
            if existing:
                # Update existing subscription
                update_query = """
                UPDATE user_subscriptions 
                SET price_threshold = %s, username = %s
                WHERE id = %s
                """
                cursor.execute(update_query, (price_threshold, username, existing[0]))
                action = "updated"
            else:
                # Create new subscription
                insert_query = """
                INSERT INTO user_subscriptions 
                (user_id, username, fuel_type, price_threshold, id_municipality)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, (user_id, username, fuel_type, price_threshold, id_municipality))
                action = "created"
            
            self.connection.commit()
            self.logger.info(f"Price alert {action} for user {username}")
            return True
            
        except Error as e:
            self.logger.error(f"Error creating price alert: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()

    def get_user_alerts(self, user_id):
        """Get all active alerts for a user."""
        if not self.connection or not self.connection.is_connected():
            self.connect()
            
        query = """
        SELECT fuel_type, price_threshold, id_municipality, created_at
        FROM user_subscriptions 
        WHERE user_id = %s AND is_active = TRUE
        ORDER BY created_at DESC
        """
        
        try:
            return pd.read_sql(query, self.connection, params=[user_id])
        except Exception as e:
            self.logger.error(f"Error getting user alerts: {e}")
            return pd.DataFrame()

    def remove_price_alert(self, user_id, fuel_type, id_municipality=None):
        """Remove a price alert."""
        if not self.connection or not self.connection.is_connected():
            self.connect()
            
        cursor = self.connection.cursor()
        
        try:
            if id_municipality:
                update_query = """
                UPDATE user_subscriptions 
                SET is_active = FALSE 
                WHERE user_id = %s AND fuel_type = %s AND id_municipality = %s AND is_active = TRUE
                """
                cursor.execute(update_query, (user_id, fuel_type, id_municipality))
            else:
                update_query = """
                UPDATE user_subscriptions 
                SET is_active = FALSE 
                WHERE user_id = %s AND fuel_type = %s AND id_municipality IS NULL AND is_active = TRUE
                """
                cursor.execute(update_query, (user_id, fuel_type))
            
            self.connection.commit()
            return cursor.rowcount > 0
            
        except Error as e:
            self.logger.error(f"Error removing price alert: {e}")
            return False
        finally:
            cursor.close()

    def check_price_alerts(self):
        """Check for triggered price alerts and return notifications."""
        if not self.connection or not self.connection.is_connected():
            self.connect()
            
        # Get all active subscriptions
        query = """
        SELECT user_id, username, fuel_type, price_threshold, id_municipality
        FROM user_subscriptions 
        WHERE is_active = TRUE
        """
        
        cursor = self.connection.cursor()
        
        try:
            cursor.execute(query)
            subscriptions = cursor.fetchall()
            alerts_to_send = []
            alerts_to_deactivate = []  # Track which alerts to deactivate
            
            for user_id, username, fuel_type, price_threshold, id_municipality in subscriptions:
                # Get current minimum price for this fuel type and municipality
                min_price_data = self._get_current_min_price(fuel_type, id_municipality)
                
                if min_price_data and min_price_data['price'] <= price_threshold:
                    # Alert is triggered - add to send list
                    alerts_to_send.append({
                        'user_id': user_id,
                        'username': username,
                        'fuel_type': fuel_type,
                        'price_threshold': price_threshold,
                        'current_price': min_price_data['price'],
                        'station_name': min_price_data['station_name'],
                        'id_municipality': id_municipality or min_price_data['id_municipality'],
                        'station_details': min_price_data
                    })
                    
                    # Add to deactivation list
                    alerts_to_deactivate.append({
                        'user_id': user_id,
                        'fuel_type': fuel_type,
                        'id_municipality': id_municipality
                    })
            
            # Deactivate triggered alerts to prevent repeated notifications
            if alerts_to_deactivate:
                self._deactivate_triggered_alerts(alerts_to_deactivate, cursor)
                self.logger.info(f"Deactivated {len(alerts_to_deactivate)} triggered alerts")
            
            return alerts_to_send
            
        except Error as e:
            self.logger.error(f"Error checking price alerts: {e}")
            return []
        finally:
            cursor.close()

    def _deactivate_triggered_alerts(self, alerts_to_deactivate, cursor):
        """Deactivate a list of triggered alerts to prevent spam."""
        try:
            for alert in alerts_to_deactivate:
                user_id = alert['user_id']
                fuel_type = alert['fuel_type']
                id_municipality = alert['id_municipality']
                
                if id_municipality:
                    update_query = """
                    UPDATE user_subscriptions 
                    SET is_active = FALSE 
                    WHERE user_id = %s AND fuel_type = %s AND id_municipality = %s AND is_active = TRUE
                    """
                    cursor.execute(update_query, (user_id, fuel_type, id_municipality))
                else:
                    update_query = """
                    UPDATE user_subscriptions 
                    SET is_active = FALSE 
                    WHERE user_id = %s AND fuel_type = %s AND id_municipality IS NULL AND is_active = TRUE
                    """
                    cursor.execute(update_query, (user_id, fuel_type))
                
                self.logger.info(f"Deactivated alert for user {user_id}, fuel {fuel_type}, municipality {id_municipality}")
            
            self.connection.commit()
            
        except Error as e:
            self.logger.error(f"Error deactivating triggered alerts: {e}")
            self.connection.rollback()
            raise

    def _get_current_min_price(self, fuel_type, id_municipality=None):
        """Get current minimum price for a fuel type and municipality ID."""
        if self.data is None or self.data.empty:
            self.load_data_from_db()
        
        if fuel_type not in FUEL_TYPES:
            return None
        
        column_name = FUEL_TYPES[fuel_type]['column'].title().replace('_', '_')
        
        # Filter data by price
        filtered = self.data[
            self.data[column_name].notna() & 
            (self.data[column_name] > 0)
        ].copy()
        
        if id_municipality and id_municipality in MUNICIPALITIES:
            # Filter by the unique ID
            filtered = filtered[filtered['IDMunicipio'] == id_municipality]
        
        if filtered.empty:
            return None
        
        # Get minimum price row
        min_row = filtered.loc[filtered[column_name].idxmin()]
        
        return {
            'price': min_row[column_name],
            'station_name': min_row['Rotulo'],
            'municipality': min_row['Localidad'],
            'id_municipality': min_row['IDMunicipio'],
            'address': min_row['Direccion'],
            'station_data': min_row
        }

    # ===============================
    # USER MANAGEMENT
    # ===============================

    def track_user_interaction(self, user_id, username=None, first_name=None, last_name=None, language_code=None):
        """Track user interactions for analytics."""
        if not self.connection or not self.connection.is_connected():
            self.connect()
            
        cursor = self.connection.cursor()
        
        # Upsert user data
        upsert_query = """
        INSERT INTO bot_users (user_id, username, first_name, last_name, language_code, interaction_count)
        VALUES (%s, %s, %s, %s, %s, 1)
        ON DUPLICATE KEY UPDATE
        username = VALUES(username),
        first_name = VALUES(first_name),
        last_name = VALUES(last_name),
        language_code = VALUES(language_code),
        last_seen = CURRENT_TIMESTAMP,
        interaction_count = interaction_count + 1,
        is_active = TRUE
        """
        
        try:
            cursor.execute(upsert_query, (user_id, username, first_name, last_name, language_code))
            self.connection.commit()
        except Error as e:
            self.logger.error(f"Error tracking user interaction: {e}")
        finally:
            cursor.close()

    def get_user_stats(self):
        """Get bot usage statistics for admin panel."""
        if not self.connection or not self.connection.is_connected():
            self.connect()
            
        try:
            cursor = self.connection.cursor()
            
            # Total users
            cursor.execute("SELECT COUNT(*) FROM bot_users")
            total_users = cursor.fetchone()[0]
            
            # Active users (used in last 30 days)
            cursor.execute("""
                SELECT COUNT(*) FROM bot_users 
                WHERE last_seen >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            """)
            active_users = cursor.fetchone()[0]
            
            # Today's interactions
            cursor.execute("""
                SELECT SUM(interaction_count) FROM bot_users 
                WHERE DATE(last_seen) = CURDATE()
            """)
            today_interactions = cursor.fetchone()[0] or 0
            
            # Active alerts
            cursor.execute("SELECT COUNT(*) FROM user_subscriptions WHERE is_active = TRUE")
            active_alerts = cursor.fetchone()[0]
            
            cursor.close()
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'today_interactions': today_interactions,
                'active_alerts': active_alerts
            }
            
        except Error as e:
            self.logger.error(f"Error getting user stats: {e}")
            return {'total_users': 0, 'active_users': 0, 'today_interactions': 0, 'active_alerts': 0}

    def debug_historical_data(self, fuel_type=None, days=30):
        """Debug method to check what historical data exists in the database."""
        if not self.connection or not self.connection.is_connected():
            self.connect()
            
        cursor = self.connection.cursor()
        
        try:
            # Check how many records we have per date
            cursor.execute("""
                SELECT date, COUNT(*) as station_count,
                       COUNT(precio_gasolina_95_e5) as gasoline_count,
                       COUNT(precio_gasoleo_a) as diesel_count
                FROM historical_prices 
                WHERE date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
                GROUP BY date 
                ORDER BY date DESC
            """, (days,))
            
            results = cursor.fetchall()
            
            print(f"\n=== Historical Data Debug (Last {days} days) ===")
            print("Date\t\tStations\tGasoline\tDiesel")
            print("-" * 50)
            
            for date, station_count, gasoline_count, diesel_count in results:
                print(f"{date}\t{station_count}\t\t{gasoline_count}\t\t{diesel_count}")
            
            if not results:
                print("No historical data found!")
                
                # Check if main table has data
                cursor.execute("SELECT COUNT(*) FROM estaciones_servicio")
                main_count = cursor.fetchone()[0]
                print(f"Main table has {main_count} stations")
                
                # Check if historical table exists and is empty
                cursor.execute("SELECT COUNT(*) FROM historical_prices")
                hist_count = cursor.fetchone()[0]
                print(f"Historical table has {hist_count} total records")
            
            # If specific fuel type requested, show sample data
            if fuel_type and fuel_type in FUEL_TYPES:
                fuel_column = FUEL_TYPES[fuel_type]['column']
                fuel_name = FUEL_TYPES[fuel_type]['display_name']
                
                cursor.execute(f"""
                    SELECT date, AVG({fuel_column}) as avg_price, COUNT(*) as count
                    FROM historical_prices 
                    WHERE {fuel_column} IS NOT NULL AND {fuel_column} > 0
                      AND date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
                    GROUP BY date 
                    ORDER BY date DESC
                    LIMIT 10
                """, (days,))
                
                fuel_results = cursor.fetchall()
                print(f"\n=== {fuel_name} Data Sample ===")
                print("Date\t\tAvg Price\tStations")
                print("-" * 40)
                
                for date, avg_price, count in fuel_results:
                    print(f"{date}\t{avg_price:.3f}€\t\t{count}")
                
        except Error as e:
            print(f"Error in debug: {e}")
        finally:
            cursor.close()

# Create global instance
menorca_data_manager = MenorcaDataManager() 