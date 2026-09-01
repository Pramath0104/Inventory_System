from beanie import Document, Indexed

class Category(Document):
    name: Indexed(str, unique=True)

    class Settings:
        name = "categories"
