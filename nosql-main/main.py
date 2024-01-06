from mongoengine import Document, StringField, DateTimeField, ListField, ReferenceField

class Author(Document):
    fullname = StringField(required=True)
    born_date = StringField(required=True)
    born_location = StringField(required=True)
    description = StringField(required=True)

class Quote(Document):
    tags = ListField(StringField())
    author = ReferenceField(Author, reverse_delete_rule=2)  # 2 means nullify
    quote = StringField(required=True)