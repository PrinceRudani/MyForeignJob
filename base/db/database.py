# base/db/database_config.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from base.utils.constant import constant
from base.utils.custom_exception import AppServices

# --- Configuration Parameters ---
DB_HOST = constant.DB_HOST
DB_USERNAME = constant.DB_USERNAME
DB_PASSWORD = constant.DB_PASSWORD
DB_PORT = constant.DB_PORT
DB_NAME = constant.DB_NAME

MYSQL_URL = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8"
print(f"MYSQL_URL = {MYSQL_URL}")
POOL_SIZE = 10
POOL_RECYCLE = 3600
POOL_TIMEOUT = 15
MAX_OVERFLOW = 0
CONNECT_TIMEOUT = 3600
POOL_PRE_PING = True

# --- SQLAlchemy Base ---
Base = declarative_base()


# --- Singleton Database Manager ---
class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.connection_is_active = False
            cls._instance.engine = None
        return cls._instance

    def get_db_connection(self):
        if not self.connection_is_active:
            connect_args = {"connect_timeout": CONNECT_TIMEOUT}
            try:
                self.engine = create_engine(
                    MYSQL_URL,
                    pool_size=POOL_SIZE,
                    pool_recycle=POOL_RECYCLE,
                    pool_timeout=POOL_TIMEOUT,
                    max_overflow=MAX_OVERFLOW,
                    connect_args=connect_args,
                    pool_pre_ping=POOL_PRE_PING,
                )
                print(
                    f"[✅] Database connection successfully established at: {MYSQL_URL}"
                )
                self.connection_is_active = True
            except Exception as exception:
                AppServices.handle_exception(exception, is_raise=True)
        return self.engine

    @staticmethod
    def get_db_session(engine):
        try:
            db_session = sessionmaker(bind=engine)
            return db_session()
        except Exception as exception:
            AppServices.handle_exception(exception, is_raise=True)


# --- Exportable Instances ---
database = Database()
engine = database.get_db_connection()

# ⚠️ Important: Don't call create_all() here; do it in startup only


# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base
#
# from base.utils.constant import constant
# from base.utils.custom_exception import AppServices
#
# DB_HOST = constant.DB_HOST
# DB_USERNAME = constant.DB_USERNAME
# DB_PASSWORD = constant.DB_PASSWORD
# DB_PORT = constant.DB_PORT
# DB_NAME = constant.DB_NAME
#
# MYSQL_URL = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8"
# print(f"MYSQL_URL = {MYSQL_URL}")
# POOL_SIZE = 10
# POOL_RECYCLE = 3600
# POOL_TIMEOUT = 15
# MAX_OVERFLOW = 0
# CONNECT_TIMEOUT = 3600
# PREPING = True
#
#
# class Database:
#     _instance = None
#
#     def __init__(self):
#         self.engine = None
#
#     def __new__(cls):
#         if cls._instance is None:
#             cls._instance = super(Database, cls).__new__(cls)
#             cls._instance.connection_is_active = False
#             cls._instance.engine = None
#         return cls._instance
#
#     # def get_db_connection(self):
#     #
#     #     if not self.connection_is_active:
#     #         connect_args = {"connect_timeout": CONNECT_TIMEOUT}
#     #         try:
#     #             self.engine = create_engine(
#     #                 MYSQL_URL,
#     #                 pool_size=POOL_SIZE,
#     #                 pool_recycle=POOL_RECYCLE,
#     #                 pool_timeout=POOL_TIMEOUT,
#     #                 max_overflow=MAX_OVERFLOW,
#     #                 connect_args=connect_args,
#     #                 pool_pre_ping=PREPING,
#     #             )
#     #             return self.engine
#     #         except Exception as exception:
#     #             AppServices.handle_exception(exception, is_raise=True)
#     #     return self.engine
#
#     def get_db_connection(self):
#         if not self.connection_is_active:
#             connect_args = {"connect_timeout": CONNECT_TIMEOUT}
#             try:
#                 self.engine = create_engine(
#                     MYSQL_URL,
#                     pool_size=POOL_SIZE,
#                     pool_recycle=POOL_RECYCLE,
#                     pool_timeout=POOL_TIMEOUT,
#                     max_overflow=MAX_OVERFLOW,
#                     connect_args=connect_args,
#                     pool_pre_ping=PREPING,
#                 )
#                 self.connection_is_active = True
#                 return self.engine
#             except Exception as exception:
#                 AppServices.handle_exception(exception, is_raise=True)
#         return self.engine
#
#     @staticmethod
#     def get_db_session(engine):
#
#         try:
#             db_session = sessionmaker(bind=engine)
#             session = db_session()
#             return session
#         except Exception as exception:
#             AppServices.handle_exception(exception, is_raise=True)
#
#
# Base = declarative_base()
# database = Database()
# engine = database.get_db_connection()
# Base.metadata.create_all(engine)
