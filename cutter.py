import sys

from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip, concatenate_videoclips, vfx
import csv

from settings import Settings
from stats import Stats

print(sys.argv[1])
settings = Settings(sys.argv[1])

# Datei mit den Markern einlesen
markers = []
with open(settings.project_folder + "/" + settings.markers_file, 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        markers.append((row[0], float(row[1])))  # Annahme: Format ist [Marker, Zeit in Sekunden]

print(len(markers))

# Video laden
video = VideoFileClip(settings.project_folder + "/" + settings.input_video)

# stats = Stats(markers)
# print("Stats: ")
# print(f"Number of Rallys: {len([m for m in markers if m[0] == 'B'])}")
# print(f"Number of Points for us: {len([m for m in markers if m[0] == 'W'])}")
# print(f"Number of Points for Opponent: {len([m for m in markers if m[0] == 'G'])}")
# print(f"Number of Pipes: {len([m for m in markers if m[0] == 'P'])}")


# Variante 1: Highlight Video erstellen
if settings.highlights:
    highlights = []
    for marker, time in markers:
        if marker == 'H':
            start_time = max(time - settings.time_before_highlight, 0)  # 10 Sekunden vor dem Highlight, aber nicht vor 0
            end_time = time + settings.time_after_highlight             # 3 Sekunden nach dem Highlight
            highlights.append((start_time, end_time))

    if len(highlights) > 0:
        highlight_clips = [video.subclip(start, end) for start, end in highlights]
        highlight_video = concatenate_videoclips(highlight_clips)
        highlight_video.write_videofile(
            "highlight_video.mp4",
            preset=settings.preset
        )   

# Variante 2: Nasenbluten Video erstellen
if settings.nasenbluten:
    highlights = []
    for marker, time in markers:
        if marker == 'N':
            start_time = max(time - settings.time_before_nasenbluten, 0)  # 10 Sekunden vor dem Highlight, aber nicht vor 0
            end_time = time + settings.time_after_nasenbluten             # 3 Sekunden nach dem Highlight
            highlights.append((start_time, end_time))

    if len(highlights) > 0:
        highlight_clips = [video.subclip(start, end) for start, end in highlights]
        highlight_video = concatenate_videoclips(highlight_clips)
        highlight_video.write_videofile(
            "nasenbluten_video.mp4",
            preset=settings.preset
        )

# Variante 3: Angriffs Video erstellen
if settings.attacks:
    for position in [1,2,3,4,5,6, "O"]:
        highlights = []
        for marker, time in markers:
            time = time/1000
            if marker == str(position):
                start_time = max(time - 5, 0)
                end_time = time + 3
                highlights.append((start_time, end_time))

        if len(highlights) > 0:
            print(highlights)
            highlight_clips = [video.subclip(start, end) for start, end in highlights]
            highlight_video = concatenate_videoclips(highlight_clips)
            highlight_video.write_videofile(
                f"{settings.project_folder}/attack_{position}.mp4",
                preset=settings.preset
            )

# Variante 4: Z Video erstellen
if settings.setter:
    highlights = []
    for marker, time in markers:
        time = time/1000
        if marker == 's':
            start_time = max(time - settings.time_before_setting, 0)   # 10 Sekunden vor dem Highlight, aber nicht vor 0
            end_time = time + settings.time_after_setting             # 3 Sekunden nach dem Highlight
            highlights.append((start_time, time, end_time))
    if len(highlights) > 0:
        highlight_clips = [
            [
                video.subclip(start, t),
                video.subclip(t, t).to_ImageClip(duration=settings.time_during_setting),
                video.subclip(t, end)

            ] for start, t, end in highlights]

        highlight_clips = [item for sublist in highlight_clips for item in sublist]
   

        highlight_video = concatenate_videoclips(highlight_clips)
        highlight_video.without_audio().write_videofile(
            settings.project_folder + "/read_own_setter_video.mp4",
            preset=settings.preset,
            fps=24,
            )

# # Variante 4: Z Video erstellen
if settings.setter:
    highlights = []
    for marker, time in markers:
        time = time/1000
        if marker == 'S':
            start_time = max(time - settings.time_before_setting, 0)   # 10 Sekunden vor dem Highlight, aber nicht vor 0
            end_time = time + settings.time_after_setting             # 3 Sekunden nach dem Highlight
            highlights.append((start_time, time, end_time))
    if len(highlights) > 0:
        highlight_clips = [
            [
                video.subclip(start, t),
                video.subclip(t, t).to_ImageClip(duration=settings.time_during_setting),
                video.subclip(t, end)

            ] for start, t, end in highlights]

        highlight_clips = [item for sublist in highlight_clips for item in sublist]
   

        highlight_video = concatenate_videoclips(highlight_clips)
        highlight_video.without_audio().write_videofile(
            settings.project_folder + "/read_foreign_setter_video.mp4",
            preset=settings.preset,
            fps=24,
            )

# False# 2: Alle Ballwechsel Videos erstellen
if settings.rallys:
    ballwechsel_clips = []
    start_time = None
    for marker, time in markers:
        time = time/1000
        if marker == 'b':
            start_time = max(time - settings.time_before_rally, 0)
        elif marker in ['w', 'W'] and start_time is not None:
            end_time = time + settings.time_after_setting
            ballwechsel_clips.append(video.subclip(start_time, end_time))

# Zusammenfügen der Ballwechsel Videos
    ballwechsel_video = concatenate_videoclips(ballwechsel_clips)
    ballwechsel_video.write_videofile(self.settings.project_folder + "/ballwechsel_video.mp4",            
        preset=settings.preset
    )

