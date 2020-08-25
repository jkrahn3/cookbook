
import datetime
from peewee import *


db = SqliteDatabase('recipes.db')


class Recipe(Model):
    name = TextField(unique=True)
    date_created = DateTimeField(default=datetime.datetime.now)
    ingredient_list = TextField()
    prep_time = TimeField(null=True)
    cook_time = TimeField(null=True)
    instructions = TextField(null=True)

    class Meta:
        database = db
        db_table = 'recipes'
