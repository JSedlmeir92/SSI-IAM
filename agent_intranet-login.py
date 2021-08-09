import os

# Getting IP ADDRESS
FileHandler = open("ip_address.txt", "r")
ip_address = FileHandler.read()
FileHandler.close()

# Starting AGENT 2 - Intranet Login
os.system('aca-py start --inbound-transport http 0.0.0.0 9000 --inbound-transport ws 0.0.0.0 9001 --outbound-transport ws --outbound-transport http --genesis-file /var/lib/indy/my-net/pool_transactions_genesis --log-level debug --wallet-type indy --seed 000000000000000000000000000Agent --wallet-key welldone --wallet-name AgentWallet2 --admin-insecure-mode --admin 0.0.0.0 9080 -e http://' + ip_address + ':9000/ --webhook http://' + ip_address + ':8001/intranet -l "Intranet Login" --auto-verify-presentation')