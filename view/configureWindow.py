from PyQt5.QtWidgets import (QMessageBox, QMainWindow, QLabel, QApplication, QPushButton, QLineEdit, QComboBox)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal, Qt
from models.antminer import Antminer
import time

class ConfigureWindow(QMainWindow):

    got_updates = pyqtSignal(str)

    def __init__(self, parent=None, list_ip=None):
        super(ConfigureWindow, self).__init__(parent)
        self.item_list = list_ip
        self.validation = False
        self.move(100, 100)
        self.setWindowTitle('Configure All ASIC')
        self.center()
        # print(list_ip)
        self.err_lbl = QLabel(self)
        self.err_lbl.setGeometry(135, 15, 150, 20)
        self.setWindowIcon(QIcon('./assets/images/icon_tool.png'))
        self.url_lbl = QLabel('<b>Pool URL:</b>', self)
        self.url_lbl.setGeometry(20, 50, 100, 20)

        self.worker_lbl = QLabel('<b>Worker:</b>', self)
        self.worker_lbl.setGeometry(20, 90, 100, 20)

        self.psd_lbl = QLabel('<b>Password:</b>', self)
        self.psd_lbl.setGeometry(20, 130, 100, 20)

        self.url_edt = QLineEdit(self)
        self.url_edt.setPlaceholderText('Input pool: ')
        self.url_edt.setGeometry(100, 50, 220, 20)

        self.worker_edt = QLineEdit(self)
        self.worker_edt.setPlaceholderText('Input workername: ')
        self.worker_edt.setGeometry(100, 90, 220, 20)

        self.psd_edt = QLineEdit(self)
        self.psd_edt.setPlaceholderText('Input key: ')
        self.psd_edt.setGeometry(100, 130, 220, 20)

        self.connect_btn = QPushButton('Configure', self)
        self.connect_btn.setGeometry(150, 185, 100, 30)
        self.connect_btn.setStyleSheet('QPushButton {background-color: #009EDD; color: white;}')
        self.connect_btn.clicked.connect(self.prepare_configure)
        self.connect_btn.clicked.connect(self.configure_device)

        self.comboBox = QComboBox(self)
        self.comboBox.setGeometry(320, 20, 120, 20)
        self.setFixedSize(450, 250)
        self.share_combobox()

    def prepare_configure(self):
        self.pool = self.url_edt.text().strip()
        self.worker = self.worker_edt.text().strip()
        self.password = self.psd_edt.text().strip()
        if self.item_list and (self.pool and self.worker and self.password):
            self.err_lbl.setText('<center><b>Start configuring.<br>It may take some minutes:</b></center>')
            self.err_lbl.setStyleSheet('color: black')
            self.connect_btn.setStyleSheet('background-color: #11f93f; color: white')
            self.connect_btn.setText('Wait')
            self.connect_btn.setEnabled(False)
            self.validation = True
            return
        else:
            self.err_lbl.setText('<center><b>Wrong Data</b></center>')
            self.err_lbl.setStyleSheet('color: red')
            self.validation = False
            return

    def configure_device(self):
        if not self.validation:
            return
        self.error_message('Press Ok, to start scanning. It may take a long time')
        curr_type = str(self.comboBox.currentText())
        if not self.worker[-1].isnumeric():
            counter = 0
        else:
            counter = int(self.worker[-1])
        for item in self.item_list:
            counter += 1
            if item[1] == curr_type:
                miner = Antminer(item[0])
                result = miner.configure_asic(self.pool, self.worker+str(counter), self.password)
                del miner

            self.err_lbl.setText('<center><b>Complete!</b></center>')
            self.err_lbl.setStyleSheet('color: green')
        self.err_lbl.setText('')
        self.connect_btn.setStyleSheet('QPushButton {background-color: #009EDD; color: white;}')
        self.connect_btn.setText('Configure')
        self.connect_btn.setEnabled(True)
        # self.got_updates.emit('1')

    def share_combobox(self):
        if self.item_list:
            buffer = []
            for item in self.item_list:
                if item[1] not in buffer:
                    buffer.append(item[1])
                    self.comboBox.addItem(item[1])

    def error_message(self, message, header='Error'):
        QMessageBox.information(self, header, str(message))

    def center(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())