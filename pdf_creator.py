import base64
import logging
import mimetypes
import os
import shutil

from PyPDF2 import PdfFileMerger, PdfFileReader
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Image, PageBreak

# Starting logging
logging.basicConfig(level=logging.NOTSET)
logger = logging.getLogger(__name__)

# global vars
photo_pdf_filename = "fotos.pdf"
merged_pdf_filename = "comprovantes.pdf"
original_files_dirname = "originals"


def create_pdf(folder_root):
    if folder_root is None:
        return None
    if not os.path.exists(folder_root):
        logger.debug('Image folder does not exists!')
        return None
    doc = SimpleDocTemplate(folder_root + "\\" + photo_pdf_filename, pagesize=A4)
    parts = []
    for dirpath, dirnames, filenames in os.walk(folder_root):
        logger.debug('dirpath: %s - filenames: %s' % (dirpath, filenames))
        for filename in filenames:
            if filename.lower().endswith(".jpg") or filename.lower().endswith(".png"):
                filepath = os.path.join(dirpath, filename)
                logger.debug('Merge Images - filename: %s - filepath: %s' % (filename, filepath))
                parts.append(Image(filepath, width=A4[0], height=A4[1], kind='proportional'))
                parts.append(PageBreak())

        # do not interate on subfolders
        break
    doc.build(parts)

    pdfMerger = PdfFileMerger(strict=False)
    for dirpath, dirnames, filenames in os.walk(folder_root):
        for filename in filenames:
            if filename.lower().endswith(".pdf"):
                filepath = os.path.join(dirpath, filename)
                logger.debug('Merge PDF - filename: %s - filepath: %s' % (filename, filepath))
                with file(filepath, 'rb') as f:
                    pdfMerger.append(PdfFileReader(f, strict=False))

        # do not interate on subfolders
        break

    pdfMerger.write(folder_root + "\\" + merged_pdf_filename)
    logger.debug('PDF created')
    # Create a directory to move the original files
    if not os.path.exists(folder_root + "\\" + original_files_dirname):
        os.mkdir(folder_root + "\\" + original_files_dirname)
    # Move all files to originals dir, except the merged pdf
    for f in [lst for lst in os.listdir(folder_root) if lst not in (merged_pdf_filename, original_files_dirname)]:
        logger.debug(
            "Move file %s to %s" % (folder_root + "\\" + f, folder_root + "\\" + original_files_dirname + "\\" + f))
        shutil.move(folder_root + "\\" + f, folder_root + "\\" + original_files_dirname + "\\" + f)
    return folder_root + "\\" + merged_pdf_filename


def to_base64(fpath):
    if fpath is None:
        logger.debug('Path is null, no base64 string was created')
        return (None,None)
    logger.debug("Encoding file (%s) to base64" %(fpath))
    with open(fpath, "rb") as pdf_file:
        encoded_file = base64.b64encode(pdf_file.read())
    return (mimetypes.types_map['.pdf'],encoded_file)


if __name__ == "__main__":
    # create_pdf("C:\\Repositorios\\thi\\replicon\\63358")
    print to_base64("C:\\Repositorios\\thi\\replicon\\63358\\all.pdf")
