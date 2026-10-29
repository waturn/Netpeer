from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QAbstractItemView,
    QHeaderView,
    QFrame,
    QHBoxLayout
)
from PySide6.QtCore import Qt

from datetime import datetime
from storage.database import get_sessions, get_session_results

import pyqtgraph as pg

class HistoryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #04091c; color: #b0b6cf;")
        
        layout = QVBoxLayout(self)
        
        title = QLabel("Previous Monitoring Sessions")
        title.setStyleSheet("background-color: #04091c; font-weight: bold; border: 1px solid #1e1e2f; color: #a8cee3; font-size: 16px; font-style: italic;")
        title.setFixedHeight(50)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        self.sessions_table = QTableWidget()
        self.sessions_table.setShowGrid(True)
        self.sessions_table.verticalHeader().setVisible(False)
        self.sessions_table.setStyleSheet("""
            QTableWidget {
                background-color: #04091c;
                color: #b0b6cf;
                gridline-color: #1e1e2f;
                border: 1px solid #1e1e2f;
                outline: none;
            }
            QTableWidget::item {
                border: none;
            }
            QHeaderView::section {
                background-color: #02030a;
                color: #b0b6cf;
                border: 1px solid #1e1e2f;
                padding: 4px;
                font-weight: bold;
            }
            QTableCornerButton::section {
                background-color: #02030a;
                border: 1px solid #1e1e2f;
            }
            QTableWidget QScrollBar:vertical,
            QTableWidget QScrollBar:horizontal {
                background-color: #04091c;
                border: none;
            }
            QTableWidget QScrollBar:vertical {
                width: 12px;
            }
            QTableWidget QScrollBar:horizontal {
                height: 12px;
            }
            QTableWidget QScrollBar::handle:vertical,
            QTableWidget QScrollBar::handle:horizontal {
                background-color: #3c3c3c;
                border: none;
                min-height: 24px;
                min-width: 24px;
            }
            QTableWidget QScrollBar::add-line:vertical,
            QTableWidget QScrollBar::sub-line:vertical,
            QTableWidget QScrollBar::add-line:horizontal,
            QTableWidget QScrollBar::sub-line:horizontal {
                background: none;
                border: none;
            }
            QTableWidget QScrollBar::add-page:vertical,
            QTableWidget QScrollBar::sub-page:vertical,
            QTableWidget QScrollBar::add-page:horizontal,
            QTableWidget QScrollBar::sub-page:horizontal {
                background: #04091c;
            }
        """)
        
        self.sessions_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.sessions_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.sessions_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        self.sessions_table.setColumnCount(4)
        self.sessions_table.setMinimumHeight(200)
        self.sessions_table.setHorizontalHeaderLabels([
            "Session ID", 
            "Target", 
            "Started at", 
            "Ended at"
        ])
        self.sessions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.sessions_table)
        
        self.sessions_table.itemSelectionChanged.connect(
            self.show_selected_session
        )
        
        self.summary_card = QFrame()
        self.summary_card.setStyleSheet("""
            QFrame {
                background-color: #02030a;
                border: 1px solid #1e1e2f;
            }
            QLabel {
                border: none;
            }
        """)
        summary_layout = QVBoxLayout(self.summary_card)
        summary_layout.setContentsMargins(12, 8, 12, 8)
        summary_layout.setContentsMargins(4, 2, 0, 12)
        summary_layout.setSpacing(6)

        self.summary_title = QLabel("Select a session")
        self.summary_title.setStyleSheet(
            "color: #a8cee3; font-size: 12px; font-weight: bold;"
        )
        summary_layout.addWidget(self.summary_title)

        metrics_layout = QHBoxLayout()
        metrics_layout.setContentsMargins(0, 0, 0, 0)
        metrics_layout.setSpacing(12)
        summary_layout.addLayout(metrics_layout)

        self.summary_values = []
        for label_text in ("Pings", "Packet loss", "Spikes"):
            metric = QVBoxLayout()
            metric.setSpacing(0)

            value = QLabel("--")
            value.setAlignment(Qt.AlignCenter)
            value.setStyleSheet(
                "color: #ffffff; font-size: 20px; font-weight: bold;"
            )

            label = QLabel(label_text)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: #b0b6cf; font-size: 12px;")

            metric.addWidget(value)
            metric.addWidget(label)
            metrics_layout.addLayout(metric, 1)
            self.summary_values.append(value)

        layout.addWidget(self.summary_card)

        self.latency_plot = pg.PlotWidget()
        self.latency_plot.setBackground("#000000")
        self.latency_plot.setTitle("Historical Latency")
        self.latency_plot.setLabel("left", "Latency", units="ms")
        self.latency_plot.setLabel("bottom", "Ping Number")

        self.latency_curve = self.latency_plot.plot(
            pen=pg.mkPen("#a8cee3", width=2),
            connect="finite"
        )
        self.latency_spikes = self.latency_plot.plot(
            pen=None,
            symbol="x",
            symbolPen=pg.mkPen("#ff5555", width=2),
            symbolBrush=pg.mkBrush("#ff5555"),
            symbolSize=12
        )

        layout.addWidget(self.latency_plot)
        
        self.jitter_plot = pg.PlotWidget()
        self.jitter_plot.setBackground("#000000")
        self.jitter_plot.setTitle("Historical Jitter")
        self.jitter_plot.setLabel("left", "Jitter", units="ms")
        self.jitter_plot.setLabel("bottom", "Ping Number")

        self.jitter_curve = self.jitter_plot.plot(
            pen=pg.mkPen("#a8cee3", width=2),
            connect="finite"
        )

        layout.addWidget(self.jitter_plot)
        
    def load_sessions(self):
        self.sessions_table.blockSignals(True)
        
        self.sessions_table.clearSelection()
        self.sessions_table.setRowCount(0)
        
        sessions = get_sessions()
        self.sessions_table.setRowCount(len(sessions))
        
        for row, session in enumerate(sessions):
            session_id, target, started_at, ended_at = session
            
            values = [
                str(session_id), 
                target, 
                self.format_timestamp(started_at), 
                self.format_timestamp(ended_at) if ended_at else "N/A"
            ]
            
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                self.sessions_table.setItem(
                    row, 
                    col, 
                    item
                )
                
        self.sessions_table.blockSignals(False)
        
        self.summary_title.setText("Select a session")
        for value in self.summary_values:
            value.setText("--")
        self.latency_curve.setData([], [])
        self.latency_spikes.setData([], [])
        self.jitter_curve.setData([], [])
                
    def show_selected_session(self):
        row = self.sessions_table.currentRow()
        
        if row < 0:
            return
        
        session_id_item = self.sessions_table.item(row, 0)
        
        if session_id_item is None:
            return
        
        session_id = int(session_id_item.text())
        
        results = get_session_results(session_id)
        
        ping_count = len(results)
        timeout_count = sum(
            1 for result in results if result[3].lower() == "timeout"
        )
        valid_packets = ping_count - sum(
            1 for result in results if result[3].lower() not in ("success", "timeout")
        )
        packet_loss = (
            timeout_count / valid_packets * 100
            if valid_packets > 0 else None
        )
        spike_count = sum(1 for result in results if result[6])

        self.summary_title.setText(f"Session #{session_id}")
        self.summary_values[0].setText(str(ping_count))
        self.summary_values[1].setText(f"{packet_loss:g}%" if packet_loss is not None else "N/A")
        self.summary_values[2].setText(str(spike_count))
        
        ping_numbers = []
        latencies = []
        spike_numbers = []
        spike_latencies = []
        jitters = []
        
        for index, result in enumerate(results, start = 1):
            ping_id, sid, timestamp, status, latency, jitter, spike, error = result
            
            ping_numbers.append(index)
            
            latencies.append(latency if latency is not None else float("nan"))
            jitters.append(jitter if jitter is not None else float("nan"))
            
            if spike and latency is not None:
                spike_numbers.append(index)
                spike_latencies.append(latency)
        
        self.latency_curve.setData(ping_numbers, latencies)
        self.latency_spikes.setData(spike_numbers, spike_latencies)
        self.jitter_curve.setData(ping_numbers, jitters)
        
        self.latency_plot.enableAutoRange()
        self.jitter_plot.enableAutoRange()
    
    def format_timestamp(self, timestamp):
        if not timestamp:
            return "N/A"

        return datetime.fromisoformat(timestamp).astimezone().strftime(
            "%Y-%m-%d %H:%M:%S"
        )