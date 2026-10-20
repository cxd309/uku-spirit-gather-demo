# UKU Spirit Data Gathering Demo

A starting point for gathering UK Ultimate Spirit of the Game scores and comments from published Google Sheets into a single SQLite database, using Python and pandas.

## What it does

1. Read `tournaments.csv`, which lists each tournament and a link to its published breakdown sheet
2. Turn each link into a CSV download link and reads it with pandas
3. Stack the results from every tournament into a single table, tagging each row with a `tournament_id`
4. Rename the columns to shorter and more SQL friendly way
5. Write two tables, `tournaments` and `results` to `spirit.db`

Database is rebuilt from scratch every time script runs

## Setup

You need [uv](https://docs.astral.sh/uv/) installed. From the project folder:

```bash
uv sync
```

This creates a virtual environment and installs the exact versions in `uv.lock`.

## Run

Run from the project folder (the script looks for `tournaments.csv` in the current directory):

```bash
uv run uku-spirit-gather-demo
```

## Adding a tournament

1. Go to the google site listing all spirit results: [link](https://sites.google.com/ukultimate.com/sotgresults/2025-26-results)
2. Open a sheet and navigate to the "Spirit Results and Breakdown" tab, there should be a `#gid=` at the end of the url
3. Copy tournament details and url into `tournaments.csv`

Dates are in 'YYYY-MM-DD' format so SQLite can recognise as a date, excel will mess with this, you have been warned.

## Example query

The following query find every score where a team was given the maximum score in a category.

```sql
select
    t.category,
    t.division,
    t.name,
    t.date,
    r.team_recipient,
    r.team_giving,
    r.rules,
    r.fouls,
    r.fair,
    r.attitude,
    r.communication,
    (r.rules + r.fouls + r.fair + r.attitude + r.communication) as total,
    r.comment
from results r
    join tournaments t on r.tournament_id = t.id
where
    r.rules = 4 or r.fouls = 4 or r.fair = 4 or r.attitude = 4 or r.communication = 4;
```

It can be run from the sqlite3 cli or with a db IDE like datagrip or DBeaver. I have also had good experiences with DuckDB in integrating and tranforming data sources.

## Limitations

1. No real schema
   - `to_sql` creates the tables but doesn't set primary or foreign keys and there is no stable table layout
2. Tournament IDs are dependant on CSV layout
   - reordering the csv will result in all the tournaments shifting about
3. No data validation
4. All tournaments are downloaded every time
   - This isn't a great long term solution as it just takes time and wastes network bandwidth
   - A potential solution would be to check if the tournament is already in the data set and only download if an addition
5. No real project structure
   - everything here is sat in `__init__.py` which is less than optimal
