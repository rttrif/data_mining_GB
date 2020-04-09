# Задача: обойти все файлы из архива https://yadi.sk/d/q5kuiXh0YG9GCQ
# Необходимо найти заводские серийные номера кассовых аппаратов из изображений и страниц PDF файлов.
# Извлечь серийные номера из файлов ( приложены в материалах урока)
# Ваша задача разобрать все фалы, распознать на них серийный номер и создать коллекцию в MongoDB
# с четким указанием из какого файла был взят тот или иной серийный номер.
# Дополнительно необходимо создать коллекцию и отдельную папку для хранения файлов в
# которых вы не смогли распознать серийный номер, если в файле встречается несколько изображений
# необходимо явно указать что в файле таком-то страница такая серийный номер не найден.

import shutil
import os
import PyPDF2
from PIL import Image
import pytesseract
import time
from pymongo import MongoClient

mongo_client = MongoClient()

pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'
#pdf_file_path = 'data_for_parse/8416_4.pdf'

# todo Отсортировать файлы jpg и pdf
os.chdir('data_for_parse')
for root, dirs, files in os.walk('C:\\Users\\User\\PycharmProjects\\algs\\data_for_parse\\СКД_Поверка весов'):
    for filename in files:
        name, ext = os.path.splitext(filename)
        ext = ext.lstrip('.')
        if ext in ('jpg', 'jpeg', 'png'):
            subdir = 'image'
        elif ext == 'pdf':
            subdir = 'pdf'
        else:
            subdir = ''
        shutil.copyfile(os.path.join(root, filename), f'C:\\Users\\User\\PycharmProjects\\algs\\data_for_parse\\{subdir}\\{name}.{ext}')

# todo Извлечь jpg из pdf и сохранить в папке изображений
def extract_pdf_image(pdf_path):
    try:
        pdf_file = PyPDF2.PdfFileReader(open(pdf_path, "rb"), strict=False)
    except PyPDF2.utils.PdfReadError as e:
        return None
    except FileNotFoundError as e:
        return None

    result = []

    for page_num in range(0, pdf_file.getNumPages()):
        page = pdf_file.getPage(page_num)
        page_obj = page['/Resources']['/XObject'].getObject()
        if page_obj['/Im0'].get('/Subtype') == "/Image":
            size = (page_obj['/Im0']['/Width'], page_obj['/Im0']['/Height'])
            data = page_obj['/Im0']._data
            if page_obj['/Im0']['/ColorSpace'] == '/DeviceRGB':
                mode = 'RGB'
            else:
                mode = 'P'

            if page_obj['/Im0']['/Filter'] == '/FlateDecode':
                file_type = 'png'
            elif page_obj['/Im0']['/Filter'] == '/DCTDecode':
                file_type = 'jpg'
            elif page_obj['/Im0']['/Filter'] == '/JPXDecode':
                file_type = 'jp2'
            else:
                file_type = 'bmp'

            result_strict = {
                'page': page_num,
                'size': size,
                'data': data,
                'mode': mode,
                'file_type': file_type,
            }
            result.append(result_strict)

    return result


def save_pdf_image(file_name, f_path, *pdf_strict):
    for item in pdf_strict:
        name = f"{file_name}_#_{item['page']}.{item['file_type']}"

        with open(f"{f_path}/{name}", "wb") as image:
            image.write(item['data'])





def extract_number(file_path):
    img_obj = Image.open(file_path)
    text = pytesseract.image_to_string(img_obj, 'rus')
    pattern = 'заводской (серийный) номер'
    pattern2 = 'заводской номер'
    result = []
    for idx, line in enumerate(text.split('\n')):
        if line.lower().find(pattern) + 1 or line.lower().find(pattern2) + 1:
            eng_text = pytesseract.image_to_string(img_obj, 'eng')
            number = eng_text.split('\n')[idx].split(' ')[-1]
            result.append(number)
# todo при отсутсвии распознавания вернуть соответсвующее сообщение или error
    if result:
        return result
    else:
        return 'не удалось извлечь'

# todo сохранить все в БД MONGO
def process_item(item):
    database = mongo_client['cashbox_finder']  # передается в строке имя базы, если такой нет - будет создана
    collection = database['cashbox_numbers']
    collection.insert_one(item)
    return item

#file_name = '8416_4'
image_path = "C:\\Users\\User\\PycharmProjects\\algs\\data_for_parse\\image"
#img_file_path = 'data_for_parse/image/8416_4_#_2.jpg'
if __name__ == '__main__':
    for root, dir, files in os.walk('C:\\Users\\User\\PycharmProjects\\algs\\data_for_parse\\pdf'):
        for filename in files:
            name, ext = os.path.splitext(filename)
            pdf_result = extract_pdf_image(filename)
            if pdf_result != None:
                save_pdf_image(name, image_path, *pdf_result)
    os.chdir(image_path)
    for root, dir, files in os.walk(image_path):
        for filename in files:
            res = extract_number(os.path.join(root, filename))
            res_dict = {'from_file': filename, 'cashbox_number': res}
            process_item(res_dict)
    print(1)

