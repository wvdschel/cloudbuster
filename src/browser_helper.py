from botasaurus.browser import Driver


class BrowserHelper:
    def __init__(self, proxy=None):
        self.proxy = proxy

    def __enter__(self):
        self.driver = Driver(proxy=self.proxy)
        return self.driver

    def __exit__(self, exception_type, exception_value, traceback):
        self.driver.close()