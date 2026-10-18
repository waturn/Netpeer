from PySide6.QtWidgets import QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTextEdit, QListWidget, QSpinBox
from PySide6.QtCore import Qt
import sys

from main import get_version_number
from .ping_worker import PingWorker

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Netpeer v" + get_version_number())
        self.resize(600, 450)
        
        # Main window layout
        # 
        # Holds all widgets in VBox style
        # Window -> Navbar & Target & Interval & StartButton
        window_container = QWidget()
        self.setCentralWidget(window_container)
        
        window_layout = QVBoxLayout()
        window_container.setLayout(window_layout)
        
        # Navbar layout
        navbar_container = QWidget()
        window_layout.addWidget(navbar_container)
        
        navbar_layout = QHBoxLayout()
        navbar_container.setLayout(navbar_layout)
        navbar_container.setStyleSheet("background-color: #04091c;")
        navbar_container.setFixedHeight(50)
        
        # Target layout
        target_container = QWidget()
        window_layout.addWidget(target_container)
        
        target_layout = QHBoxLayout()
        target_container.setLayout(target_layout)
        target_layout.setSpacing(8)
        
        # Interval layout
        interval_container = QWidget()
        window_layout.addWidget(interval_container)
        
        interval_layout = QHBoxLayout()
        interval_container.setLayout(interval_layout)
        interval_layout.setSpacing(8)
        
        # Button layout
        button_container = QWidget()
        window_layout.addWidget(button_container)
        
        button_layout = QHBoxLayout()
        button_container.setLayout(button_layout)
        button_layout.setSpacing(8)
        
        # Output layout
        output_container = QWidget()
        window_layout.addWidget(output_container)
        
        output_layout = QHBoxLayout()
        output_container.setLayout(output_layout)
        output_layout.setSpacing(8)
        
        
        
        # Navbar labels
        program_label = QLabel("Netpeer v" + get_version_number())
        program_label.setAlignment(Qt.AlignCenter)
        program_label.setStyleSheet("color: #a8cee3; font-size: 16px; font-style: italic;")
        
        # Target labels
        target_label = QLabel("Target: ")
        target_label.setAlignment(Qt.AlignCenter)
        target_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Enter target address")
        self.target_input.setStyleSheet("background-color: #1e1e2f; color: white; font-size: 16px; border: 1px solid #3c3c3c; border-radius: 4px; padding: 4px;")
        self.target_input.setFixedWidth(200)
        
        # Interval labels
        interval_label = QLabel("Interval: ")
        interval_label.setAlignment(Qt.AlignCenter)
        interval_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        
        self.interval_input = QSpinBox()
        self.interval_input.setRange(1, 3600)
        self.interval_input.setValue(1)
        self.interval_input.setStyleSheet("background-color: #1e1e2f; color: white; font-size: 16px; border: 1px solid #3c3c3c; border-radius: 4px; padding: 4px;")
        self.interval_input.setFixedWidth(200)
        
        # Output labels
        output_label = QLabel("Output: ")
        output_label.setAlignment(Qt.AlignCenter)
        output_label.setStyleSheet("color: #6b7378; font-size: 12px; font-style: italic;")
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setStyleSheet("background-color: #1e1e2f; color: white; font-size: 12px; border: 1px solid #3c3c3c; border-radius: 4px; padding: 4px;") 
        self.output_text.setFixedWidth(400)
        self.output_text.setFixedHeight(200)
        
        # Buttons
        self.start_button = QPushButton("Start")
        self.start_button.setCursor(Qt.PointingHandCursor)
        self.start_button.setFixedWidth(300)
        self.start_button.setStyleSheet("""
                                   QPushButton {
                                        background-color: #3c3c3c; 
                                        color: #a8cee3; 
                                        font-size: 16px; 
                                        border: none; 
                                        border-radius: 4px; 
                                        padding: 8px 16px;
                                   }
                                   QPushButton:hover {
                                        background-color: #5c5c5c;
                                   }
                                   QPushButton:pressed {
                                        background-color: #2c2c2c;
                                   }
                                   """)
        
        self.start_button.clicked.connect(self.start_monitoring)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.setCursor(Qt.PointingHandCursor)
        self.stop_button.setFixedWidth(300)
        self.stop_button.setStyleSheet("""
                                QPushButton {
                                            background-color: #3c3c3c; 
                                            color: #a8cee3; 
                                            font-size: 16px; 
                                            border: none; 
                                            border-radius: 4px; 
                                            padding: 8px 16px;
                                }
                                QPushButton:hover {
                                            background-color: #5c5c5c;
                                }
                                QPushButton:pressed {
                                            background-color: #2c2c2c;
                                }
                                """)
        
        self.stop_button.clicked.connect(self.stop_monitoring)
        
        self.ping_worker = None

        # Implement program
        navbar_layout.addWidget(program_label)
        
        target_layout.addStretch()
        target_layout.addWidget(target_label)
        target_layout.addWidget(self.target_input)
        target_layout.addStretch()
        
        interval_layout.addStretch()
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.interval_input)
        interval_layout.addStretch()
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        
        output_layout.addStretch()
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_text)
        output_layout.addStretch()

        self.stop_button.setDisabled(True)

    def start_monitoring(self):
        # Start monitoring the target address with the specified interval
    
        self.output_text.setPlainText("")
        
        target = self.target_input.text().strip()
        interval = self.interval_input.value()

        # Validate the target address
        if not target:
            self.output_text.setPlainText("Enter a target address.")
            return
        if interval <= 0:
            self.output_text.setPlainText("Enter a valid interval.")
            return
        
        if self.ping_worker is not None:
            return
        
        self.setWindowTitle("Netpeer v" + get_version_number() + " - Monitoring: " + self.target_input.text().strip())
        
        self.ping_worker = PingWorker(target, interval)
        
        self.ping_worker.result_ready.connect(self.update_output)
        self.ping_worker.finished.connect(self.worker_finished)
        
        self.ping_worker.start()
        
        self.start_button.setDisabled(True)
        self.stop_button.setDisabled(False)

    def update_output(self, response):
        # Update the output text area with the ping result
        status = response.get("status", "unknown").upper()
        message = response.get("error")

        if status == "SUCCESS":
            latency = response.get("latency_ms")
            message = f"{latency} ms" if latency is not None else "Reachable"

        line = f"{status}: {message or 'No response'}"
        self.output_text.append(line)

    def stop_monitoring(self):
        # Stop monitoring the target address
        self.setWindowTitle("Netpeer v" + get_version_number())
        
        if self.ping_worker is not None:
            self.ping_worker.stop()
            self.stop_button.setDisabled(True)
    
    def worker_finished(self):
        self.ping_worker = None
        
        self.start_button.setDisabled(False)
        self.stop_button.setDisabled(True)
        
        self.output_text.append("Monitoring stopped.")
    
    def closeEvent(self, event):
        if self.ping_worker is not None:
            if self.ping_worker.isRunning():
                self.ping_worker.stop()
                self.ping_worker.wait()

        super().closeEvent(event)