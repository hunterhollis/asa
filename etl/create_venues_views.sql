-- team venues
CREATE OR REPLACE VIEW v_team_venues AS (

WITH mls AS (
	SELECT *,
		CASE
			WHEN name = 'Austin' THEN 'Austin FC'
			WHEN name = 'Charlotte' THEN 'Charlotte FC'
			WHEN name = 'Chicago Fire' THEN 'Chicago Fire FC'
			WHEN name = 'DC United' THEN 'D.C. United'
			WHEN name = 'Houston Dynamo' THEN 'Houston Dynamo FC'
			WHEN name = 'Inter Miami' THEN 'Inter Miami CF'
			WHEN name = 'Montreal Impact' THEN 'CF Montreal'
			WHEN name = 'Seattle Sounders' THEN 'Seattle Sounders FC'
			WHEN name = 'St. Louis City' THEN 'St. Louis City SC'
			WHEN name = 'Vancouver Whitecaps' THEN 'Vancouver Whitecaps FC'
		ELSE name END AS display_name
	FROM mls_teams),

mlb AS (
	SELECT *,
		CASE
			WHEN name = 'St.Louis Cardinals' THEN 'St. Louis Cardinals'
			WHEN name = 'Cleveland Indians' THEN 'Cleveland Guardians'
			WHEN name IN ('American League', 'National League') THEN NULL
		ELSE name END AS display_name,
		(id+200) AS display_id		-- OFFSETTING MLB TEAM IDS BY 200 TO NOT OVERLAP WITH NFL
	FROM mlb_teams),

all_leagues AS (
	SELECT id AS team_id, display_name AS team
	FROM mls
	UNION ALL
	SELECT display_id AS team_id, display_name AS team
	FROM mlb
	UNION ALL
	SELECT id AS team_id, name AS team
	FROM nba_teams
	UNION ALL
	SELECT id AS team_id, name AS team
	FROM nfl_teams
	UNION ALL
	SELECT id AS team_id, name AS team
	FROM nhl_teams)

SELECT *
FROM all_leagues
JOIN team_venues USING(team));


-- MLB game venues
CREATE OR REPLACE VIEW v_mlb_game_venues AS (

WITH games AS (
	SELECT mlb_games.id AS game_id,
		mlb_games.date,
		mlb_games.time,
		(mlb_games.home_id+200) AS home_id,
		mlb_games.home_name,
		(mlb_games.away_id+200) AS away_id,
		mlb_games.away_name
	FROM mlb_games)
	
SELECT g.game_id,
	g.date,
	g.time,
	g.home_id,
	g.home_name,
	g.away_id,
	g.away_name,
	v.current_stadium AS venue_name,
	v.city,
	v.state,
	v.full_address,
	v.lat,
	v.lon,
	v.metro_area,
	v.metro_team_num
FROM games g
JOIN v_team_venues v ON g.home_id = v.team_id
ORDER BY game_id);


-- NBA game venues
CREATE OR REPLACE VIEW v_nba_game_venues AS (

WITH games AS (
	 SELECT nba_games.id AS game_id,
		nba_games.date,
		nba_games.time,
		nba_games.home_id AS home_id,
		nba_games.home_name,
		nba_games.away_id AS away_id,
		nba_games.away_name
	   FROM nba_games
	)
	
SELECT g.game_id,
	g.date,
	g.time,
	g.home_id,
	g.home_name,
	g.away_id,
	g.away_name,
	v.current_stadium AS venue_name,
	v.city,
	v.state,
	v.full_address,
	v.lat,
	v.lon,
	v.metro_area,
	v.metro_team_num
FROM games g
 JOIN v_team_venues v ON g.home_id = v.team_id
ORDER BY g.game_id);


