from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from peewee import TextField

from module.db.models.base import BaseModel


class Storage(BaseModel):

    identifier = TextField()

    key = TextField()

    value = TextField(
        null=True,
        default='',
    )

    class Meta:
        table_name = 'storage'
