from datetime import *
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from onec_utils.fields import CurrencyField
from markup_mixin.models import MarkupMixin
from onec_utils.models import USAddressPhoneMixin
from django_extensions.db.models import TitleSlugDescriptionModel, TimeStampedModel
from photologue.models import Photo
from notes.models import Note
from attributes.models import BaseAttribute, AttributeOption

from farm.managers import OnTheFarmManager

class Farm(TitleSlugDescriptionModel, TimeStampedModel, USAddressPhoneMixin):
    """
    Farm model class.
    
    Info about a farm
    """
    current=models.BooleanField(_('Current'), default=False)
        
    class Meta:
        verbose_name=_('Farm')
        verbose_name_plural=_('Farms')
  
    def __unicode__(self):
        return u'%s' % self.title

class Species(TitleSlugDescriptionModel):
    """
    Species model class.
    
    Keeps track of the various species on a farm.
    """
        
    class Meta:
        verbose_name=_('species')
        verbose_name_plural=_('species')
  
    def __unicode__(self):
        return u'%s' % self.title

    @models.permalink
    def get_absolute_url(self):
        return ('fm-breed-detail', None, {'slug': self.slug})
        
class Breed(TitleSlugDescriptionModel):
    """
    Breed model class.
    
    Keeps track of the various breeds on a farm.
    """
    species = models.ForeignKey(Species)
        
    class Meta:
        verbose_name=_('Breed')
        verbose_name_plural=_('Breeds')
  
    def __unicode__(self):
        return u'%s %s' % (self.title, self.species)

    @models.permalink
    def get_absolute_url(self):
        return ('fm-breed-detail', None, {'slug': self.slug, 'species_slug': self.species.slug})
        
class RegistrationBody(TitleSlugDescriptionModel):
    breed = models.ForeignKey(Breed)
    website = models.URLField(_('Website'), blank=True, null=True)

    class Meta:
        verbose_name=_('Registration body')
        verbose_name_plural=_('Registration bodies')
  
    def __unicode__(self):
        return u'%s' % self.name

class SecondaryBreed(models.Model):
    breed = models.ForeignKey(Breed)
    percentage = models.IntegerField(_('Percentage'), max_length=2)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey("content_type", "object_id")
    
    class Meta:
        verbose_name=_('Secondary breed')
        verbose_name_plural=_('Secondary breeds')
    
    def __unicode__(self):
        return u'%s (%s)' % (self.breed, self.percentage )

class Animal(MarkupMixin, TitleSlugDescriptionModel, TimeStampedModel):
    """
    Animal model class.
    
    Keeps track of individual animals on a farm
    """
    SEX_CHOICES=[
            ('M', 'Male'),
            ('F', 'Female'),]

    primary_breed = models.ForeignKey(Breed)
    mother = models.ForeignKey('self', related_name="mother_", blank=True, null=True)
    father = models.ForeignKey('self', related_name="father_", blank=True, null=True)
    birthday = models.DateField(_('Birthday'), blank=True, null=True)
    birthtime = models.TimeField(_('Birthtime'), blank=True, null=True)
    deathday = models.DateField(_('Deathday'), blank=True, null=True)
    rendered_description = models.TextField(_('Rendered description'), blank=True, null=True, editable=False)
    photos=models.ManyToManyField(Photo, blank=True, null=True)
    registered=models.BooleanField(_('Registered'), default=False)
    on_farm=models.BooleanField(_('On farm?'), default=False)
    sex=models.CharField(_('Sex'), choices=SEX_CHOICES, default='f', max_length=1)
    notes=generic.GenericRelation(Note)
    secondary_breeds=generic.GenericRelation('SecondaryBreed')
        
    objects = models.Manager()
    onthefarm = OnTheFarmManager()

    class Meta:
        verbose_name=_('Animal')
        verbose_name_plural=_('Animals')
  
    class MarkupOptions:
        source_field = 'description'
        rendered_field = 'rendered_description'
        
    def __unicode__(self):
        return u'%s - %s' % (self.title, self.primary_breed )

    def __init__(self, *args, **kwargs):
        super (Animal, self).__init__(*args, **kwargs)
        self._mixed_breed = None
        self._registrations = None

    @property
    def registrations(self):
        if not self._registrations:
            self._registrations = self.registration_set.all()
        return self._registrations

    @property
    def breed(self):
        if self.mixed_breed():
            self._breed = 'Mixed ' + self.primary_breed.__unicode__()
        else:
            self._breed = self.primary_breed.__unicode__()
        return self._breed

    def mixed_breed(self):
        if not self._mixed_breed:
            if self.secondary_breeds.all():
                return True
            else:
                return False

    @models.permalink
    def get_absolute_url(self):
        return ('fm-animal-detail', None, {'slug': self.slug, 'breed_slug': self.primary_breed.slug, 'species_slug': self.primary_breed.species.slug})


class AnimalAttributeOption(AttributeOption):

    class Meta:
        verbose_name = _('Animal attribute options')
        verbose_name_plural = _('Animal attribute options')

class AnimalAttribute(BaseAttribute):
    animal = models.ForeignKey(Animal)

    class Meta:
        verbose_name = _('Animal attribute')
        verbose_name_plural = _('Animal attributes')

class AnimalRegistration(models.Model):
    animal = models.ForeignKey(Animal)
    body = models.ForeignKey(RegistrationBody)
    date = models.DateField(_('Registration date'), blank=True, null=True)
    reg_id = models.CharField(_('Registration ID'), blank=True, null=True, max_length=255)

    class Meta:
        verbose_name=_('Animal registration')
        verbose_name_plural=_('Animals registrations')
  
    def __unicode__(self):
        return u'Registration of %s at %s' % (self.animal, self.body)
    
class ProductType(TitleSlugDescriptionModel):
    """
    ProductType model class.
    
    Keeps track of the various product types on a farm, such as produce, meat, soap, preserves etc...
    """
        
    class Meta:
        verbose_name=_('Product type')
        verbose_name_plural=_('Product types')
  
    def __unicode__(self):
        return u'%s' % self.title

    @models.permalink
    def get_absolute_url(self):
        return ('fm-product-type-detail', None, {'slug': self.slug})
        
class ProductAttributeOption(AttributeOption):

    class Meta:
        verbose_name = _('Product attribute options')
        verbose_name_plural = _('Product attribute options')

class ProductAttribute(BaseAttribute):
    product = models.ForeignKey('Product')

    class Meta:
        verbose_name = _('Product attribute')
        verbose_name_plural = _('Product attributes')

class Product(TitleSlugDescriptionModel, TimeStampedModel):
    type = models.ForeignKey(ProductType)
    photos=models.ManyToManyField(Photo, blank=True, null=True)
    price=CurrencyField(_('Price'), blank=True, null=True, decimal_places=2, max_digits=5)
    unit=models.CharField(_('Unit'), blank=True, null=True, max_length=100)
    verbose_price=models.CharField(_('Verbose price'), blank=True, null=True, max_length=255)

    class Meta:
        verbose_name=_('Product')
        verbose_name_plural=_('Products')
  
    def __unicode__(self):
        return u'%s' % self.title
        
    @models.permalink
    def get_absolute_url(self):
        return ('fm-product-detail', None, {'slug': self.slug, 'type_slug': self.type.slug})
