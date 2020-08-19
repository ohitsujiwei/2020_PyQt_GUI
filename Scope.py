import struct
import sys
import time

import bluetooth
import matplotlib.pyplot as plt
import serial.tools.list_ports
import xlwt
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QThreadPool, QThread, pyqtSignal, QRunnable, QObject
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox

from Scope_GUI import Ui_MainWindow

gDeviceSerial = None
gDeviceBluetooth = None
gListDatas = list()


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.guiFunction()

    def mScanDevices(self):
        self.pushButton_Scan.setText("Scanning...")
        self.pushButton_Scan.setEnabled(False)
        self.listWidget_Bluetooth.setEnabled(False)
        self.listWidget_Serial.setEnabled(False)

        self.mThreadScan = ThreadScan()
        self.mThreadScan.mSignalBluetooth.connect(self.runThreadScanListBluetooth)
        self.mThreadScan.mSignalSerial.connect(self.runThreadScanListSerial)
        self.mThreadScan.start()

    def mDisconnect(self):
        global gDeviceSerial, gDeviceBluetooth

        gListDatas.clear()
        del(self.mExcelBook)
        del(self.mExcelSheet)
        self.mExcelBook = xlwt.Workbook()
        self.mExcelSheet = self.mExcelBook.add_sheet('sheet')
        self.mExcelRows = 0

        if self.mThreadTransfer.mRunning is True:
            self.mRecvBluetooth()

        if gDeviceSerial is not None:
            gDeviceSerial.close()
            gDeviceSerial = None
            self.textBrowser_Send.append("Disconnected from \"" + self.mSelectSerialName + "\".")
            self.label_Serial.setText("Serial")

        if gDeviceBluetooth is not None:
            gDeviceBluetooth.close()
            gDeviceBluetooth = None
            self.textBrowser_Recv.append("Disconnected from \"" + self.mSelectBluetoothName + "\".")
            self.label_Bluetooth.setText("Bluetooth")

        self.pushButton_Scan.setEnabled(True)
        self.pushButton_Disc.setEnabled(False)
        self.pushButton_Send.setEnabled(False)
        self.pushButton_Recv.setEnabled(False)
        self.listWidget_Bluetooth.setEnabled(True)
        self.listWidget_Serial.setEnabled(True)

    def mRecvBluetooth(self):
        if self.mThreadTransfer.mRunning is True:
            if self.mThreadTransfer.mSending is True:
                self.mSendSerial()
            self.mThreadTransfer.mRun(False)
            self.pushButton_Recv.setText("Receive from Bluetooth")
        else:
            self.mThreadTransfer.mRun(True)
            self.pushButton_Recv.setText("Stop Receiving Data!")

    def mSendSerial(self):
        if self.mThreadTransfer.mSending is True:
            self.mThreadTransfer.mSend(False)
            self.pushButton_Send.setText("Send to Serial")
        else:
            self.mThreadTransfer.mSend(True)
            self.pushButton_Send.setText("Stop Sending Data!")

    def mSelectBluetooth(self):
        self.label_Bluetooth.setText("Connecting...")
        self.listWidget_Bluetooth.setEnabled(False)
        self.nBluetoothAddress = self.mListBluetooth[self.listWidget_Bluetooth.currentRow()]
        self.mThreadConnect = ThreadConnect(0, self.nBluetoothAddress)
        self.mThreadConnect.mSignalState.connect(self.runThreadConnectBluetooth)
        self.mThreadConnect.start()

    def mSelectSerial(self):
        self.label_Serial.setText("Connecting...")
        self.listWidget_Serial.setEnabled(False)
        nSelectPort = self.mListSerial[self.listWidget_Serial.currentRow()][0]
        self.mThreadConnect = ThreadConnect(1, nSelectPort)
        self.mThreadConnect.mSignalState.connect(self.runThreadConnectSerial)
        self.mThreadConnect.start()

    def runThreadConnectBluetooth(self, nState):
        if nState is False:
            QMessageBox.critical(QMessageBox(), "OSError", "Can't connect to Bluetooth device.", QMessageBox.Ok)
            self.label_Bluetooth.setText("Bluetooth")
            self.listWidget_Bluetooth.setEnabled(True)
        else:
            self.mSelectBluetoothName = bluetooth.lookup_name(self.mListBluetooth[self.listWidget_Bluetooth.currentRow()])
            self.textBrowser_Recv.append("Connect to \"" + self.mSelectBluetoothName + "\" (" + self.nBluetoothAddress + ").")
            self.label_Bluetooth.setText(self.mSelectBluetoothName)
            self.pushButton_Recv.setEnabled(True)
            self.pushButton_Disc.setEnabled(True)

    def runThreadConnectSerial(self, nState):
        if nState is False:
            QMessageBox.critical(QMessageBox(), "OSError", "Can't connect to Serial device.", QMessageBox.Ok)
            self.label_Serial.setText("Serial")
            self.listWidget_Serial.setEnabled(True)
        else:
            self.mSelectSerialName = self.mListSerial[self.listWidget_Serial.currentRow()][1]
            self.textBrowser_Send.append("Connect to \"" + self.mSelectSerialName + "\".")
            self.label_Serial.setText(self.mSelectSerialName)
            self.pushButton_Disc.setEnabled(True)
            self.pushButton_Send.setEnabled(True)
            self.listWidget_Serial.setEnabled(False)

    def runThreadScanListBluetooth(self, nListBluetooth):
        self.listWidget_Bluetooth.clear()
        self.listWidget_Bluetooth.setEnabled(True)
        self.mListBluetooth = nListBluetooth
        for nDevice in self.mListBluetooth:
            item = QtWidgets.QListWidgetItem(bluetooth.lookup_name(nDevice))
            item.setFont(self.font)
            self.listWidget_Bluetooth.addItem(item)

    def runThreadScanListSerial(self, nListSerial):
        self.listWidget_Serial.clear()
        self.listWidget_Serial.setEnabled(True)
        self.mListSerial = nListSerial
        for nPort in self.mListSerial:
            item = QtWidgets.QListWidgetItem(nPort[1])  # nPort[0, 1] = [COMx, Name]
            item.setFont(self.font)
            self.listWidget_Serial.addItem(item)
        self.pushButton_Scan.setText("Scan")
        self.pushButton_Scan.setEnabled(True)

    def runThreadTransferShow(self, nBuffer):
        try:
            nListValue = struct.unpack('f' * int(nBuffer[2] / 4), nBuffer[3:])
            if float('inf') in [abs(nValue) for nValue in nListValue]:
                raise Exception
            nStringHex = ', '.join(format(nData, '02x') for nData in nBuffer)
            nStringVal = ', '.join(format(nData, '.2f') for nData in nListValue)
            self.textBrowser_Recv.append("Recv : [ %s ]" % (nStringHex))
            self.textBrowser_Recv.append(" = [ %s ]" % (nStringVal))
            if self.mThreadTransfer.mSending is True:
                self.textBrowser_Send.append("Send : [ %s ]" % nStringHex)

            self.mExcelSheet.write(self.mExcelRows, 0, time.strftime("%H:%M:%S", time.localtime()))
            nExcelCols = 1
            for nData in nListValue:
                self.mExcelSheet.write(self.mExcelRows, nExcelCols, nData)
                gListDatas.append(nData)
                nExcelCols += 1
            self.mExcelRows += 1
        except Exception:
            self.textBrowser.append("Recv : [ Error ]")

    def mSaveDatas(self):
        nTimeNow = time.strftime("%Y%m%d_%H%M%S_", time.localtime())
        try:
            self.mExcelBook.save(nTimeNow + "DataSet.xls")
        except PermissionError:
            QMessageBox.critical(QMessageBox(), "PermissionError", "File access failed.", QMessageBox.Ok)

    def mFigurePlot(self):
        if self.mExcelRows > 0:
            try:
                plt.clf()
                nCols = int(len(gListDatas) / self.mExcelRows)
                nListY = list()
                for nIter in range(0, nCols):
                    for nCount in range(nIter, len(gListDatas), nCols):
                        nListY.append(gListDatas[nCount])
                    nListY = nListY[-50:]
                    plt.plot(range(0, len(nListY)), nListY)
                    nListY = list()
                plt.show()
            except Exception:
                QMessageBox.critical(QMessageBox(), "FatalError", "Plotter is crash.", QMessageBox.Ok)
        else:
            QMessageBox.information(QMessageBox(), "Warning", "No data to plot!", QMessageBox.Ok)

    def guiFunction(self):
        # Widgets
        self.pushButton_Scan.clicked.connect(self.mScanDevices)
        self.pushButton_Disc.clicked.connect(self.mDisconnect)
        self.pushButton_Recv.clicked.connect(self.mRecvBluetooth)
        self.pushButton_Send.clicked.connect(self.mSendSerial)
        self.pushButton_Data.clicked.connect(self.mSaveDatas)
        self.pushButton_Plot.clicked.connect(self.mFigurePlot)
        self.listWidget_Serial.itemActivated.connect(self.mSelectSerial)
        self.listWidget_Bluetooth.itemActivated.connect(self.mSelectBluetooth)

        # Initialization
        self.font = QtGui.QFont("微軟正黑體", 12)

        self.mExcelBook = xlwt.Workbook()
        self.mExcelSheet = self.mExcelBook.add_sheet('sheet')
        self.mExcelRows = 0

        self.mThreadTransfer = ThreadTransfer()
        self.mThreadTransfer.mSignalBuffer.connect(self.runThreadTransferShow)
        self.mThreadTransfer.start()

        self.mScanDevices()

        self.statusBar.showMessage("Scope Ver. 1.0.0 made with PyQt By FAN")
        self.statusBar.setFont(self.font)
        MainWindow.setWindowTitle(self, "Scope Ver. 1.0.0")


