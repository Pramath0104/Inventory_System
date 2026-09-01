from beanie import Document, Indexed
from pydantic import EmailStr

class Customer(Document):
    name: str
    email: Indexed(EmailStr, unique=True)

    class Settings:
        name = "customers"
