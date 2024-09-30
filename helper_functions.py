import requests
import pandas as pd

class apiSports:
        
    def __init__(self, api_key, sport, version='v1'):
        self.api_key = api_key
        self.sport = sport
        self.version = version

    def request(self, payload, endpoint):
        url = f"https://{self.version}.{self.sport}.api-sports.io/"
        headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': f'{self.version}.{self.sport}.api-sports.io'
        }
        response = requests.get(url=url+endpoint, headers=headers, params=payload).json()
        return response
    
    def clean(self, endpoint, df_current):
        df = df_current.copy()
        if endpoint=='teams':
            if self.sport=='baseball':
                # expand country
                df[['country_id', 'country_name']] = pd.json_normalize(df.country)[['id', 'name']]
                df = df.drop(columns=['country'])
                return df
            elif self.sport=='american-football':
                # expand country (without id)
                df[['country_name']] = pd.json_normalize(df.country)[['name']]
                df = df.drop(columns=['country'])
                return df
            elif self.sport=='basketball':
                df[['country_id', 'country_name']] = pd.json_normalize(df.country)[['id', 'name']]
                df = df.drop(columns=['country'])
                df = df.rename(columns={'nationnal':'national'})
                return df
            elif self.sport=='hockey':
                df[['country_id', 'country_name']] = pd.json_normalize(df.country)[['id', 'name']]
                df[['arena_name', 'arena_location']] = pd.json_normalize(df.arena)[['name', 'location']]
                df = df.drop(columns=['country', 'arena'])
                return df
            elif self.sport=='football':
                # expand team dicts into df
                teams_df_clean = df.copy()
                teams_df_clean = pd.json_normalize(teams_df_clean['team'])

                # expand venue dicts into df
                venues_df_clean = df.copy()
                venues_df_clean = pd.json_normalize(venues_df_clean['venue'])

                # attach venue id to teams df
                teams_df_final = pd.concat([teams_df_clean, venues_df_clean['id']], axis=1)
                teams_df_final.columns.values[-1] = 'venue_id'

                # attach team id to venues df
                venues_df_final = pd.concat([venues_df_clean, teams_df_clean['id']], axis=1)
                venues_df_final.columns.values[-1] = 'team_id'

                return teams_df_final, venues_df_final
            else:
                print('This sport is not supported. Clean teams manually.')
        if endpoint=='games':
            if self.sport=='baseball':
                # date data types
                df['datetime'] = pd.to_datetime([d[0] for d in df['date'].str.rsplit('-', n=1)])
                df['date'] = df['datetime'].dt.date

                # expand teams
                df[['home_id', 'home_name', 'away_id', 'away_name']] = \
                    pd.json_normalize(df.teams)[['home.id', 'home.name', 'away.id', 'away.name']]

                # expand status
                df['status'] = pd.json_normalize(df.status)['short']

                # expand country
                df[['country_id', 'country_name']] = pd.json_normalize(df.country)\
                                                        [['id', 'name']]

                # expand league
                df[['league_id', 'league_name']] = pd.json_normalize(df.league)\
                                                        [['id', 'name']]

                # expand scores
                expanded_score_cols = ['home.hits', 'home.errors', 'home.total',
                                       'away.hits', 'away.errors', 'away.total']
                new_score_cols = ['home_hits', 'home_errors', 'home_total',
                                  'away_hits', 'away_errors', 'away_total']
                df[new_score_cols] = pd.json_normalize(df.scores)[expanded_score_cols]
                
                # select columns
                cols = ['id', 'date', 'time', 'datetime', 'timezone', 'week', 'status',
                        'country_id', 'country_name', 'league_id', 'league_name',
                        'home_id', 'home_name', 'away_id', 'away_name'] + new_score_cols
                df = df[cols]
            elif self.sport=='basketball':
                # date data types
                df['datetime'] = pd.to_datetime([d[0] for d in df['date'].str.rsplit('-', n=1)])
                df['date'] = df['datetime'].dt.date

                # expand teams
                df[['home_id', 'home_name', 'away_id', 'away_name']] = \
                    pd.json_normalize(df.teams)[['home.id', 'home.name', 'away.id', 'away.name']]

                # expand status
                df['status'] = pd.json_normalize(df.status)['short']

                # expand country
                df[['country_id', 'country_name']] = pd.json_normalize(df.country)\
                                                        [['id', 'name']]

                # expand league
                df[['league_id', 'league_name']] = pd.json_normalize(df.league)\
                                                        [['id', 'name']]

                # expand scores
                expanded_score_cols = ['home.total', 'away.total']
                new_score_cols = ['home_total', 'away_total']
                df[new_score_cols] = pd.json_normalize(df.scores)[expanded_score_cols]
                
                # select columns
                cols = ['id', 'date', 'time', 'datetime', 'timezone', 'week', 'status',
                        'country_id', 'country_name', 'league_id', 'league_name',
                        'home_id', 'home_name', 'away_id', 'away_name'] + new_score_cols
                df = df[cols]
            elif self.sport=='hockey':
                # date data types
                df['datetime'] = pd.to_datetime([d[0] for d in df['date'].str.rsplit('-', n=1)])
                df['date'] = df['datetime'].dt.date

                # expand teams
                df[['home_id', 'home_name', 'away_id', 'away_name']] = \
                    pd.json_normalize(df.teams)[['home.id', 'home.name', 'away.id', 'away.name']]

                # expand status
                df['status'] = pd.json_normalize(df.status)['short']

                # expand country
                df[['country_id', 'country_name']] = pd.json_normalize(df.country)\
                                                        [['id', 'name']]

                # expand league
                df[['league_id', 'league_name']] = pd.json_normalize(df.league)\
                                                        [['id', 'name']]

                # expand scores
                df[['home_total', 'away_total']] = pd.json_normalize(df.scores)[['home', 'away']]  
                
                # select columns
                cols = ['id', 'date', 'time', 'datetime', 'timezone', 'week', 'status',
                        'country_id', 'country_name', 'league_id', 'league_name',
                        'home_id', 'home_name', 'away_id', 'away_name', 'home_total', 'away_total']
                df = df[cols]
            elif self.sport=='american-football':
                # expand/clean fixture
                cols = ['id', 'stage', 'week', 'date.date', 'date.time', 'date.timestamp',
                        'date.timezone', 'venue.name', 'venue.city', 'status.short']
                new_cols = ['id', 'stage', 'week', 'date', 'time', 'timestamp', 'timezone',
                            'venue_name', 'venue_city', 'status']
                df[new_cols] = pd.json_normalize(df.game)[cols]

                # expand league
                df[['league_id', 'league_name', 'country_name']] = pd.json_normalize(df.league)\
                                                                [['id', 'name', 'country.name']]

                # expand teams
                new_cols = ['home_id', 'home_name', 'away_id', 'away_name']
                df[new_cols] = pd.json_normalize(df.teams)[['home.id', 'home.name','away.id', 'away.name']]

                # expand goals
                df[['home_total', 'away_total']] = pd.json_normalize(df.scores)[['home.total', 'away.total']]

                # drop un-needed original columns
                df.drop(columns=['game', 'league', 'teams', 'scores'], inplace=True)

            elif self.sport=='football':
                # expand/clean fixture
                df_clean = pd.json_normalize(df.fixture)[['id', 'date', 'timestamp', 'timezone',
                                                                    'venue.id', 'status.short']]

                df_clean['datetime'] = pd.to_datetime([d[0] for d in df_clean['date'].str.rsplit('-', n=1)])
                df_clean['date'] = df_clean['datetime'].dt.date

                df_clean = df_clean.rename(columns={'venue.id': 'venue_id', 'status.short': 'status'})
                df_clean = df_clean[['id', 'date', 'timestamp', 'datetime', 'timezone', 'venue_id', 'status']]

                # expand league
                df_clean[['league_id', 'league_name', 'country_name']] = pd.json_normalize(df.league)[['id', 'name', 'country']]

                # expand teams
                new_cols = ['home_id', 'home_name', 'home_winner', 'away_id', 'away_name', 'away_winner']
                df_clean[new_cols] = pd.json_normalize(df.teams)[['home.id', 'home.name', 'home.winner', 
                                                                    'away.id', 'away.name', 'away.winner']]

                # expand goals
                df_clean[['home_total', 'away_total']] = pd.json_normalize(df.goals)[['home', 'away']]

                return df_clean
            else:
                print("Sport not found.")

            return df