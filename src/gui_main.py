import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

from gui.dashboard import Dashboard
from storage.database import init_database


def main():
    init_database()
    
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI"))
    app.setStyleSheet("""
        * {
            font-family: Segoe UI;
        }
        QMainWindow {
            background-color: #07080d;
        }
    """)

    window = Dashboard()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()