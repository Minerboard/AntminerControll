from PyQt5.QtWidgets import (QWidget, QLabel, QProgressBar, QMessageBox, QApplication, QPushButton, QLineEdit)
from PyQt5.QtCore import (pyqtSignal, QRect, QThread)
from PyQt5.QtGui import QIcon
from models.lib.util import Util
from time import sleep
from models.scanner import ASICScanner


class ScanWindow(QWidget):

        got_asics = pyqtSignal(str)

        def __init__(self, parent=None):
            super(ScanWindow, self).__init__()
            self.result = None
            self.validation = True

            self.setFixedSize(400, 250)
            self.move(100, 100)
            self.setWindowTitle('Scan For ASICs ')
            self.center()

            self.status_lbl = QLabel(self)
            self.status_lbl.setGeometry(100, 5, 210, 40)

            self.setWindowIcon(QIcon('./assets/images/icon_tool.png'))

            self.progressBar = QProgressBar(self)
            self.progressBar.setGeometry(QRect(95, 140, 220, 20))
            self.progressBar.setProperty("value", 0)
            self.progressBar.setTextVisible(False)
            self.progressBar.hide()

            self.ip_lbl = QLabel(self)
            self.ip_lbl.setGeometry(175, 15, 80, 20)

            self.url_lbl = QLabel('<b>Start From:</b>', self)
            self.url_lbl.setGeometry(20, 50, 100, 20)

            self.worker_lbl = QLabel('<b>Up to:</b>', self)
            self.worker_lbl.setGeometry(55, 90, 100, 20)

            self.start_ip_edt = QLineEdit(self)
            self.start_ip_edt.setPlaceholderText('Example: 192.168.1.1')
            self.start_ip_edt.setText('192.168.100.1')
            self.start_ip_edt.setGeometry(115, 50, 180, 20)

            self.last_ip_edt = QLineEdit(self)
            self.last_ip_edt.setPlaceholderText('Example: 192.168.2.223')
            self.last_ip_edt.setText('192.168.100.16')
            self.last_ip_edt.setGeometry(115, 90, 180, 20)

            self.scan_btn = QPushButton('Scan', self)
            self.scan_btn.setGeometry(90, 185, 100, 30)
            self.scan_btn.setStyleSheet('background-color: #009EDD; color: white')
            self.scan_btn.clicked.connect(self.prepare_scan)
            self.scan_btn.clicked.connect(self.onStart)

            self.stop_btn = QPushButton('Stop', self)
            self.stop_btn.setGeometry(220, 185, 100, 30)
            self.stop_btn.setStyleSheet('background-color: #009EDD; color: white')
            self.stop_btn.clicked.connect(self.onStop)

        def onStart(self):
            if not self.validation:
                return
            self.progressBar.show()
            self.progressBar.setRange(0,0)

            print('start scan')
            self.error_message('Press Ok, to start scanning. It may take a long time')

            self.myLongTask = TaskThread(self.start_ip, self.end_ip)
            self.myLongTask.taskFinished.connect(self.onFinished)
            self.scan_btn.setEnabled(False)
            self.myLongTask.start()

        def finish_scan(self):
            print('finally scanned')
            if self.myLongTask.status:
                self.status_lbl.setText("<center><b>Complete</b></center>")
                self.got_asics.emit('1')
                self.scan_btn.setStyleSheet('background-color: #009EDD; color: white')
                sleep(1)
                self.close()

            else:
                self.got_asics.emit('2')
                self.status_lbl.setText('<center>No ASICs detected.</center>')
                self.status_lbl.setStyleSheet('color: red')
                self.scan_btn.setStyleSheet('background-color: #009EDD; color: white')
                self.scan_btn.setText('Scan')
                return

        def onFinished(self):
            self.progressBar.setRange(0,100)
            self.scan_btn.setEnabled(True)
            self.stop_btn.setEnabled(True)
            self.progressBar.hide()
            self.finish_scan()

        def onStop(self):
            self.stop_btn.setEnabled(False)
            self.myLongTask.stop()
            self.myLongTask.taskFinished.connect(self.onFinished)

        def prepare_scan(self):
            self.validation = True
            self.start_ip, self.end_ip = self.start_ip_edt.text().strip(), self.last_ip_edt.text().strip()
            print('prepare1')
            if (self.start_ip == '' or self.end_ip == '') or (not Util.check_ipv4(self.start_ip) or not
                Util.check_ipv4(self.end_ip)) or (not Util.compare_ipv4(self.start_ip, self.end_ip)):
                self.status_lbl.setText("<center>Missing data or<br>Wrong range.</center>")
                self.status_lbl.setStyleSheet('color: red')
                self.validation = False
                print('done')
                return
            print('prepare2')
            if self.validation:
                self.status_lbl.setText('<center><b>Start scanning.<br>It may take some minutes:</b></center>')
                self.status_lbl.setStyleSheet('color: black')
                self.scan_btn.setStyleSheet('background-color: #11f93f; color: white')
                self.scan_btn.setText('Wait')
                print('done')
                return

        def error_message(self, message='What is going on??'):
            QMessageBox.information(self, 'Notification', str(message))


        def center(self):
            frameGm = self.frameGeometry()
            screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
            centerPoint = QApplication.desktop().screenGeometry(screen).center()
            frameGm.moveCenter(centerPoint)
            self.move(frameGm.topLeft())

class TaskThread(QThread):
    taskFinished = pyqtSignal()
    def __init__(self, start_ip, end_ip):
        super(TaskThread, self).__init__()
        print('thread')
        self.start_ip = start_ip
        self.end_ip = end_ip

    def run(self):
        self.scanner = ASICScanner(self.start_ip, self.end_ip)
        print('scanner created')
        self.scanner.control_range_scan()
        self.taskFinished.emit()

    def stop(self):
        self.scanner.stop()

    @property
    def status(self):
        return self.scanner.status