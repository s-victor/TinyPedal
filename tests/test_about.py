import sys

sys.path.append(".")

from tinypedal.about import About


if __name__ == "__main__":
    root = About()
    root.deiconify()
    root.mainloop()
