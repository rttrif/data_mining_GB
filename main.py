import requests
import bs4
from home_work_3.database import DataBase
from home_work_3.models import Post, User, Comment


class Parser:

    def __init__(self, start_url):
        self.headers = {
            'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:73.0) Gecko/20100101 Firefox/73.0'}

        self.__start_url = start_url
        db = DataBase('sqlite:///gb_habr.db')
        self._session = db.get_session()

    def get_soap(self, response):
        return bs4.BeautifulSoup(response.text, 'lxml')

    def get_next(self, soap):
        return soap.select_one('a#next_page.arrows-pagination__item-link')

    def get_posts_url(self, soap):
        posts = soap.select('div.posts_list ul.content-list li.content-list__item article.post h2 a')
        return [a['href'] for a in posts]

    def get_writer(self, soap):
        url = soap.select_one('a.post__user-info')['href']

        user = self._session.query(User).filter(User.url == url).first()
        if not user:
            soap = self.get_soap(requests.get(url, headers=self.headers))
            user = User(url=url, name=soap.select_one('h1.user-info__name a').text)
            self._session.add(user)
            self._session.commit()
        return user

    def parse_post_page(self, url):
        post = self._session.query(Post).filter(Post.url == url).first()
        if not post:
            response = requests.get(url, headers=self.headers)
            soap = self.get_soap(response)
            data = {
                'title': soap.select_one('span.post__title-text').text,
                'date': soap.select_one('span.post__time')['data-time_published'],
                'writer': self.get_writer(soap),
                'url': url,
            }

            post = Post(**data)
            self._session.add(post)
            self._session.commit()
        print(1)

    def parse(self):
        url = self.__start_url
        while url:
            resp = requests.get(url, headers=self.headers)
            soap = self.get_soap(resp)
            url = self.get_next(soap)
            url = url['href'] if url else None
            for post_url in self.get_posts_url(soap):
                self.parse_post_page(post_url)

            print(1)


if __name__ == '__main__':
    start_url = 'https://habr.com/ru/top/weekly/'

    parser = Parser(start_url)
    parser.parse()
