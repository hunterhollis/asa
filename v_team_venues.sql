DROP VIEW IF EXISTS v_team_venues;

CREATE VIEW v_team_venues AS (

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

SELECT *
FROM v_team_venues;