# -*- coding: utf-8 -*-
import logging

import xlwings as xw

import pdf_creator
import win32com.client as win32
from replicon import Replicon
from datetime import timedelta
import tarfile
import shutil
import os

from win32com.client.gencache import EnsureDispatch

# Starting logging
logging.basicConfig(level=logging.NOTSET)
logger = logging.getLogger(__name__)

# Get Configured ranges
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


def create_replicon(password, all_sheets=False):
    logger.debug('Running create_replicon with all_sheets = %s' % (all_sheets))
    sheets = [xw.sheets.active] if not all_sheets else xw.sheets

    for sheet in sheets:
        # If Config sheet or if Expense number is filled, do nothing
        if sheet.name.__eq__("Config"):
            continue
        sheet.activate()
        logger.debug('Processisng sheet = %s' % (sheet.name))

        # Clean Error Cell
        xw.Range(error_rg).value = ''

        # Create dictionary to get column indexes
        dispo_idx = {a: int(b) for col, (a, b) in enumerate(xw.sheets["Config"].range(disposition_rg).value)}
        # Set global exchange Rate
        global_currency = xw.Range(currency_rg).value.split('#')[-1]

        # Get Replicon
        try:
            repl = Replicon(userid=xw.sheets["Config"].range("D2").value, password=password,
                            project_cc=int(xw.Range("C2").value),
                            expenseSlug=str(int(xw.Range(repl_num_rg).value)) if xw.Range(
                                repl_num_rg).value is not None else None,
                            description=xw.Range(repl_descr_rg).value, isExpense=True)
        except Exception as e:
            xw.Range(error_rg).value = e.message
            continue

        # Check if replicon is open to overwrite the entries
        if not repl.expenseStatus.__eq__(repl.EXPENSE_STATUS_OPEN):
            xw.Range(error_rg).value = 'This Replicon is not Open!'
            continue

        # Build Entries
        entries = []
        for meals in xw.Range(meals_rg).value:
            if meals[1] is not (None):
                logger.debug('Add Entry: %s - %s' % (meals[dispo_idx['DATE']], meals[dispo_idx['AMOUNT']]))
                entries.append(repl.get_new_entry(date=meals[dispo_idx['DATE']], amount=meals[dispo_idx['AMOUNT']],
                                                  entry_desc=meals[dispo_idx['DESCRIPTION']],
                                                  expense_code=meals[dispo_idx['EXPENSE CODE']].split('#')[-1],
                                                  bill_client=meals[dispo_idx['BILLABLE']],
                                                  reimburse_emp=meals[dispo_idx['REIMBURSE']],
                                                  currency=meals[dispo_idx['CURRENCY']].split('#')[-1]))

        for transp in xw.Range(transp_rg).value:
            if transp[1] is not (None):
                logger.debug('Add Entry: %s - %s' % (transp[dispo_idx['DATE']], transp[dispo_idx['AMOUNT']]))
                entries.append(
                    repl.get_new_entry(date=transp[dispo_idx['DATE']], amount=transp[dispo_idx['AMOUNT']],
                                       entry_desc=transp[dispo_idx['DESCRIPTION']],
                                       expense_code=transp[dispo_idx['EXPENSE CODE']].split('#')[-1],
                                       bill_client=transp[dispo_idx['BILLABLE']],
                                       reimburse_emp=transp[dispo_idx['REIMBURSE']],
                                       currency=transp[dispo_idx['CURRENCY']].split('#')[-1]))

        parking = xw.Range(parking_rg).value
        if parking[1] is not (None):
            logger.debug('Add Entry: %s - %s' % (parking[dispo_idx['DATE']], parking[dispo_idx['AMOUNT']]))
            entries.append(repl.get_new_entry(date=parking[dispo_idx['DATE']], amount=parking[dispo_idx['AMOUNT']],
                                              entry_desc=parking[dispo_idx['DESCRIPTION']],
                                              expense_code=parking[dispo_idx['EXPENSE CODE']].split('#')[-1],
                                              bill_client=parking[dispo_idx['BILLABLE']],
                                              reimburse_emp=parking[dispo_idx['REIMBURSE']],
                                              currency=parking[dispo_idx['CURRENCY']].split('#')[-1]))

        printing = xw.Range(print_rg).value
        if printing[1] is not (None):
            base64_pdf = (None, None)  # pdf_creator.to_base64(pdf_path)
            logger.debug('Add Entry: %s - %s' % (printing[dispo_idx['DATE']], printing[dispo_idx['AMOUNT']]))
            entries.append(repl.get_new_entry(date=printing[dispo_idx['DATE']], amount=printing[dispo_idx['AMOUNT']],
                                              entry_desc=printing[dispo_idx['DESCRIPTION']],
                                              project_cc=xw.Range("C2").value,
                                              expense_code=printing[dispo_idx['EXPENSE CODE']].split('#')[-1],
                                              bill_client=printing[dispo_idx['BILLABLE']],
                                              reimburse_emp=printing[dispo_idx['REIMBURSE']], mime_type=base64_pdf[0],
                                              base64_file=base64_pdf[1],
                                              currency=printing[dispo_idx['CURRENCY']].split('#')[-1]))

        repl.add_expense_entries(entries, global_currency)
        # Record replicon number to the sheet
        xw.Range(repl_num_rg).value = repl.expenseUri.split(':')[-1]


