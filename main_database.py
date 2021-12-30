import json
from extent_table import ExtentTable
from table_maker import TableMaker
from db import database
from modifica_json import principal
from datetime import datetime

now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

def adequacio():
    with open('/your/path/to/json_processing/combinat.json', 'r', encoding="utf8") as arxiu:
        data=json.load(arxiu)
        extent_table = ExtentTable()
        table_maker = TableMaker(extent_table)
        table_maker.convert_json_objects_to_tables(data, "data")
        table_maker.show_tables(21)
        table_maker.save_tables("/your/path/to/json_processing/combinat_per_importar.csv", export_as="csv")

principal()
adequacio()
database()
print(dt_string)
    
