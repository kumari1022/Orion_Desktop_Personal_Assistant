from datetime import datetime
import platform


class SystemContext:

    @staticmethod
    def get_context():
        return {
            "current_time": datetime.now().strftime("%H:%M:%S"),
            "current_date": datetime.now().strftime("%Y-%m-%d"),
            "system": platform.system(),
            "machine": platform.machine()
        }