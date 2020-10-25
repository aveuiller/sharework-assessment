"""
This package handles models from a backend point of view.
This could have been merged with the 'matching' module models if they intend
to use the same database.

But for simplicity of queries, we are using an ORM on this side.
"""
from typing import List, Type, TypeVar

from sqlalchemy import Column, ForeignKey, Integer, String, or_
from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.ext.declarative import (
    as_declarative, declared_attr
)
from sqlalchemy.orm import Query, Session, relationship, sessionmaker

_T = TypeVar("_T")


@as_declarative()
class Base(object):
    @classmethod
    def get_sql_engine(cls, db_uri: str) -> Engine:
        """Create a new SQL engine from the given DB uri

        :param db_uri: The database to use.
        :return: A new Engine.
        """
        return create_engine(db_uri)

    @classmethod
    def session_from_path(cls, db_uri: str) -> Session:
        """Create a new engine and a session from this engine.

        :param db_uri: The database to use.
        :return: A new Session.
        """
        return sessionmaker(
            bind=cls.get_sql_engine(db_uri), autocommit=False, autoflush=False
        )()

    @classmethod
    def session_from_engine(cls, engine: Engine) -> Session:
        """Uses the current Engine to generate a new session.

        :param engine: The current engine.
        :return: A new Session.
        """
        return sessionmaker(
            bind=engine, autocommit=False, autoflush=False
        )()

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)

    @classmethod
    def fetch_all(cls: Type[_T], session: Session, limit: int, offset: int) \
            -> List[_T]:
        """List all available models withing the given bounds.

        :param session: The session to query onto.
        :param limit: The limit of results returned.
        :param offset: The query offset.
        :return: A list of Company.
        """
        return Query(cls, session=session).limit(limit).offset(offset).all()

    @classmethod
    def fetch_one(cls: Type[_T], session: Session, identifier: int) -> _T:
        """Fetch one model from id

        :param session: The session to query onto.
        :param identifier: Match identifier.
        :return: A Match, or None if not found.
        """
        return Query(cls, session=session).get(identifier)


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


class Match(Base):
    __tablename__ = "matches"
    left_company_id = Column(Integer, ForeignKey(Company.id), nullable=False)
    left_company = relationship(Company, foreign_keys=[left_company_id])

    right_company_id = Column(Integer, ForeignKey(Company.id), nullable=False)
    right_company = relationship(Company, foreign_keys=[right_company_id])

    def delete(self, session: Session) -> None:
        """Delete the match from database.

        # TODO: This could become a soft-delete to avoid losing data.

        :param session: The session to query onto.
        """
        session.query(Match).filter_by(id=self.id).delete()

    @classmethod
    def fetch_all(cls, session: Session, limit: int, offset: int,
                  company_id: int = None) -> List['Match']:
        query = Query(cls, session=session)

        if company_id:
            query = query.filter(or_(
                Match.left_company_id == company_id,
                Match.right_company_id == company_id
            ))

        query = query.limit(limit).offset(offset)
        return query.all()
