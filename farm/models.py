from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from onec_utils.utils import unique_slugify
from onec_utils.fields import CurrencyField
from onec_utils.models import USAddressPhoneMixin
from photologue.models import Photo
from markup_mixin.models import MarkupMixin
from django_extensions.db.models import TitleSlugDescriptionModel, TimeStampedModel
from notes.models import Note
from attributes.models import BaseAttribute, AttributeOption
from uuidfield import UUIDField

from farm.utils import get_fancy_time
from farm.managers import OnTheFarmManager 

class Farm(TitleSlugDescriptionModel, TimeStampedModel, USAddressPhoneMixin):
    """
    Farm model class.
    
    Info about a farm
    """
    contact=models.CharField(_('Contact'), max_length=200, blank=True, null=True)
    active=models.BooleanField(_('Active'), help_text='Is this your farm?', default=False)
        
    class Meta:
        verbose_name=_('Farm')
        verbose_name_plural=_('Farms')
  
    def __unicode__(self):
        return u'%s' % self.title

class Genus(TitleSlugDescriptionModel):
    """
    Genus model class.
    
    Keeps track of the various genus on a farm.
    """
    plural_name=models.CharField(_('Plural name'), help_text="Only use if adding an 's' does not work.", blank=True, null=True, max_length=200)
    technical_name=models.CharField(_('Technical title'), blank=True, null=True, max_length=200)
    
        
    class Meta:
        verbose_name=_('Genus')
        verbose_name_plural=_('Genus')
  
    def __unicode__(self):
        return u'%s' % self.title

    @models.permalink
    def get_absolute_url(self):
        return ('fm-genus-detail', None, {'slug': self.slug})

    @property
    def plural_title(self):
        if self.plural_name: return self.plural_name
        else: return self.title + 's'
        
class Breed(TitleSlugDescriptionModel):
    """
    Breed model class.
    
    Keeps track of the various breeds on a farm.
    """
    genus = models.ForeignKey(Genus)
        
    class Meta:
        verbose_name=_('Breed')
        verbose_name_plural=_('Breeds')
  
    def __unicode__(self):
        return u'%s %s' % (self.title, self.genus)

    @models.permalink
    def get_absolute_url(self):
        return ('fm-breed-detail', None, {'slug': self.slug, 'genus_slug': self.genus.slug})
        
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

