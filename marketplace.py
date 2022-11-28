# each product is represented by an application
# buy product by making a call to the app and performing a payment to the creator

from pyteal import *

class Item:
    # class holds the variables
    class Vars:
        supplier = Bytes("Supplier")
        name = Bytes("Name")
        image = Bytes("Image")
        description = Bytes("Description")
        price = Bytes("Price")
        sold = Bytes("Sold")
    # class holds the methods
    class Methods:
        Fund = Bytes("Fund")
    # method creates a product
    def app_creation(self):
        return Seq(
            # requires 5 app args for call
            Assert(Txn.application_args.length() == Int(5)),
            # requires note
            Assert(Txn.note() == Bytes("marketplace:uv1")),
            # requires price is greater than zero
            Assert(Btoi(Txn.application_args[4]) > Int(0)),
            # supplier is first app arg
            App.globalPut(self.Vars.supplier, Txn.application_args[0]),
            
        )
    
