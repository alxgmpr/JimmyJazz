import threading
from time import sleep, time
from datetime import datetime
from classes.logger import Logger
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Worker(threading.Thread):
    def __init__(self, worker_id, billing, dummy_variant, drop_time, retry, proxy=None):
        super().__init__()
        self.start_time = time()
        self.worker_id = worker_id
        lg = Logger(worker_id=worker_id)
        self.log = lg.log
        self.err = lg.err
        self.suc = lg.suc
        self.drop_time = drop_time
        self.variant = billing['target_variant']
        self.dummy_variant = dummy_variant
        self.retry_delay = retry
        self.build_ids = list()
        self.billing = billing
        self.s = requests.session()
        self.s.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/71.0.3578.98 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Languate': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'DNT': '1'
        }
        self.s.verify = False
        if proxy is not None:
            _ = proxy.split(':')
            if len(_) == 4:
                self.s.proxies = {
                    'http': 'http://{}:{}@{}:{}'.format(_[2], _[3], _[0], _[1]),
                    'https': 'https://{}:{}@{}:{}'.format(_[2], _[3], _[0], _[1])
                }
            elif len(_) == 2:
                self.s.proxies = {
                    'http': 'http://{}:{}'.format(_[0], _[1]),
                    'https': 'https://{}:{}'.format(_[0], _[1])
                }
            else:
                self.err('[error] Malformed proxy {}'.format(proxy))
                exit(-1)

    def add_to_cart(self, variant):
        self.log('Adding to {} cart'.format(variant))
        url = 'http://www.jimmyjazz.com/cart-request/cart/add/{}/1'.format(variant)
        r = self.s.get(url)
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            self.err('[error] Bad status {} while atc'.format(r.status_code))
            if r.status_code == 429:
                self.err('[error] Proxy banned')
                return False
            if r.status_code > 499:
                sleep(self.retry_delay)
                return self.add_to_cart(variant)
            return False

        if r.text == 'false':
            self.err('[error] Product not live yet')
            return False

        j = r.json()
        if j['success'] == 1:
            return True
        else:
            return False

    def remove_from_cart(self, variant):
        self.log('Removing {} from cart'.format(variant))
        url = 'http://www.jimmyjazz.com/cart-request/cart/remove/{}'.format(variant)
        r = self.s.get(url)
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            self.err('[error] Bad status {} while removing'.format(r.status_code))
            if r.status_code == 429:
                self.err('[error] Proxy banned')
                return False
            if r.status_code > 499:
                sleep(self.retry_delay)
                return self.remove_from_cart(variant)
            return False
        j = r.json()
        if j['success'] == 1:
            return True
        else:
            return False

    def go_to_checkout(self):
        self.log('Going to checkout')
        url = 'https://www.jimmyjazz.com/cart/checkout'
        r = self.s.get(url)
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            self.err('[error] Bad status {} while going to checkout'.format(r.status_code))
            if r.status_code == 429:
                self.err('[error] Proxy banned')
                return False
            if r.status_code > 499:
                sleep(self.retry_delay)
                return self.go_to_checkout()
            return False
        else:
            self.build_ids.append(r.text.split('" value="form-')[1].split('"')[0])
            return True

    def submit_checkout(self):
        self.log('Submitting shipping/billing information')
        url = 'https://www.jimmyjazz.com/cart/checkout'
        r = self.s.post(
            url=url,
            data={
                'billing_email': self.billing['email'],
                'billing_email_confirm': self.billing['email'],
                'billing_phone': self.billing['phone'],
                'email_opt_in': 1,
                'shipping_first_name': self.billing['first_name'],
                'shipping_last_name': self.billing['last_name'],
                'shipping_address1': self.billing['address1'],
                'shipping_address2': self.billing['address2'],
                'shipping_city': self.billing['city'],
                'shipping_state': self.billing['state'],
                'shipping_zip': self.billing['zip'],
                'shipping_country_html': 'United States',
                'shipping_method': 0,
                'signature_required': 1,
                'billing_same_as_shipping': 1,
                'billing_first_name': '',
                'billing_last_name': '',
                'billing_country': 'US',
                'billing_address1': '',
                'billing_address2': '',
                'billing_city': '',
                'billing_state': '',
                'billing_zip': '',
                'payment_type': 'credit_card',
                'cc_type': self.billing['type'],
                'cc_number': self.billing['cc_nm'],
                'cc_exp_month': self.billing['month'],
                'cc_exp_year': self.billing['year'],
                'cc_cvv': self.billing['cvv'],
                'gc_num': '',
                'form_build_id': 'form-' + self.build_ids[0],
                'form_id': 'cart_checkout_form'
            }
        )
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            self.err('[error] Bad status {} while submitting billing'.format(r.status_code))
            if r.status_code == 429:
                self.err('[error] Proxy banned')
                return False
            if r.status_code > 499:
                sleep(self.retry_delay)
                return self.submit_checkout()
            return False
        if '/confirm' in r.url:
            self.build_ids.append(r.text.split('" value="form-')[1].split('"')[0])
            return True
        else:
            self.err('[error] expected to go to /confirm but went to {} instead'.format(r.url))
            return False

    def confirm_order(self):
        self.log('Submitting order confirmation')
        url = 'https://www.jimmyjazz.com/cart/confirm'
        r = self.s.post(
            url=url,
            data={
                'form_build_id': 'form-' + self.build_ids[1],
                'form_id': 'cart_confirm_form'
            }
        )
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            self.err('[error] Bad status {} while submitting confirm'.format(r.status_code))
            if r.status_code == 429:
                self.err('[error] Proxy banned')
                return False
            if r.status_code > 499:
                sleep(self.retry_delay)
                return self.confirm_order()
            return False
        else:
            self.log('Went to ' + r.url)
            return True

    def run(self):
        if self.add_to_cart(self.dummy_variant):
            self.suc('Dummy variant was added to cart successfully')
            if self.go_to_checkout():
                self.suc('Navigated to checkout successfully')
                if self.submit_checkout():
                    self.suc('Submitted billing info successfully')
                    self.log('Waiting for drop time {}'.format(self.drop_time.strftime('%x %I:%M:%S%p')))
                    delta = (self.drop_time - datetime.now()).total_seconds()
                    _ = sleep(delta) if delta > 0 else 0
                    while True:
                        if self.add_to_cart(self.variant):
                            self.suc('Added to cart successfully')
                            break
                        self.log('Trying again in {}s'.format(self.retry_delay))
                        sleep(self.retry_delay)
                    if self.remove_from_cart(self.dummy_variant):
                        self.suc('Removed dummy variant from cart successfully')
                        if self.confirm_order():
                            self.suc('Order confirmation was submitted successfully - check your email {}'.format(self.billing['email']))
        self.log('Finished running - {0:.2f}s'.format(abs(time() - self.start_time)))
