# VB Cutter
## Usage

1. Create a project folder
2. Copy the video into the folder
3. Copy the `default.toml` into the folder and adapt project folder and input_video
4. Adapt other parameters in the `toml` if needed.
5. View the video (`python viewer_gui.py [toml file]`) and input the codes. See for the codes and control keys down below.
6. Run `python cutter.py [toml file]` to generate attack videos, rally videos and setter videos.
7. Run `python highlight_cutter.py [toml file]` to generate Highlights, Nasenbluten and other videos. Enter the codes you want to see in the textbox (default `Hh`) and load markers. Edit time before and time after by double-clicking on the cells. Double click on on the left side of the row to see the clip. Generate the video by using the button down below. 

## Codes

| Key | Decscription|
|----------------|---------|
| b | Rally beginns (Own service) |
| B | Rally beginns (Foreign team service)|
| w | Point (Own team wins a point) |
| W | Point (Foreign team wins a point)|
| S | Set (Own setter sets) |
| S | Set (Foreign setter sets)|
| n | Nasenbluten (Own team has Nasenbluten) |
| N | Point (Foreign team has Nasenbluten)|
| h | Point (Own team has a Highlight) |
| H | Point (Foreign team has a Highlight)|
| o | Out of System attack (Own team) |
| O | Out of System attack (Foreign team)|
| 1 | Attack at pos 1 |
| 2 | Attack at pos 2 |
| 3 | Attack at pos 3 |
| 4 | Attack at pos 4 |
| 5 | Attack at pos 5 |
| 6 | Attack at pos 6 |



## Control keys
| Key | Decscription|
|----------------|---------|
| Up | 0.05% faster |
| Down | 0.05% slower |
| Left | Go 3s back |
| Right | Skip 3s |
| Space | Pause |
| Delete | Delete last marker |