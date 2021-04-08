import sys

from silenium import Ui_MainWindow
from PySide2 import QtWidgets

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    WindowX = QtWidgets.QMainWindow()
    ui = Ui_MainWindow(WindowX)
    ui.setupUi(WindowX)
    WindowX.show()
    # события
    # основной цикл
    sys.exit(app.exec_())
