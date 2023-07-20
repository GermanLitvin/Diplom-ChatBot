from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base
from config import db_url_object

import sqlalchemy as sq

metadata = MetaData()
Base = declarative_base()
engine = create_engine(db_url_object)


class Viewed(Base):
    __tablename__ = 'viewed'
    profile_id = sq.Column(sq.Integer, primary_key=True)
    worksheet_id = sq.Column(sq.Integer, primary_key=True)


# добавление записи в БД
def add_user(engine, profile_id, worksheet_id):
    with Session(engine) as session:
        to_bd = Viewed(profile_id=profile_id, worksheet_id=worksheet_id)
        session.add(to_bd)
        session.commit()

# проверка записей в БД
def check_user(engine, profile_id, worksheet_id):
    with Session(engine) as session:
        from_bd = session.query(Viewed).filter(
            Viewed.profile_id == profile_id,
            Viewed.worksheet_id == worksheet_id
        ).first()
        return True if from_bd else False

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    #res = check_user(engine, 2113, 124512)
    #print(res)