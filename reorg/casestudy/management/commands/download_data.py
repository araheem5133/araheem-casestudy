import os
import requests
from django.core.management.base import BaseCommand, CommandParser
from django.conf import settings

#Downloads the most recent data. Takes an operator for the number of 1MB chunks you want to download from the URL
class Command(BaseCommand):
    help = 'Download data.csv from a given URL in chunks, with a maximum chunk limit'

    def add_arguments(self, parser):
        parser.add_argument('max_chunks', type=int, help="Maximum number of chunks to download")

    def handle(self, *args, **kwargs):
        url = "https://openpaymentsdata.cms.gov/api/1/metastore/schemas/dataset/items/df01c2f8-dc1f-4e79-96cb-8208beaf143c?show-reference-ids=false"
        chunk_size = 1024 * 1024  # 1 MB chunks
        max_chunks = kwargs['max_chunks']

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            download_url = data["distribution"][0]["data"]["downloadURL"]

            csv_response = requests.get(download_url, stream=True)
            if csv_response.status_code == 200:
                base_dir = settings.BASE_DIR  # Use Django's built-in settings
                file_path = os.path.join(base_dir, "data.csv")

                with open(file_path, "wb") as f:
                    total_chunks = 0
                    for chunk in csv_response.iter_content(chunk_size):
                        if chunk:
                            f.write(chunk)
                            total_chunks += 1
                            self.stdout.write(f"Chunks written: {total_chunks}\r", ending="")

                            if total_chunks >= max_chunks:
                                self.stdout.write("\nMaximum chunk limit reached. Download stopped.")
                                break

                self.stdout.write(self.style.SUCCESS("CSV file downloaded successfully."))
            else:
                self.stderr.write("Failed to download CSV file.")
        else:
            self.stderr.write("Failed to fetch data from the provided URL.")
