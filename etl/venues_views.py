from creds import postgresql_pw
from sqlalchemy import create_engine, text

# create postgresql connection
engine = create_engine(f'postgresql+psycopg2://postgres:{postgresql_pw}@localhost:5432/api_sports')

# run create_venues_views.sql
with engine.connect() as conn:
    with open("create_venues_views.sql") as file:
        conn.execute(text(file.read()))
        conn.commit()

print(f"{'-'*70}", "\nDatabase venues views created.\n")