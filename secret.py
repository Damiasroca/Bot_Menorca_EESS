#!/usr/bin/env python

# Secret configuration for Menorca Fuel Price Telegram Bot
# Following the structure described in technical_description.txt

secret = {
    # Telegram Bot Configuration
    "bot_token": "TELEGRAM_BOT_TOKEN",
    
    # Database Configuration  
    "db_host": "localhost",
    "db_user": "USER",
    "db_password": "PASSWORD", 
    "db_name": "menorca_fuel_prices",  # Updated for Menorca
    
    # Admin User IDs (list of Telegram user IDs with admin access)
    "admin_user_ids": [
        # Add your Telegram user IDs here
        # Example: 123456789, 987654321
    ]
}

# For backward compatibility, also expose individual values
bot_token = secret["bot_token"]
db_host = secret["db_host"]
db_user = secret["db_user"]
db_password = secret["db_password"]
db_name = secret["db_name"]
admin_user_ids = secret["admin_user_ids"]
