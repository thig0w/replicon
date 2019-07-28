# -*- coding: utf-8 -*-
import logging
import re

from PIL import Image
from PyQt5.QtCore import QThread
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Sefaz(QThread):
    def __init__(self, url):
        super().__init__()
        key = re.match(".*=([0-9]{44}\|[0-9]\|[0-9]\|[0-9]\|[A-Z0-9]{40})", url.upper())
        print(key.groups())
        logger.debug('URL: %s', key.groups()[0])
        self.url = 'https://www.sefaz.rs.gov.br/ASP/AAE_ROOT/NFE/SAT-WEB-NFE-NFC_QRCODE_1.asp?p=' + \
                   key.groups()[0]
        self.total_value = 0

    def run(self):
        driver = webdriver.PhantomJS("./phantomjs.exe")  # the normal SE phantomjs binding
        driver.set_window_size(1024, 768)
        driver.get(self.url)  # whatever reachable url
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="respostaWS"]')))
        self.total_value = driver.find_element_by_xpath(
            '//*[@id="respostaWS"]/tbody/tr/td/table/tbody/tr[3]/td/table/tbody/tr/td/table/tbody/tr[6]/td/table/tbody/tr[1]/td[2]').text
        element = driver.find_element_by_xpath('//*[@id="respostaWS"]')
        location = element.location
        size = element.size
        x = location['x']
        y = location['y']
        width = location['x'] + size['width']
        height = location['y'] + size['height']

        driver.save_screenshot("C:\\Users\\LOGIC\\Desktop\\teste.png")  # screen.png is a big red rectangle :)

        im = Image.open('C:\\Users\\LOGIC\\Desktop\\teste.png')
        im = im.crop((int(x), int(y), int(width), int(height)))
        im.save('C:\\Users\\LOGIC\\Desktop\\teste_croped.png')

        driver.quit()

        logger.debug('NFCe total value: %s', self.total_value)


if __name__ == "__main__" or __name__ == "__builtin__":
    url = 'https://www.sefaz.rs.gov.br/NFCE/NFCE-COM.aspx?p=43190693015006003210651270004470561759268442|2|1|1|4242DC7DF093B2756A42B54D5E8AAA094070A7F8'
    url_frame = 'https://www.sefaz.rs.gov.br/ASP/AAE_ROOT/NFE/SAT-WEB-NFE-NFC_QRCODE_1.asp?p=43190693015006003210651270004470561759268442|2|1|1|4242DC7DF093B2756A42B54D5E8AAA094070A7F8'
    a = Sefaz(url_frame)
    a.run()
