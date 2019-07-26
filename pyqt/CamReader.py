import cv2
import pyzbar.pyzbar as pyzbar
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage


class CamReader(QThread):
    change_pixmap = pyqtSignal(QImage)

    def run(self):
        cap = cv2.VideoCapture(0)
        font = cv2.FONT_HERSHEY_PLAIN

        while True:
            _, frame = cap.read()
            decoded_objects = pyzbar.decode(frame)
            for obj in decoded_objects:
                cv2.putText(frame, str(obj.data), (50, 50), font, 2,
                            (255, 0, 0), 3)
                print("Data", obj.data)
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            convert_to_qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            p = convert_to_qt_format.scaled(221, 181, Qt.KeepAspectRatio)
            self.change_pixmap.emit(p.mirrored(True, False))
            # cv2.namedWindow("Frame", cv2.WINDOW_GUI_NORMAL)
            # cv2.imshow("Frame", frame)
            key = cv2.waitKey(1)
            if key == 27:
                cap.release()
                # cv2.destroyWindow("Frame")
                break

# https://www.sefaz.rs.gov.br/NFCE/NFCE-COM.aspx?p=43190693015006003210651270004470561759268442|2|1|1|4242DC7DF093B2756A42B54D5E8AAA094070A7F8
