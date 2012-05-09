CELERY_RESULT_BACKEND = "database"
CELERY_RESULT_DBURI = "sqlite:///celerydb.sqlite"

#BROKER_URL = 'redis://localhost:6379/0'
BROKER_TRANSPORT = "sqlalchemy"
BROKER_HOST = "sqlite:///celerydb.sqlite"

SQLALCHEMY_DATABASE_URI = 'sqlite:///snapshots.sqlite'
