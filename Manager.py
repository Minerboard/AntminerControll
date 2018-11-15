#!/usr/bin/env python
import sys
import re
from models.antminer import Antminer
from view.configureWindow import ConfigureWindow
from view.scanWindow import ScanWindow
from pprint import pprint
from PyQt5.QtWidgets import (QMainWindow, QLabel, QAction, QApplication, QPushButton,
                             QInputDialog, QListWidget, QMessageBox)
from PyQt5.QtGui import QIcon, QFont
from models.lib.util import Util


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.scanWin = None
        self.confWindow = None
        self.asics = {}
        self.current_item = None
        self.device_container = []

        self.asicCount = 0
        self.toolbar = self.addToolBar('Settings')
        self.setFixedSize(1200, 680)
        self.setWindowTitle('Minerboard ASIC manager')
        self.setFont(QFont('SansSerif', 9))
        self.setWindowIcon(QIcon('./assets/images/icon_tool.png'))
        self.listWidget = QListWidget(self)
        self.listWidget.setGeometry(10, 100, 1180, 550)

        self.add_action = QAction('Add new ASIC', self)
        self.add_action.setShortcut('Ctrl+N')
        self.add_action.setStatusTip('Add ASIC')  # show when move mouse to the icon
        self.add_action.triggered.connect(self.add_single_asic)
        self.add_action.setFont(QFont('SansSerif', 9))

        self.configure_action = QAction('Configure all ASICs', self)
        self.configure_action.setShortcut('Ctrl+E')
        self.configure_action.setStatusTip('Connect all ASICs')  # show when move mouse to the icon
        self.configure_action.triggered.connect(self.show_confWindow)
        self.configure_action.setFont(QFont('SansSerif', 9))

        self.scann_action = QAction('Scan for ASICs', self)
        self.scann_action.setShortcut('Ctrl+F')
        self.scann_action.setStatusTip('Scan network for ASICs')  # show when move mouse to the icon
        self.scann_action.triggered.connect(self.show_scanWindow)
        self.scann_action.setFont(QFont('SansSerif', 9))

        self.update_action = QAction('Update ASICs', self)
        self.update_action.setShortcut('Ctrl+U')
        self.update_action.setStatusTip('Update ASICs')  # show when move mouse to the icon
        self.update_action.triggered.connect(self.init_asics)
        self.update_action.setFont(QFont('SansSerif', 9))

        self.cleanup_action = QAction('CleanUp list', self)
        self.cleanup_action.setShortcut('Ctrl+Del')
        self.cleanup_action.setStatusTip('Delete all ASICs from memory')  # show when move mouse to the icon
        self.cleanup_action.triggered.connect(self.cleanup)
        self.cleanup_action.setFont(QFont('SansSerif', 9))

        self.reboot_action = QAction('Reboot all ASICs', self)
        self.reboot_action.setShortcut('Ctrl+R')
        self.reboot_action.setStatusTip('Reboot all ASICs')  # show when move mouse to the icon
        self.reboot_action.triggered.connect(self.reboot_all)
        self.reboot_action.setFont(QFont('SansSerif', 9))

        self.toolbar.addAction(self.add_action)
        self.toolbar.addAction(self.scann_action)
        self.toolbar.addAction(self.configure_action)
        self.toolbar.addAction(self.reboot_action)
        self.toolbar.addAction(self.cleanup_action)
        self.toolbar.addAction(self.update_action)

        self.listWidget.itemClicked.connect(self.listClicked)

        self.item_ip_lbl = QLabel('Address', self)
        self.item_ip_lbl.move(45, 60)

        self.item_status_lbl = QLabel('Status', self)
        self.item_status_lbl.move(175, 60)

        self.item_type_lbl = QLabel('Type', self)
        self.item_type_lbl.move(290, 60)

        self.item_hr_lbl = QLabel('GHash 5s', self)
        self.item_hr_lbl.move(415, 60)

        self.item_fan_lbl = QLabel('Temp ℃', self)
        self.item_fan_lbl.move(520, 60)

        self.item_temp_lbl = QLabel('Fan (r/min)', self)
        self.item_temp_lbl.move(620, 60)

        self.item_incchip_lbl = QLabel('Pool1', self)
        self.item_incchip_lbl.setGeometry(860, 65, 120, 20)

        self.item_lastscan_lbl = QLabel('Worker1', self)
        self.item_lastscan_lbl.move(1110, 60)

        self.total_asic_lbl = QLabel('<b>Total ASICs: </b>', self)
        self.total_asic_lbl.setGeometry(20, 655, 90, 20)
        self.total_asic_lbl.setFont(QFont('SansSerif', 9))

        self.total_asic_val = QLabel(str(self.asicCount), self)
        self.total_asic_val.setGeometry(115, 655, 150, 20)
        self.total_asic_val.setFont(QFont('SansSerif', 9))
        for i in [self.item_ip_lbl, self.item_fan_lbl, self.item_hr_lbl, self.item_type_lbl, self.item_temp_lbl,
                  self.item_status_lbl, self.item_lastscan_lbl, self.item_incchip_lbl]:
            i.setFont(QFont('SansSerif', 10))

        self.center()
        self.show()
        # self.init_asics('1')
        # self.show_confWindow()


    def init_asics(self, result):
        print(result)
        print(Util.load_asics_json())
        self.listWidget.clear()
        if not result and self.device_container:
            doc_string = ''
            for i in self.device_container:
                asic = Antminer(i.ip)
                if not asic.existence:
                    print(asic.ip)
                    self.device_container.remove(i)
                    Util.delete_from_json(asic.ip)
                    continue
                doc_string ='  {0}{7}{1}{7}{2}{7}{3}{7}{4}{7}{5}{7}{6}{7}{8} '.format(asic.ip, asic.status,
                                                                                      asic.type, asic.rate,
                                                                                      asic.temp, asic.fan,
                                                                                      asic.pool,
                                                                                      ' ' * 18, asic.worker)
                self.listWidget.addItem(doc_string)
        elif result == '1':
            self.device_container.clear()
            asics = Util.load_asics_json()
            if asics and isinstance(asics, list):
                for i in asics:
                    asic = Antminer(i)
                    doc_string = '  {0}{7}{1}{7}{2}{7}{3}{7}{4}{7}{5}{7}{6}{7}{8} '.format(asic.ip, asic.status,
                                                                                           asic.type, asic.rate,
                                                                                           asic.temp, asic.fan,
                                                                                           asic.pool,
                                                                                           ' ' * 18, asic.worker)
                    self.listWidget.addItem(doc_string)
                    self.device_container.append(asic)
        else:
            self.error_message('No ASICs found in list')
        self.total_asic_val.setText(str(len(self.device_container)))
        print(self.device_container)

    def show_scanWindow(self):
        if self.scanWin:
            self.scanWin.close()
        self.scanWin = ScanWindow(self)
        self.scanWin.show()
        self.scanWin.got_asics.connect(self.init_asics)

    def show_confWindow(self, curr_ip=None):
        if self.confWindow:
            self.confWindow.close()
        list_ip = []
        if self.device_container and curr_ip:
            print(1)
            ip = re.search(r'[0-9]+(?:\.[0-9]+){3}', curr_ip.strip()).group(0)
            if ip:
                print(2)
                for i in self.device_container:
                    if i.ip == ip:
                        list_ip.append([i.ip, i.type])
                    self.confWindow = ConfigureWindow(self, list_ip=list_ip)
                    self.confWindow.show()
                    print(3)
        elif self.device_container and not curr_ip:
            for i in self.device_container:
                list_ip.append([i.ip, i.type])
            self.confWindow = ConfigureWindow(self, list_ip=list_ip)
            self.confWindow.show()
        else:
            self.error_message('No ASIC found in the list')


    def cleanup(self):
        if self.delete_confirmation("Are you sure you want to delete all ASICs"):
            self.listWidget.clear()
            self.device_container.clear()
            Util.cleanup_json()

    def center(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def add_single_asic(self):
        ip, result = QInputDialog.getText(self, 'Add new ASIC', 'Enter IPv4 address of new ASIC: ')
        ip = ip.strip()
        if (result == True) and (Util.check_ipv4(ip)):
            if self.device_container:
                for i in self.device_container:
                    if ip == i.ip:
                        self.error_message(' ' * 10 + 'ASIC already in the list' + ' ' * 10)
                        return
            asic = Antminer(ip)
            print(asic.ip,asic.existence)
            if asic.existence:
                self.listWidget.addItem('  {0}{7}{1}{7}{2}{7}{3}{7}{4}{7}{5}{7}{6}{7}{8} '.format(asic.ip, asic.status,
                                                                                                  asic.type, asic.rate,
                                                                                                  asic.temp, asic.fan,
                                                                                                  asic.pool,
                                                                                                  ' ' * 18, asic.worker))
                self.asicCount += 1
                self.total_asic_val.setText(str(self.asicCount))
                self.device_container.append(asic)
            else:
                self.error_message(' '*10 + 'No ASIC Found' + ' '*10)
                self.add_single_asic()
        elif (result == True) and not (Util.check_ipv4(ip)):
            self.error_message(' '*10 + 'Wrong IP' + ' '*10)
            self.add_single_asic()

    def reboot_selected(self, item):
        message = 'Can not connect to ASIC'
        ip = re.search(r'[0-9]+(?:\.[0-9]+){3}', item.text().strip()).group(0)
        asic = Antminer(ip)
        if asic.existence:
            for i in self.device_container:
                if ip == i.ip:
                    self.error_message('Try to reboot ASIC\nIt may take a minute.', header='Reboot status')
                    result = asic.reboot()
                    if result:
                        message = "ASIC rebooted successfully"
        self.error_message(message, header='Reboot report')

    def reboot_all(self):
        if self.device_container:
            self.error_message('Try to reboot all ASICs\nIt may take some minutes.', header='Reboot status')
            errored_list = []
            rebooted_list = []
            for i in self.device_container:
                result = i.reboot()
                if result:
                    rebooted_list.append(i.ip)
                else:
                    errored_list.append(i.ip)
            rebooted_mess = 'Rebooted ASICs:\n' + '\n'.join(rebooted_list)
            err_mess = 'Not rebooted ASICs:\n' + '\n'.join(errored_list)
            if rebooted_list:
                self.error_message(rebooted_mess)
            elif errored_list:
                self.error_message(err_mess)
        else:
            self.error_message('There are no scanned ASIC')

    def listClicked(self, item):
        msgBox = QMessageBox()
        msgBox.setWindowTitle('What do you want to do?')
        msgBox.setText("<b>You`ve chosen:</b>\t" + item.text().split()[0])
        msgBox.addButton(QPushButton('Cancel'), QMessageBox.RejectRole)
        msgBox.addButton(QPushButton('Configure'), QMessageBox.YesRole)
        msgBox.addButton(QPushButton('Delete'), QMessageBox.NoRole)
        msgBox.addButton(QPushButton('Reboot'), QMessageBox.ActionRole)
        res = msgBox.exec_()
        # print(res)
        if res == 0:
            print('cancel')
        elif res == 1:
            self.current_item = item
            self.show_confWindow(curr_ip=item.text())
        elif res == 2:
            self.delete_item(item)
        elif res == 3:
            self.reboot_selected(item)

    def delete_item(self, item):
        if self.delete_confirmation("Are you sure you want to delete the unit"):
            # delete chosen
            ip = re.search(r'[0-9]+(?:\.[0-9]+){3}', item.text().strip()).group(0)
            for item in self.listWidget.selectedItems():
                self.listWidget.takeItem(self.listWidget.row(item))
            if ip:
                Util.delete_from_json(ip)
                for i in self.device_container:
                    if i.ip == ip:
                        self.device_container.remove(i)
                        self.total_asic_val.setText(str(self.asicCount))
                        break
        else:
            self.listClicked(item)

    def delete_confirmation(self, message):
        reply = QMessageBox.question(self, 'Delete comfirmation',
                                     message, QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            return True
        return False

    def error_message(self, message, header='Error'):
        QMessageBox.information(self, header, str(message))

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Exit',
                                     "Are you sure to quit?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.scanWin:
                self.scanWin.close()
            elif self.confWindow:
                self.confWindow.close()
            event.accept()
        else:
            event.ignore()

def create_app():
    app = QApplication(sys.argv)
    tutorial_window = MainWindow()
    tutorial_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    create_app()


