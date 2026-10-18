from PySide6.QtCore import QThread, Signal

class PingWorker(QThread):
    result_ready = Signal(dict)
    

    def __init__(self, target, interval):
        super().__init__()
        self.target = target
        self.interval = interval
    
    def run(self):
        from main import startup
        startup(
            self.target,
            self.interval,
            self.result_ready.emit,
            self.isInterruptionRequested
        )

    def stop(self):
        self.requestInterruption()