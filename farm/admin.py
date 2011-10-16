import logging
from django.forms import models, ValidationError
from django.contrib import admin
from django.contrib.contenttypes import generic

from farm.models import Farm, Genus, Breed, Animal, Product, ProductType, Note, SecondaryBreed, AnimalAttribute, AnimalAttributeOption, ProductAttribute, ProductAttributeOption, Building, BuildingSpace, Field, FieldType, BuildingAttribute, FieldAttribute, BuildingAttributeOption, FieldAttributeOption, Milking
from notes.admin import NoteInline
from attributes.admin import clean_attribute_value

class AnimalAttributeInlineForm(models.ModelForm):

    def clean_value(self):
        print 'Farm admin.py: cleaning values and have data: %s' % self.cleaned_data
        return clean_attribute_value(self.cleaned_data, self.cleaned_data['animal'])

class AnimalAttributeInline(admin.TabularInline):
    model = AnimalAttribute
    #form = AnimalAttributeInlineForm

class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute

class SecondaryBreedInline(generic.GenericTabularInline):
    model = SecondaryBreed

class AnimalAdmin(admin.ModelAdmin):
    list_filter = ('owner_farm', 'breeder_farm', 'alt_owner', 'alt_breeder', )
    list_display = ('sex', 'name', 'dam', 'birthday', 'primary_breed',)
    inlines = [ AnimalAttributeInline, SecondaryBreedInline, NoteInline, ]

class MilkingAdmin(admin.ModelAdmin):
    inlines = [ NoteInline, ]

class ProductAdmin(admin.ModelAdmin):
    inlines = [ ProductAttributeInline, NoteInline, ]

admin.site.register(Milking, MilkingAdmin)
admin.site.register(Animal, AnimalAdmin)
admin.site.register(Farm)
admin.site.register(Genus)
admin.site.register(Breed)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductType)
admin.site.register(AnimalAttribute)
admin.site.register(AnimalAttributeOption)
admin.site.register(ProductAttributeOption)
admin.site.register(Building)
admin.site.register(BuildingSpace)
admin.site.register(Field)
admin.site.register(FieldType)
admin.site.register(BuildingAttribute)
admin.site.register(FieldAttribute)
admin.site.register(BuildingAttributeOption)
admin.site.register(FieldAttributeOption)
