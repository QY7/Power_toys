import  sys
from PyQt5.QtWidgets import  *
from PyQt5 import QtWidgets, QtCore
from power_toys.gui.loss_analysis_gui import MainWindow

if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())