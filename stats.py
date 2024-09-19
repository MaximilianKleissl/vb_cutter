import sys
import csv

import pprint

import settings


class Stats:
    def __init__(self, settings_file):
        self.settings = settings.Settings(settings_file)
        self.markers = []
        with open(
            self.settings.project_folder + "/" + self.settings.markers_file, "r"
        ) as file:
            reader = csv.reader(file)
            for row in reader:
                self.markers.append((row[0], float(row[1])))
        self.validate()
        stats_dict = self.get_stats()

    def validate(self):
        rally_markers = [m[0] for m in self.markers if m[0] in ("W", "w", "B", "b")]
        assert len(rally_markers) % 2 == 0

        assert not "b" in rally_markers[1::2]
        assert not "B" in rally_markers[1::2]
        assert not "w" in rally_markers[::2]
        assert not "W" in rally_markers[::2]

    def print_stats(self):
        pprint.pprint(self.get_stats())

    def count_followed_by_win_and_lose(self, element):
        count_win = 0
        count_loose = 0
        count_actions = 0
        for i, t in self.markers:
            if i == element:
                count_actions += 1
            if i == "w":
                count_win += count_actions
                count_actions = 0
            if i == "W":
                count_loose += count_actions
                count_actions = 0
        return count_win, count_loose

    def get_stats(self):
        my_stats = {}
        my_stats["Points won"] = len([1 for m, t in self.markers if m == "w"])
        my_stats["Points loose"] = len([1 for m, t in self.markers if m == "W"])
        my_stats["Attacks over 1"] = len([1 for m, t in self.markers if m == "1"])
        my_stats["Points Won/Lost after Attack over 1"] = (
            self.count_followed_by_win_and_lose("1")
        )
        my_stats["Attacks over 2"] = len([1 for m, t in self.markers if m == "2"])
        my_stats["Points Won/Lost after Attack over 2"] = (
            self.count_followed_by_win_and_lose("2")
        )
        my_stats["Attacks over 3"] = len([1 for m, t in self.markers if m == "3"])
        my_stats["Points Won/Lost after Attack over 3"] = (
            self.count_followed_by_win_and_lose("3")
        )
        my_stats["Attacks over 4"] = len([1 for m, t in self.markers if m == "4"])
        my_stats["Points Won/Lost after Attack over 4"] = (
            self.count_followed_by_win_and_lose("4")
        )
        my_stats["Attacks over 5"] = len([1 for m, t in self.markers if m == "5"])
        my_stats["Points Won/Lost after Attack over 5"] = (
            self.count_followed_by_win_and_lose("5")
        )
        my_stats["Attacks over 6"] = len([1 for m, t in self.markers if m == "6"])
        my_stats["Points Won/Lost after Attack over 6"] = (
            self.count_followed_by_win_and_lose("6")
        )
        return my_stats


if __name__ == "__main__":
    stats = Stats(sys.argv[1])
    stats.print_stats()
