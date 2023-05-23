import os
import argparse

from dotenv import dotenv_values
from wallsetter import WallSetter


def main():
    dotenv_path = os.path.join(os.path.dirname(__file__), "../.env")
    config = dotenv_values(f"{dotenv_path}")
    api_key = config.get("API_KEY")

    parser = argparse.ArgumentParser(
        prog="wallsetter", description="downloads and set wallpaper from wallhaven"
    )

    parser.add_argument(
        "-gi", "--generate-index", help="generate wallhaven index", action="store_true"
    )
    args = parser.parse_args()

    wall_setter = WallSetter(api_key)

    if args.generate_index:
        wall_setter.generate_wallhaven_index(20)
        return

    image = wall_setter.get_random_wallpaper()
    if image != "Invalid":
        wall_setter.download_and_set_wallpaper(image)


if __name__ == "__main__":
    main()
