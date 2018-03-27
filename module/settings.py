from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from peewee import SqliteDatabase


DATABASE_FILENAME = 'files.db'

DATABASE = SqliteDatabase(DATABASE_FILENAME)
