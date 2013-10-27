import sys, os
pyscript_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(pyscript_dir, '..'))
from bitme import BitmeAPI

# Read keys
with open('APIKEY', 'r') as f:
    API_KEY = f.read().strip()
with open('APISECRET', 'r') as f:
    API_SECRET = f.read().strip()

api = BitmeAPI(API_KEY, API_SECRET)
print api.accounts()
