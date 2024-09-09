import pprint
import os
import vlc
import csv
import curses
import time

class ViewerSettings:
    skip_after_rally_stops: int = 5000

# Global variables to control markers
markers = []
is_paused = False
CURSES_SPACE = 32
viewer_settings = ViewerSettings()
k = 0

def delete_last_marker():
    global markers
    markers = markers[:-1]
    print(markers)

def print_markers(stdscr):
    stdscr.clear()
    pw = 0
    pg = 0
    for marker in markers[-50:]:
        stdscr.addstr(f"{marker[0]} | {marker[1]} \n")
        if marker[0] == "W":
            pw += 1
        if marker[0] == "G":
            pg += 1
    stdscr.addstr(f"{pw} : {pg}")


# Function to add a marker
def save_marker(marker_type: str, player: vlc.MediaPlayer, stdscr):
    global k
    current_time = player.get_time() / 1000  # Time in seconds
    markers.append((marker_type, current_time))
    print(f"Marker {marker_type} set at {current_time:.2f} seconds")
    if marker_type.lower() in ("w", "g"):
        player.set_time(player.get_time() + viewer_settings.skip_after_rally_stops)
    print_markers(stdscr)
    k += 1
    if k > 10:
        save_markers_to_csv()
        k = 0

# Function to save markers to a CSV file
def save_markers_to_csv(filename="markers.csv"):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(markers)
    print(f"Markers saved to {filename}.")

# Function to toggle pause and play
def toggle_pause(player, stdscr):
    global is_paused
    if player.is_playing():
        player.pause()
        is_paused = True
    else:
        player.play()
        is_paused = False

# Function to quit the program
def quit_program(player, stdscr):
    player.stop()
    markers.sort(key=lambda x: x[1])
    save_markers_to_csv()
    print("Program ended. Markers saved.")
    curses.endwin()
    exit(0)

def player_skip(player, time_in_ms):
    player.set_time(player.get_time() + time_in_ms)

def player_change_speed(player, speed):
    player.set_rate(player.get_rate() + speed)
    print(f"Changed Speed to {player.get_rate()}")

# Main function to play video with VLC and handle keyboard input using curses
def play_video_with_markers(stdscr):
    global is_paused

    # Set up VLC player
    video_path = "input_video.mp4"  # Specify your video path here
    if os.path.isfile("markers.csv"):
        with open('markers.csv', newline='') as csvfile:
            # Create a CSV reader object
            reader = csv.reader(csvfile)
            
            # Iterate through the rows of the CSV
            for row in reader:
                # Append the pair (tuple) to the list
                markers.append((row[0], float(row[1])))

    player = vlc.MediaPlayer(video_path)
    player.play()
    player.set_time(int(markers[-1][1] * 1000))
    time.sleep(1)  # Short pause to ensure the player starts

    # Clear screen and set up curses
    stdscr.clear()
    stdscr.addstr("Video Marker Tool\n")
    stdscr.addstr("Press 'b' for Ballwechsel begins\n")
    stdscr.addstr("Press 'g' for Gegner point\n")
    stdscr.addstr("Press 'w' for our point\n")
    stdscr.addstr("Press 'h' for highlight\n")
    stdscr.addstr(f"Press 'p' ({ord('p')}) to pipe\n")
    stdscr.addstr("Press 't' to timeout\n")
    stdscr.addstr("Press 'z' if other setter has the ball\n")
    stdscr.addstr("Press 's' to show current markers\n")
    stdscr.addstr("Press 'q' to quit\n")

    while True:
        ch = stdscr.getch()  # Get user input
        if ch == ord('b'):  # Ballwechsel beginnt
            save_marker('B', player, stdscr)
        elif ch == ord('g'):  # Gegner Punkt
            save_marker('G', player, stdscr)
        elif ch == ord('w'):  # Unser Punkt
            save_marker('W', player, stdscr)
        elif ch == ord('h'):  # Highlight
            save_marker('H', player, stdscr)
        elif ch == 32:  # Pause/Resume
            toggle_pause(player, stdscr)
        elif ch == curses.KEY_BACKSPACE:
            delete_last_marker()
        elif ch == ord('q'):  # Quit 32 is SPACE
            quit_program(player, stdscr)
        elif ch == ord("z"): # Gegnerischer Z hat Ball in der Hand
            save_marker("Z", player, stdscr)
        elif ch == ord("p"): #Wir spielen Pipe
            save_marker("P", player, stdscr)
        elif ch == ord("s"):
            print_markers(stdscr)
        elif ch == ord("t"): # set time
            player.pause()
            player.is_playing = False
            player.set_time(goto_time)
        elif ch == curses.KEY_LEFT:
            player_skip(player, -3000)
        elif ch == curses.KEY_RIGHT:
            player_skip(player, 3000)
        elif ch == curses.KEY_UP:
            player_change_speed(player, 0.05)
        elif ch == curses.KEY_DOWN:
            player_change_speed(player, -0.05)
        elif ch == ord("n"):
            save_marker("N", player, stdscr)
        else:
            stdscr.addstr(f"Invalid key: {ch}.\n")
            stdscr.refresh()


# Initialize curses and run the main function
if __name__ == "__main__":
    curses.wrapper(play_video_with_markers)
