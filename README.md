
# undetected_chromedriver #

https://github.com/ultrafunkamsterdam/undetected-chromedriver

Optimized Selenium Chromedriver patch which does not trigger anti-bot services like Distill Network / Imperva / DataDome / Botprotect.io
Automatically downloads the driver binary and patches it.

* **Tested until current chrome beta versions**
* **Works also on Brave Browser and many other Chromium based browsers**
* **Python 3.6++**

## Installation ##
```
pip install undetected-chromedriver
```

## Usage ##

To prevent unnecessary hair-pulling and issue-raising, please mind the **[important note at the end of this document](#important-note) .**

<br>

### The Version 2 way ###
Literally, this is all you have to do. 
Settings are included and your browser executable is found automagically.
This is also the snippet i recommend using in case you experience an issue.
```python
import undetected_chromedriver.v2 as uc
driver = uc.Chrome()
with driver:
    driver.get('https://nowsecure.nl')  # known url using cloudflare's "under attack mode"
```

### The Version 2 more advanced way, including setting profie folder ###
Literally, this is all you have to do. 
If a specified folder does not exist, a NEW profile is created.
Data dirs which are specified like this will not be autoremoved on exit.


```python
import undetected_chromedriver.v2 as uc
options = uc.ChromeOptions()

# setting profile
options.user_data_dir = "c:\\temp\\profile"

# another way to set profile is the below (which takes precedence if both variants are used
options.add_argument('--user-data-dir=c:\\temp\\profile2')

# just some options passing in to skip annoying popups
options.add_argument('--no-first-run --no-service-autorun --password-store=basic')
driver = uc.Chrome(options=options)

with driver:
    driver.get('https://nowsecure.nl')  # known url using cloudflare's "under attack mode"

```


### The Version 2 expert mode, including Devtool/Wire events!  ###
Literally, this is all you have to do. 
You can now listen and subscribe to the low level devtools-protocol.
I just recently found out that is also on planning for future release of the official chromedriver.
However i implemented my own for now. Since i needed it myself for investigation.


```python

import undetected_chromedriver.v2 as uc
from pprint import pformat

driver = uc.Chrome(enable_cdp_event=True)

def mylousyprintfunction(eventdata):
    print(pformat(eventdata))
    
# set the callback to Network.dataReceived to print (yeah not much original)
driver.add_cdp_listener("Network.dataReceived", mylousyprintfunction)
driver.get('https://nowsecure.nl')  # known url using cloudflare's "under attack mode"


def mylousyprintfunction(message):
    print(pformat(message))


# for more inspiration checkout the link below
# https://chromedevtools.github.io/devtools-protocol/1-3/Network/

# and of couse 2 lousy examples
driver.add_cdp_listener('Network.requestWillBeSent', mylousyprintfunction)
driver.add_cdp_listener('Network.dataReceived', mylousyprintfunction)

# hint: a wildcard captures all events!
# driver.add_cdp_listener('*', mylousyprintfunction)

# now all these events will be printed in my console

with driver:
    driver.get('https://nowsecure.nl')


{'method': 'Network.requestWillBeSent',
 'params': {'documentURL': 'https://nowsecure.nl/',
            'frameId': 'F42BAE4BDD4E428EE2503CB5A7B4F700',
            'hasUserGesture': False,
            'initiator': {'type': 'other'},
            'loaderId': '449906A5C736D819123288133F2797E6',
            'request': {'headers': {'Upgrade-Insecure-Requests': '1',
                                    'User-Agent': 'Mozilla/5.0 (Windows NT '
                                                  '10.0; Win64; x64) '
                                                  'AppleWebKit/537.36 (KHTML, '
                                                  'like Gecko) '
                                                  'Chrome/90.0.4430.212 '
                                                  'Safari/537.36',
                                    'sec-ch-ua': '" Not A;Brand";v="99", '
                                                 '"Chromium";v="90", "Google '
                                                 'Chrome";v="90"',
                                    'sec-ch-ua-mobile': '?0'},
                        'initialPriority': 'VeryHigh',
                        'method': 'GET',
                        'mixedContentType': 'none',
                        'referrerPolicy': 'strict-origin-when-cross-origin',
                        'url': 'https://nowsecure.nl/'},
            'requestId': '449906A5C736D819123288133F2797E6',
            'timestamp': 190010.996717,
            'type': 'Document',
            'wallTime': 1621835932.112026}}
{'method': 'Network.requestWillBeSentExtraInfo',
 'params': {'associatedCookies': [],
            'headers': {':authority': 'nowsecure.nl',
                        ':method': 'GET',
                        ':path': '/',
                        ':scheme': 'https',
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                        'accept-encoding': 'gzip, deflate, br',
                        'accept-language': 'en-US,en;q=0.9',
                        'sec-ch-ua': '" Not A;Brand";v="99", '
                                     '"Chromium";v="90", "Google '
                                     'Chrome";v="90"',
                        'sec-ch-ua-mobile': '?0',
                        'sec-fetch-dest': 'document',
                        'sec-fetch-mode': 'navigate',
                        'sec-fetch-site': 'none',
                        'sec-fetch-user': '?1',
                        'upgrade-insecure-requests': '1',
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; '
                                      'x64) AppleWebKit/537.36 (KHTML, like '
                                      'Gecko) Chrome/90.0.4430.212 '
                                      'Safari/537.36'},
            'requestId': '449906A5C736D819123288133F2797E6'}}
{'method': 'Network.responseReceivedExtraInfo',
 'params': {'blockedCookies': [],
            'headers': {'alt-svc': 'h3-27=":443"; ma=86400, h3-28=":443"; '
                                   'ma=86400, h3-29=":443"; ma=86400',
                        'cache-control': 'private, max-age=0, no-store, '
                                         'no-cache, must-revalidate, '
                                         'post-check=0, pre-check=0',
                        'cf-ray': '65444b779ae6546f-LHR',
                        'cf-request-id': '0a3e8d7eba0000546ffd3fa000000001',
                        'content-type': 'text/html; charset=UTF-8',
                        'date': 'Mon, 24 May 2021 05:58:53 GMT',
                        'expect-ct': 'max-age=604800, '
                                     'report-uri="https://report-uri.cloudflare.com/cdn-cgi/beacon/expect-ct"',
                        'expires': 'Thu, 01 Jan 1970 00:00:01 GMT',
                        'nel': '{"report_to":"cf-nel","max_age":604800}',
                        'permissions-policy': 'accelerometer=(),autoplay=(),camera=(),clipboard-read=(),clipboard-write=(),fullscreen=(),geolocation=(),gyroscope=(),hid=(),interest-cohort=(),magnetometer=(),microphone=(),payment=(),publickey-credentials-get=(),screen-wake-lock=(),serial=(),sync-xhr=(),usb=()',
                        'report-to': '{"endpoints":[{"url":"https:\\/\\/a.nel.cloudflare.com\\/report?s=CAfobYlmWImQ90e%2B4BFBhpPYL%2FyGyBvkcWAj%2B%2FVOLoEq0NVrD5jU9m5pi%2BKI%2BOAnINLPXOCoX2psLphA5Z38aZzWNr3eW%2BDTIK%2FQidc%3D"}],"group":"cf-nel","max_age":604800}',
                        'server': 'cloudflare',
                        'vary': 'Accept-Encoding',
                        'x-frame-options': 'SAMEORIGIN'},
            'requestId': '449906A5C736D819123288133F2797E6',
            'resourceIPAddressSpace': 'Public'}}
{'method': 'Network.responseReceived',
 'params': {'frameId': 'F42BAE4BDD4E428EE2503CB5A7B4F700',
            'loaderId': '449906A5C736D819123288133F2797E6',
            'requestId': '449906A5C736D819123288133F2797E6',
            'response': {'connectionId': 158,
                         'connectionReused': False,
                         'encodedDataLength': 851,
                         'fromDiskCache': False,
                         'fromPrefetchCache': False,
                         'fromServiceWorker': False,
                         'headers': {'alt-svc': 'h3-27=":443"; ma=86400, '
                                                'h3-28=":443"; ma=86400, '
                                                'h3-29=":443"; ma=86400',
                                     'cache-control': 'private, max-age=0, '
                                                      'no-store, no-cache, '
                                                      'must-revalidate, '
                                                      'post-check=0, '
                                                      'pre-check=0',
                                     'cf-ray': '65444b779ae6546f-LHR',
                                     'cf-request-id': '0a3e8d7eba0000546ffd3fa000000001',
                                     'content-type': 'text/html; charset=UTF-8',
                                     'date': 'Mon, 24 May 2021 05:58:53 GMT',
                                     'expect-ct': 'max-age=604800, '
                                                  'report-uri="https://report-uri.cloudflare.com/cdn-cgi/beacon/expect-ct"',
                                     'expires': 'Thu, 01 Jan 1970 00:00:01 GMT',
                                     'nel': '{"report_to":"cf-nel","max_age":604800}',
                                     'permissions-policy': 'accelerometer=(),autoplay=(),camera=(),clipboard-read=(),clipboard-write=(),fullscreen=(),geolocation=(),gyroscope=(),hid=(),interest-cohort=(),magnetometer=(),microphone=(),payment=(),publickey-credentials-get=(),screen-wake-lock=(),serial=(),sync-xhr=(),usb=()',
                                     'report-to': '{"endpoints":[{"url":"https:\\/\\/a.nel.cloudflare.com\\/report?s=CAfobYlmWImQ90e%2B4BFBhpPYL%2FyGyBvkcWAj%2B%2FVOLoEq0NVrD5jU9m5pi%2BKI%2BOAnINLPXOCoX2psLphA5Z38aZzWNr3eW%2BDTIK%2FQidc%3D"}],"group":"cf-nel","max_age":604800}',
                                     'server': 'cloudflare',
                                     'vary': 'Accept-Encoding',
                                     'x-frame-options': 'SAMEORIGIN'},
                         'mimeType': 'text/html',
                         'protocol': 'h2',
                         'remoteIPAddress': '104.21.5.197',
                         'remotePort': 443,
                         'requestHeaders': {':authority': 'nowsecure.nl',
                                            ':method': 'GET',
                                            ':path': '/',
                                            ':scheme': 'https',
                                            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                                            'accept-encoding': 'gzip, deflate, '
                                                               'br',
                                            'accept-language': 'en-US,en;q=0.9',
                                            'sec-ch-ua': '" Not '
                                                         'A;Brand";v="99", '
                                                         '"Chromium";v="90", '
                                                         '"Google '
                                                         'Chrome";v="90"',
                                            'sec-ch-ua-mobile': '?0',
                                            'sec-fetch-dest': 'document',
                                            'sec-fetch-mode': 'navigate',
                                            'sec-fetch-site': 'none',
                                            'sec-fetch-user': '?1',
                                            'upgrade-insecure-requests': '1',
                                            'user-agent': 'Mozilla/5.0 '
                                                          '(Windows NT 10.0; '
                                                          'Win64; x64) '
                                                          'AppleWebKit/537.36 '
                                                          '(KHTML, like Gecko) '
                                                          'Chrome/90.0.4430.212 '
                                                          'Safari/537.36'},
                         'responseTime': 1621835932177.923,
                         'securityDetails': {'certificateId': 0,
                                             'certificateTransparencyCompliance': 'compliant',
                                             'cipher': 'AES_128_GCM',
                                             'issuer': 'Cloudflare Inc ECC '
                                                       'CA-3',
                                             'keyExchange': '',
                                             'keyExchangeGroup': 'X25519',
                                             'protocol': 'TLS 1.3',
                                             'sanList': ['sni.cloudflaressl.com',
                                                         '*.nowsecure.nl',
                                                         'nowsecure.nl'],
                                             'signedCertificateTimestampList': [{'hashAlgorithm': 'SHA-256',
                                                                                 'logDescription': 'Google '
                                                                                                   "'Argon2021' "
                                                                                                   'log',
                                                                                 'logId': 'F65C942FD1773022145418083094568EE34D131933BFDF0C2F200BCC4EF164E3',
                                                                                 'origin': 'Embedded '
                                                                                           'in '
                                                                                           'certificate',
                                                                                 'signatureAlgorithm': 'ECDSA',
                                                                                 'signatureData': '30450221008A25458182A6E7F608FE1492086762A367381E94137952FFD621BA2E60F7E2F702203BCDEBCE1C544DECF0A113DE12B33E299319E6240426F38F08DFC04EF2E42825',
                                                                                 'status': 'Verified',
                                                                                 'timestamp': 1598706372839.0},
                                                                                {'hashAlgorithm': 'SHA-256',
                                                                                 'logDescription': 'DigiCert '
                                                                                                   'Yeti2021 '
                                                                                                   'Log',
                                                                                 'logId': '5CDC4392FEE6AB4544B15E9AD456E61037FBD5FA47DCA17394B25EE6F6C70ECA',
                                                                                 'origin': 'Embedded '
                                                                                           'in '
                                                                                           'certificate',
                                                                                 'signatureAlgorithm': 'ECDSA',
                                                                                 'signatureData': '3046022100A95A49C7435DBFC73406AC409062C27269E6E69F443A2213F3A085E3BCBD234A022100DEA878296F8A1DB43546DC1865A4C5AD2B90664A243AE0A3A6D4925802EE68A8',
                                                                                 'status': 'Verified',
                                                                                 'timestamp': 1598706372823.0}],
                                             'subjectName': 'sni.cloudflaressl.com',
                                             'validFrom': 1598659200,
                                             'validTo': 1630238400},
                         'securityState': 'secure',
                         'status': 503,
                         'statusText': '',
                         'timing': {'connectEnd': 40.414,
                                    'connectStart': 0,
                                    'dnsEnd': 0,
                                    'dnsStart': 0,
                                    'proxyEnd': -1,
                                    'proxyStart': -1,
                                    'pushEnd': 0,
                                    'pushStart': 0,
                                    'receiveHeadersEnd': 60.361,
                                    'requestTime': 190011.002239,
                                    'sendEnd': 41.348,
                                    'sendStart': 41.19,
                                    'sslEnd': 40.405,
                                    'sslStart': 10.853,
                                    'workerFetchStart': -1,
                                    'workerReady': -1,
                                    'workerRespondWithSettled': -1,
                                    'workerStart': -1},
                         'url': 'https://nowsecure.nl/'},
            'timestamp': 190011.06449,
            'type': 'Document'}}
{'method': 'Page.frameStartedLoading',
 'params': {'frameId': 'F42BAE4BDD4E428EE2503CB5A7B4F700'}}
{'method': 'Page.frameNavigated',
 'params': {'frame': {'adFrameType': 'none',
                      'crossOriginIsolatedContextType': 'NotIsolated',
                      'domainAndRegistry': 'nowsecure.nl',
                      'gatedAPIFeatures': ['SharedArrayBuffers',
                                           'SharedArrayBuffersTransferAllowed'],
                      'id': 'F42BAE4BDD4E428EE2503CB5A7B4F700',
                      'loaderId': '449906A5C736D819123288133F2797E6',
                      'mimeType': 'text/html',
                      'secureContextType': 'Secure',
                      'securityOrigin': 'https://nowsecure.nl',
                      'url': 'https://nowsecure.nl/'}}}
{'method': 'Network.dataReceived',
 'params': {'dataLength': 9835,
            'encodedDataLength': 0,
            'requestId': '449906A5C736D819123288133F2797E6',
            'timestamp': 190011.093343}}
{'method': 'Network.loadingFinished',
 'params': {'encodedDataLength': 10713,
            'requestId': '449906A5C736D819123288133F2797E6',
            'shouldReportCorbBlocking': False,
            'timestamp': 190011.064011}}
{'method': 'Network.requestWillBeSent',
 'params': {'documentURL': 'https://nowsecure.nl/',
            'frameId': 'F42BAE4BDD4E428EE2503CB5A7B4F700',
            'hasUserGesture': False,
            'initiator': {'stack': {'callFrames': [{'columnNumber': 51,
                                                    'functionName': '',
                                                    'lineNumber': 114,
                                                    'scriptId': '8',
                                                    'url': 'https://nowsecure.nl/'},
                                                   {'columnNumber': 9,
                                                    'functionName': '',
                                                    'lineNumber': 115,
                                                    'scriptId': '8',
                                                    'url': 'https://nowsecure.nl/'}]},
                          'type': 'script'},
            'loaderId': '449906A5C736D819123288133F2797E6',
            'request': {'headers': {'Referer': 'https://nowsecure.nl/',
                                    'User-Agent': 'Mozilla/5.0 (Windows NT '
                                                  '10.0; Win64; x64) '
                                                  'AppleWebKit/537.36 (KHTML, '
                                                  'like Gecko) '
                                                  'Chrome/90.0.4430.212 '
                                                  'Safari/537.36',
                                    'sec-ch-ua': '" Not A;Brand";v="99", '
                                                 '"Chromium";v="90", "Google '
                                                 'Chrome";v="90"',
                                    'sec-ch-ua-mobile': '?0'},
                        'initialPriority': 'Low',
                        'method': 'GET',
                        'mixedContentType': 'none',
                        'referrerPolicy': 'strict-origin-when-cross-origin',
                        'url': 'https://nowsecure.nl/cdn-cgi/challenge-platform/h/b/orchestrate/jsch/v1?ray=65444b779ae6546f'},
            'requestId': '17180.2',
            'timestamp': 190011.106133,
            'type': 'Script',
            'wallTime': 1621835932.221325}}
{'method': 'Network.requestWillBeSent',
 'params': {'documentURL': 'https://nowsecure.nl/',
            'frameId': 'F42BAE4BDD4E428EE2503CB5A7B4F700',
            'hasUserGesture': False,
            'initiator': {'columnNumber': 13,
                          'lineNumber': 117,
                          'type': 'parser',
                          'url': 'https://nowsecure.nl/'},
            'loaderId': '449906A5C736D819123288133F2797E6',
            'request': {'headers': {'Referer': 'https://nowsecure.nl/',
                                    'User-Agent': 'Mozilla/5.0 (Windows NT '
                                                  '10.0; Win64; x64) '
                                                  'AppleWebKit/537.36 (KHTML, '
                                                  'like Gecko) '
                                                  'Chrome/90.0.4430.212 '
                                                  'Safari/537.36',
                                    'sec-ch-ua': '" Not A;Brand";v="99", '
                                                 '"Chromium";v="90", "Google '
                                                 'Chrome";v="90"',
                                    'sec-ch-ua-mobile': '?0'},
                        'initialPriority': 'Low',
                        'method': 'GET',
                        'mixedContentType': 'none',
                        'referrerPolicy': 'strict-origin-when-cross-origin',
                        'url': 'https://nowsecure.nl/cdn-cgi/images/trace/jschal/js/transparent.gif?ray=65444b779ae6546f'},
            'requestId': '17180.3',
            'timestamp': 190011.106911,
            'type': 'Image',
            'wallTime': 1621835932.222102}}
{'method': 'Network.requestWillBeSent',
 'params': {'documentURL': 'https://nowsecure.nl/',
            'frameId': 'F42BAE4BDD4E428EE2503CB5A7B4F700',
            'hasUserGesture': False,
            'initiator': {'type': 'parser', 'url': 'https://nowsecure.nl/'},
            'loaderId': '449906A5C736D819123288133F2797E6',
            'request': {'headers': {'Referer': 'https://nowsecure.nl/',
                                    'User-Agent': 'Mozilla/5.0 (Windows NT '
                                                  '10.0; Win64; x64) '
                                                  'AppleWebKit/537.36 (KHTML, '
                                                  'like Gecko) '
                                                  'Chrome/90.0.4430.212 '
                                                  'Safari/537.36',
                                    'sec-ch-ua': '" Not A;Brand";v="99", '
                                                 '"Chromium";v="90", "Google '
                                                 'Chrome";v="90"',
                                    'sec-ch-ua-mobile': '?0'},
                        'initialPriority': 'Low',
                        'method': 'GET',
                        'mixedContentType': 'none',
                        'referrerPolicy': 'strict-origin-when-cross-origin',
                        'url': 'https://nowsecure.nl/cdn-cgi/images/trace/jschal/nojs/transparent.gif?ray=65444b779ae6546f'},
            'requestId': '17180.4',
            'timestamp': 190011.109527,
            'type': 'Image',
            'wallTime': 1621835932.224719}}
{'method': 'Page.domContentEventFired', 'params': {'timestamp': 190011.110345}}
{'method': 'Network.requestWillBeSentExtraInfo',
 'params': {'associatedCookies': [],
            'clientSecurityState': {'initiatorIPAddressSpace': 'Public',
                                    'initiatorIsSecureContext': True,
                                    'privateNetworkRequestPolicy': 'WarnFromInsecureToMorePrivate'},
            'headers': {':authority': 'nowsecure.nl',
                        ':method': 'GET',
                        ':path': '/cdn-cgi/images/trace/jschal/js/transparent.gif?ray=65444b779ae6546f',
                        ':scheme': 'https',
                        'accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                        'accept-encoding': 'gzip, deflate, br',
                        'accept-language': 'en-US,en;q=0.9',
                        'referer': 'https://nowsecure.nl/',
                        'sec-ch-ua': '" Not A;Brand";v="99", '
                                     '"Chromium";v="90", "Google '
                                     'Chrome";v="90"',
                        'sec-ch-ua-mobile': '?0',
                        'sec-fetch-dest': 'image',
                        'sec-fetch-mode': 'no-cors',
                        'sec-fetch-site': 'same-origin',
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; '
                                      'x64) AppleWebKit/537.36 (KHTML, like '
                                      'Gecko) Chrome/90.0.4430.212 '
                                      'Safari/537.36'},
            'requestId': '17180.3'}}
{'method': 'Network.requestWillBeSentExtraInfo',
 'params': {'associatedCookies': [],
            'clientSecurityState': {'initiatorIPAddressSpace': 'Public',
                                    'initiatorIsSecureContext': True,
                                    'privateNetworkRequestPolicy': 'WarnFromInsecureToMorePrivate'},
            'headers': {':authority': 'nowsecure.nl',
                        ':method': 'GET',
                        ':path': '/cdn-cgi/challenge-platform/h/b/orchestrate/jsch/v1?ray=65444b779ae6546f',
                        ':scheme': 'https',
                        'accept': '*/*',
                        'accept-encoding': 'gzip, deflate, br',
                        'accept-language': 'en-US,en;q=0.9',
                        'referer': 'https://nowsecure.nl/',
                        'sec-ch-ua': '" Not A;Brand";v="99", '
                                     '"Chromium";v="90", "Google '
                                     'Chrome";v="90"',
                        'sec-ch-ua-mobile': '?0',
                        'sec-fetch-dest': 'script',
                        'sec-fetch-mode': 'no-cors',
                        'sec-fetch-site': 'same-origin',
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; '
                                      'x64) AppleWebKit/537.36 (KHTML, like '
                                      'Gecko) Chrome/90.0.4430.212 '
                                      'Safari/537.36'},
            'requestId': '17180.2'}}
{'method': 'Network.requestWillBeSentExtraInfo',
 'params': {'associatedCookies': [],
            'clientSecurityState': {'initiatorIPAddressSpace': 'Public',
                                    'initiatorIsSecureContext': True,
                                    'privateNetworkRequestPolicy': 'WarnFromInsecureToMorePrivate'},
            'headers': {':authority': 'nowsecure.nl',
                        ':method': 'GET',
                        ':path': '/cdn-cgi/images/trace/jschal/nojs/transparent.gif?ray=65444b779ae6546f',
                        ':scheme': 'https',
                        'accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                        'accept-encoding': 'gzip, deflate, br',
                        'accept-language': 'en-US,en;q=0.9',
                        'referer': 'https://nowsecure.nl/',
                        'sec-ch-ua': '" Not A;Brand";v="99", '
                                     '"Chromium";v="90", "Google '
                                     'Chrome";v="90"',
                        'sec-ch-ua-mobile': '?0',
                        'sec-fetch-dest': 'image',
                        'sec-fetch-mode': 'no-cors',
                        'sec-fetch-site': 'same-origin',
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; '
                                      'x64) AppleWebKit/537.36 (KHTML, like '
                                      'Gecko) Chrome/90.0.4430.212 '
                                      'Safari/537.36'},
            'requestId': '17180.4'}}
{'method': 'Network.responseReceivedExtraInfo',
 'params': {'blockedCookies': [],
            'headers': {'accept-ranges': 'bytes',
                        'cache-control': 'max-age=7200\npublic',
                        'cf-ray': '65444b781d1de604-LHR',
                        'content-length': '42',
                        'content-type': 'image/gif',
                        'date': 'Mon, 24 May 2021 05:58:53 GMT',
                        'etag': '"60a4d856-2a"',
                        'expires': 'Mon, 24 May 2021 07:58:53 GMT',
                        'last-modified': 'Wed, 19 May 2021 09:20:22 GMT',
                        'server': 'cloudflare',
                        'vary': 'Accept-Encoding',
                        'x-content-type-options': 'nosniff',
                        'x-frame-options': 'DENY'},
            'requestId': '17180.3',
            'resourceIPAddressSpace': 'Public'}}
{'method': 'Network.responseReceivedExtraInfo',
 'params': {'blockedCookies': [],
            'headers': {'accept-ranges': 'bytes',
                        'cache-control': 'max-age=7200\npublic',
                        'cf-ray': '65444b781d1fe604-LHR',
                        'content-length': '42',
                        'content-type': 'image/gif',
                        'date': 'Mon, 24 May 2021 05:58:53 GMT',
                        'etag': '"60a4d856-2a"',
                        'expires': 'Mon, 24 May 2021 07:58:53 GMT',
                        'last-modified': 'Wed, 19 May 2021 09:20:22 GMT',
                        'server': 'cloudflare',
                        'vary': 'Accept-Encoding',
                        'x-content-type-options': 'nosniff',
                        'x-frame-options': 'DENY'},
            'requestId': '17180.4',
            'resourceIPAddressSpace': 'Public'}}
{'method': 'Network.resourceChangedPriority',
 'params': {'newPriority': 'High',
            'requestId': '17180.4',
            'timestamp': 190011.171057}}
{'method': 'Network.responseReceived',
 'params': {'frameId': 'F42BAE4BDD4E428EE2503CB5A7B4F700',
            'loaderId': '449906A5C736D819123288133F2797E6',
            'requestId': '17180.3',
            'response': {'connectionId': 0,
                         'connectionReused': False,
                         'encodedDataLength': 214,
                         'fromDiskCache': False,
                         'fromPrefetchCache': False,
                         'fromServiceWorker': False,
                         'headers': {'accept-ranges': 'bytes',
                                     'cache-control': 'max-age=7200\npublic',
                                     'cf-ray': '65444b781d1de604-LHR',
                                     'content-length': '42',
                                     'content-type': 'image/gif',
                                     'date': 'Mon, 24 May 2021 05:58:53 GMT',
                                     'etag': '"60a4d856-2a"',
                                     'expires': 'Mon, 24 May 2021 07:58:53 GMT',
                                     'last-modified': 'Wed, 19 May 2021 '
                                                      '09:20:22 GMT',
                                     'server': 'cloudflare',
                                     'vary': 'Accept-Encoding',
                                     'x-content-type-options': 'nosniff',
                                     'x-frame-options': 'DENY'},
                         'mimeType': 'image/gif',
                         'protocol': 'h3-29',
                         'remoteIPAddress': '104.21.5.197',
                         'remotePort': 443,
                         'requestHeaders': {':authority': 'nowsecure.nl',
                                            ':method': 'GET',
                                            ':path': '/cdn-cgi/images/trace/jschal/js/transparent.gif?ray=65444b779ae6546f',
                                            ':scheme': 'https',
                                            'accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                                            'accept-encoding': 'gzip, deflate, '
                                                               'br',
                                            'accept-language': 'en-US,en;q=0.9',
                                            'referer': 'https://nowsecure.nl/',
                                            'sec-ch-ua': '" Not '
                                                         'A;Brand";v="99", '
                                                         '"Chromium";v="90", '
                                                         '"Google '
                                                         'Chrome";v="90"',
                                            'sec-ch-ua-mobile': '?0',
                                            'sec-fetch-dest': 'image',
                                            'sec-fetch-mode': 'no-cors',
                                            'sec-fetch-site': 'same-origin',
                                            'user-agent': 'Mozilla/5.0 '
                                                          '(Windows NT 10.0; '
                                                          'Win64; x64) '
                                                          'AppleWebKit/537.36 '
                                                          '(KHTML, like Gecko) '
                                                          'Chrome/90.0.4430.212 '
                                                          'Safari/537.36'},
                         'responseTime': 1621835932265.169,
                         'securityDetails': {'certificateId': 0,
                                             'certificateTransparencyCompliance': 'compliant',
                                             'cipher': 'AES_128_GCM',
                                             'issuer': 'Cloudflare Inc ECC '
                                                       'CA-3',
                                             'keyExchange': '',
                                             'keyExchangeGroup': 'X25519',
                                             'protocol': 'QUIC',
                                             'sanList': ['sni.cloudflaressl.com',
                                                         '*.nowsecure.nl',
                                                         'nowsecure.nl'],
                                             'signedCertificateTimestampList': [{'hashAlgorithm': 'SHA-256',
                                                                                 'logDescription': 'Google '
                                                                                                   "'Argon2021' "
                                                                                                   'log',
                                                                                 'logId': 'F65C942FD1773022145418083094568EE34D131933BFDF0C2F200BCC4EF164E3',
                                                                                 'origin': 'Embedded '
                                                                                           'in '
                                                                                           'certificate',
                                                                                 'signatureAlgorithm': 'ECDSA',
                                                                                 'signatureData': '30450221008A25458182A6E7F608FE1492086762A367381E94137952FFD621BA2E60F7E2F702203BCDEBCE1C544DECF0A113DE12B33E299319E6240426F38F08DFC04EF2E42825',
                                                                                 'status': 'Verified',
                                                                                 'timestamp': 1598706372839.0},
                                                                                {'hashAlgorithm': 'SHA-256',
                                                                                 'logDescription': 'DigiCert '
                                                                                                   'Yeti2021 '
                                                                                                   'Log',
                                                                                 'logId': '5CDC4392FEE6AB4544B15E9AD456E61037FBD5FA47DCA17394B25EE6F6C70ECA',
                                                                                 'origin': 'Embedded '
                                                                                           'in '
                                                                                           'certificate',
                                                                                 'signatureAlgorithm': 'ECDSA',
                                                                                 'signatureData': '3046022100A95A49C7435DBFC73406AC409062C27269E6E69F443A2213F3A085E3BCBD234A022100DEA878296F8A1DB43546DC1865A4C5AD2B90664A243AE0A3A6D4925802EE68A8',
                                                                                 'status': 'Verified',
                                                                                 'timestamp': 1598706372823.0}],
                                             'subjectName': 'sni.cloudflaressl.com',
                                             'validFrom': 1598659200,
                                             'validTo': 1630238400},
                         'securityState': 'secure',
                         'status': 200,
                         'statusText': '',
                         'timing': {'connectEnd': 26.087,
                                    'connectStart': 0,
                                    'dnsEnd': 0,
                                    'dnsStart': 0,
                                    'proxyEnd': -1,
                                    'proxyStart': -1,
                                    'pushEnd': 0,
                                    'pushStart': 0,
                                    'receiveHeadersEnd': 40.709,
                                    'requestTime': 190011.109386,
                                    'sendEnd': 26.346,
                                    'sendStart': 26.182,
                                    'sslEnd': 26.087,
                                    'sslStart': 0,
                                    'workerFetchStart': -1,
                                    'workerReady': -1,
                                    'workerRespondWithSettled': -1,
                                    'workerStart': -1},
                         'url': 'https://nowsecure.nl/cdn-cgi/images/trace/jschal/js/transparent.gif?ray=65444b779ae6546f'},
            'timestamp': 190011.174536,
            'type': 'Image'}}
{'method': 'Network.dataReceived',
 'params': {'dataLength': 42,
            'encodedDataLength': 0,
            'requestId': '17180.3',
            'timestamp': 190011.174737}}
{'method': 'Network.dataReceived',
 'params': {'dataLength': 0,
            'encodedDataLength': 44,
            'requestId': '17180.3',
            'timestamp': 190011.17524}}
{'method': 'Network.loadingFinished',
 'params': {'encodedDataLength': 258,
            'requestId': '17180.3',
            'shouldReportCorbBlocking': False,
            'timestamp': 190011.152073}}
{'method': 'Network.responseReceived',
 'params': {'frameId': 'F42BAE4BDD4E428EE2503CB5A7B4F700',
            'loaderId': '449906A5C736D819123288133F2797E6',
            'requestId': '17180.4',
            'response': {'connectionId': 0,
                         'connectionReused': True,
                         'encodedDataLength': 178,
                         'fromDiskCache': False,
                         'fromPrefetchCache': False,
                         'fromServiceWorker': False,
                         'headers': {'accept-ranges': 'bytes',
                                     'cache-control': 'max-age=7200\npublic',
                                     'cf-ray': '65444b781d1fe604-LHR',
                                     'content-length': '42',
                                     'content-type': 'image/gif',
                                     'date': 'Mon, 24 May 2021 05:58:53 GMT',
                                     'etag': '"60a4d856-2a"',
                                     'expires': 'Mon, 24 May 2021 07:58:53 GMT',
                                     'last-modified': 'Wed, 19 May 2021 '
                                                      '09:20:22 GMT',
                                     'server': 'cloudflare',
                                     'vary': 'Accept-Encoding',
                                     'x-content-type-options': 'nosniff',
                                     'x-frame-options': 'DENY'},
                         'mimeType': 'image/gif',
                         'protocol': 'h3-29',
                         'remoteIPAddress': '104.21.5.197',
                         'remotePort': 443,
                         'requestHeaders': {':authority': 'nowsecure.nl',
                                            ':method': 'GET',
                                            ':path': '/cdn-cgi/images/trace/jschal/nojs/transparent.gif?ray=65444b779ae6546f',
                                            ':scheme': 'https',
                                            'accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                                            'accept-encoding': 'gzip, deflate, '
                                                               'br',
                                            'accept-language': 'en-US,en;q=0.9',
                                            'referer': 'https://nowsecure.nl/',
                                            'sec-ch-ua': '" Not '
                                                         'A;Brand";v="99", '
                                                         '"Chromium";v="90", '
                                                         '"Google '
                                                         'Chrome";v="90"',
                                            'sec-ch-ua-mobile': '?0',
                                            'sec-fetch-dest': 'image',
                                            'sec-fetch-mode': 'no-cors',
                                            'sec-fetch-site': 'same-origin',
                                            'user-agent': 'Mozilla/5.0 '
                                                          '(Windows NT 10.0; '
                                                          'Win64; x64) '
                                                          'AppleWebKit/537.36 '
                                                          '(KHTML, like Gecko) '
                                                          'Chrome/90.0.4430.212 '
                                                          'Safari/537.36'},
                         'responseTime': 1621835932268.067,
                         'securityDetails': {'certificateId': 0,
                                             'certificateTransparencyCompliance': 'compliant',
                                             'cipher': 'AES_128_GCM',
                                             'issuer': 'Cloudflare Inc ECC '
                                                       'CA-3',
                                             'keyExchange': '',
                                             'keyExchangeGroup': 'X25519',
                                             'protocol': 'QUIC',
                                             'sanList': ['sni.cloudflaressl.com',
                                                         '*.nowsecure.nl',
                                                         'nowsecure.nl'],
                                             'signedCertificateTimestampList': [{'hashAlgorithm': 'SHA-256',
                                                                                 'logDescription': 'Google '
                                                                                                   "'Argon2021' "
                                                                                                   'log',
                                                                                 'logId': 'F65C942FD1773022145418083094568EE34D131933BFDF0C2F200BCC4EF164E3',
                                                                                 'origin': 'Embedded '
                                                                                           'in '
                                                                                           'certificate',
                                                                                 'signatureAlgorithm': 'ECDSA',
                                                                                 'signatureData': '30450221008A25458182A6E7F608FE1492086762A367381E94137952FFD621BA2E60F7E2F702203BCDEBCE1C544DECF0A113DE12B33E299319E6240426F38F08DFC04EF2E42825',
                                                                                 'status': 'Verified',
                                                                                 'timestamp': 1598706372839.0},
                                                                                {'hashAlgorithm': 'SHA-256',
                                                                                 'logDescription': 'DigiCert '
                                                                                                   'Yeti2021 '
                                                                                                   'Log',
                                                                                 'logId': '5CDC4392FEE6AB4544B15E9AD456E61037FBD5FA47DCA17394B25EE6F6C70ECA',
                                                                                 'origin': 'Embedded '
                                                                                           'in '
                                                                                           'certificate',
                                                                                 'signatureAlgorithm': 'ECDSA',
                                                                                 'signatureData': '3046022100A95A49C7435DBFC73406AC409062C27269E6E69F443A2213F3A085E3BCBD234A022100DEA878296F8A1DB43546DC1865A4C5AD2B90664A243AE0A3A6D4925802EE68A8',
                                                                                 'status': 'Verified',
                                                                                 'timestamp': 1598706372823.0}],
                                             'subjectName': 'sni.cloudflaressl.com',
                                             'validFrom': 1598659200,
                                             'validTo': 1630238400},
                         'securityState': 'secure',
                         'status': 200,
                         'statusText': '',
                         'timing': {'connectEnd': -1,
                                    'connectStart': -1,
                                    'dnsEnd': -1,
                                    'dnsStart': -1,
                                    'proxyEnd': -1,
                                    'proxyStart': -1,
                                    'pushEnd': 0,
                                    'pushStart': 0,
                                    'receiveHeadersEnd': 42.415,
                                    'requestTime': 190011.110341,
                                    'sendEnd': 25.713,
                                    'sendStart': 25.609,
                                    'sslEnd': -1,
                                    'sslStart': -1,
                                    'workerFetchStart': -1,
                                    'workerReady': -1,
                                    'workerRespondWithSettled': -1,
                                    'workerStart': -1},
                         'url': 'https://nowsecure.nl/cdn-cgi/images/trace/jschal/nojs/transparent.gif?ray=65444b779ae6546f'},
            'timestamp': 190011.175727,
            'type': 'Image'}}
{'method': 'Network.dataReceived',
 'params': {'dataLength': 42,
            'encodedDataLength': 0,
            'requestId': '17180.4',
            'timestamp': 190011.175856}}
{'method': 'Network.dataReceived',
 'params': {'dataLength': 0,
            'encodedDataLength': 44,
            'requestId': '17180.4',
            'timestamp': 190011.176133}}
{'method': 'Network.loadingFinished',
 'params': {'encodedDataLength': 222,
            'requestId': '17180.4',
            'shouldReportCorbBlocking': False,
            'timestamp': 190011.153335}}
{'method': 'Network.responseReceivedExtraInfo',
 'params': {'blockedCookies': [],
            'headers': {'alt-svc': 'h3-27=":443"; ma=86400, h3-28=":443"; '
                                   'ma=86400, h3-29=":443"; ma=86400',
                        'cache-control': 'max-age=0, must-revalidate',
                        'cf-ray': '65444b781d1ee604-LHR',
                        'cf-request-id': '0a3e8d7f140000e60496387000000001',
                        'content-encoding': 'br',
                        'content-type': 'text/javascript',
                        'date': 'Mon, 24 May 2021 05:58:53 GMT',
                        'expect-ct': 'max-age=604800, '
                                     'report-uri="https://report-uri.cloudflare.com/cdn-cgi/beacon/expect-ct"',
                        'nel': '{"report_to":"cf-nel","max_age":604800}',
                        'report-to': '{"endpoints":[{"url":"https:\\/\\/a.nel.cloudflare.com\\/report?s=ZtI%2Bx8B7DpI8%2FsDA72maecFVCPvIsfBOyJjT8weyiqfmrHrmcBYpRhc%2FI%2F6JmIlnxW%2F%2BBohxLi1F8mpjAUabJ0kXLYnmjGKp2Ndio9M%3D"}],"group":"cf-nel","max_age":604800}',
                        'server': 'cloudflare',
                        'vary': 'Accept-Encoding'},
            'requestId': '17180.2',
            'resourceIPAddressSpace': 'Public'}}
{'method': 'Network.responseReceived',
 'params': {'frameId': 'F42BAE4BDD4E428EE2503CB5A7B4F700',
            'loaderId': '449906A5C736D819123288133F2797E6',
            'requestId': '17180.2',
            'response': {'connectionId': 0,
                         'connectionReused': True,
                         'encodedDataLength': 510,
                         'fromDiskCache': False,
                         'fromPrefetchCache': False,
                         'fromServiceWorker': False,
                         'headers': {'alt-svc': 'h3-27=":443"; ma=86400, '
                                                'h3-28=":443"; ma=86400, '
                                                'h3-29=":443"; ma=86400',
                                     'cache-control': 'max-age=0, '
                                                      'must-revalidate',
                                     'cf-ray': '65444b781d1ee604-LHR',
                                     'cf-request-id': '0a3e8d7f140000e60496387000000001',
                                     'content-encoding': 'br',
                                     'content-type': 'text/javascript',
                                     'date': 'Mon, 24 May 2021 05:58:53 GMT',
                                     'expect-ct': 'max-age=604800, '
                                                  'report-uri="https://report-uri.cloudflare.com/cdn-cgi/beacon/expect-ct"',
                                     'nel': '{"report_to":"cf-nel","max_age":604800}',
                                     'report-to': '{"endpoints":[{"url":"https:\\/\\/a.nel.cloudflare.com\\/report?s=ZtI%2Bx8B7DpI8%2FsDA72maecFVCPvIsfBOyJjT8weyiqfmrHrmcBYpRhc%2FI%2F6JmIlnxW%2F%2BBohxLi1F8mpjAUabJ0kXLYnmjGKp2Ndio9M%3D"}],"group":"cf-nel","max_age":604800}',
                                     'server': 'cloudflare',
                                     'vary': 'Accept-Encoding'},
                         'mimeType': 'text/javascript',
                         'protocol': 'h3-29',
                         'remoteIPAddress': '104.21.5.197',
                         'remotePort': 443,
                         'requestHeaders': {':authority': 'nowsecure.nl',
                                            ':method': 'GET',
                                            ':path': '/cdn-cgi/challenge-platform/h/b/orchestrate/jsch/v1?ray=65444b779ae6546f',
                                            ':scheme': 'https',
                                            'accept': '*/*',
                                            'accept-encoding': 'gzip, deflate, '
                                                               'br',
                                            'accept-language': 'en-US,en;q=0.9',
                                            'referer': 'https://nowsecure.nl/',
                                            'sec-ch-ua': '" Not '
                                                         'A;Brand";v="99", '
                                                         '"Chromium";v="90", '
                                                         '"Google '
                                                         'Chrome";v="90"',
                                            'sec-ch-ua-mobile': '?0',
                                            'sec-fetch-dest': 'script',
                                            'sec-fetch-mode': 'no-cors',
                                            'sec-fetch-site': 'same-origin',
                                            'user-agent': 'Mozilla/5.0 '
                                                          '(Windows NT 10.0; '
                                                          'Win64; x64) '
                                                          'AppleWebKit/537.36 '
                                                          '(KHTML, like Gecko) '
                                                          'Chrome/90.0.4430.212 '
                                                          'Safari/537.36'},
                         'responseTime': 1621835932301.817,
                         'securityDetails': {'certificateId': 0,
                                             'certificateTransparencyCompliance': 'compliant',
                                             'cipher': 'AES_128_GCM',
                                             'issuer': 'Cloudflare Inc ECC '
                                                       'CA-3',
                                             'keyExchange': '',
                                             'keyExchangeGroup': 'X25519',
                                             'protocol': 'QUIC',
                                             'sanList': ['sni.cloudflaressl.com',
                                                         '*.nowsecure.nl',
                                                         'nowsecure.nl'],
                                             'signedCertificateTimestampList': [{'hashAlgorithm': 'SHA-256',
                                                                                 'logDescription': 'Google '
                                                                                                   "'Argon2021' "
                                                                                                   'log',
                                                                                 'logId': 'F65C942FD1773022145418083094568EE34D131933BFDF0C2F200BCC4EF164E3',
                                                                                 'origin': 'Embedded '
                                                                                           'in '
                                                                                           'certificate',
                                                                                 'signatureAlgorithm': 'ECDSA',
                                                                                 'signatureData': '30450221008A25458182A6E7F608FE1492086762A367381E94137952FFD621BA2E60F7E2F702203BCDEBCE1C544DECF0A113DE12B33E299319E6240426F38F08DFC04EF2E42825',
                                                                                 'status': 'Verified',
                                                                                 'timestamp': 1598706372839.0},
                                                                                {'hashAlgorithm': 'SHA-256',
                                                                                 'logDescription': 'DigiCert '
                                                                                                   'Yeti2021 '
                                                                                                   'Log',
                                                                                 'logId': '5CDC4392FEE6AB4544B15E9AD456E61037FBD5FA47DCA17394B25EE6F6C70ECA',
                                                                                 'origin': 'Embedded '
                                                                                           'in '
                                                                                           'certificate',
                                                                                 'signatureAlgorithm': 'ECDSA',
                                                                                 'signatureData': '3046022100A95A49C7435DBFC73406AC409062C27269E6E69F443A2213F3A085E3BCBD234A022100DEA878296F8A1DB43546DC1865A4C5AD2B90664A243AE0A3A6D4925802EE68A8',
                                                                                 'status': 'Verified',
                                                                                 'timestamp': 1598706372823.0}],
                                             'subjectName': 'sni.cloudflaressl.com',
                                             'validFrom': 1598659200,
                                             'validTo': 1630238400},
                         'securityState': 'secure',
                         'status': 200,
                         'statusText': '',
                         'timing': {'connectEnd': -1,
                                    'connectStart': -1,
                                    'dnsEnd': -1,
                                    'dnsStart': -1,
                                    'proxyEnd': -1,
                                    'proxyStart': -1,
                                    'pushEnd': 0,
                                    'pushStart': 0,
                                    'receiveHeadersEnd': 78.885,
                                    'requestTime': 190011.107975,
                                    'sendEnd': 27.934,
                                    'sendStart': 27.809,
                                    'sslEnd': -1,
                                    'sslStart': -1,
                                    'workerFetchStart': -1,
                                    'workerReady': -1,
                                    'workerRespondWithSettled': -1,
                                    'workerStart': -1},
                         'url': 'https://nowsecure.nl/cdn-cgi/challenge-platform/h/b/orchestrate/jsch/v1?ray=65444b779ae6546f'},
            'timestamp': 190011.188468,
            'type': 'Script'}}
{'method': 'Network.dataReceived',
 'params': {'dataLength': 31556,
            'encodedDataLength': 0,
            'requestId': '17180.2',
            'timestamp': 190011.188663}}
{'method': 'Network.dataReceived',
 'params': {'dataLength': 6737,
            'encodedDataLength': 11251,
            'requestId': '17180.2',
            'timestamp': 190011.198249}}
{'method': 'Network.dataReceived',
 'params': {'dataLength': 0,
            'encodedDataLength': 2049,
            'requestId': '17180.2',
            'timestamp': 190011.200943}}
{'method': 'Network.loadingFinished',
 'params': {'encodedDataLength': 13810,
            'requestId': '17180.2',
            'shouldReportCorbBlocking': False,
            'timestamp': 190011.198142}}
{'method': 'Page.loadEventFired', 'params': {'timestamp': 190011.204711}}
{'method': 'Page.frameScheduledNavigation',
 'params': {'delay': 12,
            'frameId': 'F42BAE4BDD4E428EE2503CB5A7B4F700',
            'reason': 'metaTagRefresh',
            'url': 'https://nowsecure.nl/'}}
{'method': 'Page.frameStoppedLoading',
 'params': {'frameId': 'F42BAE4BDD4E428EE2503CB5A7B4F700'}}
{'method': 'Network.requestWillBeSent',
 'params': {'documentURL': 'https://nowsecure.nl/',
            'frameId': 'F42BAE4BDD4E428EE2503CB5A7B4F700',
            'hasUserGesture': False,
            'initiator': {'type': 'other'},
            'loaderId': '449906A5C736D819123288133F2797E6',
            'request': {'headers': {'Referer': 'https://nowsecure.nl/',
                                    'User-Agent': 'Mozilla/5.0 (Windows NT '
                                                  '10.0; Win64; x64) '
                                                  'AppleWebKit/537.36 (KHTML, '
                                                  'like Gecko) '
                                                  'Chrome/90.0.4430.212 '
                                                  'Safari/537.36',
                                    'sec-ch-ua': '" Not A;Brand";v="99", '
                                                 '"Chromium";v="90", "Google '
                                                 'Chrome";v="90"',
                                    'sec-ch-ua-mobile': '?0'},
                        'initialPriority': 'High',
                        'method': 'GET',
                        'mixedContentType': 'none',
                        'referrerPolicy': 'strict-origin-when-cross-origin',
                        'url': 'https://nowsecure.nl/favicon.ico'},
            'requestId': '17180.5',
            'timestamp': 190011.210491,
            'type': 'Other',
            'wallTime': 1621835932.325683}}
{'method': 'Network.requestWillBeSentExtraInfo',
 'params': {'associatedCookies': [{'blockedReasons': [],
                                   'cookie': {'domain': 'nowsecure.nl',
                                              'expires': 1621839532,
                                              'httpOnly': False,
                                              'name': 'cf_chl_prog',
                                              'path': '/',
                                              'priority': 'Medium',
                                              'sameParty': False,
                                              'secure': False,
                                              'session': False,
                                              'size': 12,
                                              'sourcePort': 443,
                                              'sourceScheme': 'Secure',
                                              'value': 'e'}}],
            'clientSecurityState': {'initiatorIPAddressSpace': 'Public',
                                    'initiatorIsSecureContext': True,
                                    'privateNetworkRequestPolicy': 'WarnFromInsecureToMorePrivate'},
            'headers': {':authority': 'nowsecure.nl',
                        ':method': 'GET',
                        ':path': '/favicon.ico',
                        ':scheme': 'https',
                        'accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                        'accept-encoding': 'gzip, deflate, br',
                        'accept-language': 'en-US,en;q=0.9',
                        'cookie': 'cf_chl_prog=e',
                        'referer': 'https://nowsecure.nl/',
                        'sec-ch-ua': '" Not A;Brand";v="99", '
                                     '"Chromium";v="90", "Google '
                                     'Chrome";v="90"',
                        'sec-ch-ua-mobile': '?0',
                        'sec-fetch-dest': 'image',
                        'sec-fetch-mode': 'no-cors',
                        'sec-fetch-site': 'same-origin',
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; '
                                      'x64) AppleWebKit/537.36 (KHTML, like '
                                      'Gecko) Chrome/90.0.4430.212 '
                                      'Safari/537.36'},

# hopefullly you get the idea.
```





<br>
<br>

#### the easy way (v1 old stuff) ####
```python
import undetected_chromedriver as uc
driver = uc.Chrome()
driver.get('https://distilnetworks.com')
```




#### target specific chrome version  (v1 old stuff) ####
```python
import undetected_chromedriver as uc
uc.TARGET_VERSION = 85
driver = uc.Chrome()
```


#### monkeypatch mode  (v1 old stuff) ####
Needs to be done before importing from selenium package

```python
import undetected_chromedriver as uc
uc.install()

from selenium.webdriver import Chrome
driver = Chrome()
driver.get('https://distilnetworks.com')

```


#### the customized way  (v1 old stuff) ####
```python
import undetected_chromedriver as uc

#specify chromedriver version to download and patch
uc.TARGET_VERSION = 78    

# or specify your own chromedriver binary (why you would need this, i don't know)

uc.install(
    executable_path='c:/users/user1/chromedriver.exe',
)

opts = uc.ChromeOptions()
opts.add_argument(f'--proxy-server=socks5://127.0.0.1:9050')
driver = uc.Chrome(options=opts)
driver.get('https://distilnetworks.com')
```


#### datadome.co example  (v1 old stuff) ####
These guys have actually a powerful product, and a link to this repo, which makes me wanna test their product.
Make sure you use a "clean" ip for this one. 
```python
#
# STANDARD selenium Chromedriver
#
from selenium import webdriver
chrome = webdriver.Chrome()
chrome.get('https://datadome.co/customers-stories/toppreise-ends-web-scraping-and-content-theft-with-datadome/')
chrome.save_screenshot('datadome_regular_webdriver.png')
True   # it caused my ip to be flagged, unfortunately


#
# UNDETECTED chromedriver (headless,even)
#
import undetected_chromedriver as uc
options = uc.ChromeOptions()
options.headless=True
options.add_argument('--headless')
chrome = uc.Chrome(options=options)
chrome.get('https://datadome.co/customers-stories/toppreise-ends-web-scraping-and-content-theft-with-datadome/')
chrome.save_screenshot('datadome_undetected_webddriver.png')

```
**Check both saved screenhots [here](https://imgur.com/a/fEmqadP)**
