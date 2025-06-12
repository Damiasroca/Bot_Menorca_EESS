# Bot Menorca EESS - Advanced Fuel Price Monitoring System

This document explains the advanced Telegram bot implementation for Menorca fuel price monitoring, featuring a robust ID-based municipality system, automatic alert management, and comprehensive data reliability improvements.

## 🏗️ Architecture Overview

The bot implements a sophisticated architecture with the following key components:

### Core Files (Production-Ready Structure)

#### Main Application Files
- **`main_bot_menorca.py`** - Main Telegram bot application with conversation handlers and advanced features
- **`data_manager_menorca.py`** - Advanced data layer with ID-based municipality system and data corrections
- **`constants_menorca.py`** - Configuration hub with ID-based municipality mappings and localized text
- **`secret.py`** - Secret management for API keys, database credentials, and admin user IDs

#### Supporting Scripts
- **`downloads_menorca.sh`** - Downloads JSON data from Spanish Ministry API for all Menorca municipalities
- **`notification_sender.py`** - Enhanced scheduled script with automatic alert deactivation
- **`bot_menorca_telegram_starter.sh`** - Service script to manage bot execution

## 🚀 Key Features Implemented

### 1. **Advanced Municipality System (ID-Based)**

✅ **Unique ID System:**
- Uses official `IDMunicipio` from government data for reliability
- Eliminates string-based matching issues
- Robust data validation and error handling

✅ **Municipality Coverage:**
```python
MUNICIPALITIES = {
    '829': {'display_name': 'Maó'},         # Official ID from JSON
    '810': {'display_name': 'Ciutadella'},  # Official ID from JSON
    '794': {'display_name': 'Alaior'},      # Official ID from JSON
    '832': {'display_name': 'Es Mercadal'}, # Official ID from JSON
    '819': {'display_name': 'Ferreries'},   # Official ID from JSON
    '848': {'display_name': 'Sant Lluís'},  # Official ID from JSON
    '666': {'display_name': 'Fornells', 'is_custom': True}  # Special case
}
```

✅ **Fornells Special Handling:**
- Custom data correction for GALP station (IDEESS '2645')
- Automatically reassigns from Es Mercadal to Fornells
- Maintains data integrity while respecting local geography

### 2. **Smart Price Alert System**

✅ **One-Time Alert Notifications:**
- Alerts trigger once and automatically deactivate
- Prevents spam notifications every 10 minutes
- Clear user communication about behavior

✅ **Advanced Alert Management:**
- Municipality-specific or island-wide alerts
- Fuel type availability validation per municipality
- Comprehensive alert history tracking

✅ **User Experience:**
- Automatic deactivation notification in alert messages
- Easy alert recreation when needed
- Detailed alert information display

### 3. **Enhanced Data Architecture**

#### Database Schema (Production-Ready)
```sql
-- Main stations table with ID-based municipality system
estaciones_servicio (
    IDEESS VARCHAR(50) PRIMARY KEY,
    Rotulo, Direccion, Localidad, Provincia,
    IDMunicipio VARCHAR(10),  -- NEW: Official municipality ID
    Horario VARCHAR(255),     -- NEW: Operating hours
    Latitud, Longitud_WGS84,
    Precio_Gasolina_95_E5, 
    Precio_Gasolina_95_E5_Premium,  -- NEW: Premium gasoline
    Precio_Gasoleo_A, Precio_Gasoleo_B, 
    Precio_Gasoleo_Premium,
    Precio_Gases_Licuados_del_petroleo,
    Fecha_Actualizacion,
    INDEX idx_idmunicipio (IDMunicipio)  -- NEW: Fast ID-based queries
)

-- Enhanced historical tracking
historical_prices (
    id, date, rotulo, localidad, 
    IDMunicipio VARCHAR(10),  -- NEW: Municipality ID tracking
    direccion, latitud, longitud_wgs84,
    precio_gasolina_95_e5, 
    precio_gasolina_95_e5_premium,  -- NEW: Premium tracking
    precio_gasoleo_a, precio_gasoleo_b,
    precio_gasoleo_premium, 
    precio_gases_licuados_del_petroleo,
    INDEX idx_idmunicipio (IDMunicipio)
)

-- Advanced user subscriptions
user_subscriptions (
    id, user_id, username, fuel_type, price_threshold,
    municipality VARCHAR(255),        -- Legacy support
    id_municipality VARCHAR(50),     -- NEW: ID-based alerts
    created_at, is_active,
    INDEX idx_id_municipality (id_municipality)
)

-- User analytics
bot_users (user_id, username, interaction_count, last_seen, is_active...)
```

