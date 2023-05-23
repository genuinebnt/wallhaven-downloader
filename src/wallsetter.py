import requests
import json
import time
import os
import shutil
import random

from utils import read_file, walk_dir, log_notify


class WallSetter:
    def __init__(self, api_key):
        self.api_key = api_key
        self.files = []
        self.image_dict = {}
        self.max_retries = 5
        self.curr_retries = 1
        self.output_file = os.path.join(os.path.dirname(__file__), "../download.txt")
        self.paths = [
            "../../../../../mnt/Files/Important Files/Wallpapers/2020-6-10/",
            "../../../../../mnt/Files/Important Files/Wallpapers/Anime Wallpapers/My Walls",
            "../../../../../home/genuine/.config/wallhaven_pics/",
        ]

    def request(self, request_url: str, retry=False):
        if retry:
            self.curr_retries += 1
            if self.curr_retries > self.max_retries:
                print("Max retries reached")
                return

        r = requests.get(request_url)

        if r.status_code == 429:
            print("Rate limit reached. Sleeping for 1 minute")
            time.sleep(60)

            print("Retrying")
            self.request(request_url, retry=True)

        elif r.status_code == 200:
            data = json.loads(r.content)
            image_urls = [value.get("path") for value in data.get("data")]

            print(f"Total images: {len(image_urls)}")

            for image in image_urls:
                image_id = image.split("/")[-1]
                if image_id not in self.files:
                    self.image_dict[image_id] = image

        else:
            print("Request failed with status code: " + r.status_code)

    def generate_wallpaper_index(self, paths: list[str]):
        file_list = []

        for path in paths:
            files = walk_dir(path)
            file_list.extend(files)

        return list(set(file_list))

    def generate_wallhaven_index(self, pages: int):
        self.files = self.generate_wallpaper_index(self.paths)

        for i in range(1, pages + 1):
            print("Scanning page: " + str(i))

            request_url = f"https://wallhaven.cc/api/v1/search?q=@rootkit&categories=010&purity=111&atleast=1920x1080&sorting=views&order=desc&ratios=landscape&ai_art_filter=1&page={i}&apikey={self.api_key}"
            self.request(request_url)

        self.write_index(self.output_file)

    def write_index(self, filename):
        with open(filename, mode="w") as file:
            for id, value in self.image_dict.items():
                if id not in self.files:
                    file.write(f"{id}:{value}\n")

    def get_random_wallpaper(self) -> str:
        images = read_file(self.output_file)

        while True:
            counter = 0
            idx = random.randint(0, len(images))
            image = images[idx]
            image_id = image.split(":", 1)[0]
            if image_id not in self.files:
                return image
            else:
                counter += 1
                log_notify("Skipping wallpaper" + image_id)

                if counter > 100:
                    log_notify("Many files in downloads.txt are already downloaded")
                    break

        return "Invalid"

    def download_and_save_wallpaper(self, image: str):
        image_id, url = image.split(":", 1)

        self.files = self.generate_wallpaper_index(self.paths)

        home = os.path.expanduser("~")
        file = f"{home}/.config/wallhaven_pics/{image_id}"

        if image_id not in self.files:
            self.request_wallpaper(url, file, image_id)
        else:
            log_notify(f"Skipping download of" + image_id)

        return file

    def request_wallpaper(self, url: str, path: str, image_id: str):
        max_tries = 5

        for i in range(0, max_tries):
            print("Downloading image:" + image_id)

            r = requests.get(
                f"{url}?apikey={self.api_key}",
                stream=True,
                headers={
                    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
                },
            )

            if r.status_code == 200:
                with open(path, "wb+") as f:
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)

                    return
            elif r.status_code == 429:
                print("Rate limit reached. Sleeping for 1 minute")
                time.sleep(60)

                print("Retrying")
            else:
                print(f"Failed request with code: {r.status_code}")
                return

        print("Max retries reached. Skipping wallpaper")

    def set_wallpaper(self, file: str):
        os.system(f"wal -i {file} && qtile cmd-obj -o cmd -f reload_config")

    def bulk_image_download(self):
        home = os.path.expanduser("~")
        download_path = f"{home}/.config/wallhaven_pics/"

        for image_id, url in self.image_dict.items():
            if image_id not in self.files:
                self.request_wallpaper(url, f"{download_path}{image_id}", image_id)