class ThreadScan(QThread):
    mSignalBluetooth = pyqtSignal(list)
    mSignalSerial = pyqtSignal(list)

    def __init__(self):
        QThread.__init__(self)

    def run(self):
        self.mSignalBluetooth.emit(bluetooth.discover_devices(duration=2, lookup_names=False))
        self.mSignalSerial.emit(serial.tools.list_ports.comports(include_links=False))


class ThreadConnect(QThread):
    mSignalState = pyqtSignal(bool)

    def __init__(self, nType, nDevice):
        QThread.__init__(self)
        self.mType = nType
        self.mDevice = nDevice

    def run(self):
        global gDeviceBluetooth
        global gDeviceSerial
        try:
            if self.mType == 0:
                gDeviceBluetooth = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                gDeviceBluetooth.connect((self.mDevice, 1))
            elif self.mType == 1:
                gDeviceSerial = serial.Serial(self.mDevice, 115200)
            self.mSignalState.emit(True)
        except OSError:
            self.mSignalState.emit(False)
        except serial.serialutil.SerialException:
            self.mSignalState.emit(False)


class ThreadTransfer(QThread):
    mSignalBuffer = pyqtSignal(bytes)

    def __init__(self):
        QThread.__init__(self)
        self.mRunning = False
        self.mSending = False

    def mRun(self, nState):
        self.mRunning = nState

    def mSend(self, nState):
        self.mSending = nState

    def run(self):
        global gDeviceBluetooth, gDeviceSerial
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
                            if self.mSending is True:
                                gDeviceSerial.write(nBuffer)
                        nIndex = 0
                        nBuffer = bytes()
                except OSError:
                    nIndex = 0
                    nBuffer = bytes()
            else:
                pass


if __name__ == "__main__":
    application = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(application.exec_())
