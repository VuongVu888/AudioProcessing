import glob
import json
from locust import HttpUser, task, between
import aiohttp
# https://drive.google.com/file/d/1Lp71BhlxrGwIsL87WS8qBIw6i0BZOMSl/view?usp=sharing
class AsyncLocustUser(HttpUser):
    wait_time = between(1, 5)  # Time between requests
    success_count = 0

    def on_start(self):
        file_list = glob.iglob("/Users/vuongvu/University/XLTN/LibriSpeech/test-clean/*/*/*.flac", recursive=True)
        self.req = []
        for file in file_list:
            with open(file, 'rb') as f:
                data = f.read()
                self.req.append(data)
                f.close()
        print("Request files: ", len(self.req))

    @task
    def make_async_request(self):
        url = "/api/audio/upload"  # Replace with your actual endpoint

        for data in self.req:
            with self.client.post(
                    url=url,
                    # headers={"content-type": "multipart/form-data", "accept": "application/json"},
                    files={"audio_file": data, "type": "audio/wav"},
                    catch_response=True,  # Enable catch_response to capture the response
            ) as response:
                if response.status_code == 200:
                    response.success()
                    self.success_count += 1
                    # pass
                else:
                    response.failure(f"Request failed with status code {response.status_code}")

    def on_stop(self):
        # This method is called when all Locust users have stopped
        print(f"Total successful requests: {self.success_count}")
