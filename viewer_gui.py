import pprint
import os
import vlc
import csv
import time
import tkinter as tk
from tkinter import ttk
import sys
import os
import time
from settings import Settings
import pandas as pd

codes_translator: dict = {
    "b" : "Wir schlagen auf",
    "B" : "Gegner schlägt auf",
    "s" : "Wir spielen zu",
    "S" : "Gegner spielt zu",
    "w" : "Wir gewinnen Ballwechsel",
    "W" : "Gegner gewinnt Ballwechsel",
    "h" : "Highlight",
    "H" : "Gegner hat Highlight",
    "n" : "Nasenbluten",
    "N" : "Gegner hat Nasenbluten",
    "o" : "We set out of System",
    "O" : "Opponent sets out of System",
    "f" : "We play Freeball / Out of System",
    "F" : "Opponent plays Freeball / Out of System",
    "1" : "Angriff über 1",
    "2" : "Angriff über 2",
    "3" : "Angriff über 3",
    "4" : "Angriff über 4",
    "5" : "Angriff über 5",
    "6" : "Angriff über 6"
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
                    players.append(row["Our Lineup"][5-1])
                elif row["Our Rotation"] == 3:
                    players.append(row["Our Lineup"][6-1])
                elif row["Our Rotation"] == 4:
                    players.append(row["Our Lineup"][1-1])
                else:
                    players.append("Wtf ???")
                continue
            if row["Marker"] == "6":
                players.append(row["Our Lineup"][{1: 5-1, 2: 6-1, 3: 1-1, 4: 5-1, 5: 6-1, 6: 1-1}[row["Our Rotation"]]])
                continue
            if row["Marker"] == "2":
                players.append(row["Our Lineup"][{1: (4-1 if row["Last Serve By Us"] else 2-1), 2: 6-1, 3: 2-1, 4: 3-1, 5: 2-1, 6: 3-1}[row["Our Rotation"]]])
                continue
            if row["Marker"] == "3":
                players.append(row["Our Lineup"][{1: 3, 2: 6-1, 3: 2-1, 4: 3-1, 5: 4-1, 6: 2-1}[row["Our Rotation"]]])
                continue
            if row["Marker"] == "4":
                players.append(row["Our Lineup"][{1: (2-1 if row["Last Serve By Us"] else 4-1), 2: 6-1, 3: 2-1, 4: 3-1, 5: 2-1, 6: 3-1}[row["Our Rotation"]]])
                continue
        else:
            if row["Marker"] == "1":
                if row["Opponent Rotation"] == 2:
                    players.append(row["Opp Lineup"][5-1])
                elif row["Opponent Rotation"] == 3:
                    players.append(row["Opp Lineup"][6-1])
                elif row["Opponent Rotation"] == 4:
                    players.append(row["Opp Lineup"][1-1])
                else:
                    players.append("Wtf ???")
                continue
            if row["Marker"] == "6":
                players.append(row["Opp Lineup"][{1: 5-1, 2: 6-1, 3: 1-1, 4: 5-1, 5: 6-1, 6: 1-1}[row["Opponent Rotation"]]])
                continue
            if row["Marker"] == "2":
                players.append(row["Opp Lineup"][{1: (2-1 if row["Last Serve By Us"] else 4-1), 2: 6-1, 3: 2-1, 4: 3-1, 5: 2-1, 6: 3-1}[row["Opponent Rotation"]]])
                continue
            if row["Marker"] == "3":
                players.append(row["Our Lineup"][{1: 3, 2: 6-1, 3: 2-1, 4: 3-1, 5: 4-1, 6: 2-1}[row["Opponent Rotation"]]])
                continue
            if row["Marker"] == "4":
                players.append(row["Opp Lineup"][{1: (4-1 if row["Last Serve By Us"] else 2-1), 2: 6-1, 3: 2-1, 4: 3-1, 5: 2-1, 6: 3-1}[row["Opponent Rotation"]]])
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
    our_lineup = [1,2,3,4,5,6]
    opp_lineup = [1,2,3,4,5,6]
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
    i=0
    for marker in df['Marker']:
        if marker in ("s", "o"):
            last_single_set_by_us = True
        if marker in ("S", "O"):
            last_single_set_by_us = False
        if marker.startswith("z"):
            our_rotation = int(marker[1:])
        if marker.startswith("Z"):
            our_rotation = int(marker[1:])
        if marker.startswith("l"):
            our_lineup = [int(n) for n in marker[1:].split(";")]
        if marker.startswith("L"):
            opp_lineup = [int(n) for n in marker[1:].split(";")]
        if marker.startswith("p"):
            our_lineup[our_lineup.index(int(marker[1:].split(":")[0]))] = int(marker[1:].split(":")[1])
        if marker.startswith("P"):
            opp_lineup[opp_lineup.index(marker[1:].split(":")[0])] = marker[1:].split(":")[1]
        if marker == "b":
            rally_begin_with_our_serve = True
        if marker == "B":
            rally_begin_with_our_serve = False
        i+=1
        if marker == 'w':
            team_score += 1
            if not rally_begin_with_our_serve:
                our_rotation = our_rotation - 1 if our_rotation != 1 else 6
                our_lineup = our_lineup[1:] + [our_lineup[0]]
        if marker == 'W':
            opponent_score += 1
            if rally_begin_with_our_serve:
                opponent_rotation = opponent_rotation - 1 if opponent_rotation != 1 else 6
                opp_lineup = opp_lineup[1:] + [opp_lineup[0]]

        if marker == 'equal':
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
        our_lineups.append(our_lineup)
        opp_lineups.append(opp_lineup)
        last_serve_by_us.append(rally_begin_with_our_serve)
        last_set_by_us.append(last_single_set_by_us)
    
    # Add the new columns to the DataFrame
    df["Last Set By Us"] = last_set_by_us
    df['Team_Points'] = team_scores
    df['Opponent_Points'] = opponent_scores
    df['Team_Sets'] = team_set_wins
    df['Opponent_Sets'] = opponent_set_wins
    df["Current Set"] = current_sets
    df["Time Readable"] = df["Timestamp"].map(lambda x: f"{int(x // (1000 * 60)):02} : {(int(x // 1000) % 60):02}")
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


class Viewer:
    skip_after_code = {
        "w" : 9000,
        "W" : 9000
    }
    keys_deactivated = False
    def sort_markers(self):
        self.markers.sort(key= lambda x: x[1])

    def __init__(self, settings_file: str):
        self.settings = Settings(settings_file)
        self.root = tk.Tk()
        self.root.title("Viewer")

        self.time_label = tk.Label(self.root, text="Current Time: 00:00:00; Speed: 1.00x", font=("Helvetica", 16))
        self.time_label.pack(pady=10)



        # Setup the treeview
        self.tree = ttk.Treeview(self.root, columns=("#", "Type", "Time", "Stand", "Our Rotation", "Opp Rotation", "Del"), show="headings")
        self.tree.heading("#", text="#")
        self.tree.column("#", width="100")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Time", text="Time")
        self.tree.column("Time", width="100")
        self.tree.heading("Stand", text="Stand")
        self.tree.heading("Our Rotation", text="Our Rot")
        self.tree.column("Our Rotation", width=100)
        self.tree.heading("Opp Rotation", text="Opp Rot")
        self.tree.column("Opp Rotation", width=100)
        self.tree.heading("Del", text="Delete")
        self.tree.column("Del", width="100")
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", self.on_row_click)
        self.tree.tag_configure("New Set", background="red")
        self.tree.tag_configure("b", background="lightgrey")
        self.tree.tag_configure("l", background="lightblue")
        self.tree.tag_configure("z", background="lightblue")
        self.tree.tag_configure("p", background="lightblue")


        # Sample data: list of pairs
        self.markers = []
        if os.path.isfile(self.settings.project_folder + "/" + self.settings.markers_file):
            with open(self.settings.project_folder + "/" + self.settings.markers_file, newline='') as csvfile:
                # Create a CSV reader object
                reader = csv.reader(csvfile)
                
                # Iterate through the rows of the CSV
                for row in reader:
                    # Append the pair (tuple) to the list
                    self.markers.append((row[0], float(row[1])))

        self.sort_markers()
        
        self.player = vlc.MediaPlayer(self.settings.project_folder + "/" + self.settings.input_video)
        self.player.play()
        if len(self.markers) > 0:
            self.player.set_time(int(self.markers[-1][1]))


        # Insert the data into the treeview
        self.show_markers()

        # Bind keyboard events
        self.root.bind("<Key>", self.on_key_press)

        self.update_time()
        self.root.mainloop()

    def update_time(self):
        # Get the current time from the player
        current_time_seconds = self.player.get_time() // 1000
        hours = (current_time_seconds // 3600) % 24
        minutes = (current_time_seconds % 3600) // 60
        seconds = current_time_seconds % 60

        # Format time as hh:mm:ss
        formatted_time = f"{hours:02}:{minutes:02}:{seconds:02}"

        # Update the label
        try:
            stand = (self.tree.item(self.tree.get_children(self.tree.get_children()[-1])[-1])["values"][3])
        except:
            stand = "0:0"

        self.time_label.config(text=f"Current Time: {formatted_time}; Speed: {self.player.get_rate():02}; Stand: {stand}")

        # Schedule the next update
        self.root.after(1000, self.update_time)  # Update every second
    
    def on_row_click(self, event):
        marker_id = self.tree.item(self.tree.identify_row(event.y), "values")[0]
        column_id = self.tree.column(self.tree.identify_column(event.x))["id"]
        if column_id == "Del":
            del self.markers[int(marker_id)]
            self.show_markers()
            return
        self.player.set_time(int(self.markers[int(marker_id)][1]) - 1000)


    def show_markers(self):
        for child in self.tree.get_children():
            self.tree.delete(child)
        self.sort_markers()
        current_set = ""
        markers_dict = get_dict(self.markers)
        for idx, row in markers_dict.iterrows():
            if row["Marker"] == "equal":
                current_set = row["Team_Sets"] + row["Opponent_Sets"]
                self.tree.insert("", "end", iid=str(row["Current Set"]), values=(
                    idx,
                    f"Set {row['Current Set']}",
                    row["Time Readable"],
                    "0:0",
                    "",
                    "",
                    "Delete"),
                    tags=["New Set"])
                continue
            self.tree.insert(str(current_set), "end", values=(
                idx,
                row["Code Readable"],
                row["Time Readable"],
                f"{row['Team_Points']:2}:{row['Opponent_Points']:2} ({row['Team_Sets']:2}:{row['Opponent_Sets']:2})",
                row["Our Rotation"],
                row["Opponent Rotation"],
                "Delete"
                ),
                tags=row["Tags"]
            )
        for item in self.tree.get_children():
            self.tree.item(item, open=True)
        self.tree.selection_set(self.tree.get_children()[-1])

    
    def toggle_pause(self):
        if self.player.is_playing():
            self.player.pause()
        else:
            self.player.play()
    
    def player_skip(self, time_in_ms):
        self.player.set_time(self.player.get_time() + time_in_ms)

    def add_marker(self, keysym):
        current_time = self.player.get_time()
        self.markers.append((keysym, current_time))
        self.show_markers()
        if keysym in self.skip_after_code:
            self.player_skip(self.skip_after_code[keysym])
        

    def player_change_speed(self, speed):
        self.player.set_rate(self.player.get_rate() + speed)

    def on_key_press(self, event):
        if self.keys_deactivated:
            return
        if event.keysym in ("Shift_L", "Super_L", "Return", "Control_R"):
            return
        if event.keysym == "space":
            self.toggle_pause()
            return
        if event.keysym == "Escape":
            self.quit_program()
            return
        if event.keysym == "Right":
            self.player_skip(3000)
            return
        if event.keysym == "Left":
            self.player_skip(-3000)
            return  
        if event.keysym == "Up":
            self.player_change_speed(0.05)
            return
        if event.keysym == "Down":
            self.player_change_speed(-0.00)
            return      
        if event.keysym == "BackSpace":
            del self.markers[-1]
            self.show_markers()
            return
        if event.keysym == "plus":
            self.player_change_speed(0.05)
            return
        if event.keysym == "minus":
            self.player_change_speed(-0.05)
            return
        if event.keysym in ("z", "Z", "l", "L", "p", "P"):
            self.keys_deactivated = True
            entry = tk.Entry(self.root)
            entry.insert(0, event.keysym)
            def save_edit(event):
                new_value = entry.get()  # Get the new value
                self.add_marker(new_value)
                entry.destroy()  # Destroy the entry widget
                self.keys_deactivated = False
                
                
            entry.bind("<Return>", save_edit)  # Bind Enter key to save the edit
            entry.pack()
            entry.focus_set()  # Set focus on the entry widget
            return
        self.add_marker(event.keysym)

    def quit_program(self):
        self.save_markers_to_csv()
        self.root.quit()
    
    def save_markers_to_csv(self):
        with open(self.settings.project_folder + "/" + self.settings.markers_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(self.markers)

if __name__ == "__main__":
    viewer = Viewer(sys.argv[1])