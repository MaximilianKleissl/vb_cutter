import csv

import pandas as pd


codes_translator: dict = {
    "b": "Wir schlagen auf",
    "B": "Gegner schlägt auf",
    "s": "Wir spielen zu",
    "S": "Gegner spielt zu",
    "w": "Wir gewinnen Ballwechsel",
    "W": "Gegner gewinnt Ballwechsel",
    "h": "Highlight",
    "H": "Gegner hat Highlight",
    "n": "Nasenbluten",
    "N": "Gegner hat Nasenbluten",
    "o": "We set out of System",
    "O": "Opponent sets out of System",
    "f": "We play Freeball / Out of System",
    "F": "Opponent plays Freeball / Out of System",
    "1": "Angriff über 1",
    "2": "Angriff über 2",
    "3": "Angriff über 3",
    "4": "Angriff über 4",
    "5": "Angriff über 5",
    "6": "Angriff über 6",
    "l": "Annahme",
    "m": "Annahme",
    "r": "Annahme",
    "L": "Annahme",
    "M": "Annahme",
    "R": "Annahme"
}


def translate_code(code):
    if code in codes_translator:
        return codes_translator[code]
    if code.startswith("z"):
        return f"Our setter is in position: {code[1:]}"
    if code.startswith("Z"):
        return f"Opponent setter is in position: {code[1:]}"
    if code.startswith("l"):
        return f"Our lineup is: {code[1:]}"
    if code.startswith("L"):
        return f"Opponent lineup is: {code[1:]}"
    if code.startswith("p"):
        return f"We change player {code[1:].split(":")[0]} with player {code[1:].split(":")[1]}"
    if code.startswith("P"):
        return f"Opponent changes player: {code[1:].split(":")[0]} with player: {code[1:].split(":")[1]}"
    return code


def tagger(row):
    return [row["code"].lower]


def estimate_player(df):
    players = []
    for idx, row in df.iterrows():
        if row["Marker"] == "s":
            players.append(row["Our Lineup"][row["Our Rotation"] - 1])
            continue
        if row["Marker"] == "S":
            players.append(row["Opp Lineup"][row["Opponent Rotation"] - 1])
            continue
        if row["Marker"] == "B":
            players.append(row["Opp Lineup"][0])
            continue
        if row["Last Set By Us"]:
            if row["Marker"] == "1":
                if row["Our Rotation"] == 2:
                    players.append(row["Our Lineup"][5 - 1])
                elif row["Our Rotation"] == 3:
                    players.append(row["Our Lineup"][6 - 1])
                elif row["Our Rotation"] == 4:
                    players.append(row["Our Lineup"][1 - 1])
                else:
                    players.append("Wtf ???")
                continue
            if row["Marker"] == "6":
                players.append(
                    row["Our Lineup"][
                        {1: 5 - 1, 2: 6 - 1, 3: 1 - 1, 4: 5 - 1, 5: 6 - 1, 6: 1 - 1}[
                            row["Our Rotation"]
                        ]
                    ]
                )
                continue
            if row["Marker"] == "2":
                players.append(
                    row["Our Lineup"][
                        {
                            1: (4 - 1 if row["Last Serve By Us"] else 2 - 1),
                            2: 4 - 1,
                            3: 2 - 1,
                            4: 3 - 1,
                            5: 2 - 1,
                            6: 3 - 1,
                        }[row["Our Rotation"]]
                    ]
                )
                continue
            if row["Marker"] == "3":
                players.append(
                    row["Our Lineup"][
                        {1: 3 - 1, 2: 4 - 1, 3: 2 - 1, 4: 3 - 1, 5: 4 - 1, 6: 2 - 1}[
                            row["Our Rotation"]
                        ]
                    ]
                )
                continue
            if row["Marker"] == "4":
                players.append(
                    row["Our Lineup"][
                        {
                            1: (2 - 1 if row["Last Serve By Us"] else 4 - 1),
                            2: 3 - 1,
                            3: 4 - 1,
                            4: 2 - 1,
                            5: 3 - 1,
                            6: 4 - 1,
                        }[row["Our Rotation"]]
                    ]
                )
                continue
        else:
            if row["Marker"] == "1":
                if row["Opponent Rotation"] == 2:
                    players.append(row["Opp Lineup"][5 - 1])
                elif row["Opponent Rotation"] == 3:
                    players.append(row["Opp Lineup"][6 - 1])
                elif row["Opponent Rotation"] == 4:
                    players.append(row["Opp Lineup"][1 - 1])
                else:
                    players.append("Wtf ???")
                continue
            if row["Marker"] == "6":
                players.append(
                    row["Opp Lineup"][
                        {1: 5 - 1, 2: 6 - 1, 3: 1 - 1, 4: 5 - 1, 5: 6 - 1, 6: 1 - 1}[
                            row["Opponent Rotation"]
                        ]
                    ]
                )
                continue
            if row["Marker"] == "2":
                players.append(
                    row["Opp Lineup"][
                        {
                            1: (2 - 1 if row["Last Serve By Us"] else 4 - 1),
                            2: 6 - 1,
                            3: 2 - 1,
                            4: 3 - 1,
                            5: 2 - 1,
                            6: 3 - 1,
                        }[row["Opponent Rotation"]]
                    ]
                )
                continue
            if row["Marker"] == "3":
                players.append(
                    row["Opp Lineup"][
                        {1: 3, 2: 6 - 1, 3: 2 - 1, 4: 3 - 1, 5: 4 - 1, 6: 2 - 1}[
                            row["Opponent Rotation"]
                        ]
                    ]
                )
                continue
            if row["Marker"] == "4":
                players.append(
                    row["Opp Lineup"][
                        {
                            1: (4 - 1 if row["Last Serve By Us"] else 2 - 1),
                            2: 3 - 1,
                            3: 2 - 1,
                            4: 2 - 1,
                            5: 3 - 1,
                            6: 4 - 1,
                        }[row["Opponent Rotation"]]
                    ]
                )
                continue
        if row["Marker"] == "b":
            players.append(row["Our Lineup"][0])
            continue
        players.append("")
    return players