#### Data Corrections System
- **Automatic data validation** and correction during ingestion
- **Fornells station correction** (IDEESS '2645' from Es Mercadal to Fornells)
- **Comprehensive logging** of all data corrections applied
- **Fallback mechanisms** for data integrity

### 4. **Advanced Features**

✅ **Smart Fuel Type Detection:**
- Per-municipality fuel availability validation
- Only shows available fuel types for alert creation
- Prevents invalid alert configurations

✅ **Enhanced Navigation:**
- Chart messages include main menu navigation button
- Robust error handling for photo vs text messages
- Seamless user experience across all features

✅ **Comprehensive Admin Tools:**
- `/stats` - Bot usage statistics
- `/debug_historical` - Historical data verification and repair
- `/debug_municipality` - Municipality system validation
- `/debug_datamanager` - Data manager testing
- `/debug_investigation` - Data discrepancy investigation
- `/status` - User session debugging
- `/id` - User ID retrieval for admin setup

## 📋 Installation & Setup

### 1. **Prerequisites**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Create logs directory
mkdir -p logs

# Make scripts executable  
chmod +x downloads_menorca.sh bot_menorca_telegram_starter.sh
```

### 2. **Configuration**

#### Database Setup
```sql
-- Create database
CREATE DATABASE menorca_fuel_prices;

-- Grant permissions
GRANT ALL PRIVILEGES ON menorca_fuel_prices.* TO 'your_user'@'localhost';
```

#### Secret Configuration
Edit `secret.py`:
```python
secret = {
    "bot_token": "YOUR_TELEGRAM_BOT_TOKEN",
    "db_host": "localhost", 
    "db_user": "your_db_user",
    "db_password": "your_db_password",
    "db_name": "menorca_fuel_prices",
    "admin_user_ids": [123456789, 987654321]  # Your Telegram user IDs
}
```

### 3. **Initial Data Load**
```bash
# Download and process initial data
./downloads_menorca.sh
```

### 4. **Start the Bot**
```bash
# Start bot service
./bot_menorca_telegram_starter.sh start

# Check status
./bot_menorca_telegram_starter.sh status

# View logs
./bot_menorca_telegram_starter.sh logs 100
```

## 🔄 Enhanced Operational Workflows

### Data Update Flow (Automated with Corrections)
1. **Cron job** runs `downloads_menorca.sh` (every 10 minutes)
2. **Downloads** latest JSON files from government API
3. **Validates** JSON format and content
4. **Applies data corrections** (Fornells station reassignment)
5. **Processes** data through `menorca_data_manager.load_json_data()`
6. **Updates database** with ID-based municipality system
7. **Stores** daily snapshot with IDMunicipio for historical tracking

### Smart Alert Flow (One-Time Notifications)
1. **Scheduled execution** of `notification_sender.py` (every 10 minutes)
2. **Fetches** all active user subscriptions using ID-based system
3. **Queries** current minimum prices with ID-based municipality filtering
4. **Compares** against user-defined thresholds
5. **Sends notifications** when thresholds are met
6. **Automatically deactivates** triggered alerts to prevent spam
7. **Logs** all alert activities with comprehensive tracking

### Enhanced User Interaction Flow
1. **ID-based municipality selection** with validation
2. **Fuel availability checking** per municipality
3. **Smart alert creation** with validation
4. **Seamless navigation** across all message types
5. **Comprehensive error handling** and user guidance

## 🔧 Administration & Monitoring

### Enhanced Bot Management
```bash
# Service control
./bot_menorca_telegram_starter.sh {start|stop|restart|status|logs}

