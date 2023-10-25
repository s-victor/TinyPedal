import sys

sys.path.append(".")

from PySide2.QtWidgets import QApplication
from tinypedal.about import About


if __name__ == "__main__":
    root = QApplication(sys.argv)
    about = About(hideonclose=False)
    about.show()
    sys.exit(root.exec_())
