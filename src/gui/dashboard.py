from PySide6.QtWidgets import QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTextEdit, QListWidget, QSpinBox
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
        
        output_layout = QHBoxLayout()
        output_container.setLayout(output_layout)
        output_layout.setSpacing(8)

        plots_layout = QVBoxLayout()
        plots_layout.setSpacing(8)

        output_details_layout = QVBoxLayout()
        output_details_layout.setSpacing(8)
        
        
        # Live Latency layout
        self.latency_ping_numbers = []
        self.latency_values = []
        self.latency_point_sizes = []
        self.latency_point_symbols = []
        self.latency_point_pens = []
        self.latency_ping_index = 0
        
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
        
        # Live Jitter layout
        self.jitter_ping_numbers = []
        self.jitter_values = []
        self.jitter_ping_index = 0
        
        self.jitter_plot = pg.PlotWidget()
        self.jitter_plot.setObjectName("jitter_plot")
        self.jitter_plot.setBackground("#000000")
        
        self.jitter_plot.setStyleSheet("""
            QWidget#jitter_plot {
                border: 1px solid #1e1e2f;
        }
        """)
        
        self.jitter_plot.setTitle("Live Jitter")
        self.jitter_plot.setLabel("left", "Jitter", units="ms")
        self.jitter_plot.setLabel("bottom", "Ping Number")

        self.jitter_plot.showGrid(x=True, y=True, alpha=0.3)
        
        self.jitter_curve = self.jitter_plot.plot(
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
        
        # Status label
        self.status = "IDLE"
        self.output_label = QLabel()
        self.output_label.setStyleSheet("color: #b2e034; font-size: 36px; font-style: italic; background-color: #1e1e2f; border: none; border-radius: 4px; padding: 4px;")
        self.output_label.setAlignment(Qt.AlignCenter)
        self.output_label.setText(self.status)
        
        # Output text
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setStyleSheet("background-color: #000000; color: white; font-size: 12px; border: 1px solid #3c3c3c; border-radius: 4px; padding: 4px;")
        self.output_text.document().setMaximumBlockCount(500)
        
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
                                   QPushButton:disabled {
                                    background-color: #222222;
                                    color: #666666;
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
                                QPushButton:disabled {
                                    background-color: #222222;
                                    color: #666666;
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
        
        plots_layout.addWidget(self.latency_plot)
        plots_layout.addWidget(self.jitter_plot)

        output_details_layout.addWidget(self.output_label)
        output_details_layout.addWidget(self.output_text)

        output_layout.addLayout(plots_layout)
        output_layout.addLayout(output_details_layout)

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
        
        self.latency_ping_numbers.clear()
        self.jitter_ping_numbers.clear()
        
        self.latency_values.clear()
        self.latency_point_sizes.clear()
        self.latency_point_symbols.clear()
        self.latency_point_pens.clear()
        self.jitter_values.clear()
        
        self.latency_ping_index = 0
        self.jitter_ping_index = 0
        
        self.latency_curve.setData([], [])
        self.latency_curve.setPen(pg.mkPen(color="#a8cee3", width=2))
        self.jitter_curve.setData([], [])
        
        self.setWindowTitle("Netpeer v" + get_version_number() + " - Monitoring: " + self.target_input.text().strip())
        
        self.ping_worker = PingWorker(target, interval)
        
        self.ping_worker.result_ready.connect(self.update_latency_graph)
        self.ping_worker.result_ready.connect(self.update_jitter_graph)
        self.ping_worker.finished.connect(self.worker_finished)
        
        self.ping_worker.start()
        
        self.start_button.setDisabled(True)
        self.stop_button.setDisabled(False)

    def update_latency_graph(self, response):
        # Update the output text area with the ping result
        status = response.get("status", "unknown").upper()
        self.status = response.get("overall_status", "UNKNOWN").upper()
        self.output_label.setText(self.status)
        status_color = {
            "CALCULATING...": "#a8cee3",
            "EXCELLENT": "#00ff00",
            "FINE": "#b2e034",
            "UNSTABLE": "#ffff00",
            "POOR": "#ffa500",
            "UNREACHABLE": "#ff0000",
            "UNKNOWN": "#ff0000"
        }.get(self.status, "#a8cee3")
        self.output_label.setStyleSheet(
            f"color: {status_color}; font-size: 36px; font-style: italic; "
            "background-color: #1e1e2f; border: none; border-radius: 4px; padding: 4px;"
        )
        message = response.get("error")

        # If the ping was successful, display the latency in milliseconds
        if status == "SUCCESS":
            latency = response.get("latency_ms")
            message = f"{latency} ms" if latency is not None else "Reachable"

        line = f"{status}: {message or 'No response'}"
        self.output_text.append(line)
        
        latency = response.get("latency_ms")

        # Update the latency graph with the new data point
        self.latency_ping_index += 1
        self.latency_ping_numbers.append(self.latency_ping_index)
        
        spike = response.get("spike", response.get("is_spike", False))
        
        # Update the point sizes and symbols based on whether it's a spike or not
        self.latency_point_sizes.append(15 if spike else 5)
        self.latency_point_symbols.append("x" if spike else "o")
        
        self.latency_point_pens.append(
            pg.mkPen("#ff5555", width=2) if spike
            else pg.mkPen("#a8cee3", width=1)
        )

        # Update the latency values
        if latency is not None:
            self.latency_values.append(latency)
        else:
            self.latency_values.append(float("nan"))

        # Limit the number of points displayed on the graph to 60
        if len(self.latency_ping_numbers) > 60:
            self.latency_ping_numbers.pop(0)
            self.latency_values.pop(0)
            self.latency_point_sizes.pop(0)
            self.latency_point_symbols.pop(0)
            self.latency_point_pens.pop(0)
        # Redraw the graph
        self.latency_curve.setData(
            self.latency_ping_numbers,
            self.latency_values,
            symbolSize=self.latency_point_sizes,
            symbol=self.latency_point_symbols,
            symbolPen=self.latency_point_pens
        )
    
    def update_jitter_graph(self, response):
        jitter = response.get("jitter_ms")

        self.jitter_ping_index += 1
        self.jitter_ping_numbers.append(self.jitter_ping_index)

        if jitter is not None:
            self.jitter_values.append(jitter)
        else:
            self.jitter_values.append(float("nan"))

        if len(self.jitter_ping_numbers) > 60:
            self.jitter_ping_numbers.pop(0)
            self.jitter_values.pop(0)

        # Redraw the graph
        self.jitter_curve.setData(
            self.jitter_ping_numbers,
            self.jitter_values
        )

    def stop_monitoring(self):
        # Stop monitoring the target address
        if self.ping_worker is not None:
            self.ping_worker.stop()
            self.stop_button.setDisabled(True)
    
    def worker_finished(self):
        self.ping_worker = None
        
        self.setWindowTitle("Netpeer v" + get_version_number())
        
        self.start_button.setDisabled(False)
        self.stop_button.setDisabled(True)
        
        self.output_text.append("Monitoring stopped.")
    
    def closeEvent(self, event):
        if self.ping_worker is not None:
            if self.ping_worker.isRunning():
                self.ping_worker.stop()
                self.ping_worker.wait()

        super().closeEvent(event)