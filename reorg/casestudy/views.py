from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django_elasticsearch_dsl.search import Search
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, Page
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Q
from django.urls import reverse
import tempfile
from openpyxl import Workbook
from .forms import PaymentRangeForm
from datetime import datetime

#Columns that we want to filter by
columns = [ "covered_recipient_profile_id",
            "covered_recipient_npi",
            "physician_full_name",
            "full_address",
            "recipient_city",
            "recipient_state",
            "recipient_zip_code",
            "recipient_country",
            "recipient_province",
            "recipient_postal_code",
            "covered_recipient_primary_type_1",
            "covered_recipient_specialty_1",
            "covered_recipient_license_state_code1",
            "submitting_applicable_manufacturer_or_applicable_gpo_name",
            "applicable_manufacturer_or_applicable_gpo_making_payment_name",
            "total_amount_of_payment_usdollars",
            "date_of_payment",
            "number_of_payments_included_in_total_amount",
            "form_of_payment_or_transfer_of_value",
            "nature_of_payment_or_transfer_of_value",
            "city_of_travel",
            "state_of_travel",
            "country_of_travel",
            "physician_ownership_indicator",
            "third_party_payment_recipient_indicator",
            "name_of_third_party_entity_receiving_payment_or_transfer",
            "charity_indicator",
            "third_party_equals_covered_recipient_indicator",
            "delay_in_publication_indicator",
            "record_id",
            "dispute_status_for_publication",
            "related_product_indicator",
]

#Holds all our active filters in a str->set dictionary
active_filters = {}

#Download data function for downloading our current query with all active filters.
def download_data(request):
    # Connect to Elasticsearch
    es = Elasticsearch(['http://elasticsearch:9200'])

    # Fetch data based on active filters
    search = Search(using=es, index='payment_data').query(build_elasticsearch_query(active_filters))
    search = search.params(size=1000)  # Adjust size as needed

    # Create a new Excel workbook
    wb = Workbook()
    ws = wb.active

    # Add headers to the worksheet
    ws.append(columns)

    # Paginate through the entire result set
    for hit in search.scan():
        row_data = [getattr(hit, column, '') for column in columns]
        ws.append(row_data)

    # Create a temporary file to save the workbook
    with tempfile.NamedTemporaryFile() as tmp:
        wb.save(tmp.name)
        tmp.seek(0)
        file_data = tmp.read()

    # Set the response content type
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    # Set the content disposition to force download
    response['Content-Disposition'] = 'attachment; filename=data.xlsx'
    response.write(file_data)
    
    return response

#Remove filter function connected to all automatically generated filters shown on the page
def remove_filter(request):
    if request.method == 'POST':
        column = request.POST.get('column')
        filter_value = request.POST.get('filter_value')

        # Handle special case for payment range filter
        if column == 'total_amount_of_payment_usdollars' or column=='date_of_payment':
            del active_filters[column]
        else:
            # Convert filter_value to boolean if it represents a boolean value
            if filter_value.lower() == 'true':
                filter_value = True
            elif filter_value.lower() == 'false':
                filter_value = False

            # Remove the filter value from active_filters dictionary
            if column in active_filters and filter_value in active_filters[column]:
                active_filters[column].remove(filter_value)
                if not active_filters[column]:
                    del active_filters[column]

    # Redirect back to the same page or any desired page
    return HttpResponseRedirect(reverse('autocomplete'))

#Builds the multifield elasticsearch query
def build_elasticsearch_query(active_filters):
    query = Q('bool')

    #Check for all items in active_filters
    for column, filter_values in active_filters.items():
        if filter_values:  # Check if there are any values
            column_query = Q('bool') 

            boolean_columns = [
                'physician_ownership_indicator',
                'third_party_payment_recipient_indicator',
                'charity_indicator',
                'third_party_equals_covered_recipient_indicator',
                'delay_in_publication_indicator',
                'dispute_status_for_publication',
                'related_product_indicator'
            ]

            if column in boolean_columns:
                # For boolean fields, there should be either True or False in filter values
                if True in filter_values:
                    column_query |= Q('match', **{column: True})
                if False in filter_values:
                    column_query |= Q('match', **{column: False})
            elif column == 'total_amount_of_payment_usdollars' and isinstance(filter_values, tuple):
                # For range queries on amount of USD
                min_amount, max_amount = filter_values
                if min_amount is not None:
                    column_query &= Q('range', **{column: {'gte': min_amount}})
                if max_amount is not None:
                    column_query &= Q('range', **{column: {'lte': max_amount}})
            elif column == 'date_of_payment' and isinstance(filter_values, tuple):
                # For date range queries
                start_date, end_date = filter_values
                if start_date is not None:
                    column_query &= Q('range', **{column: {'gte': start_date}})
                if end_date is not None:
                    column_query &= Q('range', **{column: {'lte': end_date}})
            else:
                # For all other fields including multiple match queries for each filter value
                for filter_value in filter_values:
                    # Include both original case and all-uppercase variations
                    individual_filter = Q('bool', should=[
                        Q('match', **{column: filter_value}),  # Match with original casing
                        Q('match', **{column: filter_value.upper()}),
                        Q('match', **{column: filter_value.capitalize()})  # Match with all uppercase
                    ])
                    column_query |= individual_filter

            if column_query:  # Check if column_query has filters
                query &= column_query  

    return query

