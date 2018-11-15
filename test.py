import time

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class Ui_Form(QMainWindow):
    def __init__(self, parent=None):
        super(Ui_Form, self).__init__(parent)
        self.setFixedSize(1200, 680)
        self.setWindowTitle('Minerboard ASIC manager')

        self.progressBar = QProgressBar(self)
        self.progressBar.setGeometry(QRect(150, 590, 118, 23))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setTextVisible(True)
        self.progressBar.setObjectName("progressBar")

        self.pushButton = QPushButton(self)
        self.pushButton.setGeometry(QRect(25, 50, 170, 40))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.onStart)

        self.myLongTask = TaskThread()
        self.myLongTask.taskFinished.connect(self.onFinished)
        self.show()

    def onStart(self):
        self.progressBar.setRange(0,0)
        self.myLongTask.start()

    def onFinished(self):
        # Stop the pulsation
        self.progressBar.setRange(0,120)

class TaskThread(QThread):
    taskFinished = pyqtSignal()
    def run(self):
        for i in range(500000):
            print(i)
        time.sleep(3)
        self.taskFinished.emit()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    Form = QWidget()
    ui = Ui_Form()
    sys.exit(app.exec_())