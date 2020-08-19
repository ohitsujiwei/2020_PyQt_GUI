import struct
import sys
import time

import bluetooth
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox

from Regulator_GUI import Ui_MainWindow


gDeviceBluetooth = None


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.guiFunction()

    def mScanDevices(self):
        self.mThreadScan = ThreadScan()
        self.mThreadScan.mSignalBluetooth.connect(self.runThreadScanListBluetooth)
        self.mThreadScan.start()

        self.pushButton_Scan.setText("Scanning...")
        self.pushButton_Scan.setEnabled(False)
        self.listWidget.setEnabled(False)

    def mDisconnect(self):
        global gDeviceBluetooth

        if self.mThreadTransfer.mRunning is True:
            self.mThreadTransfer.mRun(False)

        if gDeviceBluetooth is not None:
            gDeviceBluetooth.close()
            gDeviceBluetooth = None
            self.textBrowser.append("Disconnected from \"" + self.mSelectBluetoothName + "\".")
            self.label_Bluetooth.setText("Bluetooth")

        self.pushButton_Scan.setEnabled(True)
        self.pushButton_Disc.setEnabled(False)
        self.pushButton_Param.setEnabled(False)
        self.listWidget.setEnabled(True)
        self.checkBox_1.setEnabled(False)
        self.checkBox_2.setEnabled(False)
        self.checkBox_3.setEnabled(False)
        self.checkBox_4.setEnabled(False)
        self.checkBox_1.setChecked(False)
        self.checkBox_2.setChecked(False)
        self.checkBox_3.setChecked(False)
        self.checkBox_4.setChecked(False)

    def mSelectBluetooth(self):
        self.label_Bluetooth.setText("Connecting...")
        self.listWidget.setEnabled(False)
        self.nBluetoothAddress = self.mListBluetooth[self.listWidget.currentRow()]
        self.mThreadConnect = ThreadConnect(self.nBluetoothAddress)
        self.mThreadConnect.mSignalState.connect(self.runThreadConnectBluetooth)
        self.mThreadConnect.start()

    def mGetParameter(self):
        if self.mThreadTransfer.mRunning is False:
            self.mThreadTransfer.mRun(True)
            self.mSendData(0.0, 5)

    def mUpdateSliderRange(self):
        try:
            nMin = float(self.lineEdit_Min_1.displayText()) / self.mResolution
            nMax = float(self.lineEdit_Max_1.displayText()) / self.mResolution
            self.slider_1.setRange(nMin, nMax)
            nMin = float(self.lineEdit_Min_2.displayText()) / self.mResolution
            nMax = float(self.lineEdit_Max_2.displayText()) / self.mResolution
            self.slider_2.setRange(nMin, nMax)
            nMin = float(self.lineEdit_Min_3.displayText()) / self.mResolution
            nMax = float(self.lineEdit_Max_3.displayText()) / self.mResolution
            self.slider_3.setRange(nMin, nMax)
            nMin = float(self.lineEdit_Min_4.displayText()) / self.mResolution
            nMax = float(self.lineEdit_Max_4.displayText()) / self.mResolution
            self.slider_4.setRange(nMin, nMax)
        except Exception:
            QMessageBox.critical(self, "InputError", "An error occurred while updating the slider range.", QMessageBox.Ok)

    def mEmittedSlider(self, nNum):
        if nNum == 1:
            nValue = self.slider_1.value() * self.mResolution
            self.label_Value_1.setNum(nValue)
            if self.checkBox_1.isChecked() is True:
                self.mSendData(nValue, nNum)
        elif nNum == 2:
            nValue = self.slider_2.value() * self.mResolution
            self.label_Value_2.setNum(nValue)
            if self.checkBox_2.isChecked() is True:
                self.mSendData(nValue, nNum)
        elif nNum == 3:
            nValue = self.slider_3.value() * self.mResolution
            self.label_Value_3.setNum(nValue)
            if self.checkBox_3.isChecked() is True:
                self.mSendData(nValue, nNum)
        elif nNum == 4:
            nValue = self.slider_4.value() * self.mResolution
            self.label_Value_4.setNum(nValue)
            if self.checkBox_4.isChecked() is True:
                self.mSendData(nValue, nNum)

    def mSendData(self, nValue, nNum):
        global gDeviceBluetooth
        try:
            gDeviceBluetooth.getsockname()
        except Exception:
            QMessageBox.critical(self, "Error", "An error occurred while connecting to the device.", QMessageBox.Ok)
        else:
            nBuffer = bytes.fromhex("ff 55 05")
            nBuffer += bytearray(struct.pack("f", nValue))
            nBuffer += bytearray(struct.pack("b", nNum))
            gDeviceBluetooth.send(nBuffer)
            nStringHex = ' '.join('{:02x}'.format(x) for x in nBuffer)
            if nNum == 5:
                self.textBrowser.append("Send : [ Param ] = [ %s ]" % (nStringHex))
            else:
                self.textBrowser.append("Send : [ K%d ] = [ %.2f ] = [ %s ]" % (nNum, nValue, nStringHex))

    def runThreadScanListBluetooth(self, nListBluetooth):
        self.pushButton_Scan.setText("Scan")
        self.pushButton_Scan.setEnabled(True)
        self.listWidget.clear()
        self.listWidget.setEnabled(True)
        self.mListBluetooth = nListBluetooth
        for nDevice in self.mListBluetooth:
            item = QtWidgets.QListWidgetItem(bluetooth.lookup_name(nDevice))
            item.setFont(self.font)
            self.listWidget.addItem(item)

    def runThreadConnectBluetooth(self, nState):
        if nState is False:
            QMessageBox.critical(QMessageBox(), "OSError", "Can't connect to Bluetooth device.", QMessageBox.Ok)
            self.label_Bluetooth.setText("Bluetooth")
            self.listWidget.setEnabled(True)
        else:
            self.mSelectBluetoothName = bluetooth.lookup_name(self.mListBluetooth[self.listWidget.currentRow()])
            self.textBrowser.append("Connect to \"" + self.mSelectBluetoothName + "\" (" + self.nBluetoothAddress + ").")
            self.label_Bluetooth.setText(self.mSelectBluetoothName)
            self.pushButton_Scan.setEnabled(False)
            self.pushButton_Disc.setEnabled(True)
            self.checkBox_1.setEnabled(True)
            self.checkBox_2.setEnabled(True)
            self.checkBox_3.setEnabled(True)
            self.checkBox_4.setEnabled(True)
            self.pushButton_Param.setEnabled(True)

    def runThreadTransferShowRecvParameter(self, nBuffer):
        try:
            nListValue = struct.unpack('f' * int(nBuffer[2] / 4), nBuffer[3:])
            if float('inf') in [abs(nValue) for nValue in nListValue]:
                raise Exception
            nStringVal = ', '.join(format(nData, '.2f') for nData in nListValue)
            self.textBrowser.append("Recv : [ k1, k2, k3, k4 ] = [ %s ]" % (nStringVal))
            self.checkBox_1.setChecked(False)
            self.checkBox_2.setChecked(False)
            self.checkBox_3.setChecked(False)
            self.checkBox_4.setChecked(False)
            self.lineEdit_Max_1.setText("%.2f" % float(nListValue[0] * 2))
            self.lineEdit_Max_2.setText("%.2f" % float(nListValue[1] * 2))
            self.lineEdit_Max_3.setText("%.2f" % float(nListValue[2] * 2))
            self.lineEdit_Max_4.setText("%.2f" % float(nListValue[3] * 2))
            self.mUpdateSliderRange()
            self.slider_1.setValue(int(float(self.lineEdit_Max_1.displayText()) / self.mResolution / 2))
            self.slider_2.setValue(int(float(self.lineEdit_Max_2.displayText()) / self.mResolution / 2))
            self.slider_3.setValue(int(float(self.lineEdit_Max_3.displayText()) / self.mResolution / 2))
            self.slider_4.setValue(int(float(self.lineEdit_Max_4.displayText()) / self.mResolution / 2))
        except Exception:
            self.textBrowser.append("Recv : [ Error ]")

    def guiFunction(self):
        # Widgets
        self.pushButton_Scan.clicked.connect(self.mScanDevices)
        self.pushButton_Disc.clicked.connect(self.mDisconnect)
        self.pushButton_Param.clicked.connect(self.mGetParameter)
        self.pushButton_Update.clicked.connect(self.mUpdateSliderRange)
        self.listWidget.itemActivated.connect(self.mSelectBluetooth)
        self.slider_1.valueChanged.connect(lambda: self.mEmittedSlider(1))
        self.slider_2.valueChanged.connect(lambda: self.mEmittedSlider(2))
        self.slider_3.valueChanged.connect(lambda: self.mEmittedSlider(3))
        self.slider_4.valueChanged.connect(lambda: self.mEmittedSlider(4))

        # Initialization
        self.font = QtGui.QFont("微軟正黑體", 12)
        self.mResolution = 0.01

        self.mThreadTransfer = ThreadTransfer()
        self.mThreadTransfer.mSignalBuffer.connect(self.runThreadTransferShowRecvParameter)
        self.mThreadTransfer.start()

        self.mScanDevices()

        self.statusBar.showMessage("Regulator Ver. 1.0.0 made with PyQt By FAN")
        self.statusBar.setFont(self.font)
        MainWindow.setWindowTitle(self, "Regulator Ver. 1.0.0")


