import os


class ProxyExtension:
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {"scripts": ["background.js"]},
        "minimum_chrome_version": "76.0.0"
    }
    """

    background_js = """
    var config = {
        mode: "fixed_servers",
        rules: {
            singleProxy: {
                scheme: "http",
                host: "%s",
                port: %d
            },
            bypassList: ["localhost"]
        }
    };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
        callbackFn,
        { urls: ["<all_urls>"] },
        ['blocking']
    );
    """

    def __init__(self, host:str, port:str, user:str, password:str):
        self._dir = os.path.join(os.path.abspath(os.getcwd()), f"extensions\\{host}")
        
        try:
            os.makedirs(self._dir)
        except FileExistsError:
            pass


        try:
            manifest_file = os.path.join(self._dir, "manifest.json")
            
            with open(manifest_file, mode="w") as f:
                f.write(self.manifest_json)

            background_js = self.background_js % (host, port, user, password)
            background_file = os.path.join(self._dir, "background.js")
            with open(background_file, mode="w") as f:
                f.write(background_js)
        except FileNotFoundError:
            pass


    @property
    def directory(self):
        return self._dir
