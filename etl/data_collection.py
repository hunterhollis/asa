# libraries and dependencies
from creds import api_key, postgresql_pw
from helper_functions import apiSports
from pprint import pprint
from sqlalchemy import create_engine
import pandas as pd

# create postgresql connection to export DataFrames to database tables
engine = create_engine(f'postgresql+psycopg2://postgres:{postgresql_pw}@localhost:5432/api_sports')

# checks API status for league object
def api_status(league_name, league_object):
    status = league_object.request({}, 'status')['response']
    print(f"{league_name.upper()}:")
    pprint(status['requests'])
    pprint(status['subscription'])
    print(f"{'-'*70}")

# creates a member of apiSports class and checks API key status
print('\nAPI STATUS', f'\n{'-'*70}')
mlb = apiSports(api_key, 'baseball', 'v1')
api_status('mlb', mlb)

# create apiSports object for MLS
mls = apiSports(api_key, 'football', 'v3')
api_status('mls', mls)

# create apiSports object for NBA
nba = apiSports(api_key, 'basketball', 'v1')
api_status('nba', nba)

# create apiSports object for NFL
nfl = apiSports(api_key, 'american-football')
api_status('nfl', nfl)

# create apiSports object for NHL
nhl = apiSports(api_key, 'hockey')
api_status('nhl', nhl)

# verify whether API has active paid subscription
def verify_api(league_object):
    sub = league_object.request({}, 'status')['response']['subscription']
    req = league_object.request({}, 'status')['response']['requests']
    if (sub['active']==True) & (sub['plan']=='Free') & (req['limit_day']-req['current']>2):
        return True
    else:
        return False

# dictionary of information relevant to updating each league
league_info = {'mlb': {'object': mlb,
                   'id': '1',
                   'current_season': 2022,
                   'update': False},
            'mls': {'object': mls,
                   'id': '253',
                   'current_season': 2022,
                   'update': False},
            'nba': {'object': nba,
                   'id': '12',
                   'current_season': 2022,
                   'update': False},
            'nfl': {'object': nfl,
                   'id': '1',
                   'current_season': 2022,
                   'update': False},
            'nhl': {'object': nhl,
                   'id': '57',
                   'current_season': 2022,
                   'update': False}
              }

# if there is an active paid subscription to the league's API, set it to update
def update_ready(league_info=league_info):
    leagues = league_info
    for name, info in leagues.items():
        info['update'] = verify_api(info['object'])
    return leagues

leagues = update_ready()

def update(league_object, league_name, league_id, season_year, target):
    """
    Function to update past seasons of team or games data
    Parameters:
        1) league_object: variable for member of apiSports class | [mlb, mls, nba, nfl, nhl]
        2) league_name: string | ['mlb', 'mls', 'nba', 'nfl', 'nhl']
        3) league_id: string | ['1', '253', '12', '1', '57']
        4) season_year: integer | [2021, 2022, 2023, 2024, 2025]
        5) target: string | ['teams', 'games']
    """ 

    # gets season year in correct string format
    if league_name == 'nba':
        season = f"{season_year}-{season_year+1}"
    else:
        season = f"{season_year}"

    # I'm glad we threw their tea in the harbor
    if (league_name == 'mls') & (target == 'games'):
        endpoint = 'fixtures'
    else:
        endpoint = target

    print(f"Retrieving {target} data for {season} {league_name.upper()} season.")

    # API call
    if target == 'games':
        payload = {'league': league_id, 'season': season, 'timezone': 'America/Chicago'}
    else:
        payload = {'league': league_id, 'season': season}
    response = league_object.request(payload, endpoint)

    # create response df
    df = pd.DataFrame(response['response'])
    print(f"Returned {len(df)} {target}.")

    if (league_name == 'mls') & (target == 'teams'):
        # dataframe cleaning
        teams_df_final, venues_df_final = league_object.clean('teams', df)

        # export teams_df and venues_df to history tables in api-sports database
        teams_df_final.to_sql('mls_teams', con=engine, if_exists='replace', index=False)
        venues_df_final.to_sql('mls_venues', con=engine, if_exists='replace', index=False)
        print(f"Cleaned and uploaded {len(teams_df_final)} teams to mls_teams,  {len(venues_df_final)} venues to mls_venues.")
    else: 
        # dataframe cleaning
        df_final = league_object.clean(target, df)

        # export final df to table in api-sports database
        df_final.to_sql(f'{league_name}_{target}', con=engine, if_exists='replace', index=False)
        print(f"Cleaned and uploaded {len(df_final)} {target} to {league_name}_{target}.")

def run_updates(endpoint, leagues=leagues):
    """
    Function to update teams tables for all leagues and seasons
    Existing table is dropped so that multiple seasons can append data to table
    Takes 2 parameters:
        1) endpoint: string | ['teams', 'games']
        2) leagues: dictionary | previously defined info about each league
    """
    for name, info in leagues.items():
        if info['update']:
            update(info['object'], name, info['id'], info['current_season'], endpoint)
        else:
            print(f"{name.upper()} is not set to update. Revise `leagues` dictionary if needed.")
        print(f"{'-'*70}")

# run teams update
run_updates('teams')

# run games update
run_updates('games')