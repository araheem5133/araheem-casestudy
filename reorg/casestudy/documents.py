from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import PaymentData

#Documentation for our ElasticSearch index
@registry.register_document
class PaymentDataDocument(Document):
    change_type = fields.KeywordField(index=False)
    covered_recipient_type = fields.KeywordField(index=False) 
    teaching_hospital_ccn = fields.KeywordField(index=False)
    teaching_hospital_id = fields.KeywordField(index=False)
    teaching_hospital_name = fields.KeywordField(index=False)
    covered_recipient_profile_id = fields.KeywordField()
    covered_recipient_npi = fields.KeywordField()
    covered_recipient_first_name = fields.TextField(analyzer='autocomplete', index=False)
    covered_recipient_middle_name = fields.TextField(analyzer='standard', index=False)
    covered_recipient_last_name = fields.TextField(analyzer='standard', index=False)
    physician_full_name = fields.CompletionField(analyzer='autocomplete')
    full_address = fields.CompletionField(analyzer='autocomplete')
    recipient_primary_business_street_address_line1 = fields.TextField(analyzer='standard', index=False) 
    recipient_primary_business_street_address_line2 = fields.TextField(analyzer='standard', index=False)  
    recipient_city = fields.KeywordField()
    recipient_state = fields.KeywordField() 
    recipient_zip_code = fields.KeywordField()
    recipient_country = fields.KeywordField()
    recipient_province = fields.KeywordField()
    recipient_postal_code = fields.KeywordField()
    covered_recipient_primary_type_1 = fields.KeywordField()
    covered_recipient_specialty_1 = fields.KeywordField()
    covered_recipient_license_state_code1 = fields.KeywordField()
    submitting_applicable_manufacturer_or_applicable_gpo_name = fields.TextField(analyzer='standard') 
    applicable_manufacturer_or_applicable_gpo_making_payment_id = fields.KeywordField() 
    applicable_manufacturer_or_applicable_gpo_making_payment_name = fields.TextField(analyzer='standard')
    total_amount_of_payment_usdollars = fields.FloatField()
    date_of_payment = fields.DateField()
    number_of_payments_included_in_total_amount = fields.KeywordField()
    form_of_payment_or_transfer_of_value = fields.KeywordField()
    nature_of_payment_or_transfer_of_value = fields.KeywordField()
    city_of_travel = fields.KeywordField()
    state_of_travel = fields.KeywordField()
    country_of_travel = fields.KeywordField()
    physician_ownership_indicator = fields.BooleanField()
    third_party_payment_recipient_indicator = fields.BooleanField()
    name_of_third_party_entity_receiving_payment_or_transfer = fields.TextField(analyzer='standard')
    charity_indicator = fields.BooleanField()
    third_party_equals_covered_recipient_indicator = fields.BooleanField()
    contextual_information = fields.TextField(analyzer='standard')
    delay_in_publication_indicator = fields.BooleanField()
    record_id = fields.KeywordField()
    dispute_status_for_publication = fields.BooleanField()
    related_product_indicator = fields.BooleanField()
    covered_or_noncovered_indicator_1 = fields.KeywordField(index=False) 
    indicate_drug_or_biological_or_device_or_medical_supply_1  = fields.KeywordField(index=False)
    product_category_or_therapeutic_area_1 = fields.KeywordField(index=False)
    name_of_drug_or_biological_or_device_or_medical_supply_1 = fields.KeywordField(index=False)
    associated_drug_or_biological_ndc_1 = fields.KeywordField(index=False)
    associated_device_or_medical_supply_pdi_1 = fields.KeywordField(index=False)

    class Index:
        name = 'payment_data' 
        #Index for our custom ngram filter
        settings = { 
            "analysis": {
                "analyzer": {
                    "autocomplete": {
                        "type": "custom",
                        "tokenizer": "standard",  
                        "filter": [
                            "lowercase",          
                            "my_edge_ngram"       
                        ]
                    }
                },
                "filter": {
                    "my_edge_ngram": {    
                        "type": "edge_ngram", 
                        "min_gram": 4,        
                        "max_gram": 20        
                    }
                }
            }
        } 
    #Django connection with PaymentData as our model
    class Django:
        model = PaymentData
        