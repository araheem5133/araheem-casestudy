import os
import requests
from django.core.management.base import BaseCommand

#Downloads the CSV file from the CSM Url using a Json request
#Speeds can be very slow, recommended to unzip if possible
class Command(BaseCommand):
    help = 'Download data.csv from a given URL'

    def handle(self, *args, **kwargs):
        # Defines the URL
        url = "https://openpaymentsdata.cms.gov/api/1/metastore/schemas/dataset/items/df01c2f8-dc1f-4e79-96cb-8208beaf143c?show-reference-ids=false"

        # Send a GET request to the URL
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            
            # Extract the download URL from the JSON response
            download_url = data["distribution"][0]["data"]["downloadURL"]
            
            # Download the CSV file
            csv_response = requests.get(download_url)
            
            # Check if the download was successful
            if csv_response.status_code == 200:
                # Get the base directory of the Django project
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                
                # Define the path to save the CSV file
                file_path = os.path.join(base_dir, "data.csv")
                
                # Save the CSV data to a file
                with open(file_path, "wb") as f:
                    f.write(csv_response.content)
                
                self.stdout.write(self.style.SUCCESS("CSV file downloaded successfully."))
            else:
                self.stderr.write("Failed to download CSV file.")
        else:
            self.stderr.write("Failed to fetch data from the provided URL.")