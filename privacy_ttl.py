import uuid
import time
from datetime import datetime, timedelta
from threading import Lock
from apscheduler.schedulers.background import BackgroundScheduler
from config import SESSION_TTL_MINUTES

class SessionManager:
    """
    Manages ephemeral sessions with auto-delete (TTL)
    Sessions are stored in-memory and automatically deleted after TTL expires
    """
    
    def __init__(self):
        self.sessions = {}  # {session_id: session_data}
        self.lock = Lock()
        
        # Start background scheduler for cleanup
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(
            self.cleanup_expired_sessions,
            'interval',
            minutes=5  # Run cleanup every 5 minutes
        )
        self.scheduler.start()
    
    def create_session(self):
        """
        Create a new session
        
        Returns:
            str: session_id
        """
        session_id = str(uuid.uuid4())
        
        with self.lock:
            self.sessions[session_id] = {
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(minutes=SESSION_TTL_MINUTES),
                "data": None
            }
        
        return session_id
    
    def store_analysis(self, session_id, analysis_data):
        """
        Store analysis results in session
        
        Args:
            session_id: str
            analysis_data: dict - Analysis results
        """
        with self.lock:
            if session_id in self.sessions:
                self.sessions[session_id]["data"] = analysis_data
                # Refresh expiry
                self.sessions[session_id]["expires_at"] = datetime.utcnow() + timedelta(minutes=SESSION_TTL_MINUTES)
    
    def get_session(self, session_id):
        """
        Retrieve session data
        
        Returns:
            dict or None
        """
        with self.lock:
            if session_id not in self.sessions:
                return None
            
            session = self.sessions[session_id]
            
            # Check if expired
            if datetime.utcnow() > session["expires_at"]:
                del self.sessions[session_id]
                return None
            
            # Refresh expiry on access
            session["expires_at"] = datetime.utcnow() + timedelta(minutes=SESSION_TTL_MINUTES)
            
            return session["data"]
    
    def delete_session(self, session_id):
        """
        Manually delete a session
        """
        with self.lock:
            if session_id in self.sessions:
                del self.sessions[session_id]
    
    def cleanup_expired_sessions(self):
        """
        Background job to clean up expired sessions
        Runs every 5 minutes
        """
        now = datetime.utcnow()
        expired_sessions = []
        
        with self.lock:
            for session_id, session in self.sessions.items():
                if now > session["expires_at"]:
                    expired_sessions.append(session_id)
            
            # Delete expired sessions
            for session_id in expired_sessions:
                del self.sessions[session_id]
        
        if expired_sessions:
            print(f"[Privacy] Deleted {len(expired_sessions)} expired sessions at {now}")
    
    def get_session_count(self):
        """
        Get current number of active sessions
        """
        with self.lock:
            return len(self.sessions)
    
    def get_session_info(self, session_id):
        """
        Get session metadata (without data)
        """
        with self.lock:
            if session_id not in self.sessions:
                return None
            
            session = self.sessions[session_id]
            return {
                "session_id": session_id,
                "created_at": session["created_at"].isoformat(),
                "expires_at": session["expires_at"].isoformat(),
                "has_data": session["data"] is not None
            }
    
    def extend_session(self, session_id, extra_minutes=None):
        """
        Extend session TTL
        
        Args:
            session_id: str
            extra_minutes: int (optional, defaults to SESSION_TTL_MINUTES)
        """
        minutes = extra_minutes or SESSION_TTL_MINUTES
        
        with self.lock:
            if session_id in self.sessions:
                self.sessions[session_id]["expires_at"] = datetime.utcnow() + timedelta(minutes=minutes)
    
    def shutdown(self):
        """
        Shutdown scheduler (call when stopping Flask app)
        """
        self.scheduler.shutdown()

# Global session manager instance
_session_manager = None

def get_session_manager():
    """
    Get or create global session manager instance
    """
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager