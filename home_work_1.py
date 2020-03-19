import requests
import json
import time

'''
--- ЗАДАНИЕ ---
Источник данных https://5ka.ru/special_offers/

Необходимо создать структуру JSON файлов где имя файла название категории, 
Содержимое файла JSON список словарей товаров пренадлежащих этой категории.
Извлекаем только товары по акции, не перегружайте сервер делайте time.sleep
В Гите хранить файлы результата не нужно, только код который приводит к созданию соответсвующих файлов

--- ПОРЯДОК ВЫПОЛНЕНИЯ --- 
1. Сделать запрос к ресурсу 
2. Пролучить список разделов каталога
3. Получить список всех товаров во всех каталогах 
4. Создать файл json с именем каталога 
5. Записать в файл json строку с товарами соответствующей категории
'''


URL = 'https://5ka.ru/api/v2/special_offers/'
headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'}
CAT_URL = 'https://5ka.ru/api/v2/categories/'

def x5ka(url, params=dict()):
    result = []
    while url:
        response = requests.get(url, headers=headers, params=params) if params else requests.get(url, headers=headers)
        params = None
        data = response.json()
        result.extend(data.get('results'))
        url = data.get('next')
        time.sleep(1)
    return result

if __name__ == '__main__':
# выгрузили категории
    response = requests.get(CAT_URL, headers=headers)
    categories_data = response.json()

# для каждой категории выгрузить товары и сохранить в файл

    for i in range(len(categories_data)):
        data = x5ka(URL, {'categories': categories_data[i].get('parent_group_code')})
        nameFile = categories_data[i].get('parent_group_name')
        with open(nameFile + '.json', 'w') as file:
            file.write(json.dumps(data))
