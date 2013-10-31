from urllib import urlencode
import requests, json, base64
import hmac, hashlib
from collections import OrderedDict
from datetime import datetime
import bitme_internal
API_URLROOT = 'https://bitme.com/rest'
class BitmeAPI:
    """
    A BitMe API Client implementation
    """
    def __init__(self, apikey, apisecret=None):
        self.apikey = apikey
        self.apisecret = base64.b64decode(apisecret)

    def _query(self, url, params={}, auth=False, method='GET'):
        """
        General query function for API

        :param url: URL suffix to append to API_URLROOT (eg. '/accounts')
        :param params: dictionary of params to include in query string or post data
        :param auth: Whether this is an authenticated request
        :param method: The request type ('GET' or 'POST')
        """
        # Generate nonce (UTC timestamp since epoch works)
        nonce = bitme_internal.datetime_to_timestamp(
                datetime.now()) * 1000 + 1000000000
        params['nonce'] = nonce
        params = OrderedDict(params)
        p_encoded = urlencode(params)
        mac = base64.b64encode(
                hmac.new(self.apisecret, p_encoded, hashlib.sha512).digest())
        headers = {'Rest-Key': self.apikey,
                   'Rest-Sign': mac}
        if method == 'GET':
            r = requests.get(API_URLROOT + url,
                              headers=headers,
                              params=params,
                              verify=True)
        elif method == 'POST':
            logging.debug('POSTDATA: ' + str(params))
            r = requests.post(API_URLROOT + url,
                              headers=headers,
                              data=params,
                              verify=True)
        else:
            raise ValueError, "Invalid request type: {}".format(method)
        return r.json()

    def verify_credentials(self):
        """
        Verify credentials work
        """
        return self._query('/verify-credentials', auth=True)

    def accounts(self):
        """
        Get account listing, including balances
        """
        return self._query('/accounts', auth=True)

    def bitcoin_address(self):
        """
        Get your own bitcoin address at BitMe
        """
        return self._query('/bitcoin-address', auth=True)

    def create_order(self, order_type_cd, quantity, rate, 
                     currency_pair='BTCLTC'):
        """
        Create a new order

        :param order_type_cd: The order type ('BID' or 'ASK')
        :param quantity: The quantity of the units to be transacted
        :param rate: The rate at which the order will be executed
        :param currency_pair: The currency pair to use for the order
        """
        params = {'order_type_cd': order_type_cd,
                  'quantity'     : quantity,
                  'currency_pair': currency_pair,
                  'rate'         : rate,
                 }
        return self._query('/order/create', params=params, method='POST',
                           auth=True)

    def open_orders(self):
        """
        Get a list of open orders
        """
        return self._query('/orders/open', auth=True)

    def cancel_order(self, uuid):
        """
        Cancel an order with a given UUID

        :param uuid: The UUID to use (eg. 28330971-6b4e-46b8-be55-9a413774f290)
        """
        return self._query('/order/cancel', params={'uuid':uuid}, method='POST',
                           auth=True)

    def get_transaction(self, txid):
        """
        Gets a transaction with a given id

        :param txid: The Transaction ID (eg. '100')
        """
        return self._query('/transaction/%s' % (txid,), auth=True)

    def get_transactions(self, currency_cd='BTC', limit=10, 
                         order_by='DESC', page='1'):
        """
        Gets a list of transactions

        :param currency_cd: The currency code (eg. 'BTC')
        :param limit: The maximum number to return
        :param order_by: How to order the results ('ASC' or 'DESC')
        :param page: Page number, starting from 1
        """
        return self._query('/transactions/%s' % (currency_cd,), 
                          params = {'limit':limit, 
                                    'orderBy':order_by,
                                    'page':page,
                                   },
                          auth=True)

    def get_order(self, uuid):
        """
        Gets an order with a given UUID

        :param uuid: The UUID to use (eg. 28330971-6b4e-46b8-be55-9a413774f290)
        """
        return self._query('/order/%s' % (uuid,), auth=True)

    def get_orderbook(self, currency_pair='BTCLTC'):
        """
        Gets the current full orderbook for a given currency pair.

        :param currency_pair: The currency pair to pull
        """
        return self._query('/orderbook/%s' % (currency_pair,))

    def get_compat_orderbook(self, currency_pair='BTCLTC'):
        """
        Gets the current Bitcoincharts-compatible orderbook for a given
        currency pair.

        :param currency_pair: The currency pair to pull
        """
        return self._query('/compat/orderbook/%s' % (currency_pair,))

    def get_compat_trades(self, currency_pair='BTCLTC'):
        """
        Gets the current Bitcoincharts-compatible trade array for a given
        currency pair.

        :param currency_pair: The currency pair to pull
        """
        return self._query('/compat/trades/%s' % (currency_pair,))

if __name__ == '__main__':
    import argparse, logging, pprint
    pp = pprint.PrettyPrinter(indent=4)
    parser = argparse.ArgumentParser(description="Bitme API")
    parser.add_argument('--apikeyfile',
                        default='APIKEY',
                        help="The file containing the API key (not the secret!)")
    parser.add_argument('--apisecretfile',
                        help="The file containing the api secret.  if unspecified, access to privileged api calls will not be possible.")
    parser.add_argument('--loglevel',
                        default='INFO',
                        help="Set log level [INFO, DEBUG, etc.]")
    args = parser.parse_args()
    logging.basicConfig(format='%(asctime)s %(message)s',
                        level=args.loglevel)
    API_KEY = None
    try:
        with open(args.apikeyfile, 'r') as f:
            API_KEY = f.read().strip()
    except IOError as e:
        logging.info("Error opening file '{}'.  Make sure it exists and contains your key.".format(args.apikeyfile))
        raise e
    logging.info('API Key: ' + API_KEY)

    # If we were given an API secret, use it
    API_SECRET = None
    if args.apisecretfile:
        try:
            with open(args.apisecretfile, 'r') as f:
                API_SECRET = f.read().strip()
        except IOError as e:
            logging.info("Error opening file '{}'.  Make sure it exists and contains your key.".format(args.apisecretfile))
            raise e

    # Create new API instance
    api = BitmeAPI(API_KEY, API_SECRET)
    logging.info("Verifying credentials")
    response = api.verify_credentials()
    pp.pprint(response)
    logging.info("Listing accounts")
    response = api.accounts()
    pp.pprint(response)
    logging.info("Getting bitcoin address")
    response = api.bitcoin_address()
    pp.pprint(response)
    logging.info("Creating order")
    response = api.create_order('BID', 1, '0.012')
    pp.pprint(response)
    # Save order uuid to cancel later
    uuid_to_cancel = None
    if 'order' in response:
        uuid_to_cancel = response['order']['uuid']
    response = api.open_orders()
    pp.pprint(response)
    if len(response['orders']) > 0 and uuid_to_cancel:
        logging.info('Cancelling order with uuid ' + uuid_to_cancel)
        response = api.cancel_order(uuid=uuid_to_cancel)
        pp.pprint(response)
    logging.info("Getting TXs")
    response = api.get_transactions()
    pp.pprint(response)
    if len(response['transactions']) > 0:
        txid = response['transactions'][0]['id']
        logging.info("Getting TX: %s" % (txid,))
        response = api.get_transaction(txid)
        pp.pprint(response)
    logging.info("Getting orderbook")
    response = api.get_orderbook()
    pp.pprint(response)
    logging.info("Getting compat orderbook")
    response = api.get_compat_orderbook()
    pp.pprint(response)
    logging.info("Getting compat trades")
    response = api.get_compat_trades()
    pp.pprint(response)
    
