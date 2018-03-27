from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from peewee import (
    IntegerField,
    TextField,
)

from module.db.models.base import BaseModel


class Package(BaseModel):
    folder = TextField(
        null=True,
    )

    name = TextField()

    packageorder = IntegerField(
        default=0,
    )

    password = TextField(
        null=True,
        default='',
    )

    queue = IntegerField(
        default=0,
    )

    site = TextField(
        null=True,
        default='',
    )

    class Meta:
        table_name = 'packages'
