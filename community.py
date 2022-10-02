# reward members with a application token (this is a ASA?)
# reward members for performing specific actions - ie sending materials to crisis zone or providing a discount
# loyalty token should be redeemable for additional member benefits - could give them a promotion as free marketing or a direct payout in some form such as algos
    # could alternatively pay out a percentage for holding these tokens

from pyteal import *

class Community:
    class Variables:
        name = Bytes("NAME")
        time_as_member = Bytes("TIME")
    class AppMethods:
        join = Bytes("join")

    def application_creation(self):
        return Seq([
            # requires that there are two arguments (name and time_as_member)
            Assert(Txn.application_args.length() == Int(1)),
            # adds a note for documentation purposes
            Assert(Txn.note() == Bytes("customer-loyalty")),
            # makes a global put of the name variable in the first application argument
            App.globalPut(self.Variables.name, Txn.application_args[0]),
            # make a global put of the time as member varibale into the second application argument
            App.globalPut(self.Variables.time_as_member, Txn.application_args[1]),
            # approves by leaving a one on the execution stack
            Approve()
        ])