class Animal(MarkupMixin, TimeStampedModel):
    """
    Animal model class.
    
    Keeps track of individual animals on a farm
    """
    SEX_CHOICES=[
            ('M', 'Male'),
            ('F', 'Female'),]

    uuid=UUIDField(auto=True, editable=True)
    name = models.CharField(_('Name'), blank=True, null=True, max_length=255)
    slug = models.SlugField(_('Slug'), blank=True)
    primary_breed = models.ForeignKey(Breed)
    dam = models.ForeignKey('self', related_name="dam_", blank=True, null=True)
    sire = models.ForeignKey('self', related_name="sire_", blank=True, null=True)
    breeder_farm=models.ForeignKey(Farm, related_name='breeder_farm', blank=True, null=True)
    alt_breeder=models.CharField(_('Other breeder'), blank=True, null=True, max_length=255)
    owner_farm= models.ForeignKey(Farm, related_name='owner_farm', blank=True, null=True)
    alt_owner=models.CharField(_('Other owner'), blank=True, null=True, max_length=255)
    birthday = models.DateField(_('Birthday'), blank=True, null=True)
    birthtime = models.TimeField(_('Birthtime'), blank=True, null=True)
    deathday = models.DateField(_('Deathday'), blank=True, null=True)
    description = models.TextField(_('Description'), blank=True, null=True)
    rendered_description = models.TextField(_('Rendered description'), blank=True, null=True, editable=False)
    photos=models.ManyToManyField(Photo, blank=True, null=True)
    sex=models.CharField(_('Sex'), choices=SEX_CHOICES, default='f', max_length=1)

    notes=generic.GenericRelation(Note)
    secondary_breeds=generic.GenericRelation('SecondaryBreed')
        
    objects = models.Manager()
    onthefarm_objects = OnTheFarmManager()

    class Meta:
        verbose_name=_('Animal')
        verbose_name_plural=_('Animals')

    class MarkupOptions:
        source_field = 'description'
        rendered_field = 'rendered_description'

    def save(self, *args, **kwargs):
        super(Animal, self).save(*args, **kwargs)

        if not self.name:
            self.slug = self.uuid
        else:
            unique_slugify(self, self.name)

        super(Animal, self).save()
        
    def __unicode__(self):
        if self.name:
            return u'%s a %s' % (self.name, self.primary_breed )
        elif self.dam:
            return u'%s from %s (ID: %s)' % (self.sex, self.dam.name, self.uuid[:10])
        else:
            return u'ID: %s - %s' % (self.uuid[:10], self.primary_breed)

    def __init__(self, *args, **kwargs):
        super (Animal, self).__init__(*args, **kwargs)
        self._mixed_breed = None
        self._registrations = None
        self._births = []
        self._litters = {}
        self._age = None

    @property
    def display_name(self):
        if self.name:
            return self.name
        elif self.dam:
            return u'Unnamed child of %s' %(self.dam.name)
        else:
            return u'Unnamed %s' %(self.primary_breed)

    @property
    def registrations(self):
        if not self._registrations:
            self._registrations = self.registration_set.all()
        return self._registrations

    @property
    def age(self):
        if not self._age:
            if self.birthday:
                if self.deathday: DELTA=self.deathday
                else: DELTA=datetime.now()
                self._age = get_fancy_time(relativedelta(DELTA, self.birthday), True)
        return self._age

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

    @property
    def location(self):
        if self.owner_farm: return self.owner_farm
        else: return self.alt_owner

    @property
    def origin(self):
        if self.breeder_farm: return self.breeder_farm
        else: return self.alt_breeder

    def sire_of(self):
        return Animal.onthefarm_objects.filter(sire=self)

    def dam_of(self):
        return Animal.onthefarm_objects.filter(dam=self)

    def progeny(self):
        return Animal.onthefarm_objects.filter(models.Q(sire=self)|models.Q(dam=self))

    def birthed_progeny(self):
        return Animal.objects.filter(models.Q(sire=self)|models.Q(dam=self))

    def lost_progeny(self):
        return Animal.objects.filter(models.Q(sire=self)|models.Q(dam=self)).filter(owner_farm__active=True).filter(deathday__isnull=False)

    def births(self):
    # Set the threshold for when births are consider contiguous
    # Some animals can go hours between births, leading into the next day easily
        delta = timedelta(days=1)
        if not self._births:
            for p in self.progeny():
                if not p.birthday in self._births:
                    recorded=False
                    for b in self._births:
                        if b+delta >  p.birthday > b-delta:
                            recorded=True
                    if not recorded:
                        self._births.append(p.birthday)
        return self._births

    def litters(self):
    # Set the threshold for when births are consider contiguous
    # Some animals can go hours between births, leading into the next day easily
        delta = timedelta(days=1)
        if not self._litters:
            for b in self.births():
                p_collection=[]
                for p in self.birthed_progeny():
                    if b+delta > p.birthday > b-delta:
                        p_collection.append(p)
                self._litters[b]=p_collection
        return self._litters


    @models.permalink
    def get_absolute_url(self):
        return ('fm-animal-detail', None, {'slug': self.slug, 'breed_slug': self.primary_breed.slug, 'genus_slug': self.primary_breed.genus.slug})

UNIT_CHOICES = ( ('g', 'gallons'), ('l', 'liters' ), ('cl', 'centiliters'), ('ml', 'mililiters'), ('pt', 'pints'), ('oz', 'ounces') )

class Milking(TimeStampedModel)
    animal = models.ForeignKey(Animal)
    milking_time = models.DateTimeField(_('Milking time'))
    quantity = models.IntegerField(_('Quantity'))
    units = models.CharField(_('Units'), choices=UNIT_CHOICES, max_length=2, default='ml')
    notes=generic.GenericRelation(Note)

    class Meta:
        verbose_name = _('Milking')
        verbose_name_plural = _('Milkings')

    def __unicode__(self):
        return u'Milking on %s of %s' %(self.milking_time, self.animal.display_name)

class AnimalAttributeOption(AttributeOption):

    class Meta:
        verbose_name = _('Animal attribute options')
        verbose_name_plural = _('Animal attribute options')

class AnimalAttribute(BaseAttribute):
    option = models.ForeignKey(AnimalAttributeOption)
    animal = models.ForeignKey(Animal)

    class Meta:
        verbose_name = _('Animal attribute')
        verbose_name_plural = _('Animal attributes')

    def __unicode__(self):
        return u'%s attribute of %s' %(self.option, self.animal.display_name)

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

