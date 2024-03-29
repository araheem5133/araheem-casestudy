from django.core.management.base import BaseCommand
import csv
from casestudy.models import PaymentData
from datetime import datetime
from django.db import transaction
import time

#Imports the CSV file for populating our PostgreSQL database
#Formatted as such: python manage.py import_csv data.csv --max=100000
#data.csv is our downloaded data file and --max=number of rows we want to parse
class Command(BaseCommand):
    help = 'Imports payment data from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str)
        parser.add_argument('--max', type=int, default=None,
                            help='Maximum number of records to import (optional)')

    def handle(self, *args, **options):
        file_path = options['path']
        CHUNK_SIZE = 5000  
        max_records = options['max']

        target_columns = [  'change_type', 
                            'covered_recipient_type',
                            'teaching_hospital_ccn',
                            'teaching_hospital_id',
                            'teaching_hospital_name',
                            'covered_recipient_profile_id',
                            'covered_recipient_npi',
                            'covered_recipient_first_name',
                            'covered_recipient_middle_name',
                            'covered_recipient_last_name',
                            'covered_recipient_name_suffix',
                            'recipient_primary_business_street_address_line1',
                            'recipient_primary_business_street_address_line2', 
                            'recipient_city',
                            'recipient_state', 
                            'recipient_zip_code',
                            'recipient_country',
                            'recipient_province',
                            'recipient_postal_code', 
                            'covered_recipient_primary_type_1',
                            'covered_recipient_specialty_1',
                            'covered_recipient_license_state_code1',
                            'submitting_applicable_manufacturer_or_applicable_gpo_name',
                            'applicable_manufacturer_or_applicable_gpo_making_payment_id',
                            'applicable_manufacturer_or_applicable_gpo_making_payment_name',
                            'total_amount_of_payment_usdollars',
                            'date_of_payment',
                            'number_of_payments_included_in_total_amount',
                            'form_of_payment_or_transfer_of_value',
                            'nature_of_payment_or_transfer_of_value',
                            'city_of_travel',
                            'state_of_travel',
                            'country_of_travel',
                            'physician_ownership_indicator', 
                            'third_party_payment_recipient_indicator', 
                            'name_of_third_party_entity_receiving_payment_or_transfer', 
                            'charity_indicator', 
                            'third_party_equals_covered_recipient_indicator', 
                            'contextual_information', 
                            'delay_in_publication_indicator', 
                            'record_id', 
                            'dispute_status_for_publication', 
                            'related_product_indicator', 
                            'covered_or_noncovered_indicator_1', 
                            'indicate_drug_or_biological_or_device_or_medical_supply_1',  
                            'product_category_or_therapeutic_area_1', 
                            'name_of_drug_or_biological_or_device_or_medical_supply_1',  
                            'associated_drug_or_biological_ndc_1',
                            'associated_device_or_medical_supply_pdi_1',
                            'program_year',
                            'payment_publication_date'
                        ]
        
        ctype = [   'Change_Type', 
                    'Covered_Recipient_Type', 
                    'Teaching_Hospital_CCN', 
                    'Teaching_Hospital_ID', 
                    'Teaching_Hospital_Name', 
                    'Covered_Recipient_Profile_ID', 
                    'Covered_Recipient_NPI', 
                    'Covered_Recipient_First_Name', 
                    'Covered_Recipient_Middle_Name', 
                    'Covered_Recipient_Last_Name', 
                    'Covered_Recipient_Name_Suffix', 
                    'Recipient_Primary_Business_Street_Address_Line1', 
                    'Recipient_Primary_Business_Street_Address_Line2', 
                    'Recipient_City', 
                    'Recipient_State', 
                    'Recipient_Zip_Code', 
                    'Recipient_Country', 
                    'Recipient_Province', 
                    'Recipient_Postal_Code', 
                    'Covered_Recipient_Primary_Type_1', 
                    'Covered_Recipient_Specialty_1',
                    'Covered_Recipient_License_State_Code1',
                    'Submitting_Applicable_Manufacturer_or_Applicable_GPO_Name',
                    'Applicable_Manufacturer_or_Applicable_GPO_Making_Payment_ID',
                    'Applicable_Manufacturer_or_Applicable_GPO_Making_Payment_Name',
                    'Total_Amount_of_Payment_USDollars',
                    'Date_of_Payment',
                    'Number_of_Payments_Included_in_Total_Amount',
                    'Form_of_Payment_or_Transfer_of_Value',
                    'Nature_of_Payment_or_Transfer_of_Value',
                    'City_of_Travel',
                    'State_of_Travel',
                    'Country_of_Travel',
                    'Physician_Ownership_Indicator', 
                    'Third_Party_Payment_Recipient_Indicator', 
                    'Name_of_Third_Party_Entity_Receiving_Payment_or_Transfer', 
                    'Charity_Indicator', 
                    'Third_Party_Equals_Covered_Recipient_Indicator', 
                    'Contextual_Information', 
                    'Delay_in_Publication_Indicator', 
                    'Record_ID', 
                    'Dispute_Status_for_Publication', 
                    'Related_Product_Indicator', 
                    'Covered_or_Noncovered_Indicator_1', 
                    'Indicate_Drug_or_Biological_or_Device_or_Medical_Supply_1', 
                    'Product_Category_or_Therapeutic_Area_1', 
                    'Name_of_Drug_or_Biological_or_Device_or_Medical_Supply_1', 
                    'Associated_Drug_or_Biological_NDC_1',
                    'Associated_Device_or_Medical_Supply_PDI_1',
                    'Program_Year',
                    'Payment_Publication_Date'
                ]

        self.stdout.write(self.style.SUCCESS(f'Starting import from {file_path}'))

        try:
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                data_chunk = []
                total_records = 0

                #print("CSV Column Headers:", reader.fieldnames) 
                start_time = time.time()
                for row in reader:
                    filtered_row = {column.lower(): row[column] if row[column] else None for column in ctype if column in row} 

                    # Date Conversion 
                    if 'Date_of_Payment' in row:
                        date_str = row['Date_of_Payment']
                        try:
                            date_obj = datetime.strptime(date_str, '%m/%d/%Y').date() 
                            filtered_row['date_of_payment'] = date_obj.strftime('%Y-%m-%d') 
                        except ValueError:
                            pass 

                    if 'Payment_Publication_Date' in row: 
                        date_str = row['Payment_Publication_Date']
                        try:
                            date_obj = datetime.strptime(date_str, '%m/%d/%Y').date() 
                            filtered_row['payment_publication_date'] = date_obj.strftime('%Y-%m-%d') 
                        except ValueError:
                            pass 
                    #Handles Boolean parsing
                    for bool_field in ['Physician_Ownership_Indicator', 'Third_Party_Payment_Recipient_Indicator',
                               'Charity_Indicator', 'Third_Party_Equals_Covered_Recipient_Indicator', 
                               'Delay_in_Publication_Indicator', 'Dispute_Status_for_Publication', 
                               'Related_Product_Indicator']:
                        if bool_field in row:
                            filtered_row[bool_field.lower()] = row[bool_field].lower() == 'yes'
                    #Appends to PaymentData
                    data_chunk.append(PaymentData(**filtered_row))
                    total_records += 1

                    if max_records is not None and total_records >= max_records:
                        break  # Stop processing if max_records is reached

                    if len(data_chunk) >= CHUNK_SIZE:
                        with transaction.atomic():
                            PaymentData.objects.bulk_create(data_chunk)
                        data_chunk = []
                        self.stdout.write(f'Imported {total_records} records...') 

            # Process remaining data
            if data_chunk:
                with transaction.atomic():
                    PaymentData.objects.bulk_create(data_chunk)

            self.stdout.write(self.style.SUCCESS(f'Import complete! Processed {total_records} records.'))
            end_time = time.time()  # Record the end time
            elapsed_time = end_time - start_time
            self.stdout.write(f'Import complete! Processed {total_records} records in {elapsed_time:.2f} seconds.')

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Unexpected error during import: {e}'))
