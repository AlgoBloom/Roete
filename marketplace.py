# each product is represented by an application
# buy product by making a call to the app and performing a payment to the creator

from pyteal import *

class Item:
    class Vars:
        supplier = Bytes("Supplier")
        name = Bytes("Name")
        image = Bytes("Image")
        description = Bytes("Description")
        price = Bytes("Price")
        sold = Bytes("Sold")
