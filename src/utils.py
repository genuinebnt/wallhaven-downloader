import os


def read_file(path: str) -> list[str]:
    with open(path, mode="r") as f:
        return [line.strip() for line in f.readlines() if line.strip() != ""]


def walk_dir(path: str) -> list[str]:
    file_list = []
    for root, dirs, files in os.walk(path):
        for name in files:
            file_list.append(name)
    return file_list


def log_notify(message: str):
    os.system("notify-send " + message)
