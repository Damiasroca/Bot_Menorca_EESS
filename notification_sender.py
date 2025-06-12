# Notification Sender for Menorca Fuel Price Telegram Bot
# This script runs as a scheduled task to check and send price alerts
# Following the architecture described in technical_description.txt

import asyncio
import logging
import sys
import os
from datetime import datetime

from telegram import Bot
from telegram.constants import ParseMode

import secret
from data_manager_menorca import menorca_data_manager
from constants_menorca import FUEL_TYPES, M_ALERT_TRIGGERED

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/notification_sender.log')
    ]
)

logger = logging.getLogger(__name__)

def format_station_message_for_alert(station_details):
    """Format station message for alert notification."""
    try:
        station = station_details['station_data']
        
        # Create Google Maps link
        lat = str(station.get('Latitud', '')).replace(',', '.')
        lon = str(station.get('Longitud_WGS84', '')).replace(',', '.')
        maps_link = f'https://www.google.com/maps/@{lat},{lon},20z'
        
        # Build message
        message = f"🔸*{station.get('Rotulo', 'Desconegut')}*\n"
        message += f"[{station.get('Direccion', 'Adreça desconeguda')}]({maps_link})\n"
        message += f"📍 {station.get('Localidad', 'Localitat desconeguda')}\n\n"
        
        # Add fuel prices
        for fuel_key, fuel_data in FUEL_TYPES.items():
            column_name = fuel_data['column'].title().replace('_', '_')
            price = station.get(column_name)
            if price is not None and price > 0:
                message += f"{fuel_data['emoji']} {fuel_data['display_name']}: *{price}€*\n"
        
        return message
    except Exception as e:
        logger.error(f"Error formatting station message for alert: {e}")
        return "Error formatant estació"

async def send_price_alerts():
    """
    Main function to check for triggered price alerts and send notifications.
    This is the core logic described in technical_description.txt for the notification system.
    """
    try:
        logger.info("Starting price alert check...")
        
        # Initialize data manager
        menorca_data_manager.connect()
        menorca_data_manager.load_data_from_db()
        
        # Check for triggered alerts
        alerts_to_send = menorca_data_manager.check_price_alerts()
        
        if not alerts_to_send:
            logger.info("No price alerts to send")
            return
        
        logger.info(f"Found {len(alerts_to_send)} price alerts to send")
        
        # Initialize Telegram bot
        bot = Bot(token=secret.secret['bot_token'])
        
        # Send alerts to users
        successful_sends = 0
        failed_sends = 0
        
        for alert in alerts_to_send:
            try:
                # Get fuel display name
                fuel_name = FUEL_TYPES[alert['fuel_type']]['display_name']
                
                # Format station details
                station_message = format_station_message_for_alert(alert['station_details'])
                
                # Create alert message following the pattern from constants
                message = M_ALERT_TRIGGERED.format(
                    fuel_name,
                    alert['station_name'],
                    alert['current_price'],
                    alert['municipality'],
                    station_message
                )
                
                # Send message to user
                await bot.send_message(
                    chat_id=alert['user_id'],
                    text=message,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True
                )
                
                successful_sends += 1
                logger.info(f"Alert sent successfully to user {alert['user_id']} for {fuel_name} at {alert['current_price']}€")
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(0.1)
                
            except Exception as e:
                failed_sends += 1
                logger.error(f"Failed to send alert to user {alert['user_id']}: {e}")
                continue
        
        logger.info(f"Price alert check completed. Sent: {successful_sends}, Failed: {failed_sends}")
        
    except Exception as e:
        logger.error(f"Error in send_price_alerts: {e}")
        raise

async def main():
    """
    Main entry point for the notification sender script.
    This script is designed to be run on a schedule (e.g., every 10 minutes via cron).
    """
    start_time = datetime.now()
    logger.info(f"Notification sender started at {start_time}")
    
    try:
        await send_price_alerts()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"Notification sender completed successfully in {duration:.2f} seconds")
        
    except Exception as e:
        logger.error(f"Notification sender failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs('logs', exist_ok=True)
    
    # Run the async main function
    asyncio.run(main()) 