# -*- coding: utf-8 -*-
import logging
import os
import shutil
import tarfile
from datetime import timedelta, datetime
import sys
import uuid

import win32com.client as win32
import xlwings as xw
from win32com.client.gencache import EnsureDispatch

from repl_uploader import Replicon
from repl_uploader.utils import pdf_creator

# Starting logging
logging.basicConfig(level=logging.NOTSET)
logger = logging.getLogger(__name__)

# Get Configured ranges
# TODO: change to get the full path to the option (eg. =Config!D10)
defautl_img_path = xw.sheets["Config"].range("D3").value
meals_rg = xw.sheets["Config"].range("D5").value
transp_rg = xw.sheets["Config"].range("D6").value
parking_rg = xw.sheets["Config"].range("D7").value
print_rg = xw.sheets["Config"].range("D8").value
error_rg = xw.sheets["Config"].range("D9").value
currency_rg = xw.sheets["Config"].range("D10").value
disposition_rg = xw.sheets["Config"].range("D11").value
repl_num_rg = xw.sheets["Config"].range("D12").value
repl_descr_rg = xw.sheets["Config"].range("D13").value
images_path_rg = xw.sheets["Config"].range("D14").value
logic_mail_rg = xw.sheets["Config"].range("D15").value
manager_mail_rg = xw.sheets["Config"].range("D16").value
user_name_rg = xw.sheets["Config"].range("D17").value
client_info_rg = xw.sheets["Config"].range("D18").value
num_days_rg = xw.sheets["Config"].range("D19").value
printing_rg = xw.sheets["Config"].range("D20").value
start_date_rg = xw.sheets["Config"].range("D21").value
repl_return_amt_rg = xw.sheets["Config"].range("D22").value

# Create dictionary to get column indexes
dispo_idx = {
    a: int(b)
    for col, (a, b) in enumerate(xw.sheets["Config"].range(disposition_rg).value)
}


def create_replicon(password, all_sheets=False):
    logger.debug("Running create_replicon with all_sheets = %s" % (all_sheets))
    sheets = [xw.sheets.active] if not all_sheets else xw.sheets

    for sheet in sheets:
        # If Config sheet or if Expense number is filled, do nothing
        if sheet.name.__eq__("Config"):
            continue
        sheet.activate()
        logger.debug("Processisng sheet = %s" % (sheet.name))

        # Clean Error Cell
        xw.Range(error_rg).value = ""

        # Set global exchange Rate
        global_currency = xw.Range(currency_rg).value.split("#")[-1]

        # Get Replicon
        try:
            repl = Replicon(
                userid=xw.sheets["Config"].range("D2").value,
                password=password,
                project_cc=int(xw.Range("C2").value),
                expenseSlug=str(int(xw.Range(repl_num_rg).value))
                if xw.Range(repl_num_rg).value is not None
                else None,
                description=xw.Range(repl_descr_rg).value,
                isExpense=True,
            )
        except Exception as e:
            xw.Range(error_rg).value = e.args[0]
            continue

        # Check if replicon is open to overwrite the entries
        if not repl.expenseStatus.__eq__(repl.EXPENSE_STATUS_OPEN):
            xw.Range(error_rg).value = "This Replicon is not Open!"
            continue

        # Build Entries
        entries = []
        if meals_rg is not (None):
            for meals in xw.Range(meals_rg).value:
                if meals[dispo_idx["AMOUNT"]] is not (None):
                    logger.debug(
                        "Add Entry: %s - %s"
                        % (meals[dispo_idx["DATE"]], meals[dispo_idx["AMOUNT"]])
                    )
                    entries.append(
                        repl.get_new_entry(
                            date=meals[dispo_idx["DATE"]],
                            amount=meals[dispo_idx["AMOUNT"]],
                            entry_desc=meals[dispo_idx["DESCRIPTION"]],
                            expense_code=meals[dispo_idx["EXPENSE CODE"]].split("#")[
                                -1
                            ],
                            bill_client=meals[dispo_idx["BILLABLE"]],
                            reimburse_emp=meals[dispo_idx["REIMBURSE"]],
                            currency=meals[dispo_idx["CURRENCY"]].split("#")[-1],
                        )
                    )

        if transp_rg is not (None):
            for transp in xw.Range(transp_rg).value:
                if transp[dispo_idx["AMOUNT"]] is not (None):
                    logger.debug(
                        "Add Entry: %s - %s"
                        % (transp[dispo_idx["DATE"]], transp[dispo_idx["AMOUNT"]])
                    )
                    entries.append(
                        repl.get_new_entry(
                            date=transp[dispo_idx["DATE"]],
                            amount=transp[dispo_idx["AMOUNT"]],
                            entry_desc=transp[dispo_idx["DESCRIPTION"]],
                            expense_code=transp[dispo_idx["EXPENSE CODE"]].split("#")[
                                -1
                            ],
                            bill_client=transp[dispo_idx["BILLABLE"]],
                            reimburse_emp=transp[dispo_idx["REIMBURSE"]],
                            currency=transp[dispo_idx["CURRENCY"]].split("#")[-1],
                        )
                    )
        if parking_rg is not (None):
            parking = xw.Range(parking_rg).value
            if parking[dispo_idx["AMOUNT"]] is not (None):
                logger.debug(
                    "Add Entry: %s - %s"
                    % (parking[dispo_idx["DATE"]], parking[dispo_idx["AMOUNT"]])
                )
                entries.append(
                    repl.get_new_entry(
                        date=parking[dispo_idx["DATE"]],
                        amount=parking[dispo_idx["AMOUNT"]],
                        entry_desc=parking[dispo_idx["DESCRIPTION"]],
                        expense_code=parking[dispo_idx["EXPENSE CODE"]].split("#")[-1],
                        bill_client=parking[dispo_idx["BILLABLE"]],
                        reimburse_emp=parking[dispo_idx["REIMBURSE"]],
                        currency=parking[dispo_idx["CURRENCY"]].split("#")[-1],
                    )
                )

        # TODO: Print line deprecated - Plan to remove it
        if print_rg is not (None):
            printing = xw.Range(print_rg).value
            if printing[dispo_idx["AMOUNT"]] is not (None):
                base64_pdf = (None, None)  # pdf_creator.to_base64(pdf_path)
                logger.debug(
                    "Add Entry: %s - %s"
                    % (printing[dispo_idx["DATE"]], printing[dispo_idx["AMOUNT"]])
                )
                entries.append(
                    repl.get_new_entry(
                        date=printing[dispo_idx["DATE"]],
                        amount=printing[dispo_idx["AMOUNT"]],
                        entry_desc=printing[dispo_idx["DESCRIPTION"]],
                        project_cc=xw.Range("C2").value,
                        expense_code=printing[dispo_idx["EXPENSE CODE"]].split("#")[-1],
                        bill_client=printing[dispo_idx["BILLABLE"]],
                        reimburse_emp=printing[dispo_idx["REIMBURSE"]],
                        mime_type=base64_pdf[0],
                        base64_file=base64_pdf[1],
                        currency=printing[dispo_idx["CURRENCY"]].split("#")[-1],
                    )
                )

        repl.add_expense_entries(entries, global_currency)
        # Record replicon number to the sheet
        xw.Range(repl_num_rg).value = repl.expenseUri.split(":")[-1]
        xw.Range(repl_return_amt_rg).value = repl.replicon_total


