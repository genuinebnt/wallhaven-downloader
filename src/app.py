import os

from gen_index import generate_wallpaper_index
from dotenv import dotenv_values
from wallsetter import WallSetter


def main():
    dotenv_path = os.path.join(os.path.dirname(__file__), "../.env")
    config = dotenv_values(f"{dotenv_path}")
    api_key = config.get("API_KEY")

    paths = [
        "../../../../../mnt/Files/Important Files/Wallpapers/2020-6-10/",
        "../../../../../mnt/Files/Important Files/Wallpapers/Anime Wallpapers/My Walls",
        "../../../.config/wallhaven_pics/",
    ]

    wall_setter = WallSetter(api_key)
    ##wall_setter.generate_wallhaven_index(20, paths)
    image_id, url = wall_setter.get_random_wallpaper().split(":", 1)
    wall_setter.download_and_set_wallpaper(url, image_id)


if __name__ == "__main__":
    main()
