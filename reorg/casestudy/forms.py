from django import forms

#Payment range form that takes min amount and max amount for the range we want our gift/payment to be in.
class PaymentRangeForm(forms.Form):
    min_amount = forms.DecimalField(label='Minimum Amount', required=False)
    max_amount = forms.DecimalField(label='Maximum Amount', required=False)

    def clean(self):
        cleaned_data = super().clean()
        min_amount = cleaned_data.get('min_amount')
        max_amount = cleaned_data.get('max_amount')

        #Validates form
        if min_amount is not None and max_amount is not None:
            if min_amount > max_amount:
                raise forms.ValidationError("Minimum amount should be less than or equal to maximum amount")

        return cleaned_data