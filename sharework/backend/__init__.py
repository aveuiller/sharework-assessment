import os

from flask import Flask
from flask_restful import Api

from sharework import DATA_DIR
from sharework.backend.models import Base
from sharework.backend.views import (
    CompaniesListView, CompanyView, MatchView,
    MatchesListViews
)


def init_flask_api() -> Flask:
    app = Flask(__name__)
    api = Api(app)
    # FIXME: This should be a configuration
    db_path = "sqlite:///" + os.path.join(DATA_DIR, "backend_base.sqlite3")

    dependencies = {
        'engine': Base.get_sql_engine(db_path)
    }
    api.add_resource(CompaniesListView, '/company',
                     resource_class_kwargs=dependencies)
    api.add_resource(CompanyView, '/company/<int:company_id>',
                     resource_class_kwargs=dependencies)
    api.add_resource(MatchesListViews, '/match',
                     resource_class_kwargs=dependencies)
    api.add_resource(MatchView, '/match/<int:match_id>',
                     resource_class_kwargs=dependencies)
    return app


def main():
    app = init_flask_api()
    app.run(debug=False)