-- NFL game venues
CREATE OR REPLACE VIEW v_nfl_game_venues AS (

WITH games AS (
	 SELECT nfl_games.id AS game_id,
		nfl_games.date,
		nfl_games.time,
		nfl_games.home_id AS home_id,
		nfl_games.home_name,
		nfl_games.away_id AS away_id,
		nfl_games.away_name,
		nfl_games.venue_city,
		nfl_games.venue_name
	   FROM nfl_games
	)
	
SELECT g.game_id,
	g.date,
	g.time,
	g.home_id,
	g.home_name,
	g.away_id,
	g.away_name,
-- different logic to handle neutral site (e.g. international) games
-- exception made to handle Raiders in "Paradise" versus "Las Vegas"
	CASE WHEN g.venue_city = v.city OR g.venue_city = 'Las Vegas' THEN v.current_stadium ELSE g.venue_name END AS venue_name,
	CASE WHEN g.venue_city = v.city OR g.venue_city = 'Las Vegas' THEN v.city ELSE g.venue_city END AS city,
	CASE WHEN g.venue_city = v.city OR g.venue_city = 'Las Vegas' THEN v.state END AS state,
	CASE WHEN g.venue_city = v.city OR g.venue_city = 'Las Vegas' THEN v.full_address END AS full_address,
	CASE WHEN g.venue_city = v.city OR g.venue_city = 'Las Vegas' THEN v.lat END AS lat,
	CASE WHEN g.venue_city = v.city OR g.venue_city = 'Las Vegas' THEN v.lon END AS lon,
	CASE WHEN g.venue_city = v.city OR g.venue_city = 'Las Vegas' THEN v.metro_area END AS metro_area,
	v.metro_team_num
FROM games g
	JOIN v_team_venues v ON g.home_id = v.team_id
ORDER BY g.game_id);


-- NHL game venues
CREATE OR REPLACE VIEW v_nhl_game_venues AS (

WITH games AS (
	 SELECT nhl_games.id AS game_id,
		nhl_games.date,
		nhl_games.time,
		nhl_games.home_id AS home_id,
		nhl_games.home_name,
		nhl_games.away_id AS away_id,
		nhl_games.away_name
	   FROM nhl_games
	)
	
SELECT g.game_id,
	g.date,
	g.time,
	g.home_id,
	g.home_name,
	g.away_id,
	g.away_name,
	v.current_stadium AS venue_name,
	v.city,
	v.state,
	v.full_address,
	v.lat,
	v.lon,
	v.metro_area,
	v.metro_team_num
FROM games g
 JOIN v_team_venues v ON g.home_id = v.team_id
ORDER BY g.game_id);


-- MLS game venues
CREATE OR REPLACE VIEW v_mls_game_venues AS (

WITH games AS (
	 SELECT mls_games.id AS game_id,
		mls_games.date,
		mls_games.datetime::timestamp::time AS time,
		mls_games.home_id AS home_id,
		mls_games.home_name,
		mls_games.away_id AS away_id,
		mls_games.away_name
	   FROM mls_games
	)
	
SELECT g.game_id,
	g.date,
	g.time,
	g.home_id,
	g.home_name,
	g.away_id,
	g.away_name,
	v.current_stadium AS venue_name,
	v.city,
	v.state,
	v.full_address,
	v.lat,
	v.lon,
	v.metro_area,
	v.metro_team_num
FROM games g
 JOIN v_team_venues v ON g.home_id = v.team_id
ORDER BY g.game_id);

-- All combined game venues
CREATE OR REPLACE VIEW v_all_game_venues AS (

SELECT 'mlb' AS league,
	'mlb_'||game_id AS game_id,
	date,
	time,
	home_id,
	home_name,
	away_id,
	away_name,
	venue_name,
	city,
	state,
	full_address,
	lat,
	lon,
	metro_area,
	metro_team_num
FROM v_mlb_game_venues

UNION ALL

SELECT 'mls' AS league,
	'mls_'||game_id AS game_id,
	date,
	time::text,
	home_id,
	home_name,
	away_id,
	away_name,
	venue_name,
	city,
	state,
	full_address,
	lat,
	lon,
	metro_area,
	metro_team_num
FROM v_mls_game_venues

UNION ALL

SELECT 'nba' AS league,
	'nba_'||game_id AS game_id,
	date,
	time,
	home_id,
	home_name,
	away_id,
	away_name,
	venue_name,
	city,
	state,
	full_address,
	lat,
	lon,
	metro_area,
	metro_team_num
FROM v_nba_game_venues

UNION ALL

SELECT 'nfl' AS league,
	'nfl_'||game_id AS game_id,
	date::date,
	time,
	home_id,
	home_name,
	away_id,
	away_name,
	venue_name,
	city,
	state,
	full_address,
	lat,
	lon,
	metro_area,
	metro_team_num
FROM v_nfl_game_venues

UNION ALL

SELECT 'nhl' AS league,
	'nhl_'||game_id AS game_id,
	date,
	time,
	home_id,
	home_name,
	away_id,
	away_name,
	venue_name,
	city,
	state,
	full_address,
	lat,
	lon,
	metro_area,
	metro_team_num
FROM v_nhl_game_venues
ORDER BY game_id);