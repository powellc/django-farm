import datetime
from django.views.generic import DetailView, ListView

from django.shortcuts import get_list_or_404, render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings

from farm.models import Animal, Breed, Product
from notes.forms import BriefNoteForm

class BreedDetailView(DetailView):
    model = Breed

    def get_queryset(self, *args, **kwargs):
        return Breed.objects.filter(genus__slug=self.kwargs['genus_slug'])

class ProductDetailView(DetailView):
    model = Product

    def get_queryset(self, *args, **kwargs):
        return Product.objects.filter(type__slug=self.kwargs['type_slug'])

class AnimalDetailView(DetailView):
    model = Animal

    def get_queryset(self, *args, **kwargs):
        return Animal.objects.filter(primary_breed__genus__slug=self.kwargs['genus_slug'], primary_breed__slug=self.kwargs['breed_slug'])

    def get_context_data(self, **kwargs):
        context = super(AnimalDetailView, self).get_context_data(**kwargs)
        context['note_form'] = BriefNoteForm()
        return context
