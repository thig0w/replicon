# -*- coding: utf-8 -*-
import io
import logging
import re

from PIL import Image
from PyQt5.QtCore import QThread
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Sefaz(QThread):
    def __init__(self, url, driver, lock):
        super().__init__()
        key = re.match(".*P=(.*)", url.upper())
        self.key = key.groups()[0]
        logger.debug("URL: %s", key.groups()[0])
        self.url = (
            "https://www.sefaz.rs.gov.br/ASP/AAE_ROOT/NFE/SAT-WEB-NFE-NFC_QRCODE_1.asp?p="
            + self.key
        )
        self.x = None
        self.y = None
        self.width = None
        self.height = None
        self.total_value = 0
        self.date = ""
        self.driver = driver
        self.lock = lock
        self.screen = None

    def run(self):
        # Locking to prevent the use of the web driver by another thread
        logger.debug("Fetching url: %s", self.url)
        self.lock.acquire()
        self.driver.set_window_size(1024, 768)
        self.driver.get(self.url)  # whatever reachable url
        WebDriverWait(self.driver, 10).until(
            ec.presence_of_element_located((By.XPATH, '//*[@id="respostaWS"]'))
        )
        self.total_value = self.driver.find_element_by_xpath(
            '//*[@id="respostaWS"]/tbody/tr/td/table/tbody/tr[3]'
            "/td/table/tbody/tr/td/table/tbody/tr[6]/td/table/tbody/tr[1]/td[2]"
        ).text
        nf_header = self.driver.find_element_by_xpath(
            '//*[@id="respostaWS"]/tbody/tr/td/table/tbody/tr[3]'
            "/td/table/tbody/tr/td/table/tbody/tr[3]/td/table/tbody/tr[1]/td"
        ).text
        self.date = re.match(".*([0-9]{2}/[0-9]{2}/[0-9]{4}).*", nf_header).groups()[0]
        element = self.driver.find_element_by_xpath('//*[@id="respostaWS"]')
        location = element.location
        size = element.size
        self.x = location["x"]
        self.y = location["y"]
        self.width = location["x"] + size["width"]
        self.height = location["y"] + size["height"]

        self.screen = self.driver.get_screenshot_as_png()
        self.lock.release()

        logger.debug(
            "NFCe total value: %s | Date: %s | url: %s",
            self.total_value,
            self.date,
            self.url,
        )

    def save_image(self, path):
        logger.debug("Creating png file!")
        if self.screen is not None:
            im = Image.open(io.BytesIO(self.screen))
            im = im.crop((int(self.x), int(self.y), int(self.width), int(self.height)))

            ordering_date = (
                self.date.split("/")[-1]
                + self.date.split("/")[-2]
                + self.date.split("/")[-3]
            )
            filename = (
                path
                + "\\sfnf_"
                + ordering_date
                + "_"
                + self.key.split("|")[-1][:10]
                + ".png"
            )
            logger.debug("Creating png file to %s", filename)

            im.save(filename)
        else:
            raise Exception("No image was captured!")


if __name__ == "__main__" or __name__ == "__builtin__":
    import threading
    from phantomjs_bin import executable_path
    from selenium import webdriver

    url_1 = (
        "https://www.sefaz.rs.gov.br/NFCE/NFCE-COM.aspx?"
        "p=43190693015006003210651270004470561759268442|2|1|1|4242DC7DF093B2756A42B54D5E8AAA094070A7F8"
    )
    url_frame = (
        "https://www.sefaz.rs.gov.br/ASP/AAE_ROOT/NFE/SAT-WEB-NFE-NFC_QRCODE_1.asp?"
        "p=43190693015006003210651270004470561759268442|2|1|1|4242DC7DF093B2756A42B54D5E8AAA094070A7F8"
    )
    a = Sefaz(
        url_frame,
        webdriver.PhantomJS(executable_path=executable_path),
        threading.Lock(),
    )
    a.run()
    a.save_image("C:\\Users\\LOGIC\\Desktop")
