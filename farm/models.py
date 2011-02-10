from datetime import *
from django.db import models
from django.utils.translation import ugettext_lazy as _
from myutils.fields import CurrencyField

try:
    from photologue.models import Photo
except:
    def Photo(models.Model):
        title=models.CharField(_('Title'), max_length=255)
        slug = models.SlugField()
        image=models.ImageField(_('Image'), upload_to='/photos/')
        description=models.TextField(_('Description'), blank=True, null=True)

class Specie(models.Model):
    """
    Specie model class.
    
    Keeps track of the various species on a farm.
    """

    name = models.CharField(_('Name'), max_length=100)
    slug = models.SlugField()
        
    class Meta:
	order_by=('name',)
        
class Breed(models.Model):
    """
    Breed model class.
    
    Keeps track of the various breeds on a farm.
    """

    name = models.CharField(_('Name'), max_length=100)
    slug = models.SlugField()
    specie = models.ForeignKey(Specie)
        
    class Meta:
	order_by=('specie', 'name',)
        
class Animal(models.Model):
    """
    Animal model class.
    
    Keeps track of individual animals on a farm
    """

    name = models.CharField(_('Name'), max_length=200)
    slug = models.SlugField()
    breed = models.ForeignKey(Breed)
    mother = models.ForeignKey(self, related_name="mother", blank=True, null=True)
    father = models.ForeignKey(self, related_name="father", blank=True, null=True)
    birthday = models.DateField(_('Birthday'), blank=True, null=True)
    birthtime = models.TimeField(_('Birthtime'), blank=True, null=True)
    description=models.TextField(_('Description'), blank=True, null=True)
    photos=models.ManyToManyField(Photo, blank=True, null=True)
    on_farm=models.BooleanField(_('On farm?', default=False)
        
    class Meta:
	order_by=('breed', 'name',)

class ProductType(models.Model):
    """
    ProductType model class.
    
    Keeps track of the various product types on a farm, such as produce, meat, soap, preserves etc...
    """

    name = models.CharField(_('Name'), max_length=100)
    slug = models.SlugField()
    description= models.TextField(_('Description'), blank=True, null=True)
        
    class Meta:
	order_by=('name',)
        
class Product(models.Model):
    name= models.CharField(_('Name'), max_length=200)
    type = models.ForeignKey(ProductType)
    description=models.TextField(_('Description'), blank=True, null=True)
    photos=models.ManyToManyField(Photo, blank=True, null=True)
    price=CurrencyField(_('Price'), blank=True, null=True)
    unit=models.CharField(_('Unit'), blank=True, null=True, max_length=100)
    verbose_price=models.CharField(_('Verbose price'), blank=True, null=True, max_length=255)

    class Meta:
	order_by=('name',)
        

