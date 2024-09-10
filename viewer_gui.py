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

class Viewer:

    codes_translator: dict = {
        "b" : "Ballwechsel beginnt",
        "p" : "Pipe",
        "P" : "Pipe",
        "s" : "Zuspiel",
        "S" : "Zuspiel",
        "w" : "Wir gewinnen Ballwechsel",
        "W" : "Gegner gewinnt Ballwechsel",
        "h" : "Highlight",
        "H" : "Gegner hat Highlight",
        "n" : "Nasenbluten",
        "N" : "Gegner hat Nasenbluten",
        "a" : "Angriff",
        "A" : "Gegner greift an",
        "1" : "Angriff über 1",
        "2" : "Angriff über 2",
        "3" : "Angriff über 3",
        "4" : "Angriff über 4",
        "5" : "Angriff über 5",
        "6" : "Angriff über 6"
    } 

    skip_after_code = {
        "w" : 9000,
        "W" : 9000
    }
    def sort_markers(self):
        self.markers.sort(key= lambda x: x[1])

    def __init__(self, settings_file: str):
        self.settings = Settings(settings_file)
        self.root = tk.Tk()
        self.root.title("Viewer")

        self.time_label = tk.Label(self.root, text="Current Time: 00:00:00; Speed: 1.00x", font=("Helvetica", 16))
        self.time_label.pack(pady=10)



        # Setup the treeview
        self.tree = ttk.Treeview(self.root, columns=("Number", "Type", "Time", "Stand", "Delete"), show="headings")
        self.tree.heading("Number", text="#")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Time", text="Time (mm:ss)")
        self.tree.heading("Stand", text="Stand")
        self.tree.heading("Delete", text="Delete")
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", self.on_row_click)
        self.tree.tag_configure("even_rally", background="white")
        self.tree.tag_configure("odd_rally", background="lightgrey")

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
        
        self.player = vlc.MediaPlayer(self.settings.project_folder + "/" + self.settings.input_file)
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
        stand = (self.tree.item(self.tree.get_children(self.tree.get_children()[-1])[-1])["values"][3])
        self.time_label.config(text=f"Current Time: {formatted_time}; Speed: {self.player.get_rate():02}; Stand: {stand}")

        # Schedule the next update
        self.root.after(1000, self.update_time)  # Update every second
    
    def on_row_click(self, event):
        marker_id = self.tree.item(self.tree.identify_row(event.y), "values")[0]
        column_id = self.tree.column(self.tree.identify_column(event.x))["id"]
        if column_id == "Delete":
            print("delete ", marker_id)
            del self.markers[int(marker_id)]
            self.show_markers()
            return
        self.player.set_time(int(self.markers[int(marker_id)][1]) - 1000)


    def show_markers(self):
        for child in self.tree.get_children():
            self.tree.delete(child)
        self.sort_markers()
        current_set = 0
        points_home = 0
        sets_home = 0
        points_away = 0
        sets_away = 0
        for idx, pair in enumerate(self.markers):
            if pair[0] == "equal":
                current_set += 1
                self.tree.insert("", "end", iid=str(current_set), values=(
                    idx,
                    f"Set {current_set}",
                    f"{int(pair[1] // (1000 * 60)):02} : {(int(pair[1] // 1000) % 60):02}",
                    "0:0",
                    "Delete"))
                points_home = 0
                points_away = 0
                continue
            self.tree.insert(str(current_set), "end", values=(
                idx,
                self.codes_translator[pair[0]] if pair[0] in self.codes_translator else pair[0],
                f"{int(pair[1] // (1000 * 60)):02} : {(int(pair[1] // 1000) % 60):02}",
                f"{points_home}:{points_away}",
                "Delete"
                ),
                tags=("even_rally" if (points_home + points_away) % 2 else "odd_rally")
            )
            if pair[0] == "w":
                points_home += 1
            if pair[0] == "W":
                points_away += 1
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
        if event.keysym in ("Shift_L", "Super_L"):
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