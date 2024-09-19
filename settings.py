import toml


class Settings:
    def __init__(self, config_file):
        config = toml.load(config_file)
        self.project_folder = config["files"]["project_folder"]
        self.input_video = config["files"]["input_video"]
        self.markers_file = config["files"]["marker_file"]

        self.receives = config["processing"]["receives"]
        self.highlights = config["processing"]["highlights"]
        self.nasenbluten = config["processing"]["nasenbluten"]
        self.attacks = config["processing"]["attacks"]
        self.setter = config["processing"]["setter"]
        self.rallys = config["processing"]["rallys"]
        self.preset = config["processing"]["preset"]
        self.services = config["processing"]["services"]
        self.output_folder = config["files"]["output_folder"]

        self.time_before_rally = config["video_settings"]["time_before_rally"]
        self.time_after_rally = config["video_settings"]["time_after_rally"]
        self.time_before_highlight = config["video_settings"]["time_before_highlight"]
        self.time_after_highlight = config["video_settings"]["time_after_highlight"]

        self.time_before_nasenbluten = config["video_settings"][
            "time_before_nasenbluten"
        ]
        self.time_after_nasenbluten = config["video_settings"]["time_after_nasenbluten"]

        self.time_before_setting = config["video_settings"]["time_before_setting"]
        self.time_during_setting = config["video_settings"]["time_after_setting"]
        self.time_after_setting = config["video_settings"]["time_after_setting"]
