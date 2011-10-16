from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic import DetailView, ListView
from farm.views import BreedDetailView, AnimalDetailView, ProductDetailView, MilkingListView
from farm.models import Animal, Genus, Breed, Product, ProductType, RegistrationBody, AnimalRegistration, Building, BuildingSpace, Field


# custom views vendors
urlpatterns = patterns('',
    url(r'^animals/$', view=ListView.as_view(model=Genus), name="fm-genus-list"),
	url(r'^animals/(?P<slug>[-\w]+)/$', view=DetailView.as_view(model=Genus), name="fm-genus-detail"),
	url(r'^animals/(?P<slug>[-\w]+)/$', view=DetailView.as_view(model=Genus), name="fm-genus-detail"),
	url(r'^animals/(?P<genus_slug>[-\w]+)/(?P<slug>[-\w]+)/$', view=BreedDetailView.as_view(), name="fm-breed-detail"),
	url(r'^animals/(?P<genus_slug>[-\w]+)/(?P<breed_slug>[-\w]+)/(?P<slug>[-\w]+)/$', view=AnimalDetailView.as_view(), name="fm-animal-detail"),
	url(r'^animals/(?P<genus_slug>[-\w]+)/(?P<breed_slug>[-\w]+)/(?P<slug>[-\w]+)/milkings/$', view=MilkingListView.as_view(), name="fm-milking-detail"),

    url(r'^products/$', view=ListView.as_view(model=Product), name="fm-product-list"),
    url(r'^products/(?P<slug>[-\w]+)/$', view=DetailView.as_view(model=ProductType), name="fm-product-type-detail"),
    url(r'^products/(?P<type_slug>[-\w]+)/(?P<slug>[-\w]+)/$', view=ProductDetailView.as_view(), name="fm-product-detail"),

    url(r'^buildings/$', view=ListView.as_view(model=Building), name="fm-building-list"),
    url(r'^buildings/(?P<slug>[-\w]+)/$', view=DetailView.as_view(model=Building), name="fm-building-detail"),
    url(r'^buildings/(?P<building_slug>[-\w]+)/(?P<slug>[-\w]+)/$', view=DetailView.as_view(model=BuildingSpace), name="fm-building-space-detail"),

    url(r'^fields/$', view=ListView.as_view(model=Field), name="fm-field-list"),
    url(r'^fields/(?P<slug>[-\w]+)/$', view=DetailView.as_view(model=Field), name="fm-field-detail"),
)
