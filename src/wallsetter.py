import requests
import json
import time
import os
import shutil
import random

from gen_index import generate_wallpaper_index
from utils import read_file


class WallSetter:
    def __init__(self, api_key):
        self.api_key = api_key
        self.files = []
        self.image_dict = {}
        self.max_retries = 5
        self.curr_retries = 1
        self.output_file = os.path.join(os.path.dirname(__file__), "../download.txt")
        self.input_file = os.path.join(os.path.dirname(__file__), "../index.txt")

    def request(self, request_url, retry=False):
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
            for image in image_urls:
                image_id = image.split("/")[-1]
                if image_id not in self.files:
                    self.image_dict[image_id] = image

    def generate_wallhaven_index(self, pages: int, paths):
        file_set = generate_wallpaper_index(paths)
        self.files = list(file_set)

        for i in range(1, pages + 1):
            print("Scanning page: " + str(i))

            request_url = f"https://wallhaven.cc/api/v1/search?q=anime&categories=010&purity=111&atleast=1920x1080&sorting=views&order=desc&ratios=landscape&ai_art_filter=1&page={i}&apikey={self.api_key}"
            self.request(request_url)

        self.write_index(self.output_file)

    def write_index(self, filename):
        with open(filename, mode="w") as file:
            for id, value in self.image_dict.items():
                if id not in self.files:
                    file.write(f"{id}:{value}\n")

    def get_random_wallpaper(self):
        images = read_file(self.output_file)

        idx = random.randint(0, len(images))

        print(images[idx])
        return images[idx]

    def download_and_set_wallpaper(self, url, image_id):
        home = os.path.expanduser("~")
        file = f"{home}/.config/wallhaven_pics/{image_id}"

        files = read_file(self.input_file)
        if image_id not in files:
            r = requests.get(
                f"{url}?apikey={self.api_key}",
                stream=True,
                headers={
                    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
                },
            )

            if r.status_code == 200:
                with open(file, "wb+") as f:
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)
        else:
            print(f"Skipping download of: {image_id}")

        os.system(f"wal -i {file} && qtile cmd-obj -o cmd -f reload_config")
