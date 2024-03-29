from django.core.management.base import BaseCommand
from casestudy.models import PaymentData 

#Clears all data from the PostgreSQL database
#!!! Do NOT use for very large datasets. Use python manage.py flush !!!
class Command(BaseCommand):
    help = 'Deletes all data from the PaymentData table'

    help = 'Deletes all data from the PaymentData table'

    def handle(self, *args, **options):
        BATCH_SIZE = 5000

        while True:
            qs = PaymentData.objects.all()[:BATCH_SIZE]
            pks = qs.values_list('pk', flat=True)  # Get primary keys
            if not pks:
                break  # No more objects to delete
            PaymentData.objects.filter(pk__in=pks).delete()  # Delete by primary key
            self.stdout.write(self.style.SUCCESS(f'Deleted {BATCH_SIZE} objects from the PaymentData table.'))