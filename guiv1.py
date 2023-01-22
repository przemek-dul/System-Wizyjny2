import cv2
import sys
from PyQt5.QtWidgets import QLabel, QApplication, QPushButton, QRadioButton, QVBoxLayout, QComboBox, \
    QFileDialog, QMainWindow
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from engine import calcPhase, calcPercentage
import time
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class Thread(QThread):
    changePixmap = pyqtSignal(QImage)
    changePixmap2 = pyqtSignal(QImage)
    per = pyqtSignal(float)
    data = pyqtSignal(list)

    def __init__(self, parent=None):
        super(Thread, self).__init__(parent)
        self.path = None
        self.threadactive = False
        self.cap = None

    def run(self):
        if self.path is not None:
            if len(self.path) == 1:
                self.cap = cv2.VideoCapture(int(self.path))
            else:
                self.cap = cv2.VideoCapture(str(self.path))
        imgs = []
        myTime = 0
        percentages = []
        while True:
            timestart = time.time()
            if self.threadactive:
                ret, frame = self.cap.read()
                if ret:
                    time.sleep(0.0005)
                    rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgbImage.shape
                    bytesPerLine = ch * w
                    convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                    p = convertToQtFormat.scaled(256, 256, Qt.KeepAspectRatio)
                    self.changePixmap.emit(p)
                    if myTime < time.time():
                        if len(imgs) == 2:
                            imgs[0] = imgs[1]
                            imgs[1] = rgbImage
                            s = calcPhase(imgs[0], imgs[1])
                            if s is not None:
                                per1 = calcPercentage(s)
                                percentages.append(per1)
                                self.data.emit(percentages)
                                self.per.emit(per1)
                                r = cv2.cvtColor(s, cv2.COLOR_GRAY2RGB)
                                h, w, ch = r.shape
                                bytesPerLine = ch * w
                                convertToQtFormat = QImage(r.data, w, h, bytesPerLine, QImage.Format_RGB888)
                                p2 = convertToQtFormat.scaled(256, 256, Qt.KeepAspectRatio)
                            self.changePixmap2.emit(p2)

                        else:
                            imgs.append(rgbImage)
                        myTime = time.time() + 1


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'Pomiar fazy'
        self.left = 100
        self.top = 100
        self.width = 200
        self.height = 480
        self.initUI()

    @pyqtSlot(QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

    @pyqtSlot(QImage)
    def printImage(self, image):
        self.label2.setPixmap(QPixmap.fromImage(image))

    @pyqtSlot(float)
    def set_percentage(self, percentage):
        self.label4.setText(f"{round(percentage, 2)}%")

    def initUI(self):

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedSize(535, 550)
        self.path = None
        self.firstClick = True

        self.start = True

        self.label = QLabel(self)
        self.label.move(10, 10)
        self.label.resize(256, 256)
        self.label.setStyleSheet('border-style: outset;border-width: 2px;border-color: blue;')

        self.label2 = QLabel(self)
        self.label2.move(10 + 256, 10)
        self.label2.resize(256, 256)
        self.label2.setStyleSheet('border-style: outset;border-width: 2px;border-color: blue;')

        self.startBtn = QPushButton(self)
        self.startBtn.move(290, 280)
        self.startBtn.resize(100, 50)
        self.startBtn.setText('START')
        self.startBtn.setStyleSheet("font-size: 14pt;")
        self.startBtn.clicked.connect(self.start_update)

        self.stopBtn = QPushButton(self)
        self.stopBtn.move(290, 280 + 60)
        self.stopBtn.resize(100, 50)
        self.stopBtn.setText('Stop')
        self.stopBtn.setStyleSheet("font-size: 14pt;")
        self.stopBtn.clicked.connect(self.stop_update)

        self.label3 = QLabel(self)
        self.label3.move(290, 280 + 120)
        self.label3.resize(200, 50)
        self.label3.setText("Aktualny udział fazowy")
        self.label3.setStyleSheet("font-size: 14pt;border-style: outset;border-width: 2px;border-color: black;")

        self.label4 = QLabel(self)
        self.label4.move(290, 280 + 180)
        self.label4.resize(200, 50)
        self.label4.setText("0 %")
        self.label4.setAlignment(Qt.AlignCenter)
        self.label4.setStyleSheet("font-size: 14pt;border-style: outset;border-width: 2px;border-color: black;")

        vbox = QVBoxLayout()
        self.mode1 = QRadioButton("Odczyt z pliku", self)
        self.mode1.move(400, 280)
        self.mode1.setChecked(True)

        self.mode2 = QRadioButton("Odczyt z kamery", self)
        self.mode2.move(400, 300)

        self.label5 = QLabel(self)
        self.label5.move(400, 340)
        self.label5.setText('Kanał:')
        self.label5.setStyleSheet("font-size:12pt;")

        self.chanels = QComboBox(self)
        self.chanels.addItem('1')
        self.chanels.addItem('2')
        self.chanels.addItem('3')
        self.chanels.addItem('4')
        self.chanels.addItem('5')
        self.chanels.resize(40, 20)

        self.chanels.move(450, 340)

        self.label6 = QLabel(self)
        self.label6.move(400, 370)
        self.label6.setText('Ścierzka:')
        self.label6.setStyleSheet("font-size:12pt;")

        self.pathBtn = QPushButton(self)
        self.pathBtn.move(470, 370)
        self.pathBtn.resize(20, 20)
        self.pathBtn.clicked.connect(self.get_file)

        self.th = None
        self.canvas = Canvas(self, width=12, height=12, dpi=55)
        self.canvas.plot([])
        self.canvas.move(20, 270)
        self.canvas.resize(260, 260)
        self.show()

    def stop_update(self):
        if self.th is not None:
            self.th.threadactive = False

    def start_update(self):
        if self.firstClick:
            self.th = Thread(self)
            self.th.changePixmap.connect(self.setImage)
            self.firstClick = False
            self.th.changePixmap2.connect(self.printImage)
            self.th.per.connect(self.set_percentage)
            self.th.data.connect(self.update_plot)
            if self.path is not None:
                self.th.path = self.path[0]
                self.th.start()
                self.th.threadactive = True

        elif self.th is not None:
            self.th.threadactive = True

    def get_file(self):
        self.path = QFileDialog.getOpenFileName(self, 'Open file', 'c:\\', "Video files (*.mp4)")
        if self.th is not None:
            self.th.path = self.path[0]
            self.th.cap = cv2.VideoCapture(str(self.th.path))
            self.th.threadactive = False

    @pyqtSlot(list)
    def update_plot(self, arr):
        self.canvas.plot(arr)


class Canvas(FigureCanvas):
    def __init__(self, parent=None, width=4, height=4, dpi=20):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

    def plot(self, arr):
        self.figure.clear()
        x = arr
        ax = self.figure.add_subplot(111)
        ax.set_ylabel("Udzaił[%]")
        ax.set_xlabel("Pomiar[-]")
        ax.plot(x)
        ax.grid()
        self.draw()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