# Data updates with corrections
./downloads_menorca.sh

# Alert checking (with automatic deactivation)
python3 notification_sender.py
```

### Advanced Admin Commands
- `/start` - Standard user interface
- `/stats` - Comprehensive bot usage statistics
- `/debug_historical` - Historical data verification and repair
- `/debug_municipality` - Municipality ID system validation  
- `/debug_datamanager` - Data manager query testing
- `/debug_investigation` - Data discrepancy analysis
- `/status` - User session debugging
- `/id` - User ID for admin configuration

### Monitoring & Logging
- `logs/main_bot_menorca.log` - Main bot operations with ID system
- `logs/downloads_menorca.log` - Data download and correction activities  
- `logs/notification_sender.log` - Enhanced alert processing
- `logs/bot_menorca_starter.log` - Service management

## 🔄 Scheduled Tasks Setup

### Enhanced Cron Configuration
```bash
# Edit crontab
crontab -e

# Add these lines:
# Update data every 10 minutes (with corrections)
*/10 * * * * /path/to/Bot_Menorca_EESS/downloads_menorca.sh

# Send alerts every 10 minutes (with auto-deactivation)
*/10 * * * * cd /path/to/Bot_Menorca_EESS && python3 notification_sender.py

# Daily log rotation
0 1 * * * find /path/to/Bot_Menorca_EESS/logs -name "*.log" -size +100M -exec mv {} {}.$(date +\%Y\%m\%d) \;
```

## 🛠️ Troubleshooting

### Common Issues

#### Municipality Data Issues
```bash
# Debug municipality mappings
# Use admin command: /debug_municipality

# Test data manager queries
# Use admin command: /debug_datamanager

# Investigate data discrepancies
# Use admin command: /debug_investigation
```

#### Alert System Issues
```bash
# Check alert auto-deactivation
python3 -c "from data_manager_menorca import menorca_data_manager; print(menorca_data_manager.check_price_alerts())"

# Verify municipality ID system
# Use admin command: /debug_municipality
```

#### Chart Navigation Issues
```bash
# The enhanced system handles both text and photo messages
# Navigation buttons are included in all message types
# Error handling covers all edge cases
```

## 📈 Performance & Reliability Improvements

### Enhanced Database Design
- **ID-based queries** eliminate string matching issues
- **Indexed municipality IDs** for instant filtering
- **Data correction logging** for operational transparency
- **Automatic schema migration** for seamless updates

### Smart Alert Management
- **One-time notifications** prevent user annoyance
- **Automatic deactivation** reduces database load
- **Fuel availability validation** prevents invalid configurations
- **Municipality-specific optimization** improves accuracy

### Robust Error Handling
- **Comprehensive validation** at all input points
- **Graceful fallbacks** for data inconsistencies
- **Detailed logging** for debugging and monitoring
- **User-friendly error messages** in Catalan

## 🔄 Key Improvements Since Initial Version

### Data Reliability
- **ID-based municipality system** eliminates string matching errors
- **Automatic data corrections** for known government data issues
- **Fornells special handling** respects local geography
- **Enhanced validation** prevents data corruption

### User Experience
- **One-time alert notifications** prevent spam
- **Smart fuel availability** shows only available options
- **Enhanced navigation** works with all message types
- **Clear user communication** about system behavior

### System Robustness
- **Comprehensive error handling** covers all edge cases
- **Advanced admin tools** for system monitoring
- **Detailed logging** for operational visibility
- **Automatic database migration** for updates

This implementation represents a production-ready, enterprise-grade fuel price monitoring system specifically designed for Menorca, with advanced features that ensure data reliability, user satisfaction, and operational excellence. 