# -*- coding: utf-8 -*-
import csv
import logging
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime

import requests
import simplejson as json

logging.basicConfig(level=logging.NOTSET)
logger = logging.getLogger(__name__)


class Replicon:
    def __init__(
        self,
        company="logicinfo",
        userid="tweidman",
        password=None,
        project_cc=2058,
        expenseSlug=None,
        description="Created by TW: Change this desc",
        isExpense=True,
    ):
        if password is None or password.__len__() == 0:
            raise Exception("Password cannot be null!")
        self.company = company
        self.userid = userid
        self.password = password
        self.expenseSlug = expenseSlug
        self.description = description
        self.EXPENSE_STATUS_OPEN = "urn:replicon:approval-status:open"
        self.replicon_total = 0

        # get user server url
        url = "https://global.replicon.com/DiscoveryService1.svc/GetUserIntegrationDetails"
        data = {"companyKey": self.company, "loginName": self.userid, "targetUrl": ""}
        jsonresponse = self.__post_to_url(url, data)

        self.serviceUrl = jsonresponse["d"]["serviceEndpointRootUrl"]

        # get user uri
        url = self.serviceUrl + "UserService1.svc/GetUriFromSlug"
        data = {"userSlug": self.userid}
        jsonresponse = self.__post_to_url(url, data)

        self.useruri = jsonresponse["d"]

        if isExpense:
            # get expense status
            if self.expenseSlug is not None:
                # Get expense sheet uri to edit it
                url = self.serviceUrl + "ExpenseService1.svc/GetUriFromExpenseSheetSlug"
                data = {"expenseSheetSlug": self.expenseSlug}
                jsonresponse = self.__post_to_url(url, data)
                self.expenseUri = jsonresponse["d"]

                # Get expense sheet status
                url = (
                    self.serviceUrl
                    + "ExpenseApprovalService1.svc/GetExpenseSheetApprovalDetails"
                )
                data = {"expenseUri": self.expenseUri}
                jsonresponse = self.__post_to_url(url, data)
                self.expenseStatus = jsonresponse["d"]["approvalStatus"]["uri"]

            else:
                self.create_new_expense(description)
                self.expenseStatus = "urn:replicon:approval-status:open"

            # get project uri
            self.set_project_uri_from_cc(project_cc, self.expenseUri)

    def __get_from_url(self, url):
        headers = {"Content-type": "application/json", "Accept": "text/plain"}
        response = requests.get(
            url,
            auth=(self.company + "\\" + self.userid, self.password),
            headers=headers,
            proxies=urllib.request.getproxies(),
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

    def __post_to_url(self, url, data):
        headers = {"Content-type": "application/json", "Accept": "text/plain"}

        response = requests.post(
            url,
            auth=(self.company + "\\" + self.userid, self.password),
            data=json.dumps(data),
            headers=headers,
            proxies=urllib.request.getproxies(),
        )
        logger.debug("post_to_url %s / %s / %s", url, json.dumps(data), response)
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

    def create_new_expense(self, description="Created by TW: Change this desc"):
        self.description = description
        url = self.serviceUrl + "ExpenseService1.svc/CreateNewExpenseSheetDraft"
        data = {"ownerUri": self.useruri}
        jsonresponse = self.__post_to_url(url, data)

        draft_uri = jsonresponse["d"]

        url = self.serviceUrl + "ExpenseService1.svc/UpdateExpenseSheetDescription"
        data = {"expenseSheetUri": draft_uri, "description": description}
        jsonresponse = self.__post_to_url(url, data)

        url = self.serviceUrl + "ExpenseService1.svc/PublishExpenseSheetDraft"
        data = {"draftUri": draft_uri}
        jsonresponse = self.__post_to_url(url, data)
        self.expenseUri = jsonresponse["d"]["uri"]

    def add_expense_entries(self, entriesList=None, currency="9"):
        data_header = {
            "parameter": {
                "target": {"uri": self.expenseUri},
                "owner": {"uri": self.useruri},
                "date": {
                    "year": time.strftime("%Y"),
                    "month": time.strftime("%m"),
                    "day": time.strftime("%d"),
                },
                "description": self.description,
                "reimbursementCurrency": {
                    "uri": "urn:replicon-tenant:logicinfo-ref:currency:%s" % (currency)
                },
                "entries": [],
                "noticeExplicitlyAccepted": "true",
            }
        }
        data_header["parameter"]["entries"] = entriesList
        url = self.serviceUrl + "ExpenseService1.svc/PutExpenseSheet"
        jsonresponse = self.__post_to_url(url, data_header)
        logger.debug("=====> %s ", json.dumps(jsonresponse))
        self.replicon_total = sum(
            [
                float(
                    jsonresponse["d"]["entries"][a]["expenseEntry"][
                        "reimbursementAmount"
                    ]["amount"]
                )
                for a in range(len(jsonresponse["d"]["entries"]))
            ]
        )

    def get_new_entry(
        self,
        entry_desc="taxi",
        project_cc="2084",
        date=datetime.today(),
        expense_code="6",
        currency="9",
        amount="1.22",
        bill_client="Yes",
        reimburse_emp="Yes",
        mime_type=None,
        base64_file=None,
    ):
        bclient = (
            "urn:replicon:expense-billing-option:bill-to-client"
            if bill_client == "Yes"
            else "urn:replicon:expense-billing-option:not-billed"
        )
        remp = (
            "urn:replicon:expense-reimbursement-option:reimburse-employee"
            if reimburse_emp == "Yes"
            else "urn:replicon:expense-reimbursement-option:not-reimbursed"
        )
        recpt = (
            {
                "target": None,
                "image": {"base64ImageData": base64_file, "mimeType": mime_type},
            }
            if base64_file is not None
            else None
        )

        entry = {
            "target": None,
            "incurredDate": {"year": date.year, "month": date.month, "day": date.day},
            "description": entry_desc,
            "expenseBillingOptionUri": bclient,
            "expenseReimbursementOptionUri": remp,
            "project": {"uri": "%s" % (self.project_uri)},
            "expenseCode": {
                "uri": "urn:replicon-tenant:logicinfo-ref:expense-code:%s"
                % (expense_code)
            },
            "flatAmountEntry": {
                "incurredAmountNet": {
                    "amount": "%s" % (amount),
                    "currency": {
                        "uri": "urn:replicon-tenant:logicinfo-ref:currency:%s"
                        % (currency)
                    },
                }
            },
            "expenseReceipt": recpt,
        }
        return entry

    def set_project_uri_from_cc(
        self,
        project_cc=2058,
        expense_uri="urn:replicon-tenant:logicinfo-ref:expense-sheet:93532",
    ):
        url = (
            self.serviceUrl
            + "ExpenseService1.svc/GetPageOfProjectsAvailableForExpenseEntryFilteredByClientAndTextSearch"
        )
        data = {
            "page": 1,
            "pageSize": 10,
            "expenseSheetUri": expense_uri,
            "textSearch": {
                "queryText": "({})".format(project_cc),
                "searchInDisplayText": True,
            },
        }
        jsonresponse = self.__post_to_url(url, data)
        try:
            self.project_uri = jsonresponse["d"][0]["project"]["uri"]
        except IndexError:
            raise Exception(
                "Project {} does not exist or you don`t have access to it.".format(
                    project_cc
                )
            )

    def generate_report(self, reportUri):
        url = self.serviceUrl + "ReportService1.svc/GenerateReport"
        data = {
            "reportUri": reportUri,
            "filterValues": [],
            "outputFormatUri": "urn:replicon:report-output-format-option:csv",
        }
        logger.debug("Generating report: %s" % (reportUri))
        jsonresponse = self.__post_to_url(url, data)
        # Fix euro sign problem encoding the string to utf-8
        # excluded encode: when moved to py3 this part was receiving a byte/string conflict error
        report_string = jsonresponse["d"]["payload"]  # .encode('utf-8')
        csv_report = csv.reader(report_string.split("\r\n")[:-1])
        return list(csv_report)


if __name__ == "__main__" or __name__ == "__builtin__":
    # getpass.win_getpass()
    repl = Replicon("logicinfo", "tweidman", "pass", 2107)
    # repl = Replicon('logicinfo', 'tweidman', 'pass', 2058, description='Teste')
    #
    # print repl.useruri
    #
    # print repl.expenseUri
    # date = datetime.strptime('21/05/2017', '%d/%m/%Y')
    # entries = [repl.get_new_entry('taxi', '2084', date, '6', '9', '4.56'),
    #            repl.get_new_entry('taxi2', '2084', date, '6', '9', '2.56'),
    #            repl.get_new_entry('taxi3', '2084', date, '6', '9', '1.56'),
    #            repl.get_new_entry('taxi4', '2084', date, '6', '9', '34.56'),
    #            repl.get_new_entry('taxi5', '2084', date, '6', '9', '24.56')]
    # repl.add_expense_entries(entries)
    # repl.get_details()
    # print repl.replicon_total