class ThreadScan(QThread):
    mSignalBluetooth = pyqtSignal(list)

    def __init__(self):
        QThread.__init__(self)

    def run(self):
        self.mSignalBluetooth.emit(bluetooth.discover_devices(2))


class ThreadConnect(QThread):
    mSignalState = pyqtSignal(bool)

    def __init__(self, nAddress):
        QThread.__init__(self)
        self.mAddress = nAddress

    def run(self):
        global gDeviceBluetooth
        try:
            gDeviceBluetooth = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            gDeviceBluetooth.connect((self.mAddress, 1))
            self.mSignalState.emit(True)
        except OSError:
            self.mSignalState.emit(False)


class ThreadTransfer(QThread):
    mSignalBuffer = pyqtSignal(bytes)

    def __init__(self):
        QThread.__init__(self)
        self.mRunning = False

    def mRun(self, nState):
        self.mRunning = nState

    def run(self):
        global gDeviceBluetooth
        nIndex = 0
        nRecv = bytes()
        nBuffer = bytes()
        while True:
            if self.mRunning is True:
                try:
                    nRecv = gDeviceBluetooth.recv(1)
                    if nIndex == 0 and nRecv[0] == 0xff:
                        nBuffer += nRecv
                        nIndex = 1
                    elif nIndex == 1 and nRecv[0] == 0x55:
                        nBuffer += nRecv
                        nIndex = 2
                    elif nIndex == 2:
                        nBuffer += nRecv
                        nCount = nRecv[0]
                        while nCount > 0:
                            nRecv = gDeviceBluetooth.recv(nCount)
                            nBuffer += nRecv
                            nCount = nCount - len(nRecv)

                        if len(nBuffer) >= 7:
                            self.mSignalBuffer.emit(nBuffer)
                            self.mRun(False)
                        nBuffer = bytes()
                        nIndex = 0
                except Exception:
                    QMessageBox.critical(QMessageBox(), "Error", "An error occurred while connecting to the device.", QMessageBox.Ok)
            else:
                pass


if __name__ == "__main__":
    application = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(application.exec_())
