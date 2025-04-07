import sys

sys.path.append(".")

from PySide2.QtWidgets import QApplication
from tinypedal.ui.about import About


if __name__ == "__main__":
    root = QApplication(sys.argv)
    about = About(None)
    sys.exit(about.exec_())
