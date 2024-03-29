from django.db import models

#Models.py for our PaymentData model
class PaymentData(models.Model):
    change_type = models.CharField(max_length=50, null=True, blank=True)
    covered_recipient_type = models.CharField(max_length=100, null=True, blank=True)
    teaching_hospital_ccn = models.IntegerField(null=True, blank=True)
    teaching_hospital_id = models.IntegerField(null=True, blank=True)
    teaching_hospital_name = models.CharField(max_length=255, null=True, blank=True)
    covered_recipient_profile_id = models.IntegerField(null=True, blank=True)
    covered_recipient_npi = models.IntegerField(null=True, blank=True)
    covered_recipient_first_name = models.CharField(max_length=100, null=True, blank=True)
    covered_recipient_middle_name = models.CharField(max_length=100, null=True, blank=True)
    covered_recipient_last_name = models.CharField(max_length=100, null=True, blank=True)
    covered_recipient_name_suffix = models.CharField(max_length=10, null=True, blank=True)
    recipient_primary_business_street_address_line1 = models.CharField(max_length=255, null=True, blank=True)
    recipient_primary_business_street_address_line2 = models.CharField(max_length=255, null=True, blank=True) 
    recipient_city = models.CharField(max_length=100, null=True, blank=True)
    recipient_state = models.CharField(max_length=2, null=True, blank=True) 
    recipient_zip_code = models.CharField(max_length=10, null=True, blank=True)
    recipient_country = models.CharField(max_length=100, null=True, blank=True)
    recipient_province = models.CharField(max_length=100, null=True, blank=True)
    recipient_postal_code = models.CharField(max_length=50, null=True, blank=True) 
    covered_recipient_primary_type_1 = models.CharField(max_length=255, null=True, blank=True)
    covered_recipient_specialty_1 = models.CharField(max_length=255, null=True, blank=True)
    covered_recipient_license_state_code1 = models.CharField(max_length=2, null=True, blank=True)
    submitting_applicable_manufacturer_or_applicable_gpo_name = models.CharField(max_length=255, null=True, blank=True)
    applicable_manufacturer_or_applicable_gpo_making_payment_id = models.CharField(max_length=255, null=True, blank=True)
    applicable_manufacturer_or_applicable_gpo_making_payment_name = models.CharField(max_length=255, null=True, blank=True)
    total_amount_of_payment_usdollars = models.FloatField(null=True, blank=True)
    date_of_payment = models.DateField(null=True, blank=True)
    number_of_payments_included_in_total_amount = models.IntegerField(null=True, blank=True)
    form_of_payment_or_transfer_of_value = models.CharField(null=True, blank=True)
    nature_of_payment_or_transfer_of_value = models.CharField(max_length=255, null=True, blank=True)
    city_of_travel = models.CharField(max_length=100, null=True, blank=True)
    state_of_travel = models.CharField(max_length=2, null=True, blank=True)
    country_of_travel = models.CharField(max_length=100, null=True, blank=True)
    physician_ownership_indicator = models.BooleanField(null=False, blank=True)
    third_party_payment_recipient_indicator = models.BooleanField(null=False, blank=True)
    name_of_third_party_entity_receiving_payment_or_transfer = models.CharField(max_length=255, null=True, blank=True) 
    charity_indicator = models.BooleanField(null=False, blank=True)
    third_party_equals_covered_recipient_indicator = models.BooleanField(null=False, blank=True)
    contextual_information = models.TextField(null=True, blank=True) 
    delay_in_publication_indicator = models.BooleanField(null=False, blank=True)
    record_id = models.IntegerField(null=True, blank=True)
    dispute_status_for_publication = models.BooleanField(null=False, blank=True) 
    related_product_indicator = models.BooleanField(null=False, blank=True)
    covered_or_noncovered_indicator_1 = models.CharField(max_length=50, null=True, blank=True)  
    indicate_drug_or_biological_or_device_or_medical_supply_1  = models.CharField(max_length=50, null=True, blank=True) 
    product_category_or_therapeutic_area_1 = models.CharField(max_length=255, null=True, blank=True) 
    name_of_drug_or_biological_or_device_or_medical_supply_1 = models.CharField(max_length=255, null=True, blank=True)  
    associated_drug_or_biological_ndc_1 = models.CharField(max_length=50, null=True, blank=True)
    associated_device_or_medical_supply_pdi_1 = models.CharField(max_length=50, null=True, blank=True)
    program_year = models.IntegerField(null=True, blank=True)
    payment_publication_date = models.DateField(null=True, blank=True)
    
    #Property for composite values such as full physician name and address
    @property
    def physician_full_name(self):
        name_parts = [
            self.covered_recipient_first_name,
            self.covered_recipient_middle_name, 
            self.covered_recipient_last_name
        ]
        return " ".join(part for part in name_parts if part)
    
    @property
    def full_address(self):
        address_parts = [
            self.recipient_primary_business_street_address_line1,
            self.recipient_primary_business_street_address_line2
        ]
        return " ".join(part for part in address_parts if part)  # Filter out empty parts