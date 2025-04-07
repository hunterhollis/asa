# American Sportsman's Almanac (ASA)

This project establishes a database of teams, games, and venues across the 5 major American sports leagues (NFL, NBA, MLB, NHL, MLS). This data is then used to find games for different teams in the same metro area within any five-day period. The working title is the American Sportsman's Almanac (ASA). All tools and APIs used are free to access.

## Background

I created this project to support my dream of seeing a home game for every team in each of the 5 major American sports leagues. Seeing multiple teams in the same trip to a city is critical to minimizing the amount of travel this undertaking requires in the face of limited time and resources.

This used to be a very manual, time-consuming process of cross-referencing individual team schedules and hoping to find overlap. However, when I was able to plan a trip to Kansas City to see all 3 teams (Chiefs, Royals, Sporting KC) in the span of 4 days, I realized the opportunities I could be missing by not approaching the problem systematically.

The end result of this project is a dashboard where I can view all of the best opportunities for seeing the greatest number of teams in the shortest amount of time. It also provides a framework to create a database of games, teams, and venues to use for other projects.

## Overview

Games and teams data is extracted from the API-Sports [website](https://www.api-football.com/) with a series of Python [files](etl). The notebook transforms the data and then loads the games and teams data into a PostgreSQL database using the SQLAlchemy ORM.

Team venue addresses were collected into an Excel [file](etl/data/team_venue_info.xlsx) through manual research, then imported to another Python [file](etl/team_venues.py) which finds the latitude and longitude for each venue with Geoapify. The notebook then loads the venues information into the database with SQLAlchemy.

pgAdmin4 is used to manage the PostgreSQL database, and a SQL [file](etl/create_venues_views.sql) creates views from the games, teams, and venues tables. Creating a database was a priority because this data could be used for other projects.

A final Jupyter Notebook [file](game_finder_v3.ipynb) extracts the data back from the database views. The notebook calculates how many different home teams play in each metro area for every five-day period. Additional notes about this process:

- The notebook reads in an Excel [file](etl/data/team_completions.xlsx) of any teams which have already been seen and excludes them from the calculation. If the intention is to count all games, then the `completed_flag` field in the Excel file would just need to be set to 0 for all teams.
- If the same team plays multiple games in a period, it is still only counted once for that period.
- The five-day periods overlap. e.g., if January 1 to January 5 is the first period, then January 2 to January 6 is the second period, *not* January 6 to January 10.
- Teams that are technically in different cities are combined into larger metro areas. e.g., the New York Giants and Jets are considered to be playing in New York, New York rather than East Rutherford, New Jersey.

The final result is a table with an observation for each game and period combination—i.e., each game will have a separate row for each five-day period the game falls within. This allows the table to keep an accurate count of the teams playing in each period and preserve individual game information for more detailed planning. The table is exported as an Excel [file](tableau/games_counts_data.csv) to use for visualization.

This project uses a Tableau [workbook](tableau/remaining_teams_dashboard.twb) to create a dashboard of 4 main visualizations:

1. A map of the metro areas where games are taking place, including:
    a. Greatest number of unseen teams with games in that metro in any five-day period.
    b. Number of five-day periods that contain the greatest number of unseen teams in that metro.
    c. Percentage of the unseen teams remaining in a metro that could be seen in an optimal period—e.g., if a metro has 4 unseen teams, and the optimal five-day period contains up to 2 unseen teams, then the percentage would be 50%.
2. A table of more detailed game information which can be filtered by clicking a metro area on the map. The table only shows games which are in any optimal five-day period.
3. KPIs about how many teams and metro areas are available to see in a given date range.
4. Information about metros which are possible to complete (see all remaining unseen teams) in an optimal five-day period, including:
    a. Which of the "100%-able" metros have the greatest opportunity (highest number of teams remaining).
    b. Which of the "100%-able" metros have the scarcest opportunity (lowest number of optimal five-day periods).

The final dashboard is published to Tableau Public as [ASA Game Finder Dashboard](https://public.tableau.com/app/profile/hunter.hollis6019/viz/remaining_teams_dashboard/GameFinderDashboard).

## Step-by-Step

Here is information for how to replicate this project.

Note: the `creds.py` [file](etl/creds.py) has places for 3 different credentials which will need to be updated to replicate the project.

### Creating Database

1. Download and install PostgreSQL and a GUI. I used pgAdmin4 and will continue to reference it in upcoming steps, but other options are available. More information and extensive documentation can be found at the PostgreSQL [website](https://www.postgresql.org/).
2. Create a database in pgAdmin4 called `api_sports`. Other names can be used, but the notebooks use this name to connect to the database. Be sure to note your database password when you create it.
3. Update the `creds.py` [file](etl/creds.py) with your PostgreSQL database password.

### Access API-Sports

1. Create an account for API-Sports at their [website](https://www.api-football.com/). **See note on [API Access Considerations](#api-access-considerations) below.**
2. Note the API-KEY created for your subscription or access the key later in the Account page.
3. Update the `creds.py` [file](etl/creds.py) with your api-sports API key.

### Access Geoapify

1. Create a free account for Geoapify at their [website](https://www.geoapify.com/).
2. Create a project and note the API key that is automatically generated.
3. Update the `creds.py` [file](etl/creds.py) with your Geoapify API key.

### Data ETL

1. Open the `data_collection.py` [file](etl/data_collection.py). Review the file for necessary parameters.
2. Note that each league has a parameter to search for a specific season. At the time of writing, those are the current or most recently released season. However, API-Sports can lag behind the leagues' schedule announcements in making an upcoming season available in the API, so you may want to verify on the API-Sports website that the notebook is using the latest season available.
3. Open the `team_venues.py` [file](etl/team_venues.py). This notebook uses the `team_completions.xlsx` [file](etl/data/team_completions.xlsx) for team venue addresses. My intention is to keep this file up-to-date, but the process is currently manual, so updating any new or changing venues after cloning the repository will be up to the user.
4. Run the `run_etl.py` [file](etl/run_etl.py), installing any necessary packages if errors arise on import. Necessary credentials will be imported from `creds.py`.

### Database Management

1. In pgAdmin4, you should now see several tables and views of games, teams, and venues data in your api_sports database.
2. If the user's goal is to create a database for another project, this can be the end step, with the possibility of also repeating the process above for other seasons of data.

### Calculating Optimal Periods

1. The `team_completions.xlsx` [file](etl/data/team_completions.xlsx) contains a flag for whether each team has been completed already. Users can update this file to match their own experience or set all `completed_flag` values to 0 to track every team.
2. Open the `game_finder_v3.ipynb` [file](game_finder_v3.ipynb). Run all cells of this file to calculate the number of teams playing in each metro area for each five-day period in the games data. The data is exported to a `games_counts_data.csv` [file](tableau/games_counts_data.csv) to use for analysis or visualization.

### Visualization

1. Create a free account for Tableau at their [website](https://www.tableau.com/) and download the latest version of Tableau Public.
2. Open the `remaining_teams_dashboard.twb` [file](tableau/remaining_teams_dashboard.twb).
3. To update the data displayed in the dashboard, click on the Data Source tab. When prompted, connect to the `games_counts_data.csv` [file](tableau/games_counts_data.csv).
4. Clicking back to the Game Finder Dashboard tab should show results based on the user's updated data. Adjust the Start Date filter if needed to find games in a given time span.
5. For any desired edits, individual sheets can be shown be right-clicking the Game Finder Dashboard tab and selecting Unhide All Sheets.
6. The user can save their changes locally and/or publish their dashboard to Tableau Public.

### Additional Files

1. The `leagues_api_data_collection_demo.ipynb` [file](leagues_api_data_collection_demo.ipynb) demonstrates the data extraction process in a Jupyter Notebook.
2. The `leagues_api_data_collection_history.ipynb` [file](leagues_api_data_collection_history.ipynb) is used to create historical tables with past seasons of data.

## Recent Updates

Some modifications and additional considerations are included in the 4/7/25 update.

### Feature Improvements

- Significantly condensed ETL process—can now be run through a single Python file. Bypasses running SQL files in pgAdmin4.
- Addition of `leagues_api_data_collection_history.ipynb` allows for historical tables.
- `game_finder_v3.ipynb` contains some markdown improvements for easier navigation.

### API Access Considerations

Since this project was first published, [API-Sports](https://www.api-football.com/) has updated its account plans. They have made the extremely disappointing decision to remove the 2 most recent seasons of data from all free plans. The cheapest plan that includes all seasons for all sports is $79 per month. In an attempt to increase revenue, they've taken away from smaller users rather than incentivize larger users.

If I hadn't built this project using API-Sports, I wouldn't still be using it. My advice to anyone starting a project like this would be to use another resource. I performed this update by using a clause in the Terms of Service that allowed for a refund for any amount of time not used on a subscription—hence why I made updates to ensure everything could be re-run in one day.

Since I did this, they've now tried to remove this option as well. The ability to cancel for a refund seems to have been made available by consumer protections under French law, but the company is now hiding behind its legal team. "By subscribing to our services, you expressly agree that access to the service is granted immediately after payment, and you waive your right of withdrawal in accordance with [Article L221-28](https://french-business-law.com/french-legislation-art/article-l221-28-of-the-french-consumer-code/) of the French Consumer Code."

Under this article: "The supply of services fully performed before the end of the withdrawal period and, if the contract imposes an obligation on the consumer to pay, the performance of which has begun with his prior and express agreement and with his acknowledgement of the loss of his right of withdrawal, when the service has been fully performed by the trader." In other words, API-Sports is going to require you to waive your right to cancel your subscription under consumer protection law because they couldn't be bothered to come up with a reasonable strategy for revenue growth.

All of this is also set atop a pitiful absence of any user support. If you're a free user, you'll only be able to use their largely useless chatbot. They don't even post an email address on the site. The chatbot will promise to forward on your questions to a real person—but in my experience, it has never led to a response.

In all, it's disheartening to know that projects like this depend on companies that will squeeze every possible dollar from their users. But hey, API-Sports, if you want to come to an agreement... I'll give you a totally reasonable price on [api-sports.com](https://www.api-sports.com/).

## Looking Ahead

There are some limitations and opportunities in the project that could be addressed in the future.

### Current Limitations

- Updating team venue information is a manual process, and API-Sports only has that information for some leagues.
- The five-day time periods may seem arbitrary, and it can be tricky to find where to adjust that number. Even then, the game finder notebook will only accept 1 time frame at a time which is a hindrance.
- API-Sports sometimes lags behind leagues' schedule announcements which can be annoying when trying to plan further into the future. At the time of writing, the MLB has released its 2025 schedule, but API-Sports has not made the games data available.

### Future Improvements

- Will make the time period parameter easier to find and include documentation about why and how to change it so that the five-day period is not locked in.
- Would like to add additional lengths of time periods and have them all exported in the final game counts file to be used in different ways in Tableau.
- API-Sports continues to expand its data, and those additions can be included. Basketball venue information was released in the most recent update, but it is not included in the notebooks.
- Far off, could also start to include some travel planning information like flight prices, Amtrak routes, or even ticket prices.

### Reflection

This is a passion project that I have tried to also turn into a portfolio piece. There are some elements of this project that may not be strictly necessary to achieve the intended results, but I wanted to use several tools and demonstrate the breadth of what can be done with this project.

Getting it to this point is a major milestone, and I am genuinely very proud of this work, regardless of any level of technical ability or experience shown. At the end of the day, I hope to grow with this project. I plan to continue developing it for a while.
