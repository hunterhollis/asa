from creds import postgresql_pw
from sqlalchemy import create_engine, text

# create postgresql connection
engine = create_engine(f'postgresql+psycopg2://postgres:{postgresql_pw}@localhost:5432/api_sports')

# run create_venues_views.sql
with engine.connect() as conn:
    query = text("DROP VIEW IF EXISTS v_all_game_venues, v_mlb_game_venues, v_mls_game_venues, v_nba_game_venues, \
                 v_nfl_game_venues, v_nhl_game_venues, v_team_venues;")
    conn.execute(query)
    conn.commit()

print(f"{'-'*70}", "\nDatabase views dropped.")