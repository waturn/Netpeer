from PySide6.QtWidgets import QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTextEdit, QListWidget, QSpinBox, QGridLayout
from PySide6.QtCore import Qt

import pyqtgraph as pg

from main import get_version_number
from .ping_worker import PingWorker

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Netpeer v" + get_version_number())
        self.resize(1200, 800)
        
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
        navbar_container.setStyleSheet("background-color: #04091c; font-weight: bold; border: 1px solid #1e1e2f;")
        navbar_container.setFixedHeight(50)
        
        # Target layout
        target_container = QWidget()
        window_layout.addWidget(target_container)
        
        target_layout = QHBoxLayout()
        target_container.setLayout(target_layout)
        target_layout.setSpacing(8)
        
        # Button layout
        button_container = QWidget()
        window_layout.addWidget(button_container)
        
        button_layout = QHBoxLayout()
        button_container.setLayout(button_layout)
        button_layout.setSpacing(8)
        
        # Output layout
        output_container = QWidget()
        output_container.setStyleSheet("background-color: #04091c; border-radius: 0px; border: 1px solid #1e1e2f;")
        window_layout.addWidget(output_container)
        
        output_layout = QGridLayout()
        output_container.setLayout(output_layout)
        output_layout.setSpacing(8)
        
        
        # Graph layout
        self.ping_numbers = []
        self.latency_values = []
        self.ping_index = 0
        
        self.latency_plot = pg.PlotWidget()
        self.latency_plot.setObjectName("latency_plot")
        self.latency_plot.setBackground("#000000")
        
        self.latency_plot.setStyleSheet("""
            QWidget#latency_plot {
                border: 1px solid #1e1e2f;
        }
        """)
        
        self.latency_plot.setTitle("Live Latency")
        self.latency_plot.setLabel("left", "Latency", units="ms")
        self.latency_plot.setLabel("bottom", "Ping Number")

        self.latency_plot.showGrid(x=True, y=True, alpha=0.3)
        
        self.latency_curve = self.latency_plot.plot(
            pen=pg.mkPen(color="#a8cee3", width=2),
            symbol="o",
            symbolSize=5,
            connect="finite"
        )
        
        
        # Navbar labels
        program_label = QLabel("Netpeer v" + get_version_number())
        program_label.setAlignment(Qt.AlignCenter)
        program_label.setStyleSheet("color: #a8cee3; font-size: 16px; font-style: italic; border: none;")
        
        # Target labels
        target_label = QLabel("Target: ")
        target_label.setAlignment(Qt.AlignCenter)
        target_label.setStyleSheet("color: #b0b6cf; font-size: 12px; font-style: italic;")
        
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Enter target address")
        self.target_input.setStyleSheet("background-color: #1e1e2f; color: white; font-size: 16px; border: 1px solid #3c3c3c; border-radius: 4px; padding: 4px;")
        self.target_input.setFixedWidth(300)
        
        # Interval labels
        interval_label = QLabel("Interval: ")
        interval_label.setAlignment(Qt.AlignCenter)
        interval_label.setStyleSheet("color: #b0b6cf; font-size: 12px; font-style: italic;")
        
        self.interval_input = QSpinBox()
        self.interval_input.setRange(1, 3600)
        self.interval_input.setValue(1)
        self.interval_input.setStyleSheet("background-color: #1e1e2f; color: white; font-size: 16px; border: 1px solid #3c3c3c; border-radius: 4px; padding: 4px;")
        self.interval_input.setFixedWidth(300)
        
        # Output text
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setStyleSheet("background-color: #000000; color: white; font-size: 12px; border: 1px solid #3c3c3c; border-radius: 4px; padding: 4px;")
        self.output_text.setFixedWidth(400)
        self.output_text.setFixedHeight(200)
        
        # Buttons
        self.start_button = QPushButton("Start")
        self.start_button.setCursor(Qt.PointingHandCursor)
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
        target_layout.addWidget(interval_label)
        target_layout.addWidget(self.interval_input)
        target_layout.addStretch()
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        
        # output_layout.addWidget((output_label), 0, 1)
        output_layout.addWidget((self.output_text), 1, 1)
        output_layout.addWidget((self.latency_plot), 1, 0)

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
        
        self.ping_numbers.clear()
        self.latency_values.clear()
        self.ping_index = 0
        self.latency_curve.setData([], [])
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
        
        latency = response.get("latency_ms")

        self.ping_index += 1
        self.ping_numbers.append(self.ping_index)

        if latency is not None:
            self.latency_values.append(latency)
        else:
            self.latency_values.append(float("nan"))

        if len(self.ping_numbers) > 60:
            self.ping_numbers.pop(0)
            self.latency_values.pop(0)

        # Redraw the graph
        self.latency_curve.setData(
            self.ping_numbers,
            self.latency_values
        )

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