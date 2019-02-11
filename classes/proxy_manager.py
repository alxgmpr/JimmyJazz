class ProxyManager:
    def __init__(self):
        self.proxies = list()
        self.index = 0

    def load_proxies(self, proxy_list):
        for proxy in proxy_list:
            self.proxies.append(str(proxy).rstrip())
        self.index = 0

    def get_new_proxy(self):
        if len(self.proxies) < 1:
            return None
        if self.index >= len(self.proxies):
            self.index = 0
        proxy = self.proxies[self.index]
        self.index += 1
        return proxy
