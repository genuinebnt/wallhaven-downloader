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
        "-gi", "--generate-index", help="generate wallhaven index", default=20, type=int
    )
    parser.add_argument(
        "-bd", "--bulk-download", help="bulk download wallpapers", action="store_true"
    )
    parser.add_argument(
        "-rw",
        "--random-wallpaper",
        help="bulk download wallpapers",
        action="store_true",
    )
    args = parser.parse_args()

    wall_setter = WallSetter(api_key)

    if args.generate_index:
        wall_setter.generate_wallhaven_index(args.generate_index)

    if args.bulk_download:
        wall_setter.bulk_image_download()

    if args.random_wallpaper:
        image = wall_setter.get_random_wallpaper()
        if image != "Invalid":
            file = wall_setter.download_and_save_wallpaper(image)
            wall_setter.set_wallpaper(file)


if __name__ == "__main__":
    main()
