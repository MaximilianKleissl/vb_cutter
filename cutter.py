import sys

from moviepy.editor import VideoFileClip, concatenate_videoclips, vfx
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import csv

from settings import Settings
import analyzer

print(sys.argv[1])
settings = Settings(sys.argv[1])

# Datei mit den Markern einlesen
markers = []
with open(f"{settings.project_folder}/{settings.markers_file}", "r") as file:
    reader = csv.reader(file)
    markers.extend((row[0], float(row[1])) for row in reader)
print(len(markers))

# Video laden
video = VideoFileClip(f"{settings.project_folder}/{settings.input_video}")

## RECEIVES
if settings.receives:
    highlights = []
    for marker, time in markers:
        time = time / 1000
        if marker == "B":
            start_time = max(time, 0)  # 10 Sekunden vor dem Highlight, aber nicht vor 0
            end_time = time + 4  # 3 Sekunden nach dem Highlight
            highlights.append((start_time, end_time))

    if highlights:
        highlight_clips = [video.subclip(start, end) for start, end in highlights]
        highlight_video = concatenate_videoclips(highlight_clips)
        highlight_video.write_videofile(
            f"{settings.output_folder}/receives_video.mp4", preset=settings.preset
        )

# Variante 1: Highlight Video erstellen
if settings.highlights:
    highlights = []
    for marker, time in markers:
        if marker in ("H", "h"):
            time = time / 1000
            start_time = max(
                time - settings.time_before_highlight, 0
            )  # 10 Sekunden vor dem Highlight, aber nicht vor 0
            end_time = (
                time + settings.time_after_highlight
            )  # 3 Sekunden nach dem Highlight
            highlights.append((start_time, end_time))

    if highlights:
        highlight_clips = [video.subclip(start, end) for start, end in highlights]
        highlight_video = concatenate_videoclips(highlight_clips)
        highlight_video.write_videofile(
            f"{settings.output_folder}/highlight_video.mp4", preset=settings.preset
        )

# Variante 2: Nasenbluten Video erstellen
if settings.nasenbluten:
    highlights = []
    for marker, time in markers:
        if marker in ("N", "n"):
            time = time / 1000
            start_time = max(
                time - settings.time_before_nasenbluten, 0
            )  # 10 Sekunden vor dem Highlight, aber nicht vor 0
            end_time = (
                time + settings.time_after_nasenbluten
            )  # 3 Sekunden nach dem Highlight
            highlights.append((start_time, end_time))

    if highlights:
        highlight_clips = [video.subclip(start, end) for start, end in highlights]
        highlight_video = concatenate_videoclips(highlight_clips)
        highlight_video.write_videofile(
            f"{settings.output_folder}/nasenbluten_video.mp4", preset=settings.preset
        )
else:
    print("Skip Nasenbluten")

# Variante 3: Angriffs Video erstellen
df = analyzer.get_dict(markers)
attacks_df = df[df["Last Set By Us"] == True]
attacks_df = attacks_df[attacks_df["Marker"].isin(["1", "2", "3", "4", "5", "6", "f"])]
if settings.attacks:
    for player in attacks_df["Player"].unique():
        attacks_df_player = attacks_df[attacks_df["Player"] == player]
        for position in [1, 2, 3, 4, 5, 6, "f"]:
            attacks_df_player_position = attacks_df_player[
                attacks_df_player["Marker"].astype(str) == str(position)
            ]
            print(f"\n\n\nAtacks by {player} at {position}")
            print(attacks_df_player_position)
            highlights = []
            for idx, row in attacks_df_player_position.iterrows():
                time = row["Timestamp"] / 1000
                start_time = max(time - 2.5, 0)
                end_time = time + 1.5
                highlights.append((start_time, end_time))

            if highlights:
                highlight_clips = [
                    video.subclip(start, end) for start, end in highlights
                ]
                highlight_video = concatenate_videoclips(highlight_clips)
                highlight_video.write_videofile(
                    f"{settings.output_folder}/attack_at_{position}_by_{player}.mp4",
                    preset=settings.preset,
                )

# Variante 3: Service Video erstellen
df = analyzer.get_dict(markers)
df = df[df["Marker"] == "b"]
if settings.services:
    for player in df["Player"].unique():
        df_player = df[df["Player"] == player]
        highlights = []
        for idx, row in df_player.iterrows():
            time = row["Timestamp"] / 1000
            start_time = max(time - 3, 0)
            end_time = time + 3
            highlights.append((start_time, end_time))

        if highlights:
            highlight_clips = [video.subclip(start, end) for start, end in highlights]
            highlight_video = concatenate_videoclips(highlight_clips)
            highlight_video.write_videofile(
                f"{settings.output_folder}/services_by_{player}.mp4",
                preset=settings.preset,
            )

# Variante 4: Z Video erstellen
if settings.setter:
    highlights = []
    for marker, time in markers:
        time = time / 1000
        if marker == "s":
            start_time = max(
                time - settings.time_before_setting, 0
            )  # 10 Sekunden vor dem Highlight, aber nicht vor 0
            end_time = (
                time + settings.time_after_setting
            )  # 3 Sekunden nach dem Highlight
            highlights.append((start_time, time, end_time))
    if highlights:
        highlight_clips = [
            [
                video.subclip(start, t),
                video.subclip(t, t).to_ImageClip(duration=settings.time_during_setting),
                video.subclip(t, end),
            ]
            for start, t, end in highlights
        ]

        highlight_clips = [item for sublist in highlight_clips for item in sublist]

        highlight_video = concatenate_videoclips(highlight_clips)
        highlight_video.without_audio().write_videofile(
            f"{settings.output_folder}/read_own_setter_video.mp4",
            preset=settings.preset,
            fps=24,
        )

# # Variante 4: Z Video erstellen
if settings.setter:
    highlights = []
    for marker, time in markers:
        time = time / 1000
        if marker == "S":
            start_time = max(
                time - settings.time_before_setting, 0
            )  # 10 Sekunden vor dem Highlight, aber nicht vor 0
            end_time = (
                time + settings.time_after_setting
            )  # 3 Sekunden nach dem Highlight
            highlights.append((start_time, time, end_time))
    if highlights:
        highlight_clips = [
            [
                video.subclip(start, t),
                video.subclip(t, t).to_ImageClip(duration=settings.time_during_setting),
                video.subclip(t, end),
            ]
            for start, t, end in highlights
        ]

        highlight_clips = [item for sublist in highlight_clips for item in sublist]

        highlight_video = concatenate_videoclips(highlight_clips)
        highlight_video.without_audio().write_videofile(
            f"{settings.output_folder}/read_foreign_setter_video.mp4",
            preset=settings.preset,
            fps=24,
        )

# False# 2: Alle Ballwechsel Videos erstellen
if settings.rallys:
    ballwechsel_clips = []
    start_time = None
    for marker, time in markers:
        time = time / 1000
        if marker in ("b", "B"):
            start_time = max(time - settings.time_before_rally, 0)
        elif marker in ["w", "W"] and start_time is not None:
            end_time = time + settings.time_after_setting
            ballwechsel_clips.append(video.subclip(start_time, end_time))

    # Zusammenfügen der Ballwechsel Videos
    ballwechsel_video = concatenate_videoclips(ballwechsel_clips)
    ballwechsel_video.write_videofile(
        "{settings.output_folder}/ballwechsel_video.mp4", preset=settings.preset
    )
