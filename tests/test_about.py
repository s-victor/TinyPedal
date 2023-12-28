import sys

sys.path.append(".")

from PySide2.QtWidgets import QApplication, QWidget
from tinypedal.ui.about import About


if __name__ == "__main__":
    root = QApplication(sys.argv)
    window = QWidget()
    about = About(window)
    about.show()
    sys.exit(root.exec_())
