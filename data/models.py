from tortoise import fields, Model


class User(Model):
    id = fields.IntField(pk=True)
    tv = fields.CharField(max_length=255)
