# -*- coding: utf-8 -*-
import logging

from isoweek import Week

import requests
import simplejson as json
import urllib.request, urllib.parse, urllib.error

# Starting logging
logging.basicConfig(level=logging.NOTSET)
logger = logging.getLogger(__name__)


class Rates:
    def __init__(self, from_cur, to_cur, precision=4):
        self.from_cur = from_cur
        self.to_cur = to_cur
        self.url = "http://currencies.apps.grandtrunk.net/getrate/"
        self.precision = precision

    def __get_from_url(self, url):
        headers = {"Content-type": "application/json", "Accept": "text/plain"}
        response = requests.get(
            url, headers=headers, proxies=urllib.request.getproxies()
        )
        logger.debug("get_from_url %s / %s", url, response)
        if response.ok:
            json_response = json.loads(response.text)
        else:
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                content = json.loads(e.response.content)
                if content["error"]["reason"].__eq__("Identifier not found."):
                    raise Exception("Replicon Number Does Not Exist!")
                else:
                    raise Exception("%s" % (content["error"]["reason"]))
        return json_response

    def get_by_week(self, year, week):
        day = Week(int(year), int(week)).monday()

        url = self.url
        url = url + day.strftime("%Y-%m-%d")
        url = url + "/"
        url = url + self.from_cur + "/" + self.to_cur

        resp = self.__get_from_url(url)

        return round(float(resp), self.precision)

    def get_by_day(self, year, month, day):
        url = self.url
        url = url + year + "-" + month + "-" + day
        url = url + "/"
        url = url + self.from_cur + "/" + self.to_cur

        resp = self.__get_from_url(url)

        return round(float(resp), self.precision)


if __name__ == "__builtin__" or __name__ == "__main__":
    rate = Rates("eur", "brl")
    print(rate.get_by_week(2018, 12))
