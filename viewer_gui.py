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
import analyzer


class Viewer:
    skip_after_code = {"w": 0, "W": 0}  # ,9000,  # 9000
    count_changes = 0
    keys_deactivated = False

    def sort_markers(self):
        self.markers.sort(key=lambda x: x[1])

    def __init__(self, settings_file: str):
        self.settings = Settings(settings_file)
        self.root = tk.Tk()
        self.root.title("Viewer")

        self.time_label = tk.Label(
            self.root,
            text="Current Time: 00:00:00; Speed: 1.00x",
            font=("Helvetica", 16),
        )
        self.time_label.pack(pady=10)

        # Setup the treeview
        self.tree = ttk.Treeview(
            self.root,
            columns=(
                "#",
                "Type",
                "Time",
                "Stand",
                "Our Rotation",
                "Opp Rotation",
                "Del",
            ),
            show="headings",
        )
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
        if os.path.isfile(
            self.settings.project_folder + "/" + self.settings.markers_file
        ):
            with open(
                self.settings.project_folder + "/" + self.settings.markers_file,
                newline="",
            ) as csvfile:
                # Create a CSV reader object
                reader = csv.reader(csvfile)

                # Iterate through the rows of the CSV
                for row in reader:
                    # Append the pair (tuple) to the list
                    self.markers.append((row[0], float(row[1])))

        self.sort_markers()
        self.save_markers_to_csv()

        self.player = vlc.MediaPlayer(
            self.settings.project_folder + "/" + self.settings.input_video
        )
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
        if self.player.get_time() + 3000 > self.player.get_length():
            self.player.set_time(0)
        current_time_seconds = self.player.get_time() // 1000
        hours = (current_time_seconds // 3600) % 24
        minutes = (current_time_seconds % 3600) // 60
        seconds = current_time_seconds % 60

        # Format time as hh:mm:ss
        formatted_time = f"{hours:02}:{minutes:02}:{seconds:02}"

        # Update the label
        try:
            stand = self.tree.item(
                self.tree.get_children(self.tree.get_children()[-1])[-1]
            )["values"][3]
        except:
            stand = "0:0"

        self.time_label.config(
            text=f"Current Time: {formatted_time}; Speed: {self.player.get_rate():02}; Stand: {stand}"
        )

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
        markers_dict = analyzer.get_dict(self.markers)
        for idx, row in markers_dict.iterrows():
            if row["Marker"] == "equal":
                current_set = row["Team_Sets"] + row["Opponent_Sets"]
                self.tree.insert(
                    "",
                    "end",
                    iid=str(row["Current Set"]),
                    values=(
                        idx,
                        f"Set {row['Current Set']}",
                        row["Time Readable"],
                        "0:0",
                        "",
                        "",
                        "Delete",
                    ),
                    tags=["New Set"],
                )
                continue
            self.tree.insert(
                str(current_set),
                "end",
                values=(
                    idx,
                    row["Code Readable"],
                    row["Time Readable"],
                    f"{row['Team_Points']:2}:{row['Opponent_Points']:2} ({row['Team_Sets']:2}:{row['Opponent_Sets']:2})",
                    row["Our Rotation"],
                    row["Opponent Rotation"],
                    "Delete",
                ),
                tags=row["Tags"],
            )
        for item in self.tree.get_children():
            self.tree.item(item, open=True)
        if len(self.tree.get_children()) > 0:
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
        if self.count_changes > 9:
            self.save_markers_to_csv()
            self.count_changes = 0

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
        with open(
            self.settings.project_folder + "/" + self.settings.markers_file,
            "w",
            newline="",
        ) as file:
            writer = csv.writer(file)
            writer.writerows(self.markers)


if __name__ == "__main__":
    viewer = Viewer(sys.argv[1])