def images_path_exists(replicon_needed=True):
    # Clean Error Cell
    xw.Range(error_rg).value = ""
    images_path = get_repl_folder()

    if (
        images_path is None
        or (xw.Range(repl_num_rg).value is None and replicon_needed)
        or not os.path.exists(images_path)
    ):
        xw.Range(
            error_rg
        ).value = "Please validate if the replicon was generated or if the path to images exists!"
        xw.Range(error_rg).select()
        return False
    return True


def send_mail():
    logger.debug("Starting send_mail")
    if xw.sheets.active.name.__eq__("Config"):
        return

    if not images_path_exists():
        return

    # check if images path contains the replicon number to rename it
    if not get_repl_folder().__contains__(xw.Range(repl_num_rg).value):
        new_path = (
            "\\".join(get_repl_folder().split("\\")[:-1])
            + "\\"
            + xw.Range(repl_num_rg).value
        )
        logger.debug("Renaming folder %s to %s" % (get_repl_folder(), new_path))
        shutil.move(get_repl_folder(), new_path)
        set_repl_folder(xw.Range(repl_num_rg).value)

    photo_pdf_path = pdf_creator.create_pdf(
        get_repl_folder(), xw.Range(repl_num_rg).value
    )
    list_pdf_path = generate_xl_pdf(get_repl_folder(), xw.Range(repl_num_rg).value)

    logger.debug("Starting Mail creation")
    outlook = win32.Dispatch("outlook.application")
    mail = outlook.CreateItem(0)
    mail.To = (
        xw.sheets["Config"].range(logic_mail_rg).value
        + ";"
        + (
            xw.sheets["Config"].range(manager_mail_rg).value
            if xw.sheets["Config"].range(manager_mail_rg).value is not None
            else ""
        )
    )
    mail.Subject = (
        xw.sheets["Config"].range(user_name_rg).value
        + " - "
        + xw.Range(repl_num_rg).value
        + " - "
        + xw.Range(client_info_rg).value
        + " Expense Sheet ("
        + str(int(xw.Range("C2").value))
        + ") - "
        + xw.Range(start_date_rg).value.strftime("%d/%m/%Y")
        + " - "
        + (xw.Range(start_date_rg).value + timedelta(days=5)).strftime("%d/%m/%Y")
    )
    mail.HtmlBody = "Seguem detalhes em anexo"
    try:
        logger.debug("attaching mail = %s" % (photo_pdf_path))
        logger.debug("attaching mail = %s" % (list_pdf_path))
        mail.Attachments.Add(photo_pdf_path)
        mail.Attachments.Add(list_pdf_path)
    except Exception as e:
        xw.Range(error_rg).value = "File not found!"
        return
    mail.Display(False)

    # copy replicon list to main folder
    logger.debug(
        "Copying pdf list from %s to %s"
        % (list_pdf_path, os.path.dirname(os.path.dirname(get_repl_folder())))
    )
    shutil.copy(list_pdf_path, os.path.dirname(get_repl_folder()))

    tar = tarfile.open(get_repl_folder() + "ok.tgz", "w:gz")
    tar.add(get_repl_folder(), filter=reset, arcname=get_repl_folder().split("\\")[-1])
    tar.close()
    shutil.rmtree(get_repl_folder(), ignore_errors=True)