def get_dict(markers):
    # Create DataFrame from the given markers
    df = pd.DataFrame(markers, columns=["Marker", "Timestamp"])

    # Initialize variables
    team_score = 0
    opponent_score = 0
    team_sets = 0
    opponent_sets = 0
    our_lineup = [1, 2, 3, 4, 5, 6]
    opp_lineup = [1, 2, 3, 4, 5, 6]
    team_scores = []
    opponent_scores = []
    team_set_wins = []
    opponent_set_wins = []
    current_sets = []
    rally_begin_with_our_serve = True
    our_rotation = 1
    opponent_rotation = 1
    our_rotations = []
    opponent_rotations = []
    our_lineups = []
    opp_lineups = []
    last_serve_by_us = []
    last_single_set_by_us = True
    last_set_by_us = []

    # Iterate through the DataFrame to update scores and sets
    i = 0
    for marker in df["Marker"]:
        if marker in ("s", "o"):
            last_single_set_by_us = True
        if marker in ("S", "O"):
            last_single_set_by_us = False
        if marker.startswith("z"):
            our_rotation = int(marker[1:])
        if marker.startswith("Z"):
            opponent_rotation = int(marker[1:])
        if marker.startswith("l"):
            our_lineup = [int(n) for n in marker[1:].split(";")]
        if marker.startswith("L"):
            opp_lineup = [int(n) for n in marker[1:].split(";")]
        if marker.startswith("p"):
            our_lineup[our_lineup.index(int(marker[1:].split(":")[0]))] = int(
                marker[1:].split(":")[1]
            )
        if marker.startswith("P"):
            opp_lineup[opp_lineup.index(int(marker[1:].split(":")[0]))] = int(
                marker[1:].split(":")[1]
            )
        if marker == "b":
            rally_begin_with_our_serve = True
        if marker == "B":
            rally_begin_with_our_serve = False
        i += 1
        if marker == "w":
            team_score += 1
            if not rally_begin_with_our_serve:
                our_rotation = our_rotation - 1 if our_rotation != 1 else 6
                our_lineup = our_lineup[1:] + [our_lineup[0]]
        if marker == "W":
            opponent_score += 1
            if rally_begin_with_our_serve:
                opponent_rotation = (
                    opponent_rotation - 1 if opponent_rotation != 1 else 6
                )
                opp_lineup = opp_lineup[1:] + [opp_lineup[0]]

        if marker == "equal":
            # Check who won the set
            if team_score > opponent_score:
                team_sets += 1
            elif opponent_score > team_score:
                opponent_sets += 1

            # Reset scores for the new set
            team_score = 0
            opponent_score = 0

        # Append current scores and sets to their respective lists
        team_scores.append(team_score)
        opponent_scores.append(opponent_score)
        team_set_wins.append(team_sets)
        opponent_set_wins.append(opponent_sets)
        current_sets.append(team_sets + opponent_sets)
        our_rotations.append(our_rotation)
        opponent_rotations.append(opponent_rotation)
        our_lineups.append(our_lineup.copy())
        opp_lineups.append(opp_lineup.copy())
        last_serve_by_us.append(rally_begin_with_our_serve)
        last_set_by_us.append(last_single_set_by_us)

    # Add the new columns to the DataFrame
    df["Last Set By Us"] = last_set_by_us
    df["Team_Points"] = team_scores
    df["Opponent_Points"] = opponent_scores
    df["Team_Sets"] = team_set_wins
    df["Opponent_Sets"] = opponent_set_wins
    df["Current Set"] = current_sets
    df["Time Readable"] = df["Timestamp"].map(
        lambda x: f"{int(x // (1000 * 60)):02} : {(int(x // 1000) % 60):02}"
    )
    df["Our Rotation"] = our_rotations
    df["Opponent Rotation"] = opponent_rotations
    df["Tags"] = df["Marker"].map(lambda x: x[0].lower())
    df["Our Lineup"] = our_lineups
    df["Opp Lineup"] = opp_lineups
    df["Last Serve By Us"] = last_serve_by_us

    df["Player"] = estimate_player(df)
    df["Code Readable"] = df["Marker"].map(translate_code)
    df["Code Readable"] = df["Code Readable"] + " (" + df["Player"].astype(str) + ")"

    return df


if __name__ == "__main__":
    markers = []
    with open("projects/14092024/wvv_pvc.csv", newline="") as csvfile:
        # Create a CSV reader object
        reader = csv.reader(csvfile)

        # Iterate through the rows of the CSV
        for row in reader:
            # Append the pair (tuple) to the list
            markers.append((row[0], float(row[1])))
    df = get_dict(markers)
    df.to_csv("analysis.csv")
