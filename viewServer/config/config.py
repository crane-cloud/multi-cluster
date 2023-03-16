# Contains Database configurations
import os


class Base:
    """ base config """
    # main
    SECRET_KEY = os.getenv("FLASK_APP_SECRET")


class Development(Base):
    """ development config """

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
    # SQLALCHEMY_DATABASE_URI = "postgresql:///flask_app_db"


class Testing(Base):
    """ test environment config """

    TESTING = True
    DEBUG = True
    # use a separate db
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_TEST_URI")
    # SQLALCHEMY_DATABASE_URI = "postgresql:///flask_app_test_db"


class Production(Base):
    """ production config """

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_PROD_URI")


app_config = {"development": Development,
              "testing": Testing, "production": Production}
