class MentorOnlineOffline:
    _instance = None
    _status = {} # Keys are IDs for mentors, values are booleans

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MentorOnlineOffline, cls).__new__(cls)
        return cls._instance

    def set_online(self, user_id: str):
        """Set a mentor's status to online."""
        self._status[user_id] = True

    def set_offline(self, user_id: str):
        """Set a mentor's status to offline."""
        self._status[user_id] = False

    def is_online(self, user_id: str) -> bool:
        """Check if a mentor is currently online."""
        return self._status.get(user_id, False)

    def get_all_online(self):
        """Return a list of all currently online mentors."""
        return [user_id for user_id, status in self._status.items() if status]
    # curl http://localhost:5001/mentor_status/all_online

# Global instance
mentor_status_tracker = MentorOnlineOffline()