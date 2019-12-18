# -*- coding: utf-8 -*-
import logging

import cv2
import pyzbar.pyzbar as pyzbar
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class CamReader(QThread):
    change_pixmap = pyqtSignal(QImage)
    found_qr = pyqtSignal("QString")

    def run(self):
        cap = cv2.VideoCapture(0)
        font = cv2.FONT_HERSHEY_PLAIN

        while True:
            read, frame = cap.read()
            if not read:
                raise Exception("Cannot read webcam!")

            decoded_objects = pyzbar.decode(frame)
            for obj in decoded_objects:
                cv2.putText(frame, str(obj.data), (50, 50), font, 2, (255, 0, 0), 3)
                self.found_qr.emit(obj.data.decode("utf-8"))
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            convert_to_qt_format = QImage(
                rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888
            )
            p = convert_to_qt_format.scaled(221, 181, Qt.KeepAspectRatio)
            self.change_pixmap.emit(p.mirrored(True, False))
            # cv2.namedWindow("Frame", cv2.WINDOW_GUI_NORMAL)
            # cv2.imshow("Frame", frame)
            key = cv2.waitKey(1)
            if key == 27:
                cap.release()
                # cv2.destroyWindow("Frame")
                break
