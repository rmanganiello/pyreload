from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from peewee import (
    ForeignKeyField,
    IntegerField,
    TextField,
)

from module.db.models.base import BaseModel
from module.db.models.package import Package


class Link(BaseModel):

    error = TextField(
        null=True,
        default='',
    )

    linkorder = IntegerField(
        default=0,
    )

    name = TextField(
        null=True,
    )

    package = ForeignKeyField(
        Package,
        column_name='package',
        field='id',
        index=True,
    )

    plugin = TextField(
        default='BasePlugin',
    )

    size = IntegerField(
        default=0,
    )

    status = IntegerField(
        default=3,
    )

    url = TextField()

    class Meta:
        table_name = 'links'
