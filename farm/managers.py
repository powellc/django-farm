from django.db.models import Manager

class OnTheFarmManager(Manager):
    def get_query_set(self):
        return super(OnTheFarmManager, self).get_query_set().filter(on_farm=True)
