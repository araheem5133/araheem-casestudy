#Abdul Raheem Case Study
##Requires Docker to run via docker-compose

###Clone repository into a container and run the application with the following commands:
pip install -r requirements.txt
cd reorg (If you are not already in the Django reorg project directory)
python manage.py makemigrations
python manage.py migrate
python manage.py download_data 100 (You may replace 100 with whatever number of megabytes you want to install from CSM General Payment 2022)
python manage.py import_csv data.csv --max=10000 (You may replace 10000 with however many rows you want to import into the PostgreSQL database)
python manage.py search_index --rebuild (Ensure this is run after every import or the query will not work properly!)

To start the application run the following command:
python manage.py runserver
Navigate to http://127.0.0.1:8000/ or whichever directory is referenced on execute.

###Querying

To query, select a column from the dropdown and input a value. Autosuggestions will fill the input bar for the query.
Multiple filters can be placed on a query set and autosuggestions will constraint to the query.

Recommended to search by name/address before anything else because it is not constrained to the query.

Once the filters are set, the page will populate on each filter along with a sample of ten data points to ensure the query is operating properly.
Filters can be removed using the remove filter button that populates once each is run.

In order to download the entire queryset, use the Download Data button atop the table.
