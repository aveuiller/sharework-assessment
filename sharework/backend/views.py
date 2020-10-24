from flask_restful import Resource, fields, marshal, reqparse
from flask_restful.reqparse import RequestParser

from sharework.backend.models import Company, DB_PATH, Match


class MatchView(Resource):
    MARSHAL_MATCH = {
        'id': fields.Integer(),
        'left_company_id': fields.String(),
        'right_company_id': fields.String(),
    }

    @staticmethod
    def _parser() -> RequestParser:
        parser = reqparse.RequestParser()
        parser.add_argument('company', type=int, location='args')
        return parser

    def get(self, match_id: int):
        session = Match.get_sql_session(DB_PATH)
        match = Match.fetch_one(session, match_id)

        session.close()

        if not match:
            return {}, 404
        return marshal(match, self.MARSHAL_MATCH), 200

    def delete(self, match_id: int):
        session = Match.get_sql_session(DB_PATH)
        match = Match.fetch_one(session, match_id)

        if not match:
            session.close()
            return {}, 404

        match.delete(session)
        session.commit()
        return marshal(match, self.MARSHAL_MATCH), 200


class CompanyView(Resource):
    MARSHAL_COMPANY = {
        'id': fields.Integer(),
        'source_name': fields.String(),
        'name': fields.String(),
        'website': fields.String(),
        'email': fields.String(),
        'phone': fields.String(),
        'address': fields.String(),
        'postal_code': fields.String(),
        'city': fields.String(),
        'country': fields.String(),
    }

    def get(self, company_id: int):
        session = Company.get_sql_session(DB_PATH)
        company = Company.fetch_one(session, company_id)
        session.close()

        if not company:
            return {}, 404
        return marshal(company, self.MARSHAL_COMPANY), 200


class CompaniesListView(Resource):
    @staticmethod
    def _index_parser() -> RequestParser:
        # TODO: We can propose more filtering parameters like data source.
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, location='args')
        parser.add_argument('limit', type=int, location='args')
        return parser

    def get(self):
        args = self._index_parser().parse_args()
        page = args.get("page") or 0
        limit = args.get("limit") or 100
        if limit > 100:
            limit = 100

        session = Company.get_sql_session(DB_PATH)
        companies = Company.fetch_all(session, limit, page * limit)
        session.close()

        return marshal(companies, CompanyView.MARSHAL_COMPANY), 200
