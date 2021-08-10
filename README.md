# SSI-IAM
IAM with Hyperledger Indy and ACA-PY

## Preparations (tested on Ubuntu 20.04)
- Clone the repository recursively (`git clone --recurse-submodules https://github.com/JSedlmeir92/SSI-IAM.git`)
- Download Python 3.8 if not yet installed
- Download an SSI wallet, e.g., the esatus wallet, from Google Playstore (Android) or App Store (iOS) 
- Add the test ledger to the wallet by sending pool_transactions_genesis to it
- Edit .env with own IP_ADDRESS and local path to the repository
- Open ports so IP_ADDRESS:PORT they can be reached from the mobile phone for PORT in {7000, 9000}. If you run the demo in a virtual machine, you may need to open also ports 7080, 9080, 8000, 8001

## Run
- run_demo.sh
- Go to 127.0.0.1:8000 to click through the demo
