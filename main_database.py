import json
from extent_table import ExtentTable
from table_maker import TableMaker
from db import database
from modifica_json import principal
from datetime import datetime
import os

now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

def adequacio():
    with open('/json_processing/combinat.json', 'r', encoding="utf8") as arxiu:
        data=json.load(arxiu)
        extent_table = ExtentTable()
        table_maker = TableMaker(extent_table)
        table_maker.convert_json_objects_to_tables(data, "data")
        table_maker.show_tables(21)
        table_maker.save_tables("/json_processing/combinat_per_importar.csv", export_as="csv")

def save_api_fetch_timestamp():
    """Save the timestamp when data was actually fetched from government APIs."""
    # Use relative path to be more portable
    script_dir = os.path.dirname(os.path.abspath(__file__))
    timestamp_file = os.path.join(script_dir, 'last_api_fetch.txt')
    try:
        with open(timestamp_file, 'w') as f:
            f.write(dt_string)
        print(f"API fetch timestamp saved: {dt_string}")
    except Exception as e:
        print(f"Error saving timestamp: {e}")

principal()
adequacio()
database()
save_api_fetch_timestamp()
print(dt_string)
    
