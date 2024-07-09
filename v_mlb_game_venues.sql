CREATE OR REPLACE VIEW v_mlb_game_venues AS (

WITH games AS (
	SELECT id AS game_id
		, date
		, time
		, (home_id+200) AS home_id
		, home_name
		, (away_id+200) AS away_id
		, away_name
	FROM mlb_games)
	
SELECT g.*
	, current_stadium AS home_venue
	, city
	, state
	, full_address
	, lat
	, lon
FROM games g
JOIN v_team_venues v ON g.home_id = v.team_id
ORDER BY game_id);

SELECT *
FROM v_mlb_game_venues;