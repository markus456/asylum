# -*- coding: utf-8 -*-
import random

import factory.django
import factory.fuzzy
from access.models import AccessType, TokenType
from members.models import MemberCommon
from members.tests.fixtures.memberlikes import firstnames, lastnames
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.template.defaultfilters import slugify

from asylum.tests.utils import FuzzyLoremipsum
from asylum.utils import get_random_objects

from .tokens import generate_value

def generate_contact_email(fname, lname):
    try:
        addr = '%s.%s@hacklab.hax' % (
            slugify(fname),
            slugify(lname)
        )
        validate_email(addr)
        return addr
    except ValidationError as e:
        return 'member_%d_%d@hacklab.hax' % (generate_unique_memberid(), random.randint(10, 2 ** 16))


def generate_contact(x):
    fname = random.choice(lastnames)
    lname = random.choice(firstnames)
    email = generate_contact_email(fname, lname)
    return "%s, %s <%s>" % (lname, fname, email)


class NonMemberTokenFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'access.NonMemberToken'
        django_get_or_create = ('ttype', 'value')
    ttype = factory.fuzzy.FuzzyChoice(TokenType.objects.all())
    notes = FuzzyLoremipsum()
    contact = factory.LazyAttribute(generate_contact)
    value = factory.LazyAttribute(generate_value)

    @factory.post_generation
    def grants(self, create, extracted, **kwargs):
        grants = []
        if extracted:
            grants = extracted
        else:
            if AccessType.objects.all().count():
                grants = get_random_objects(AccessType, random.randint(1, AccessType.objects.all().count()))
        for grant in grants:
            self.grants.add(grant)
