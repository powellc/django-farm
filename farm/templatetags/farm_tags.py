from django import template
from django.db.models import Q
from django.core.cache import cache
from django.core.urlresolvers import resolve, reverse, Resolver404
from farm.models import Genus, Breed, Animal
from django.core.cache import cache
from datetime import datetime
from django import template

register = template.Library()

class GetBreedsNode(template.Node):
    """
    Retrieves a list of breeds with animals in them and places it into the context
    """
    def __init__(self, varname):
        self.varname = varname

    def render(self, context):
        breeds = Breed.objects.all()
        context[self.varname] = breeds
        return ''

def get_breeds(parser, token):
    """
    Retrieves a list of breeds and places it into the context

    {% get_breeds as breeds %}
    """
    args = token.split_contents()
    argc = len(args)

    try:
        assert argc == 3 and args[1] == 'as'
    except AssertionError:
        raise template.TemplateSyntaxError('get_breeds syntax: {% get_breeds as varname %}')

    return GetBreedsNode(args[2])

class GetGenusNode(template.Node):
    """
    Retrieves a list of genus with animals in them and places it into the context
    """
    def __init__(self, all, ex_obj, varname):
        self.varname = varname
        self.ex_obj = ex_obj
        self.all = all

    def render(self, context):
        ex_obj = context.get(self.ex_obj, None)
        cache_key = 'genuses'
        genuses = cache.get(cache_key)
        if genuses is None:
            if all:
                genuses = Genus.objects.all()
            else:
                genus_ids=Animal.onthefarm_objects.values('primary_breed__genus').distinct()
                ids=[]
                for g in genus_ids:
                    ids.append(g['primary_breed__genus'])
                try:
                    genuses=Genus.objects.filter(id__in=ids).exclude(id=ex_obj.id)
                except:
                    genuses=Genus.objects.filter(id__in=ids)
            context[self.varname] = genuses
        return ''

def get_genuses(parser, token):
    """
    Retrieves a list of genus with animals on the farm in them and places it into the context

    {% get_genuses as genuses %}
    {% get_genuses all as genuses %}
    {% get_genuses as genuses exclude obj %}
    """
    args = token.split_contents()
    argc = len(args)

    try:
        assert argc == 3 or (argc == 4 and args[1].lower() == 'all') or (argc == 5 and args[-2].lower() == 'exclude')
    except AssertionError:
        raise template.TemplateSyntaxError('Invalid get_genuses syntax.')

    # determine what parameters to use
    ex_obj = varname = all = None
    if argc == 3: t, a, varname = args
    if argc == 4: t, all, a, varname = args
    elif argc == 5: t, a, varname, e, ex_obj = args

    if all: all = True

    return GetGenusNode(all=all, ex_obj=ex_obj, varname=varname)

class GetNamedAnmialsNode(template.Node):
    """
    Retrieves a list of animals on the farm with names and places it into the
    context.
    """
    def __init__(self, varname):
        self.varname = varname

    def render(self, context):
        cache_key = 'named_animals'
        animals = cache.get(cache_key)
        if animals is None:
            animals=Animal.onthefarm_objects.filter(name__isnull=False)
            context[self.varname] = animals
        return ''

def get_named_animals(parser, token):
    """
    Retrieves a list of named animals on the farm.

    {% get_named_animals as nanimals %}
    """
    args = token.split_contents()
    argc = len(args)

    try:
        assert argc == 3 and args[1] == 'as'
    except AssertionError:
        raise template.TemplateSyntaxError('get_named_animals syntax: {% get_named_animals as varname %}')

    return GetNamedAnimalsNode(args[2])

def child_table_for(obj, switch=''):
    """Provides a table of children for a given animal.
        
       Optionally responds to a switch for dam/sire.
    """

    # Get all the children for the specified object
    if switch == 'dam':
        children = obj.dam_of()
    elif switch == 'sire':
        children = obj.sire_of()
    else:
        children = obj.progeny()

    if len(children) == 0:
        # go no further
        return {}

    return {'children': children}

register.tag(get_genuses)
register.tag(get_breeds)
register.tag(get_named_animals)
register.inclusion_tag('farm/_child_table.html')(child_table_for) 

