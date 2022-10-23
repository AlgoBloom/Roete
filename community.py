# reward members with a application token (this is a ASA?)
# reward members for performing specific actions - ie sending materials to crisis zone or providing a discount
# loyalty token should be redeemable for additional member benefits - could give them a promotion as free marketing or a direct payout in some form such as algos
    # could alternatively pay out a percentage for holding these tokens

from pyteal import *

def approval_program():
    
    basic_checks = And(
        Txn.rekey_to() == Global.zero_address(),    
        Txn.close_remainder_to() == Global.zero_address(),
        Txn.asset_close_to() == Global.zero_address()
    )

    # creates the smart contract and the values within it
    on_creation = Seq(
        [
            ## WHY? ## checks that the application argument length is one
            Assert(Txn.application_args.length() == Int(1)),
            # total amount
            App.globalPut(Bytes("total amount"), Btoi(Txn.application_args[0])), # 1000000
            # decimals
            App.globalPut(Bytes("decimals"), Btoi(Txn.application_args[1])), # 0
            # asset name
            App.globalPut(Bytes("asset name"), Txn.application_args[2]), # Tesla
            # asset unit name
            App.globalPut(Bytes("asset unit name"), Txn.application_args[3]), # TSLA
            # local put that designates the minter as the admin of the asset
            App.localPut(Int(0), Bytes("admin"), Int(1)),
            # local put that tracks the balance of the asset
            App.localPut(Int(0), Bytes("balance"), Int(0)),
            # approves the sequence by leaving one on the stack
            Return(Int(1))
        ]
    )

    # returns boolean showing if address is admin
    is_admin = App.localGet(Int(0), Bytes("admin"))

    # allows accounts to opt out of the application
    on_closeout = Seq(
        [
            # returns the balance of the account to the reserve
            App.globalPut(
                Bytes("reserve"),
                App.globalGet(Bytes("reserve"))
                + App.localGet(Int(0), Bytes("balance")),
            ),
            Return(Int(1)),
        ]
    )

    # opts an acct into the app
    register = Seq(
        [
            App.localPut(
                Int(0), 
                Bytes("balance"), 
                Int(0)),
            Return(Int(1))
        ]
    )

    # set admin to Txn.accounts[1]
    # sender must be admin
    new_admin_status = Btoi(Txn.application_args[1])
    set_admin = Seq(
        [
            Assert(And(is_admin, Txn.application_args.length() == Int(2))),
            # sets the first account to the new admin
            App.localPut(Int(1), Bytes("admin"), new_admin_status),
            Return(Int(1))
        ]
    )

    # separating the mint amount as a var, first app arg is amount
    mint_amount = Btoi(Txn.application_args[1])
    # subroutine mints assets
    mint = Seq(
        [
            # must be two application arguments
            Assert(Txn.application_args.length() == Int(2)),
            # cannot mint more than the acct balance of the minter
            Assert(mint_amount <= App.globalGet(Bytes("reserve"))),
            # updates the global reserve in the sc
            App.globalPut(
                Bytes("reserve"),
                App.globalGet(Bytes("reserve")) - mint_amount,
            ),
            # updates the local balance
            App.localPut(
                Int(1), # does the order of the array change based on who the sender of the transaction is?
                Bytes("balance"),
                App.localGet(Int(0), Bytes("balance")) + mint_amount,
            ),
        ]
    )

    # set amount to transfer as app arg one
    transfer_amount = Btoi(Txn.application_args[1])
    # transfers the asset
    transfer = Seq(
        [
            # requires there are two app args
            Assert(Txn.application_args.length() == Int(2)),
            # txn amount is less than the local acct balance
            Assert(transfer_amount <= App.localGet(Int(0), Bytes("balance"))),
            # changing balance for sending acct
            App.localPut(
                Int(0),
                Bytes("balance"),
                App.localGet(Int(0), Bytes("balance")) - transfer_amount,
            ),
            # changing balance for receiving acct
            App.localPut(
                Int(1),
                Bytes("balance"),
                App.localGet(Int(1), Bytes("balance")) + transfer_amount,
            ),
            Return(Int(1))
        ]
    )

    program = Cond(
        # checks if the smart contract already exists
        [Txn.application_id() == Int(0), on_creation],
        # deletes the application
        [Txn.on_completion() == OnComplete.DeleteApplication, Return(is_admin)],
        # update application subroutine
        [Txn.on_completion() == OnComplete.UpdateApplication, Return(is_admin)],
        # closeout application subroutine
        [Txn.on_completion() == OnComplete.CloseOut, on_closeout],
        # opt in subroutine
        [Txn.on_completion() == OnComplete.OptIn, register],
        # sets the administrator 
        [Txn.application_args[0] == Bytes("set admin"), set_admin],
        # mints the asset
        [Txn.application_args[0] == Bytes("mint"), mint],
        # transfers the asset
        [Txn.application_args[0] == Bytes("transfer"), transfer],
        # burns the asset
        [Txn.application_args[0] == Bytes("burn"), burn]
    )

    return program

def clear_state_program():
    program = Seq(
        [
            App.globalPut(
                Bytes("reserve"),
                App.globalGet(Bytes("reserve"))
                + App.localGet(Int(0), Bytes("balance")),
            ),
            Return(Int(1)),
        ]
    )

    return program


if __name__ == "__main__":
    with open("asset_approval.teal", "w") as f:
        compiled = compileTeal(approval_program(), mode=Mode.Application, version=2)
        f.write(compiled)

    with open("asset_clear_state.teal", "w") as f:
        compiled = compileTeal(clear_state_program(), mode=Mode.Application, version=2)
        f.write(compiled)



