"""
Match sync file logger for debugging save failures
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

class MatchSyncLogger:
    """Logs match sync operations to a file for debugging"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.session_file = self.log_dir / f"match_sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        
    def log_save_attempt(self, match_id: str, puuid: str, has_timeline: bool, context: str = ""):
        """Log when attempting to save a match"""
        self._write_log({
            "timestamp": datetime.now().isoformat(),
            "event": "save_attempt",
            "match_id": match_id,
            "puuid": puuid,
            "has_timeline": has_timeline,
            "context": context
        })
    
    def log_save_success(self, match_id: str, puuid: str, verified: bool = False):
        """Log successful save"""
        self._write_log({
            "timestamp": datetime.now().isoformat(),
            "event": "save_success",
            "match_id": match_id,
            "puuid": puuid,
            "verified": verified
        })
    
    def log_save_failure(self, match_id: str, puuid: str, reason: str, error: Optional[str] = None):
        """Log save failure"""
        self._write_log({
            "timestamp": datetime.now().isoformat(),
            "event": "save_failure",
            "match_id": match_id,
            "puuid": puuid,
            "reason": reason,
            "error": error
        })
    
    def log_verification_failure(self, match_id: str, puuid: str):
        """Log when save succeeded but verification failed"""
        self._write_log({
            "timestamp": datetime.now().isoformat(),
            "event": "verification_failure",
            "match_id": match_id,
            "puuid": puuid
        })
    
    def log_batch_summary(self, total_attempted: int, total_saved: int, total_failed: int, puuid: str):
        """Log batch summary"""
        self._write_log({
            "timestamp": datetime.now().isoformat(),
            "event": "batch_summary",
            "puuid": puuid,
            "total_attempted": total_attempted,
            "total_saved": total_saved,
            "total_failed": total_failed,
            "success_rate": f"{(total_saved/total_attempted*100):.1f}%" if total_attempted > 0 else "N/A"
        })
    
    def _write_log(self, data: Dict[str, Any]):
        """Write log entry to file"""
        try:
            with open(self.session_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(data) + '\n')
        except Exception as e:
            print(f"Error writing to match sync log: {e}")

# Global instance
_logger_instance = None

def get_match_sync_logger() -> MatchSyncLogger:
    """Get or create the global match sync logger instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = MatchSyncLogger()
    return _logger_instance
