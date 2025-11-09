from database.database import engine, Base
from database.models import Note

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully!")