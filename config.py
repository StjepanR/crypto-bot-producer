import yaml

class Config:
    def __init__(self):
        with open("config.yml", "r") as f:
            self.config = yaml.safe_load(f)

    def get_config(self):
        return self.config
