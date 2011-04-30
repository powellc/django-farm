import datetime
from django.views.generic import DetailView, ListView

from django.shortcuts import get_list_or_404, render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings

from farm.models import Animal, Breed, Product

class BreedDetailView(DetailView):
    model = Breed

    def get_queryset(self, *args, **kwargs):
        return Breed.objects.filter(species__slug=self.kwargs['species_slug'])

class ProductDetailView(DetailView):
    model = Product

    def get_queryset(self, *args, **kwargs):
        return Product.objects.filter(type__slug=self.kwargs['type_slug'])

class AnimalDetailView(DetailView):
    model = Animal

    def get_queryset(self, *args, **kwargs):
        return Animal.objects.filter(primary_breed__species__slug=self.kwargs['species_slug'], primary_breed__slug=self.kwargs['breed_slug'])

