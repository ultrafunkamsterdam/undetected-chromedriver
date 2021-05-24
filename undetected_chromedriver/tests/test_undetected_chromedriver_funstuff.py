import asyncio
import logging

import cv2

import undetected_chromedriver.v2 as uc

logging.basicConfig(level=10)

just_some_urls = [
    "https://bing.com",
    "http://www.google.com",
    "https://codepen.io",
    "https://",
]


class ChromeDriverCV2Streamer:
    def __init__(self, driver):
        super().__init__()
        self.driver = driver
        self.display = None
        self.event = asyncio.Event()
        self.daemon = True

    def stop(self):
        self.event.set()

    def start(self):
        asyncio.ensure_future(self._start_capture_loop())

    async def _start_capture_loop(self):
        executor = None
        self.display = cv2.namedWindow("display")
        while not self.event.is_set():
            await asyncio.sleep(0.25)
            try:
                success = await loop.run_in_executor(
                    executor, self.driver.save_screenshot, "capture.tmp.png"
                )
                logging.getLogger().debug("got screenshot? %s", success)
                frame = await loop.run_in_executor(
                    executor, cv2.imread, "capture.tmp.png"
                )
                logging.getLogger().debug("frame: %s", frame)
                await loop.run_in_executor(executor, cv2.imshow, "display", frame)
                await loop.run_in_executor(executor, cv2.waitKey, 1)
                logging.getLogger().debug("waited key success")
            except Exception as e:
                print(e)


async def main():
    opts = uc.ChromeOptions()
    opts.headless = True
    driver = uc.Chrome(options=opts)

    streamer = ChromeDriverCV2Streamer(driver)
    streamer.start()
    for url in just_some_urls:
        # with driver:
        driver.get("https://nu.nl")
        await asyncio.sleep(3)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
