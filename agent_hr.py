import os

# Getting IP ADDRESS
FileHandler = open("ip_address.txt", "r")
ip_address = FileHandler.read()
FileHandler.close()

# Starting AGENT 1 - HR DEPARTMENT
os.system('aca-py start --inbound-transport http 0.0.0.0 7000 --inbound-transport ws 0.0.0.0 7001 --outbound-transport ws --outbound-transport http --genesis-file /var/lib/indy/my-net/pool_transactions_genesis --log-level debug --wallet-type indy --seed 000000000000000000000000Steward3 --wallet-key welldone --wallet-name StewardWallet3 --admin-insecure-mode --admin 0.0.0.0 7080 -e "http://' + ip_address + ':7000/" -l "HR Department"')