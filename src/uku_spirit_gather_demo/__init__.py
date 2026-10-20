import sqlite3

import pandas as pd

DATABASE = "spirit.db"

# rename columns from tournament csv
TOURNAMENT_COLUMNS = {
    "Category": "category",
    "Tournament": "name",
    "Date": "date",
    "Division": "division",
    "Breakdown Sheet Link": "link",
}

# rename columns results google sheet
RESULT_COLUMNS = {
    "Your Team Name": "team_giving",
    "Opponent Team Name": "team_recipient",
    "Opposition Rules Knowledge and Use": "rules",
    "Opposition Fouls and Body Contact": "fouls",
    "Opposition Fair-Mindedness": "fair",
    "Opposition Positive Attitude and Self-Control": "attitude",
    "Opposition Communication": "communication",
    "Comments": "comment",
}


def csv_url(link):
    """Turn a published-sheet link ending in #gid=... into a CSV download link"""
    base, gid = link.split("#gid=")
    base = base.replace("/pubhtml", "/pub")
    return f"{base}?gid={gid}&single=true&output=csv"


def main():
    tournaments = pd.read_csv("tournaments.csv")
    # rename tournament columns, raising an error
    tournaments = tournaments.rename(columns=TOURNAMENT_COLUMNS, errors="raise")
    # add index to tournaments as a fk for results
    tournaments.index.name = "id"

    all_results = []

    for tournament_id, row in tournaments.iterrows():
        print(f"Downloading {row['name']}...")
        url = csv_url(row["link"])
        results = pd.read_csv(url)

        # link result row back to tournament with id as fk
        results["tournament_id"] = tournament_id

        all_results.append(results)

    # concat all the results together into a single df
    # ignore index, not relevant for this
    results = pd.concat(all_results, ignore_index=True)
    # rename the columns from the breakdown google sheet
    # raise an error so that any deviation from the expected format fails loudly
    results = results.rename(columns=RESULT_COLUMNS, errors="raise")

    conn = sqlite3.connect(DATABASE)
    tournaments.to_sql("tournaments", conn, if_exists="replace")
    results.to_sql("results", conn, if_exists="replace", index_label="id")
    conn.close()

    print(
        f"Saved {len(tournaments)} tournaments and {len(results)} results to {DATABASE}"
    )
