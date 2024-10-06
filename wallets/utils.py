import yaml


def get_config(key):
    with open('config/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        return config[key]