from PySide6.QtCore import QThread, Signal

class PingWorker(QThread):
    result_ready = Signal(dict)
    

    def __init__(self, target, interval):
        super().__init__()
        self.target = target
        self.interval = interval
    
    def run(self):
        from datetime import datetime, timezone
        from storage.database import insert_session
        from main import handle_ping

        # Create a new monitoring session
        session_id = insert_session(
            self.target,
            datetime.now(timezone.utc).isoformat()
        )

        # Start monitoring without calling terminal startup
        handle_ping(
            self.target,
            self.interval,
            session_id,
            self.result_ready.emit,
            self.isInterruptionRequested
        )

    def stop(self):
        self.requestInterruption()