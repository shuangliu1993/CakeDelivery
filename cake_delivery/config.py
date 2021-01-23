import yaml

with open("put_your_info_here.yml", "r") as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)
