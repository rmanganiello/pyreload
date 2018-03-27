from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from peewee import Model

from module import settings


class BaseModel(Model):

    class Meta:
        database = settings.DATABASE
