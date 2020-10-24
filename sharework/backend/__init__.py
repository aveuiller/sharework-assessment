from flask import Flask
from flask_restful import Api

from sharework.backend.views import CompaniesListView, CompanyView, MatchView


def init_flask_api() -> Flask:
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(CompaniesListView, '/company')
    api.add_resource(CompanyView, '/company/<int:company_id>')
    api.add_resource(MatchView, '/match/<int:match_id>')
    return app


def main():
    app = init_flask_api()
    app.run(debug=True)
