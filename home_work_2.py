"""
Домашнее задание:

Ресурс, https://geekbrains.ru/posts

Обойти список статей, с использованием библиотеки BS4

Сохранить полученые данные в виде json файлов:
Отдельный файл для тегов, в котором хранится сам тег, ссылка на тег, и список ссылок на записи в блоге с этип тегом.
"""
''' Пример


# file tags.json

{
    "tag_name": {'url': "", 'posts': ['url_post', ]}
}

# file url_post.json

{
    'url': 'post_url',
    'image': 'image_url',
    'title': 'Загаловок',
    'writer': {'name': 'wrater_name',
               'url': 'full_writer_url'
               },
    'tags': [{'tag_name':'tag_url'}, ]
}
отдельно для каждой записи в блоге создать json файл с именем равным url данной записи, и полями заголовка, ссылки на изображение, url, данных на автора статьи, и списко тегов пример структуры:

{
    'url': 'post_url',
    'image': 'image_url',
    'title': 'Загаловок',
    'writer': {'name': 'wrater_name',
               'url': 'full_writer_url'
               },
    'tags': [{'tag_name':'tag_url'}, ]
}

'''  # Пример

import requests
import json
import bs4

headers = {
    'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}
URL = 'https://geekbrains.ru/posts'
BASE_URL = 'https://geekbrains.ru'


# todo Получить URL блога

def get_page(url):
    while url:
        print(url)
        response = requests.get(url, headers=headers)
        soap = bs4.BeautifulSoup(response.text, 'lxml')
        yield soap
        url = get_next_page(soap)


# todo Организовать переход по страницам блога

def get_next_page(soap: bs4.BeautifulSoup) -> str:
    ul = soap.find('ul', attrs={'class': 'gb__pagination'})
    a = ul.find(lambda tag: tag.name == 'a' and tag.text == '›')
    return f'{BASE_URL}{a["href"]}' if a else None


# todo Получить URL поста

def get_post_url(soap: bs4.BeautifulSoup) -> set:
    post_a = soap.select('div.post-items-wrapper div.post-item a')
    return set(f'{BASE_URL}{a["href"]}' for a in post_a)


# todo Получить данные поста

def get_post_data(post_url: str) -> dict:
    template_data = {'url': '',
                     'title': '',
                     'tags': [],
                     'writer': {'name': '',
                                'url': ''}
                     }

    response = requests.get(post_url, headers=headers)
    soap = bs4.BeautifulSoup(response.text, 'lxml')
    template_data['url'] = post_url
    template_data['title'] = soap.select_one('article h1.blogpost-title').text
    template_data['tags'] = {itm.text: f'{BASE_URL}{itm["href"]}' for itm in soap.select('article a.small')}
    template_data['writer']['name'] = soap.find('div', attrs={'itemprop': 'author'}).text
    template_data['writer']['url'] = f"{BASE_URL}{soap.find('div', attrs={'itemprop': 'author'}).parent['href']}"
    return template_data


def clear_file_name(url: str):
    return url.replace('/', '_')

if __name__ == '__main__':
    for_tags = {}

    # todo Обойти список статей
    for soap in get_page(URL):
        posts = get_post_url(soap)
        data = [get_post_data(url) for url in posts]

    # todo Собрать данные из всех статей

        for post in data:
            file_name = clear_file_name(post['url'])

            for name, url in post['tags'].items():
                if not for_tags.get(name):
                    for_tags[name] = {'posts': []}
                for_tags[name]['url'] = url
                for_tags[name]['posts'].append(post['url'])

    # todo Сохранить полученные данные в формате json

            with open(f'{file_name}.json', 'w') as file:
                file.write(json.dumps(post))
    with open('tags.json', 'w') as file:
        file.write(json.dumps(for_tags))
