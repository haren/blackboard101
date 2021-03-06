# MULTISIGS - PART TWO - SPENDING FROM A MULTISIG ADDRESS
# wobine code for world bitcoin network blackboard 101
# Educational Purposes only
# Python 2.7.6 and relies on bitcoind & bitcoinrpc & wobine's github connection file
# We had to change the bitcoinrpc 'connection.py' file to add multisig support

from bitcoinrpc.util import *
from bitcoinrpc.exceptions import *
from bitcoinrpc.__init__ import *
from bitcoinrpc.config import *
from bitcoinrpc.proxy import *
from bitcoinrpc.data import *
from bitcoinrpc.connection import *


bitcoin = connect_to_local() #creates an object called 'bitcoin' that allows for bitcoind calls

# YOU NEED AT LEAST TWO OF THE PRIVATE KEYS FROM PART ONE
multisigprivkeyone = "L4VKzfujD6sTdWDsBMYUYWib4kFezuRNoJWNbzqYpQxgXtYJdiUP"
multisigprivkeytwo = "L3cYbSShrexaL64N7psvDMJ7617RfeVRAurZH6KMssh9qT4pS5kp"

unspent = bitcoin.listunspent() #List all unspent funds in bitcoind to see if you have some multisigs to spend from

print "Your Bitcoin-QT/d has",len(unspent),"unspent outputs"
for i in range(0, len(unspent)):
    print
    print "Output",i+1,"has",unspent[i]["amount"],"bitcoins, or",int(unspent[i]["amount"]*100000000),"satoshis"
    print "The transaction id for output",i+1,"is"
    print unspent[i]["txid"]
    print "The ScriptPubKey is", unspent[i]["scriptPubKey"]
    print "on Public Address",unspent[i]["address"]

print
totalcoin = int(bitcoin.getbalance()*100000000)
print "The total value of unspent satoshis is", totalcoin
print

WhichTrans = int(raw_input('Spend from which output? '))-1
if WhichTrans > len(unspent): #Basic idiot check. Clearly a real wallet would do more checks.
    print "Sorry that's not a valid output" 
else:
    tempaddy = str(unspent[WhichTrans]["address"])
    print
    if int(tempaddy[0:1]) == 1:
        print "The receivng address on that tx starts with a 1 - its not multisig."
    elif int(tempaddy[0:1]) == 3:
        print "The receivng address on that tx starts with a '3' which makes it a multisig."
        print "To create a raw multisig transaction we need : txid, scriptPubKey and redeemScript"
        print # fortunately all of this is right there in the bitcoind 'listunspent' call from before
        print "The txid is:",unspent[WhichTrans]["txid"]
        print "The ScriptPubKey is:", unspent[WhichTrans]["scriptPubKey"]
        print "And only multisigs have redeemScripts."
        print "The redeemScript is:",unspent[WhichTrans]["redeemScript"]
        print
        
        print "You have",int(unspent[WhichTrans]["amount"]*100000000),"satoshis in this output."

        HowMuch = int(raw_input('How much do you want to spend? '))
        if HowMuch > int(unspent[WhichTrans]["amount"]*100000000):
            print "Sorry not enough funds in that account"
        else:
            print
            SendAddress = str(raw_input('Send funds to which bitcoin address? ')) or "1M72Sfpbz1BPpXFHz9m3CdqATR44Jvaydd" #default value Sean's Outpost
            print
            print "This send to",SendAddress,"will leave", int(unspent[WhichTrans]["amount"]*100000000) - HowMuch,"Satoshis in your accounts"
            print
            print "Creating the raw transaction for User One - Private Key One"
            print
            
            rawtransact = bitcoin.createrawtransaction ([{"txid":unspent[WhichTrans]["txid"],
                    "vout":unspent[WhichTrans]["vout"],
                    "scriptPubKey":unspent[WhichTrans]["scriptPubKey"],
                    "redeemScript":unspent[WhichTrans]["redeemScript"]}],{SendAddress:0.0001})
            print "bitcoind decoderawtransaction", rawtransact
            print
            print
            print "And now we'll sign the raw transaction -> The first user gets a 'False'"
            print "This makes sense because in multisig, no single entity can sign alone"
            print
            print "For fun you can paste this FIRST signrawtransaction into bitcoind to verify multisig address"
            print "%s%s%s%s%s%s%s%s%s%s%s%s%s" % ('bitcoind signrawtransaction \'',rawtransact,'\' \'[{"txid":"',unspent[WhichTrans]["txid"],'","vout":',
                                      unspent[WhichTrans]["vout"],',"scriptPubKey":"',unspent[WhichTrans]["scriptPubKey"],'","redeemScript":"',
                                      unspent[WhichTrans]["redeemScript"],'"}]\' \'["',multisigprivkeyone,'"]\'')
            print
            signedone = bitcoin.signrawtransaction (rawtransact,
                    [{"txid":unspent[WhichTrans]["txid"],
                    "vout":0,"scriptPubKey":unspent[WhichTrans]["scriptPubKey"],
                    "redeemScript":unspent[WhichTrans]["redeemScript"]}],
                    [multisigprivkeyone])
            print signedone
            print
            print "In a real world situation, the 'hex' part of this thing above would be sent to the second"
            print "user or the wallet provider. Notice, the private key is not there. It has been signed digitally"
            print
            print
            print "For fun you can paste this SECOND signrawtransaction into bitcoind to verify multisig address"
            print "%s%s%s%s%s%s%s%s%s%s%s%s%s" % ('bitcoind signrawtransaction \'',signedone["hex"],'\' \'[{"txid":"',unspent[WhichTrans]["txid"],'","vout":',
                                      unspent[WhichTrans]["vout"],',"scriptPubKey":"',unspent[WhichTrans]["scriptPubKey"],'","redeemScript":"',
                                      unspent[WhichTrans]["redeemScript"],'"}]\' \'["',multisigprivkeytwo,'"]\'')
            print
            print bitcoin.signrawtransaction (signedone["hex"],
                    [{"txid":unspent[WhichTrans]["txid"],
                    "vout":0,"scriptPubKey":unspent[WhichTrans]["scriptPubKey"],
                    "redeemScript":unspent[WhichTrans]["redeemScript"]}],
                    [multisigprivkeytwo])
            print
            
            #print "The following is a regular transaction - not multisig"
            #print "bitcoind createrawtransaction", bitcoin.createrawtransaction([{"txid": unspent[WhichTrans]["txid"],
            #        "vout": unspent[WhichTrans]["vout"]}],
            #        {SendAddress : HowMuch})