def autocomplete(request):
    #Runs an Elasticsearch index
    es = Elasticsearch(
    ['http://elasticsearch:9200'], 
    )
    #Gets payment range form. Look in forms.py for more info
    payment_range_form = PaymentRangeForm(request.POST or None) 

    #Runs on submit button
    if request.method == 'POST':
        #Takes column and written input
        column = request.POST.get('column')
        fname = request.POST.get('fname')

        #If we have a written input, add it to the set
        if(fname):
            if column in active_filters:
                active_filters[column].add(fname)
            else:
                active_filters[column] = {fname}
        #Otherwise if a column is a boolean column, put either true or false for the filter.
        elif column in ['physician_ownership_indicator', 'third_party_payment_recipient_indicator', 'charity_indicator', 'third_party_equals_covered_recipient_indicator', 'delay_in_publication_indicator', 'dispute_status_for_publication', 'related_product_indicator', 'covered_or_noncovered_indicator_1']:
            response_checkbox = request.POST.get('response')
            if response_checkbox == 'on':
                active_filters[column] = {True}
            else:
                active_filters[column] = {False}
        #Logs the payment range form. Check forms.py for more information. Takes min and max amount as a range.
        if payment_range_form.is_valid():
            min_amount = payment_range_form.cleaned_data.get('min_amount')
            max_amount = payment_range_form.cleaned_data.get('max_amount')
            if min_amount is not None and max_amount is not None:
                # Add range filter to active_filters
                active_filters['total_amount_of_payment_usdollars'] = (min_amount, max_amount)
        #Handles date of payment information
        if column == 'date_of_payment' and 'start-date' in request.POST and 'end-date' in request.POST:
            start_date = request.POST.get('start-date')
            end_date = request.POST.get('end-date')
            if start_date and end_date:
                # Convert start_date and end_date strings to datetime objects
                start_date = datetime.strptime(start_date, '%m/%d/%Y')
                end_date = datetime.strptime(end_date, '%m/%d/%Y')

                # Check if start_date is before end_date
                if start_date <= end_date:
                    # Add the date range to active_filters
                    active_filters['date_of_payment'] = (start_date, end_date)

        #Builds our elastic search with the BEQ function and active filers
        search = Search(index='payment_data').query(build_elasticsearch_query(active_filters))
        search = search.extra(from_=0, size=10)
        response = search.execute()

        #Renders all relevant context to home.html
        return render(request, 'home.html', {
            'active_filters': active_filters,
            'column_names': columns,
            'hits': response.hits,
            'columns': columns,
            'payment_range_form': payment_range_form
        })

    #Handles our autosuggestion and typeahead
    if 'term' in request.GET:
        #Term triggers with our JS function on every letter typed into the input field.
        search_term = request.GET.get('term')
        search_column = request.GET.get('column', 'covered_recipient_profile_id')

        #Builds the same search index with all currently existing active filters.
        search = Search(index='payment_data')
        active_query = build_elasticsearch_query(active_filters)
        search = search.query(active_query)

        #Full address and physician full name handled differently because they are ngram filters.
        if search_column in ['full_address', 'physician_full_name']:
            suggest_query = {
                "suggest": {
                    "name_suggestions": {
                        "prefix": search_term,
                        "completion": {
                            "field": search_column,
                            "skip_duplicates": True  # Ensure uniqueness
                        },
                    },
                },
                "query": {
                    "bool": {
                        "filter": build_elasticsearch_query(active_filters).to_dict()  # Add active filters to the query
                    }
                }
            }
            
            #Searchs with the ElasticSearch client and populates suggestions
            response = es.search(index="payment_data", body=suggest_query)
            sugge = response["suggest"]["name_suggestions"][0]["options"]
            suggestions = []
            if sugge:
                for suggestion in sugge:
                    suggestions.append(suggestion['text'])
            else:
                print("No suggestions found.")
        else:  # Prefix search for other columns that use KeyField
            search = search.query('prefix', **{search_column: search_term})
            response = search.execute()
            #Makes sure to use a set for no duplicate values
            suggestions = list(set(str(getattr(hit, search_column)) for hit in response.hits))
        #Return suggestion as a JsonResponse
        return JsonResponse(suggestions, safe=False)
    #Shows a sample of 10 data points in the table to ensure query is operating properly.
    search = Search(index='payment_data').query(build_elasticsearch_query(active_filters))
    search = search.extra(from_=0, size=10)
    response = search.execute()
    #Render all relevant data.
    return render(request, 'home.html', {
            'active_filters': active_filters,
            'columns': columns,
            'column_names': columns,
            'hits': response.hits,
            'payment_range_form': payment_range_form
        })