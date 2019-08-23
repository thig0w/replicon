# -*- coding: utf-8 -*-
import logging
import xlwings as xw

from repl_uploader import Replicon
from repl_uploader.utils.ex_rates import Rates

# Starting logging
logging.basicConfig(level=logging.NOTSET)
logger = logging.getLogger(__name__)

local_currency = "BRL"


@xw.func
def hello(name):
    return "hello {0}".format(name)


def get_report(password, reportUri=None):
    logger.debug("Initializing Report Generation...")
    sheet = xw.sheets.active

    try:
        logger.debug("Init Replicon")
        repl = Replicon(
            userid="tweidman",
            password=password,
            project_cc=None,
            expenseSlug=None,
            description=None,
            isExpense=False,
        )
    except Exception as e:
        logger.debug("Error trying o init Replicon %s" % e.message)
        # xw.Range(error_rg).value = e.message
    resp = repl.generate_report(reportUri=reportUri)

    return resp


def get_expense_values(password):
    if xw.Range("O1").value is None:
        reportUri = "urn:replicon-tenant:logicinfo-ref:report:c2d6e884-6950-45e0-925a-6584e794def0"
    else:
        reportUri = xw.Range("O1").value
    list_report = get_report(password=password, reportUri=reportUri)

    # Save last total value
    xw.Range("M3").value = xw.Range("M2").value

    # Remove header and total row from the dataset
    report_header = list_report.pop(0)
    report_total = list_report.pop(-1)

    for i in range(list_report.__len__()):
        list_report[i][4] = list_report[i][4][:3]
        if list_report[i][4] != local_currency:
            r = Rates(list_report[i][4], local_currency)
            list_report[i][6] = r.get_by_week(list_report[i][0], list_report[i][1][-2:])

    row = 1
    while True:
        # The first row is the header
        row += 1
        # Finds empty row
        if xw.Range("A" + str(row)).value is None:
            break
        # Finds the mininum week of the report
        if int(list_report[0][0]) == xw.Range("A" + str(row)).value and list_report[0][
            1
        ].__eq__(str(xw.Range("B" + str(row)).value)):
            break

    xw.Range("A" + str(row)).value = list_report


def get_resource_values(password):
    if xw.Range("O1").value is None:
        reportUri = "urn:replicon-tenant:logicinfo-ref:report:23e6dac9-8b11-4c0f-81db-c508bc997e45"
    else:
        reportUri = xw.Range("O1").value
    list_report = get_report(password=password, reportUri=reportUri)

    # Save last total value
    xw.Range("M3").value = xw.Range("M2").value

    # Remove header and total row from the dataset
    report_header = list_report.pop(0)
    # report_total = list_report.pop(-1)

    row = 1
    while True:
        # The first row is the header
        row += 1
        # Finds empty row
        if xw.Range("B" + str(row)).value is None:
            break
        # Finds the mininum week of the report
        if int(list_report[0][0]) == xw.Range("B" + str(row)).value and list_report[0][
            1
        ].__eq__(str(xw.Range("C" + str(row)).value)):
            break

    xw.Range("B" + str(row)).value = list_report


if __name__ == "__builtin__" or __name__ == "__main__":
    # get_expense_values('')
    get_resource_values("")
