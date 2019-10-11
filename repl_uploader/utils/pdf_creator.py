# -*- coding: utf-8 -*-
import base64
import logging
import mimetypes
import os
import shutil
from glob import glob
from math import floor

import fitz
from PyPDF2 import PdfFileMerger, PdfFileReader
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Image, PageBreak

# Starting logging
logging.basicConfig(level=logging.NOTSET)
logger = logging.getLogger(__name__)

# global vars
photo_pdf_filename = "fotos.pdf"
original_files_dirname = "originals"


def create_pdf(folder_root, replicon_no):
    merged_pdf_filename = replicon_no + "_comprovantes.pdf"
    if folder_root is None:
        return None
    if not os.path.exists(folder_root):
        logger.debug("Image folder does not exists!")
        return None

    # Create a directory to move the original files
    if not os.path.exists(folder_root + "\\" + original_files_dirname):
        os.mkdir(folder_root + "\\" + original_files_dirname)

    # Merge NF files
    create_pdf_panel(folder_root)

    doc = SimpleDocTemplate(folder_root + "\\" + photo_pdf_filename, pagesize=A4)
    parts = []
    images_ext = ("JPG", "JPEG", "PNG")

    for filename in filter(
        lambda x: x.split(".")[-1].upper() in images_ext,
        glob(folder_root + "\\*", recursive=False),
    ):
        logger.debug("Merge Images - filename: {} ".format(filename))
        parts.append(
            Image(
                filename,
                width=doc.width - 12,
                height=doc.height - 12,
                kind="proportional",
            )
        )
        parts.append(PageBreak())
    doc.build(parts)

    pdf_merger = PdfFileMerger(strict=False)
    for filename in glob(folder_root + "\\*.pdf", recursive=False):
        logger.debug("Merge PDF - filename: {}".format(filename))
        with open(filename, "rb") as f:
            pdf_merger.append(PdfFileReader(f, strict=False))

    pdf_merger.write(folder_root + "\\" + merged_pdf_filename)
    logger.debug("PDF created")

    # Move all files to originals dir, except the merged pdf
    for f in filter(
        lambda x: x
        not in (
            folder_root + "\\" + merged_pdf_filename,
            folder_root + "\\" + original_files_dirname,
        ),
        glob(folder_root + "\\*", recursive=False),
    ):
        logger.debug(
            "Move file %s to %s"
            % (f, folder_root + "\\" + original_files_dirname + "\\")
        )
        shutil.move(f, folder_root + "\\" + original_files_dirname + "\\")
    return folder_root + "\\" + merged_pdf_filename


def create_pdf_panel(folder_root):
    logger.debug("Starting nfs pdf panel creation")
    # nf files
    nfs = glob(folder_root + "\\sfnf*")
    if nfs.__len__() == 0:
        return

    # empty output PDF
    final_doc = fitz.open()

    # get a4 paper size to calculate the panels
    width, height = fitz.PaperSize("a4")  # A4 portrait output page format

    # -------------
    # |r1   |r2   |
    # |     |     |
    # -------------
    # |r3   |r4   |
    # |     |     |
    # -------------
    # |r5   | r6  |
    # |     |     |
    # -------------
    # define the 6 rectangles per page
    r1 = fitz.Rect(0, 0, width * 0.5, floor(height * 0.33 + 3))
    r2 = r1 + (r1.width, 0, r1.width, 0)
    r3 = r1 + (0, r1.height, 0, r1.height)
    r4 = r2 + (0, r2.height, 0, r2.height)
    r5 = r3 + (0, r3.height, 0, r3.height)
    r6 = r4 + (0, r4.height, 0, r4.height)

    # put them in a list
    r_tab = [r1, r2, r3, r4, r5, r6]
    page_count = 0

    for infile in nfs:
        logger.debug("Opening file {}".format(infile))
        src = fitz.open(infile)
        # now copy input pages to output
        for spage in src:
            if page_count % 6 == 0:  # create new output page
                page = final_doc.newPage(-1, width=width, height=height)
            # insert input page into the correct rectangle
            page.showPDFpage(
                r_tab[page_count % 6],  # select output rect
                src,  # input document
                spage.number,
            )  # input file page number
            page_count += 1
        logger.debug("Closing file {}".format(infile))

    # By all means, save new file using garbage collection and compression
    logger.debug("Saving 6up file")
    final_doc.save("{}\\6up.pdf".format(folder_root), garbage=4, deflate=True)

    final_doc.close()
    src.close()

    # Move all files to originals dir, except the merged pdf
    logger.debug("Moving original nf files")
    for i in nfs:
        shutil.move(i, folder_root + "\\" + original_files_dirname + "\\")
    logger.debug("Starting nfs pdf panel creation")


# TODO: Deprecated, we do not attach the pdf to the replicon anymore
def to_base64(fpath):
    if fpath is None:
        logger.debug("Path is null, no base64 string was created")
        return (None, None)
    logger.debug("Encoding file (%s) to base64" % (fpath))
    with open(fpath, "rb") as pdf_file:
        encoded_file = base64.b64encode(pdf_file.read())
    return (mimetypes.types_map[".pdf"], encoded_file)


if __name__ == "__main__" or __name__ == "__builtin__":
    create_pdf("C:\\Users\\LOGIC\\Dropbox\\Trabalho\\Replicon\\123", "123")
    # print to_base64("C:\\Repositorios\\thi\\replicon\\63358\\all.pdf")
    # create_pdf_panel('C:\\Users\\LOGIC\\Dropbox\\Trabalho\\Replicon\\demo1')
