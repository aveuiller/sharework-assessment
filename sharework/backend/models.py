"""
This package handles models from a backend point of view.
This could have been merged with the 'matching' module models if they intend
to use the same database.

But for simplicity of queries, we are using an ORM on this side.
"""
import os
from typing import List

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.ext.declarative import (
    as_declarative, declared_attr
)
from sqlalchemy.orm import Query, Session, relationship, sessionmaker

from sharework import DATA_DIR

# FIXME: This should be a configuration
DB_PATH = "sqlite:///" + os.path.join(DATA_DIR, "backend_base.sqlite3")


@as_declarative()
class Base(object):
    SQL_ENGINE: Engine = None

    @classmethod
    def get_sql_engine(cls, db_path: str) -> Engine:
        if cls.SQL_ENGINE is None:
            cls.SQL_ENGINE = create_engine(db_path)
        return cls.SQL_ENGINE

    @classmethod
    def get_sql_session(cls, db_path: str) -> Session:
        return sessionmaker(
            bind=cls.get_sql_engine(db_path), autocommit=False, autoflush=False
        )()

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)


class Company(Base):
    __tablename__ = "companies"
    source_id = Column(Integer, nullable=False)
    source_name = Column(String(64), nullable=False)
    name = Column(String(512), nullable=False)
    website = Column(String(512), nullable=True)
    email = Column(String(512), nullable=True)
    phone = Column(String(512), nullable=True)
    address = Column(String(512), nullable=True)
    postal_code = Column(String(512), nullable=True)
    city = Column(String(512), nullable=True)
    country = Column(String(512), nullable=True)

    @staticmethod
    def fetch_all(session: Session, limit: int, offset: int) \
            -> List['Company']:
        """List all available companies withing the given bounds.

        :param session: The session to query onto.
        :param limit: The limit of results returned.
        :param offset: The query offset.
        :return: A list of Company.
        """
        query = Query(Company, session=session).limit(limit).offset(offset)
        return query.all()

    @staticmethod
    def fetch_one(session: Session, identifier: int) -> 'Company':
        """Fetch one company from id

        :param session: The session to query onto.
        :param identifier: Company identifier.
        :return: A Company, or None if not found.
        """
        return Query(Company, session=session).get(identifier)


class Match(Base):
    __tablename__ = "matches"
    left_company_id = Column(Integer, ForeignKey(Company.id), nullable=False)
    left_company = relationship(Company, foreign_keys=[left_company_id])

    right_company_id = Column(Integer, ForeignKey(Company.id), nullable=False)
    right_company = relationship(Company, foreign_keys=[right_company_id])

    @staticmethod
    def fetch_one(session: Session, identifier: int) -> 'Match':
        """Fetch one match from id

        :param session: The session to query onto.
        :param identifier: Match identifier.
        :return: A Match, or None if not found.
        """
        return Query(Match, session=session).get(identifier)

    def delete(self, session: Session) -> None:
        """Delete the match from database.

        # TODO: This could become a soft-delete to avoid losing data.

        :param session: The session to query onto.
        """
        session.query(Match).filter_by(id=self.id).delete()
