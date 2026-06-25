from db.database import engine

from models.import_session import ImportSession
from models.import_field import ImportField

ImportSession.metadata.create_all(bind=engine)

print("table created")