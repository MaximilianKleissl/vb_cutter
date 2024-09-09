import toml

class Settings:
    def __init__(self, config_file):
        config = toml.load(config_file)
        self.input_file = config['video']['input_file']

        self.highlights = config['processing']['highlights']
        self.nasenbluten = config['processing']['nasenbluten']
        self.pipe = config['processing']['pipe']
        self.setter = config['processing']['setter']
        self.rallys = config['processing']['rallys']
        self.preset = config["processing"]["preset"]

        self.time_before_rally = config["video_settings"]["time_before_rally"]
        self.time_after_rally = config["video_settings"]["time_after_rally"]
        self.time_before_highlight = config["video_settings"]["time_before_highlight"]
        self.time_after_highlight = config["video_settings"]["time_after_highlight"]

        self.time_before_nasenbluten = config["video_settings"]["time_before_nasenbluten"]
        self.time_after_nasenbluten = config["video_settings"]["time_after_nasenbluten"]

        self.time_before_setting = config["video_settings"]["time_before_setting"]
        self.time_during_setting = config["video_settings"]["time_after_setting"]
        self.time_after_setting = config["video_settings"]["time_after_setting"]