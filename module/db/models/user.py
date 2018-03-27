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


class User(BaseModel):
    email = TextField(
        default='',
    )

    name = TextField()

    password = TextField()

    permission = IntegerField(
        default=0,
    )

    role = IntegerField(
        default=0,
    )

    template = TextField(
        default='default',
    )

    class Meta:
        table_name = 'users'
