from django.db.models import Manager
from datetime import datetime

class OnTheFarmManager(Manager):
    def get_query_set(self):
        return super(OnTheFarmManager, self).get_query_set().filter(owner_farm__active=True).filter(deathday__isnull=True)