def reset(tarinfo):
    tarinfo.uid = tarinfo.gid = 0
    tarinfo.uname = tarinfo.gname = "root"
    return tarinfo


def generate_xl_pdf(path, repl_num):
    # Get the Excel Application COM object
    xl = EnsureDispatch("Excel.Application")
    print_area = printing_rg
    pdf_path = path + "\\" + str(repl_num) + "_lista_expenses.pdf"

    wb = xl.ActiveWorkbook
    ws = wb.ActiveSheet

    ws.PageSetup.Zoom = False
    ws.PageSetup.FitToPagesTall = False
    ws.PageSetup.FitToPagesWide = 1
    ws.PageSetup.LeftMargin = False
    ws.PageSetup.RightMargin = False
    ws.PageSetup.TopMargin = False
    ws.PageSetup.BottomMargin = False
    ws.PageSetup.Orientation = 2

    ws.PageSetup.PrintArea = print_area

    ws.ExportAsFixedFormat(0, pdf_path)

    return pdf_path


def clean_xl():
    if meals_rg is not (None):
        for meals in xw.Range(meals_rg).rows:
            meals[dispo_idx["AMOUNT"]].clear_contents()

    if transp_rg is not (None):
        for transp in xw.Range(transp_rg).rows:
            transp[dispo_idx["AMOUNT"]].clear_contents()

    if parking_rg is not (None):
        xw.Range(parking_rg)[dispo_idx["AMOUNT"]].clear_contents()

    if repl_num_rg is not None:
        xw.Range(repl_num_rg).clear_contents()

    if images_path_rg is not None:
        xw.Range(images_path_rg).api.MergeArea.ClearContents()


def get_repl_folder():
    if xw.Range(images_path_rg).value is None:
        xw.Range(images_path_rg).value = uuid.uuid4().hex[0:10]
        os.mkdir(defautl_img_path + "\\" + xw.Range(images_path_rg).value)
    return defautl_img_path + "\\" + xw.Range(images_path_rg).value


def set_repl_folder(value):
    xw.Range(images_path_rg).value = value


def fill_xl_from_list(list):
    xw.Range(error_rg).value = ""
    # Convert to datetime
    for i in list:
        i[0] = datetime.strptime(i[0], "%d/%m/%Y")

    # Sort the list
    list.sort(key=lambda x: x[0])

    if list[0][0] < xw.Range(start_date_rg).value:
        xw.Range(error_rg).value = (
            "Scanned NFs Not in Excel Range, please change the value on Cell: "
            + start_date_rg
        )
        xw.Range(start_date_rg).select()

    if list[-1][0] > xw.Range(meals_rg).rows[-1][dispo_idx["DATE"]].value:
        xw.Range(error_rg).value = (
            "Scanned NFs Not in Excel Range, please check last date: " + start_date_rg
        )
        xw.Range(meals_rg).rows[-1][dispo_idx["DATE"]].select()

    # watchdog to prevent looping too much
    last_visited = 0
    for i in list:
        if meals_rg is not None:
            for meals in xw.Range(meals_rg).rows[last_visited:]:
                if (
                    meals[dispo_idx["DATE"]].value.__eq__(i[0])
                    and meals[dispo_idx["AMOUNT"]].value is None
                ):
                    meals[dispo_idx["AMOUNT"]].value = float(i[1].replace(",", "."))
                    break
            last_visited = last_visited + 1


def init_camera():
    from repl_uploader.pyqt.qrcode import UiDialog

    xw.Range(error_rg).value = ""
    if not images_path_exists(False):
        return
    try:
        ui = UiDialog()
    except:
        xw.Range(error_rg).value = "Unexpected error: {}".format(sys.exc_info()[0])
    del ui


def get_version():
    import repl_uploader

    xw.Range("A1").value = repl_uploader.VERSION


if __name__ == "__main__" or __name__ == "__builtin__":
    # create_replicon('', False)
    # send_mail()
    # generate_xl_pdf('C:\Users\LOGIC\Dropbox\Trabalho\Replicon', '1234')
    # generate_xl_pdf()
    # fill_xl_from_list(
    #     [
    #         ["07/08/2019", "20,00"],
    #         ["07/08/2019", "21,00"],
    #         ["08/08/2019", "30,00"],
    #         ["09/08/2019", "20,00"],
    #     ]
    # )
    clean_xl()
