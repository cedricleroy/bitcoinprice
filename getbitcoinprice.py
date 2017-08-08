""" Bitcoin prices and events handler to explain PyQt5 QThreads example """
import sys
import time
import datetime
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal
import requests


DEFAULT_NUMBER = 10


class Example(QtWidgets.QWidget):
    def __init__(self) -> None:
        super(Example, self).__init__()

        self.counter = Counter()
        self.counter.counter_signal.connect(self.counter_event)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('QThreads Example')
        ok_button = QtWidgets.QPushButton("OK")
        ok_button.clicked.connect(self.click)
        self.text_log = QtWidgets.QTextEdit()
        self.number = QtWidgets.QSpinBox()
        self.number.setMinimum(0)
        self.number.setMaximum(DEFAULT_NUMBER)
        self.number.setValue(DEFAULT_NUMBER)
        self.number.valueChanged.connect(self.change_number)
        self.pbar = QtWidgets.QProgressBar(self)
        self.pbar.setMaximum(DEFAULT_NUMBER)
        self.bitcoin = QtWidgets.QCheckBox('get bitcoin price')
        self.bitcoin.setChecked(True)
        self.bitcoin.stateChanged.connect(self.bitcoin_check)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.number)
        vbox.addWidget(ok_button)
        vbox.addWidget(self.bitcoin)
        vbox.addWidget(self.pbar)
        vbox.addWidget(self.text_log)
        self.setLayout(vbox)

        self.timer = Timer()
        self.timer.timer_signal.connect(self.timer_event)
        self.timer.start()

        self.show()

    def click(self) -> None:
        self.log('button clicked', kind='info')
        if not self.counter.running:
            self.counter.start()
        else:
            self.log('one thread is already running!', kind='error')

    def bitcoin_check(self, state: int) -> None:
        self.log('bitcoin state changed [%s]' % state, kind='info')
        if state > 0:
            self.timer.get_price = True
        else:
            self.timer.get_price = False

    def change_number(self, number: int) -> None:
        self.log('new number: %s' % number, kind='info')
        self.counter.number = number
        self.pbar.setMaximum(number)

    def counter_event(self, event: dict) -> None:
        self.log(event, kind='ok')
        self.pbar.setValue(event['counter'] + 1)

    def timer_event(self, event: dict) -> None:
        self.log(str(event), kind='bitcoin')

    def log(self, text: str, kind: str = 'error') -> None:
        if kind == 'info':
            color = "#0000ff"
        elif kind == 'ok':
            color = "#008000"
        elif kind == 'bitcoin':
            color = "#A9A9A9"
        else:
            color = "#ff0000"
        now = datetime.datetime.utcnow()
        fulltext = "[%s]" % now
        fulltext += "[%s]" % text
        ans = "<span style=\" font-size:8pt; font-weight:600; color:%s;\" >" % (color)
        ans += fulltext
        ans += "</span>"
        self.text_log.append(ans)
        self.text_log.moveCursor(QtGui.QTextCursor.End)


class Counter(QtCore.QThread):

    counter_signal = pyqtSignal(dict)

    def __init__(self) -> None:
        super(Counter, self).__init__()
        self.running = False
        self.number = DEFAULT_NUMBER

    def run(self) -> None:
        self.running = True
        self.count()
        self.running = False

    def count(self) -> None:
        for count in range(self.number):
            data_structure = {'counter': count, 'maximum': self.number}
            self.counter_signal.emit(data_structure)
            time.sleep(1)


class Timer(QtCore.QThread):

    timer_signal = pyqtSignal(dict)

    def __init__(self) -> None:
        super(Timer, self).__init__()
        self.get_price = True

    def run(self) -> None:
        while True:
            if self.get_price:
                req = requests.get('https://api.coindesk.com/v1/bpi/currentprice.json')
                self.timer_signal.emit(req.json())
                time.sleep(5)
            else:
                time.sleep(1)


def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