def send_mail():
    logger.debug('Starting send_mail')
    if xw.sheets.active.name.__eq__("Config"):
        return
    # Clean Error Cell
    xw.Range(error_rg).value = ''

    if xw.Range(images_path_rg).value is None or xw.Range(repl_num_rg).value is None or not os.path.exists(
            xw.Range(images_path_rg).value):
        xw.Range(error_rg).value = 'Please validate if the replicon was generated or if the path to images exists!'
        return

    # check if images path contains the replicon number to rename it
    if not xw.Range(images_path_rg).value.__contains__(xw.Range(repl_num_rg).value):
        new_path = '\\'.join(xw.Range(images_path_rg).value.split("\\")[:-1]) + '\\' + xw.Range(repl_num_rg).value
        logger.debug('Renaming folder %s to %s' % (xw.Range(images_path_rg).value, new_path))
        shutil.move(xw.Range(images_path_rg).value, new_path)
        xw.Range(images_path_rg).value = new_path

    photo_pdf_path = pdf_creator.create_pdf(xw.Range(images_path_rg).value)
    list_pdf_path = generate_xl_pdf(xw.Range(images_path_rg).value, xw.Range(repl_num_rg).value)

    logger.debug('Starting Mail creation')
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    mail.To = xw.sheets["Config"].range(logic_mail_rg).value + ';' + (
        xw.sheets["Config"].range(manager_mail_rg).value if xw.sheets["Config"].range(
            manager_mail_rg).value is not None else '')
    mail.Subject = xw.sheets["Config"].range(user_name_rg).value + ' - ' + xw.Range(repl_num_rg).value + ' - ' + \
                   xw.Range(client_info_rg).value + ' Expense Sheet (' + \
                   str(int(xw.Range("C2").value)) + ') - ' + \
                   xw.Range(start_date_rg).value.strftime('%d/%m/%Y') + ' - ' + \
                   (xw.Range(start_date_rg).value + timedelta(days=5)).strftime('%d/%m/%Y')
    mail.HtmlBody = 'Seguem detalhes em anexo'
    try:
        logger.debug('attaching mail = %s' % (photo_pdf_path))
        logger.debug('attaching mail = %s' % (list_pdf_path))
        mail.Attachments.Add(photo_pdf_path)
        mail.Attachments.Add(list_pdf_path)
    except Exception as e:
        xw.Range(error_rg).value = 'File not found!'
        return
    mail.Display(False)

    # copy replicon list to main folder
    logger.debug('Copying pdf list from %s to %s' % (
        list_pdf_path, os.path.dirname(os.path.dirname(xw.Range(images_path_rg).value))))
    shutil.copy(list_pdf_path, os.path.dirname(xw.Range(images_path_rg).value))

    tar = tarfile.open(xw.Range(images_path_rg).value + "ok.tgz", "w:gz")
    tar.add(xw.Range(images_path_rg).value, filter=reset, arcname=xw.Range(images_path_rg).value.split("\\")[-1])
    tar.close()
    shutil.rmtree(xw.Range(images_path_rg).value, ignore_errors=True)


def reset(tarinfo):
    tarinfo.uid = tarinfo.gid = 0
    tarinfo.uname = tarinfo.gname = "root"
    return tarinfo


def generate_xl_pdf(path, repl_num):
    # Get the Excel Application COM object
    xl = EnsureDispatch("Excel.Application")
    print_area = printing_rg
    pdf_path = path + '\\' + str(repl_num) + '_list.pdf'

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


if __name__ == "__main__" or __name__ == "__builtin__":
    # create_replicon('', False)
    # send_mail()
    generate_xl_pdf('C:\Users\LOGIC\Dropbox\Trabalho\Replicon', '1234')
    # generate_xl_pdf()
