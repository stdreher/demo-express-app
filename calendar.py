
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class CalendarApp:
    def __init__(self):
        self.current_date = datetime.now()
        self.selected_date: Optional[str] = None
        self.events: Dict[str, List[Dict]] = {}
        self.month_names = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
    
    def previous_month(self):
        """Navigate to previous month"""
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month - 1)
    
    def next_month(self):
        """Navigate to next month"""
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month + 1)
    
    def get_month_year_display(self) -> str:
        """Get formatted month and year for display"""
        return f"{self.month_names[self.current_date.month - 1]} {self.current_date.year}"
    
    def get_days_in_month(self) -> int:
        """Get number of days in current month"""
        year = self.current_date.year
        month = self.current_date.month
        
        if month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, month + 1, 1)
        
        last_day = next_month - timedelta(days=1)
        return last_day.day
    
    def get_first_day_of_week(self) -> int:
        """Get the day of week for the first day of current month (0=Monday, 6=Sunday)"""
        first_day = datetime(self.current_date.year, self.current_date.month, 1)
        return first_day.weekday()
    
    def add_event(self, date: str, title: str) -> bool:
        """Add an event to a specific date"""
        if not date or not title.strip():
            return False
        
        if date not in self.events:
            self.events[date] = []
        
        event = {
            'title': title.strip(),
            'id': int(datetime.now().timestamp() * 1000)  # milliseconds timestamp
        }
        
        self.events[date].append(event)
        return True
    
    def delete_event(self, date: str, event_id: int) -> bool:
        """Delete an event by date and event ID"""
        if date not in self.events:
            return False
        
        initial_count = len(self.events[date])
        self.events[date] = [event for event in self.events[date] if event['id'] != event_id]
        
        if len(self.events[date]) == 0:
            del self.events[date]
        
        return len(self.events[date]) < initial_count
    
    def get_events_for_date(self, date: str) -> List[Dict]:
        """Get all events for a specific date"""
        return self.events.get(date, [])
    
    def has_events_on_date(self, date: str) -> bool:
        """Check if there are events on a specific date"""
        return date in self.events and len(self.events[date]) > 0
    
    def get_upcoming_events(self, limit: int = 10) -> List[Dict]:
        """Get upcoming events sorted by date"""
        all_events = []
        
        for date, events in self.events.items():
            for event in events:
                all_events.append({**event, 'date': date})
        
        # Sort by date
        all_events.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'))
        
        # Filter upcoming events
        today = datetime.now().strftime('%Y-%m-%d')
        upcoming = [event for event in all_events if event['date'] >= today]
        
        return upcoming[:limit]
    
    def format_date(self, date_string: str) -> str:
        """Format date string for display"""
        try:
            date = datetime.strptime(date_string, '%Y-%m-%d')
            return date.strftime('%a, %b %d, %Y')
        except ValueError:
            return date_string
    
    def select_date(self, date: str) -> bool:
        """Select a specific date"""
        try:
            datetime.strptime(date, '%Y-%m-%d')
            self.selected_date = date
            return True
        except ValueError:
            return False
    
    def clear_selection(self):
        """Clear the currently selected date"""
        self.selected_date = None
    
    def is_today(self, date: str) -> bool:
        """Check if the given date is today"""
        today = datetime.now().strftime('%Y-%m-%d')
        return date == today
    
    def export_events(self) -> str:
        """Export events as JSON string"""
        return json.dumps(self.events, indent=2)
    
    def import_events(self, json_string: str) -> bool:
        """Import events from JSON string"""
        try:
            imported_events = json.loads(json_string)
            if isinstance(imported_events, dict):
                self.events = imported_events
                return True
            return False
        except (json.JSONDecodeError, TypeError):
            return False
