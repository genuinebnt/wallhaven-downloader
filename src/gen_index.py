import os

from utils import walk_dir


def generate_wallpaper_index(paths: list[str]):
    file_list = []
    file_set = set()

    with open(
        os.path.join(os.path.dirname(__file__), os.pardir, "index.txt"), mode="w"
    ) as file:
        for path in paths:
            files = walk_dir(path)
            file_list.extend(files)

        file_set = set(file_list)
        file.write(str(file_set))

    return file_set
