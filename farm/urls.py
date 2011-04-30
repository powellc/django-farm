from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic import DetailView, ListView
from farm.views import BreedDetailView, AnimalDetailView, ProductDetailView
from farm.models import Animal, Species, Breed, Product, ProductType, RegistrationBody, AnimalRegistration


# custom views vendors
urlpatterns = patterns('',
    url(r'^animals/$', view=ListView.as_view(model=Animal), name="fm-animal-list"),
	url(r'^animals/(?P<slug>[-\w]+)/$', view=DetailView.as_view(model=Species), name="fm-species-detail"),
	url(r'^animals/(?P<species_slug>[-\w]+)/(?P<slug>[-\w]+)/$', view=BreedDetailView.as_view(), name="fm-breed-detail"),
	url(r'^animals/(?P<species_slug>[-\w]+)/(?P<breed_slug>[-\w]+)/(?P<slug>[-\w]+)/$', view=AnimalDetailView.as_view(), name="fm-animal-detail"),

    url(r'^products/$', view=ListView.as_view(model=Product), name="fm-product-list"),
    url(r'^products/(?P<slug>[-\w]+)/$', view=DetailView.as_view(model=ProductType), name="fm-product-type-detail"),
    url(r'^products/(?P<type_slug>[-\w]+)/(?P<slug>[-\w]+)/$', view=ProductDetailView.as_view(), name="fm-product-detail"),
)