class Building(MarkupMixin, TitleSlugDescriptionModel, TimeStampedModel):
    farm=models.ForeignKey(Farm)
    built=models.DateField(_('Built'), blank=True, null=True)
    photos=models.ManyToManyField(Photo, blank=True, null=True)
    rendered_description=models.TextField(_('Rendered description'), blank=True, null=True, editable=False)

    class Meta:
        verbose_name=_('Building')
        verbose_name_plural=_('Buildings')

    class MarkupOptions:
        source_field = 'description'
        rendered_field = 'rendered_description'
  
    def __unicode__(self):
        return u'%s' % self.title

    def __init__(self, *args, **kwargs):
        super (Building, self).__init__(*args, **kwargs)
        self._age = None
        
    @property
    def age(self):
        if not self._age:
            if self.built:
                DELTA=datetime.now()
                self._age = get_fancy_time(relativedelta(DELTA, self.built), True)
            else: self._age = "Unknown"
        return self._age

    @models.permalink
    def get_absolute_url(self):
        return ('fm-building-detail', None, {'slug': self.slug})

class BuildingAttributeOption(AttributeOption):

    class Meta:
        verbose_name = _('Building attribute options')
        verbose_name_plural = _('Building attribute options')

class BuildingAttribute(BaseAttribute):
    option = models.ForeignKey(BuildingAttributeOption)
    building = models.ForeignKey(Building)

    class Meta:
        verbose_name = _('Building attribute')
        verbose_name_plural = _('Building attributes')

    def __unicode__(self):
        return u'%s attribute of %s' %(self.option, self.building.title)

class BuildingSpace(MarkupMixin, TitleSlugDescriptionModel):
    """
    Bulding Space model class.

    Keeps track of the various spaces in a bulding (rooms, lofts, corners
    etc...)
    """
    building=models.ForeignKey(Building)
    photos = models.ManyToManyField(Photo, blank=True, null=True)
    rendered_description=models.TextField(_('Rendered description'), blank=True, null=True)

    class Meta:
        verbose_name=_('Building space')
        verbose_name_plural=_('Building spaces')

    class MarkupOptions:
        source_field = 'description'
        rendered_field = 'rendered_description'
  
    def __unicode__(self):
        return u'%s' % self.title

    def __init__(self, *args, **kwargs):
        super (BuildingSpace, self).__init__(*args, **kwargs)

class FieldType(TitleSlugDescriptionModel):
    """
    Field Type model class.
    
    Keeps track of the various field types on a farm, such as pasture, garden,
    grain, etc...
    """
        
    class Meta:
        verbose_name=_('Field type')
        verbose_name_plural=_('Field types')
  
    def __unicode__(self):
        return u'%s' % self.title

    @models.permalink
    def get_absolute_url(self):
        return ('fm-field-type-detail', None, {'slug': self.slug})

class Field(MarkupMixin, TitleSlugDescriptionModel, TimeStampedModel):
    farm=models.ForeignKey(Farm)
    type=models.ForeignKey(FieldType, blank=True, null=True)
    photos=models.ManyToManyField(Photo, blank=True, null=True)
    rendered_description=models.TextField(_('Rendered description'), blank=True, null=True, editable=False)

    class Meta:
        verbose_name=_('Field')
        verbose_name_plural=_('Fields')

    class MarkupOptions:
        source_field = 'description'
        rendered_field = 'rendered_description'
  
    def __unicode__(self):
        return u'%s' % self.title

    def __init__(self, *args, **kwargs):
        super (Field, self).__init__(*args, **kwargs)
        
    @models.permalink
    def get_absolute_url(self):
        return ('fm-field-detail', None, {'slug': self.slug})

class FieldAttributeOption(AttributeOption):

    class Meta:
        verbose_name = _('Field attribute options')
        verbose_name_plural = _('Field attribute options')

class FieldAttribute(BaseAttribute):
    option = models.ForeignKey(FieldAttributeOption)
    field = models.ForeignKey(Field)

    class Meta:
        verbose_name = _('Field attribute')
        verbose_name_plural = _('Field attributes')

    def __unicode__(self):
        return u'%s attribute of %s' %(self.option, self.field.title)
