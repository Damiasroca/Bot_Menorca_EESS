import pandas as pd
import mysql.connector as msql
from mysql.connector import Error
import secret
import datetime
from geopy.distance import geodesic
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
import os

class DataManager:
    def __init__(self):
        self.db_config = {
            'host': secret.secret['db_host'],
            'user': secret.secret['db_user'],
            'password': secret.secret['db_password'],
            'database': secret.secret['db_name']
        }
        self.connection = None
        self.data = None
        self.last_update_time = None

    def connect(self):
        try:
            self.connection = msql.connect(**self.db_config)
            print("Connected to MySQL database")
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            raise

    def create_tables(self):
        """Create tables for historical data and user subscriptions if they don't exist."""
        if not self.connection or not self.connection.is_connected():
            self.connect()
        
        cursor = self.connection.cursor()
        
        # Create historical prices table
        historical_prices_table = """
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
        """
        
        # Create user subscriptions table
        user_subscriptions_table = """
        CREATE TABLE IF NOT EXISTS user_subscriptions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id BIGINT NOT NULL,
            username VARCHAR(255),
            fuel_type VARCHAR(50) NOT NULL,
            price_threshold DECIMAL(5, 3) NOT NULL,
            town VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            INDEX idx_user_id (user_id),
            INDEX idx_fuel_type (fuel_type),
            INDEX idx_active (is_active)
        )
        """
        
        # Create users table for analytics and user management
        users_table = """
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
            cursor.execute(historical_prices_table)
            cursor.execute(user_subscriptions_table)
            cursor.execute(users_table)
            self.connection.commit()
            print("Database tables created successfully")
        except Error as e:
            print(f"Error creating tables: {e}")
            raise
        finally:
            cursor.close()

    def load_data(self):
        if not self.connection or not self.connection.is_connected():
            self.connect()
        
        # Create tables if they don't exist
        self.create_tables()
        
        if self.connection:
            query = "SELECT * FROM menorca.benzineres"
            try:
                self.data = pd.read_sql(query, self.connection)
                
                print(f"Original columns: {list(self.data.columns)}")
                
                # Clean column names for easier access
                clean_cols = {
                    'Rótulo': 'Rotulo',
                    'Precio Gasolina 95 E5': 'Precio_Gasolina_95_E5',
                    'Precio Gasoleo A': 'Precio_Gasoleo_A',
                    'Dirección': 'Direccion',
                    'Longitud (WGS84)': 'Longitud_WGS84',
                    'Precio Gasoleo B': 'Precio_Gasoleo_B',
                    'Precio Gasoleo Premium': 'Precio_Gasoleo_Premium',
                    'Precio Gases Licuados del petróleo': 'Precio_Gases_Licuados_del_petroleo'
                }
                
                # Only rename columns that actually exist
                existing_renames = {old: new for old, new in clean_cols.items() if old in self.data.columns}
                self.data.rename(columns=existing_renames, inplace=True)
                
                print(f"Cleaned columns: {list(self.data.columns)}")

                # Load the actual API fetch timestamp instead of using current time
                self._load_api_fetch_timestamp()
                print("Data loaded successfully")
                if self.data.empty:
                    print("Warning: 'benzineres' table is empty.")
                    
                # Store daily snapshot for historical data
                self.store_daily_snapshot()
                    
            except Exception as e:
                print(f"Error loading data from 'benzineres' table: {e}")
                raise
        else:
            raise ConnectionError("Failed to establish database connection.")

    def _load_api_fetch_timestamp(self):
        """Load the actual API fetch timestamp from file."""
        # Use relative path to be more portable - same as main_database.py
        script_dir = os.path.dirname(os.path.abspath(__file__))
        timestamp_file = os.path.join(script_dir, 'last_api_fetch.txt')
        try:
            with open(timestamp_file, 'r') as f:
                timestamp_str = f.read().strip()
                self.last_update_time = datetime.datetime.strptime(timestamp_str, "%d/%m/%Y %H:%M:%S")
                print(f"Loaded API fetch timestamp: {timestamp_str}")
        except FileNotFoundError:
            print("API fetch timestamp file not found, using current time")
            self.last_update_time = datetime.datetime.now()
        except Exception as e:
            print(f"Error loading API fetch timestamp: {e}, using current time")
            self.last_update_time = datetime.datetime.now()

    def _convert_decimal(self, value):
        """Convert comma-decimal to dot-decimal for MySQL."""
        if value is None or pd.isna(value):
            return None
        try:
            # Convert to string and replace comma with dot
            str_val = str(value).replace(',', '.')
            return float(str_val)
        except (ValueError, TypeError):
            return None

    def store_daily_snapshot(self):
        """Store a daily snapshot of current prices for historical tracking."""
        if not self.connection or not self.connection.is_connected():
            self.connect()
            
        cursor = self.connection.cursor()
        today = datetime.date.today()
        
        # Check if we already have data for today
        check_query = "SELECT COUNT(*) FROM historical_prices WHERE date = %s"
        cursor.execute(check_query, (today,))
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"Historical data for {today} already exists")
            cursor.close()
            return
            
        # Insert today's data
        insert_query = """
        INSERT INTO historical_prices 
        (date, rotulo, localidad, direccion, latitud, longitud_wgs84, 
         precio_gasolina_95_e5, precio_gasoleo_a, precio_gasoleo_b, 
         precio_gasoleo_premium, precio_gases_licuados_del_petroleo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        try:
            for _, row in self.data.iterrows():
                # Use get() method to handle missing columns gracefully and convert decimals
                cursor.execute(insert_query, (
                    today,
                    row.get('Rotulo', None),
                    row.get('Localidad', None),
                    row.get('Direccion', None),
                    self._convert_decimal(row.get('Latitud', None)),
                    self._convert_decimal(row.get('Longitud_WGS84', None)),
                    self._convert_decimal(row.get('Precio_Gasolina_95_E5', None)),
                    self._convert_decimal(row.get('Precio_Gasoleo_A', None)),
                    self._convert_decimal(row.get('Precio_Gasoleo_B', None)),
                    self._convert_decimal(row.get('Precio_Gasoleo_Premium', None)),
                    self._convert_decimal(row.get('Precio_Gases_Licuados_del_petroleo', None))
                ))
            
            self.connection.commit()
            print(f"Daily snapshot stored for {today}")
            
        except Error as e:
            print(f"Error storing daily snapshot: {e}")
            self.connection.rollback()
        finally:
            cursor.close()

    def get_historical_data(self, fuel_type, days=30, town=None):
        """Get historical price data for chart generation."""
        if not self.connection or not self.connection.is_connected():
            self.connect()
            
        fuel_column_map = {
            'BENZINA': 'precio_gasolina_95_e5',
            'GASOLIA': 'precio_gasoleo_a',
            'GASOLIB': 'precio_gasoleo_b',
            'GASOLIP': 'precio_gasoleo_premium',
            'GLP': 'precio_gases_licuados_del_petroleo'
        }
        
        if fuel_type not in fuel_column_map:
            return pd.DataFrame()
            
        fuel_column = fuel_column_map[fuel_type]
        start_date = datetime.date.today() - datetime.timedelta(days=days)
        
        query = f"""
        SELECT date, AVG({fuel_column}) as avg_price, MIN({fuel_column}) as min_price, MAX({fuel_column}) as max_price
        FROM historical_prices 
        WHERE date >= %s AND {fuel_column} IS NOT NULL
        """
        
        params = [start_date]
        
        if town:
            town_map = {
                'MAO': 'MAO',
                'CIUTADELLA': 'CIUTADELLA DE MENORCA',
                'ESMERCADAL': 'MERCADAL (ES)',
                'ALAIOR': 'ALAIOR',
                'FERRERIES': 'FERRERIES',
                'ESCASTELL': 'SON VILAR',
                'SANTLLUÍS': 'SANT LLUIS',
                'FORNELLS': 'MERCADAL (ES)'
            }
            mapped_town = town_map.get(town.upper().replace(" ", ""))
            if mapped_town:
                query += " AND localidad = %s"
                params.append(mapped_town)
        
        query += " GROUP BY date ORDER BY date"
        
        try:
            return pd.read_sql(query, self.connection, params=params)
        except Exception as e:
            print(f"Error getting historical data: {e}")
            return pd.DataFrame()

    def generate_price_chart(self, fuel_type, days=30, town=None):
        """Generate a price chart and return it as bytes."""
        historical_data = self.get_historical_data(fuel_type, days, town)
        
        if historical_data.empty:
            return None
            
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
        fuel_names = {
            'BENZINA': 'Benzina 95 E5',
            'GASOLIA': 'Gasoli A',
            'GASOLIB': 'Gasoli B', 
            'GASOLIP': 'Gasoli Premium',
            'GLP': 'GLP'
        }
        
        title = f"Evolució preus - {fuel_names.get(fuel_type, fuel_type)}"
        if town:
            title += f" - {town}"
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('Data')
        ax.set_ylabel('Preu (€/L)')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Format dates on x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, days//10)))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        # Convert to bytes
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close()
        
        return buf

    def find_stations_near_location(self, user_lat, user_lon, radius_km=10):
        """Find gas stations within radius of user location."""
        stations_in_radius = []
        user_location = (user_lat, user_lon)
        
        for _, station in self.data.iterrows():
            if pd.isna(station['Latitud']) or pd.isna(station['Longitud_WGS84']):
                continue
                
            station_location = (float(str(station['Latitud']).replace(',', '.')), 
                              float(str(station['Longitud_WGS84']).replace(',', '.')))
            
            distance = geodesic(user_location, station_location).kilometers
            
            if distance <= radius_km:
                station_data = station.to_dict()
                station_data['distance'] = round(distance, 2)
                stations_in_radius.append(station_data)
        
        # Sort by distance
        stations_in_radius.sort(key=lambda x: x['distance'])
        return stations_in_radius

    def add_price_alert(self, user_id, username, fuel_type, price_threshold, town=None):
        """Add a price alert subscription for a user."""
        if not self.connection or not self.connection.is_connected():
            self.connect()
            
        cursor = self.connection.cursor()
        
        # Check if user already has this subscription
        if town is None:
            check_query = """
            SELECT id FROM user_subscriptions 
            WHERE user_id = %s AND fuel_type = %s AND town IS NULL AND is_active = TRUE
            """
            cursor.execute(check_query, (user_id, fuel_type))
        else:
            check_query = """
            SELECT id FROM user_subscriptions 
            WHERE user_id = %s AND fuel_type = %s AND town = %s AND is_active = TRUE
            """
            cursor.execute(check_query, (user_id, fuel_type, town))
        
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
                (user_id, username, fuel_type, price_threshold, town)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, (user_id, username, fuel_type, price_threshold, town))
                action = "created"
            
            self.connection.commit()
            print(f"Price alert {action} for user {username}")
            return True
            
        except Error as e:
            print(f"Error adding price alert: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()

    def remove_price_alert(self, user_id, fuel_type, town=None):
        """Remove a price alert subscription."""
        if not self.connection or not self.connection.is_connected():
            self.connect()
            
        cursor = self.connection.cursor()
        
        try:
            if town is None:
                update_query = """
                UPDATE user_subscriptions 
                SET is_active = FALSE 
                WHERE user_id = %s AND fuel_type = %s AND town IS NULL AND is_active = TRUE
                """
                cursor.execute(update_query, (user_id, fuel_type))
                print(f"Removing alert for user {user_id}, fuel {fuel_type}, town=NULL")
            else:
                update_query = """
                UPDATE user_subscriptions 
                SET is_active = FALSE 
                WHERE user_id = %s AND fuel_type = %s AND town = %s AND is_active = TRUE
                """
                cursor.execute(update_query, (user_id, fuel_type, town))
                print(f"Removing alert for user {user_id}, fuel {fuel_type}, town={town}")
            
            self.connection.commit()
            rows_affected = cursor.rowcount
            print(f"Alert removal affected {rows_affected} rows")
            
            return rows_affected > 0
            
        except Error as e:
            print(f"Error removing price alert: {e}")
            return False
        finally:
            cursor.close()

    def get_user_subscriptions(self, user_id):
        """Get all active subscriptions for a user."""
        if not self.connection or not self.connection.is_connected():
            self.connect()
            
        query = """
        SELECT fuel_type, price_threshold, town, created_at
        FROM user_subscriptions 
        WHERE user_id = %s AND is_active = TRUE
        ORDER BY created_at DESC
        """
        
        try:
            return pd.read_sql(query, self.connection, params=[user_id])
        except Exception as e:
            print(f"Error getting user subscriptions: {e}")
            return pd.DataFrame()

    def check_price_alerts(self):
        """Check for price alerts that should be triggered and return them."""
        if not self.connection or not self.connection.is_connected():
            self.connect()
            
        # Get all active subscriptions
        query = """
        SELECT user_id, username, fuel_type, price_threshold, town
        FROM user_subscriptions 
        WHERE is_active = TRUE
        """
        
        cursor = self.connection.cursor()
        
        try:
            cursor.execute(query)
            subscriptions = cursor.fetchall()
            alerts_to_send = []
            
            for user_id, username, fuel_type, price_threshold, town in subscriptions:
                # Get current prices for this fuel type and town
                current_data = self.get_current_prices_for_alert(fuel_type, town)
                
                # Check if any station meets the price threshold
                if not current_data.empty:
                    min_price = current_data.min()
                    if min_price <= price_threshold:
                        # Find the station with this price
                        matching_stations = self.get_stations_at_price(fuel_type, min_price, town)
                        if not matching_stations.empty:
                            alerts_to_send.append({
                                'user_id': user_id,
                                'username': username,
                                'fuel_type': fuel_type,
                                'price_threshold': price_threshold,
                                'current_price': min_price,
                                'town': town,
                                'stations': matching_stations.head(3).to_dict('records')
                            })
            
            return alerts_to_send
            
        except Error as e:
            print(f"Error checking price alerts: {e}")
            return []
        finally:
            cursor.close()

    def get_current_prices_for_alert(self, fuel_type, town=None):
        """Get current prices for alert checking."""
        fuel_column_map = {
            'BENZINA': 'Precio_Gasolina_95_E5',
            'GASOLIA': 'Precio_Gasoleo_A',
            'GASOLIB': 'Precio_Gasoleo_B',
            'GASOLIP': 'Precio_Gasoleo_Premium',
            'GLP': 'Precio_Gases_Licuados_del_petroleo'
        }
        
        if fuel_type not in fuel_column_map:
            return pd.Series()
            
        fuel_column = fuel_column_map[fuel_type]
        df = self.data[self.data[fuel_column].notna()]
        
        if town:
            town_map = {
                'MAO': 'MAO',
                'CIUTADELLA': 'CIUTADELLA DE MENORCA',
                'ESMERCADAL': 'MERCADAL (ES)',
                'ALAIOR': 'ALAIOR',
                'FERRERIES': 'FERRERIES',
                'SANTLLUÍS': 'SANT LLUIS',
                'FORNELLS': 'MERCADAL (ES)'
            }
            mapped_town = town_map.get(town.upper().replace(" ", ""))
            if mapped_town:
                df = df[df['Localidad'] == mapped_town]
        
        return df[fuel_column]

    def get_stations_at_price(self, fuel_type, price, town=None):
        """Get stations that have a specific price for a fuel type."""
        fuel_column_map = {
            'BENZINA': 'Precio_Gasolina_95_E5',
            'GASOLIA': 'Precio_Gasoleo_A',
            'GASOLIB': 'Precio_Gasoleo_B',
            'GASOLIP': 'Precio_Gasoleo_Premium',
            'GLP': 'Precio_Gases_Licuados_del_petroleo'
        }
        
        if fuel_type not in fuel_column_map:
            return pd.DataFrame()
            
        fuel_column = fuel_column_map[fuel_type]
        df = self.data[self.data[fuel_column] == price]
        
        if town:
            town_map = {
                'MAO': 'MAO',
                'CIUTADELLA': 'CIUTADELLA DE MENORCA',
                'ESMERCADAL': 'MERCADAL (ES)',
                'ALAIOR': 'ALAIOR',
                'FERRERIES': 'FERRERIES',
                'SANTLLUÍS': 'SANT LLUIS',
                'FORNELLS': 'MERCADAL (ES)'
            }
            mapped_town = town_map.get(town.upper().replace(" ", ""))
            if mapped_town:
                df = df[df['Localidad'] == mapped_town]
        
        return df

    def get_all_data(self):
        return self.data

    def get_last_update_time(self):
        """Get the last time data was actually fetched from government APIs (not bot restart time)."""
        if self.last_update_time:
            return self.last_update_time.strftime("%d/%m/%Y %H:%M:%S")
        else:
            return "N/A - No API fetch data available"

    def check_historical_data_status(self):
        """Check the status of historical data table."""
        if not self.connection or not self.connection.is_connected():
            self.connect()
            
        cursor = self.connection.cursor()
        
        try:
            # Check if historical_prices table exists
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = %s AND table_name = 'historical_prices'
            """, (self.db_config['database'],))
            
            table_exists = cursor.fetchone()[0] > 0
            
            if not table_exists:
                print("❌ historical_prices table does not exist")
                return False
                
            # Check how many records exist
            cursor.execute("SELECT COUNT(*) FROM historical_prices")
            total_records = cursor.fetchone()[0]
            
            # Check date range
            cursor.execute("SELECT MIN(date), MAX(date) FROM historical_prices")
            date_range = cursor.fetchone()
            
            print(f"📊 Historical data status:")
            print(f"   • Total records: {total_records}")
            print(f"   • Date range: {date_range[0]} to {date_range[1]}" if date_range[0] else "   • No data yet")
            
            return total_records > 0
            
        except Error as e:
            print(f"Error checking historical data status: {e}")
            return False
        finally:
            cursor.close()

    def force_populate_historical_data(self):
        """Manually populate historical data from current data (for initial setup)."""
        if not self.connection or not self.connection.is_connected():
            self.connect()
            
        cursor = self.connection.cursor()
        today = datetime.date.today()
        
        try:
            # Create table if it doesn't exist
            self.create_tables()
            
            # Check if we already have data for today
            cursor.execute("SELECT COUNT(*) FROM historical_prices WHERE date = %s", (today,))
            count = cursor.fetchone()[0]
            
            if count > 0:
                print(f"Historical data for {today} already exists ({count} records)")
                return True
            
            if self.data is None or self.data.empty:
                print("❌ No current data available to populate historical data")
                return False
                
            # Insert today's data
            insert_query = """
            INSERT INTO historical_prices 
            (date, rotulo, localidad, direccion, latitud, longitud_wgs84, 
             precio_gasolina_95_e5, precio_gasoleo_a, precio_gasoleo_b, 
             precio_gasoleo_premium, precio_gases_licuados_del_petroleo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            records_inserted = 0
            for _, row in self.data.iterrows():
                cursor.execute(insert_query, (
                    today,
                    row.get('Rotulo', None),
                    row.get('Localidad', None),
                    row.get('Direccion', None),
                    self._convert_decimal(row.get('Latitud', None)),
                    self._convert_decimal(row.get('Longitud_WGS84', None)),
                    self._convert_decimal(row.get('Precio_Gasolina_95_E5', None)),
                    self._convert_decimal(row.get('Precio_Gasoleo_A', None)),
                    self._convert_decimal(row.get('Precio_Gasoleo_B', None)),
                    self._convert_decimal(row.get('Precio_Gasoleo_Premium', None)),
                    self._convert_decimal(row.get('Precio_Gases_Licuados_del_petroleo', None))
                ))
                records_inserted += 1
            
            self.connection.commit()
            print(f"✅ Manually populated {records_inserted} historical records for {today}")
            return True
            
        except Error as e:
            print(f"Error populating historical data: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()

    # Per estacions de servei
    def estacions_servei_extraccio_benzina_ascendent(self):
        df = self.data[self.data['Precio_Gasolina_95_E5'].notna()]
        return df.sort_values(by='Precio_Gasolina_95_E5', ascending=True)

    def estacions_servei_extraccio_benzina_descendent(self):
        df = self.data[self.data['Precio_Gasolina_95_E5'].notna()]
        return df.sort_values(by='Precio_Gasolina_95_E5', ascending=False)

    def estacions_servei_extraccio_diesel_A_ascendent(self):
        df = self.data[self.data['Precio_Gasoleo_A'].notna()]
        return df.sort_values(by='Precio_Gasoleo_A', ascending=True)

    #Per carburants
    def carburants_extraccio_diesel_A_ascendent(self):
        df = self.data[self.data['Precio_Gasoleo_A'].notna()]
        return df.sort_values(by='Precio_Gasoleo_A', ascending=True)

    def carburants_extraccio_diesel_B_ascendent(self):
        df = self.data[self.data['Precio_Gasoleo_B'].notna()]
        return df.sort_values(by='Precio_Gasoleo_B', ascending=True)

    def carburants_extraccio_diesel_premium_ascendent(self):
        df = self.data[self.data['Precio_Gasoleo_Premium'].notna()]
        return df.sort_values(by='Precio_Gasoleo_Premium', ascending=True)

    def carburants_extraccio_GLP_ascendent(self):
        df = self.data[self.data['Precio_Gases_Licuados_del_petroleo'].notna()]
        return df.sort_values(by='Precio_Gases_Licuados_del_petroleo', ascending=True)

    #Per Municipis
    def get_town_data(self, town_name):
        town_map = {
            'MAO': 'MAO',
            'CIUTADELLA': 'CIUTADELLA DE MENORCA',
            'ESMERCADAL': 'MERCADAL (ES)',
            'ALAIOR': 'ALAIOR',
            'FERRERIES': 'FERRERIES',
            'SANTLLUÍS': 'SANT LLUIS',
            'FORNELLS': 'MERCADAL (ES)' 
        }
        
        mapped_name = town_map.get(town_name.upper().replace(" ", ""))
        if not mapped_name:
            return pd.DataFrame()

        df = self.data[self.data['Localidad'] == mapped_name]
        
        if town_name.upper() == 'FORNELLS':
            df = df[df['Rotulo'] == 'GALP']
            
        return df.sort_values(by='Precio_Gasolina_95_E5', ascending=True)

    def track_user_interaction(self, user_id, username=None, first_name=None, last_name=None, language_code=None):
        """Track user interaction for analytics and user management."""
        if not self.connection or not self.connection.is_connected():
            self.connect()
            
        cursor = self.connection.cursor()
        
        try:
            # Check if user exists
            check_query = "SELECT user_id, interaction_count FROM bot_users WHERE user_id = %s"
            cursor.execute(check_query, (user_id,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                # Update existing user
                update_query = """
                UPDATE bot_users 
                SET username = COALESCE(%s, username),
                    first_name = COALESCE(%s, first_name),
                    last_name = COALESCE(%s, last_name),
                    language_code = COALESCE(%s, language_code),
                    last_seen = CURRENT_TIMESTAMP,
                    interaction_count = interaction_count + 1,
                    is_active = TRUE
                WHERE user_id = %s
                """
                cursor.execute(update_query, (username, first_name, last_name, language_code, user_id))
                print(f"Updated user {user_id} (interactions: {existing_user[1] + 1})")
            else:
                # Insert new user
                insert_query = """
                INSERT INTO bot_users 
                (user_id, username, first_name, last_name, language_code, first_seen, last_seen, interaction_count)
                VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1)
                """
                cursor.execute(insert_query, (user_id, username, first_name, last_name, language_code))
                print(f"New user registered: {user_id} ({username or first_name})")
            
            self.connection.commit()
            return True
            
        except Error as e:
            print(f"Error tracking user interaction: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()

    def get_user_stats(self):
        """Get user statistics for admin purposes."""
        if not self.connection or not self.connection.is_connected():
            self.connect()
            
        cursor = self.connection.cursor()
        
        try:
            stats_query = """
            SELECT 
                COUNT(*) as total_users,
                COUNT(CASE WHEN DATE(last_seen) = CURDATE() THEN 1 END) as today_active,
                COUNT(CASE WHEN DATE(last_seen) >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) THEN 1 END) as week_active,
                COUNT(CASE WHEN DATE(last_seen) >= DATE_SUB(CURDATE(), INTERVAL 30 DAY) THEN 1 END) as month_active,
                SUM(interaction_count) as total_interactions,
                AVG(interaction_count) as avg_interactions_per_user
            FROM bot_users 
            WHERE is_active = TRUE
            """
            
            cursor.execute(stats_query)
            stats = cursor.fetchone()
            
            return {
                'total_users': stats[0] or 0,
                'today_active': stats[1] or 0,
                'week_active': stats[2] or 0,
                'month_active': stats[3] or 0,
                'total_interactions': stats[4] or 0,
                'avg_interactions_per_user': round(stats[5] or 0, 2)
            }
            
        except Error as e:
            print(f"Error getting user stats: {e}")
            return {}
        finally:
            cursor.close()

    def get_top_users(self, limit=10):
        """Get most active users."""
        if not self.connection or not self.connection.is_connected():
            self.connect()
            
        cursor = self.connection.cursor()
        
        try:
            query = """
            SELECT user_id, username, first_name, interaction_count, last_seen
            FROM bot_users 
            WHERE is_active = TRUE
            ORDER BY interaction_count DESC, last_seen DESC
            LIMIT %s
            """
            
            cursor.execute(query, (limit,))
            return cursor.fetchall()
            
        except Error as e:
            print(f"Error getting top users: {e}")
            return []
        finally:
            cursor.close()

    def deactivate_user(self, user_id):
        """Mark a user as inactive (for privacy/GDPR compliance)."""
        if not self.connection or not self.connection.is_connected():
            self.connect()
            
        cursor = self.connection.cursor()
        
        try:
            update_query = "UPDATE bot_users SET is_active = FALSE WHERE user_id = %s"
            cursor.execute(update_query, (user_id,))
            self.connection.commit()
            
            # Also deactivate their alerts
            alert_query = "UPDATE user_subscriptions SET is_active = FALSE WHERE user_id = %s"
            cursor.execute(alert_query, (user_id,))
            self.connection.commit()
            
            return cursor.rowcount > 0
            
        except Error as e:
            print(f"Error deactivating user: {e}")
            return False
        finally:
            cursor.close()

    def get_user_info(self, user_id):
        """Get detailed information about a specific user."""
        if not self.connection or not self.connection.is_connected():
            self.connect()
            
        cursor = self.connection.cursor()
        
        try:
            user_query = """
            SELECT user_id, username, first_name, last_name, language_code,
                   first_seen, last_seen, interaction_count, is_active
            FROM bot_users 
            WHERE user_id = %s
            """
            
            cursor.execute(user_query, (user_id,))
            user_data = cursor.fetchone()
            
            if not user_data:
                return None
                
            # Get user's active alerts
            alerts_query = """
            SELECT fuel_type, price_threshold, town, created_at
            FROM user_subscriptions 
            WHERE user_id = %s AND is_active = TRUE
            """
            
            cursor.execute(alerts_query, (user_id,))
            alerts = cursor.fetchall()
            
            return {
                'user_id': user_data[0],
                'username': user_data[1],
                'first_name': user_data[2],
                'last_name': user_data[3],
                'language_code': user_data[4],
                'first_seen': user_data[5],
                'last_seen': user_data[6],
                'interaction_count': user_data[7],
                'is_active': user_data[8],
                'active_alerts': len(alerts),
                'alerts': alerts
            }
            
        except Error as e:
            print(f"Error getting user info: {e}")
            return None
        finally:
            cursor.close()

# Global instance of DataManager
data_manager = DataManager() 