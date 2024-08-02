def last():
    with open('/municipis_original/mao.json', encoding='utf-8') as f:
        data = f.read(31)
    f.close()
    data1 = data.replace('{"Fecha":"','')
    data2 = data1.replace('/', '') 
    return data2

