import sys
import csv
import time
import tkinter as tk

from moviepy.editor import VideoFileClip, concatenate_videoclips
from tkinter import ttk, messagebox
import vlc


import analyzer
from settings import Settings


class CutterEditor:
    def __init__(self, master, settings):
        self.master = master
        self.master.title("Highlight Video Editor")
        self.settings = settings
        self.clips = []
        self.load_markers()
        self.video_path = self.settings.project_folder + "/" + self.settings.input_video
        self.player = vlc.MediaPlayer(self.video_path)

        self.create_widgets()

    def create_widgets(self):
        # Create filter options
        self.filter_column_1 = ttk.Combobox(
            self.master, values=list(self.marker_df.columns)
        )
        self.filter_column_1.set("Select Column")
        self.filter_column_1.pack()

        self.filter_value_1 = tk.Entry(self.master)
        self.filter_value_1.pack()

        self.filter_column_2 = ttk.Combobox(
            self.master, values=list(self.marker_df.columns)
        )
        self.filter_column_2.set("Select Column")
        self.filter_column_2.pack()

        self.filter_value_2 = tk.Entry(self.master)
        self.filter_value_2.pack()

        self.filter_column_3 = ttk.Combobox(
            self.master, values=list(self.marker_df.columns)
        )
        self.filter_column_3.set("Select Column")
        self.filter_column_3.pack()

        self.filter_value_3 = tk.Entry(self.master)
        self.filter_value_3.pack()

        self.load_button = tk.Button(self.master, text="Load", command=self.load)
        self.load_button.pack()
        self.tree = ttk.Treeview(
            self.master, columns=("Marker", "Time", "Start", "End"), show="headings"
        )
        self.tree.heading("Marker", text="Marker")
        self.tree.heading("Time", text="Time in ms")
        self.tree.heading("Start", text="Time Before in s")
        self.tree.heading("End", text="Time Afte in s")

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.on_double_click)

        self.save_button = tk.Button(
            self.master, text="Save Highlight Video", command=self.save_highlight_video
        )
        self.save_button.pack(pady=10)

    def on_double_click(self, event):
        column = self.tree.identify_column(
            event.x
        )  # Get the column that was double-clicked
        item = self.tree.identify_row(event.y)  # Get the row that was double-clicked
        if not item:
            return
        print(column)
        if int(column[1:]) < 3:
            start = float(self.tree.item(item, "values")[2]) * 1000
            mid = float(self.tree.item(item, "values")[1])
            end = float(self.tree.item(item, "values")[3]) * 1000
            print(start, mid, end)
            start_time = max(int(mid - start), 0)
            self.player.play()
            print(self.player.get_time(), start_time)
            self.player.set_time(start_time)
            print(self.player.get_time())
            while self.player.get_time() < mid + end:
                time.sleep(0.1)  # Check every 0.1 seconds
            self.player.stop()
            return

        x, y, width, height = self.tree.bbox(
            item, column
        )  # Get bounding box of the cell
        value = self.tree.item(item, "values")[
            int(column[1:]) - 1
        ]  # Get current cell value

        entry = tk.Entry(self.master)
        entry.place(x=x, y=y, width=width, height=height)
        # entry.insert(0, value)  # Insert the current value into the entry widget

        def save_edit(event):
            new_value = entry.get()  # Get the new value
            values = list(self.tree.item(item, "values"))
            values[int(column[1:]) - 1] = new_value  # Update the value in the list
            self.tree.item(
                item, values=values
            )  # Update the treeview with the new values
            entry.destroy()  # Destroy the entry widget

        entry.bind("<Return>", save_edit)  # Bind Enter key to save the edit
        entry.focus_set()  # Set focus on the entry widget

    def load(self):
        for child in self.tree.get_children():
            self.tree.delete(child)
        column_1 = self.filter_column_1.get()
        value_1 = self.filter_value_1.get()
        column_2 = self.filter_column_2.get()
        value_2 = self.filter_value_2.get()
        column_3 = self.filter_column_3.get()
        value_3 = self.filter_value_3.get()
        print(column_1)
        if column_1 != "Select Column":
            self.filtered_df = self.marker_df[
                self.marker_df[column_1].astype(str) == value_1
            ]
        else:
            self.filtered_df = self.marker_df
        if column_2 != "Select Column":
            self.filtered_df = self.filtered_df[
                self.filtered_df[column_2].astype(str) == value_2
            ]
        if column_3 != "Select Column":
            self.filtered_df = self.filtered_df[
                self.filtered_df[column_3].astype(str) == value_3
            ]

        for i, row in self.filtered_df.iterrows():
            self.tree.insert(
                "", "end", iid=str(i), values=(row["Marker"], row["Timestamp"], 3, 3)
            )

    def save_highlight_video(self):
        video = VideoFileClip(self.video_path)
        clips = []
        for item in self.tree.get_children():
            marker, t, start, end = self.tree.item(item)["values"]
            start = float(t) / 1000 - float(start)
            end = float(t) / 1000 + float(end)
            print((start, end))
            clips.append(video.subclip(start, end))
        print(clips)
        if clips:
            highlight_video = concatenate_videoclips(clips)
            output_path = (
                f"highlight_video_{self.marker_input.get("1.0", "end-1c")}.mp4"
            )
            highlight_video.write_videofile(
                self.settings.project_folder + "/" + output_path,
                preset=self.settings.preset,
            )
            messagebox.showinfo("Success", f"Highlight video saved as {output_path}")
        else:
            messagebox.showwarning("No Highlights", "No highlight clips were selected.")

    def load_markers(self):
        self.markers = []
        with open(
            self.settings.project_folder + "/" + self.settings.markers_file, "r"
        ) as file:
            reader = csv.reader(file)
            for row in reader:
                self.markers.append((row[0], float(row[1])))
        self.marker_df = analyzer.get_dict(self.markers)


if __name__ == "__main__":
    settings = Settings(sys.argv[1])

    root = tk.Tk()
    app = CutterEditor(root, settings)
    root.mainloop()
