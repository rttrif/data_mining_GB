from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from home_work_3.models import Base


class DataBase:

    def __init__(self, url):
        # engine = create_engine('sqlite:///gb_blog.db')
        engine = create_engine(url)
        Base.metadata.create_all(engine)
        self.__session_db = sessionmaker(bind=engine)

    def get_session(self) -> Session:
        return self.__session_db()
