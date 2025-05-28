
import pytest
import json
from datetime import datetime, timedelta
from calendar import CalendarApp

class TestCalendarApp:
    
    @pytest.fixture
    def calendar_app(self):
        """Create a fresh CalendarApp instance for each test"""
        return CalendarApp()
    
    @pytest.fixture
    def calendar_with_events(self):
        """Create a CalendarApp instance with some test events"""
        app = CalendarApp()
        app.add_event('2024-01-15', 'Test Event 1')
        app.add_event('2024-01-15', 'Test Event 2')
        app.add_event('2024-02-20', 'Future Event')
        return app
    
    def test_initialization(self, calendar_app):
        """Test that CalendarApp initializes correctly"""
        assert calendar_app.current_date is not None
        assert calendar_app.selected_date is None
        assert calendar_app.events == {}
        assert len(calendar_app.month_names) == 12
        assert calendar_app.month_names[0] == 'January'
        assert calendar_app.month_names[11] == 'December'
    
    def test_previous_month_navigation(self, calendar_app):
        """Test navigating to previous month"""
        # Set to March 2024
        calendar_app.current_date = datetime(2024, 3, 15)
        initial_month = calendar_app.current_date.month
        
        calendar_app.previous_month()
        assert calendar_app.current_date.month == initial_month - 1
        assert calendar_app.current_date.year == 2024
        
        # Test year rollover (January to December)
        calendar_app.current_date = datetime(2024, 1, 15)
        calendar_app.previous_month()
        assert calendar_app.current_date.month == 12
        assert calendar_app.current_date.year == 2023
    
    def test_next_month_navigation(self, calendar_app):
        """Test navigating to next month"""
        # Set to March 2024
        calendar_app.current_date = datetime(2024, 3, 15)
        initial_month = calendar_app.current_date.month
        
        calendar_app.next_month()
        assert calendar_app.current_date.month == initial_month + 1
        assert calendar_app.current_date.year == 2024
        
        # Test year rollover (December to January)
        calendar_app.current_date = datetime(2024, 12, 15)
        calendar_app.next_month()
        assert calendar_app.current_date.month == 1
        assert calendar_app.current_date.year == 2025
    
    def test_get_month_year_display(self, calendar_app):
        """Test month/year display formatting"""
        calendar_app.current_date = datetime(2024, 3, 15)
        assert calendar_app.get_month_year_display() == "March 2024"
        
        calendar_app.current_date = datetime(2023, 12, 1)
        assert calendar_app.get_month_year_display() == "December 2023"
    
    def test_get_days_in_month(self, calendar_app):
        """Test getting correct number of days in month"""
        # Test regular month
        calendar_app.current_date = datetime(2024, 4, 15)  # April
        assert calendar_app.get_days_in_month() == 30
        
        # Test leap year February
        calendar_app.current_date = datetime(2024, 2, 15)  # 2024 is leap year
        assert calendar_app.get_days_in_month() == 29
        
        # Test non-leap year February
        calendar_app.current_date = datetime(2023, 2, 15)  # 2023 is not leap year
        assert calendar_app.get_days_in_month() == 28
        
        # Test 31-day month
        calendar_app.current_date = datetime(2024, 1, 15)  # January
        assert calendar_app.get_days_in_month() == 31
    
    def test_add_event_success(self, calendar_app):
        """Test successfully adding events"""
        result = calendar_app.add_event('2024-01-15', 'Test Event')
        assert result is True
        assert '2024-01-15' in calendar_app.events
        assert len(calendar_app.events['2024-01-15']) == 1
        assert calendar_app.events['2024-01-15'][0]['title'] == 'Test Event'
        assert 'id' in calendar_app.events['2024-01-15'][0]
    
    def test_add_event_multiple_same_date(self, calendar_app):
        """Test adding multiple events to the same date"""
        calendar_app.add_event('2024-01-15', 'Event 1')
        calendar_app.add_event('2024-01-15', 'Event 2')
        
        assert len(calendar_app.events['2024-01-15']) == 2
        titles = [event['title'] for event in calendar_app.events['2024-01-15']]
        assert 'Event 1' in titles
        assert 'Event 2' in titles
    
    def test_add_event_failure_cases(self, calendar_app):
        """Test cases where adding events should fail"""
        # Empty date
        assert calendar_app.add_event('', 'Test Event') is False
        
        # Empty title
        assert calendar_app.add_event('2024-01-15', '') is False
        
        # Whitespace-only title
        assert calendar_app.add_event('2024-01-15', '   ') is False
        
        # Both empty
        assert calendar_app.add_event('', '') is False
    
    def test_delete_event_success(self, calendar_with_events):
        """Test successfully deleting an event"""
        # Get an event ID to delete
        event_id = calendar_with_events.events['2024-01-15'][0]['id']
        initial_count = len(calendar_with_events.events['2024-01-15'])
        
        result = calendar_with_events.delete_event('2024-01-15', event_id)
        assert result is True
        assert len(calendar_with_events.events['2024-01-15']) == initial_count - 1
    
    def test_delete_event_last_event_removes_date(self, calendar_app):
        """Test that deleting the last event removes the date key"""
        calendar_app.add_event('2024-01-15', 'Only Event')
        event_id = calendar_app.events['2024-01-15'][0]['id']
        
        calendar_app.delete_event('2024-01-15', event_id)
        assert '2024-01-15' not in calendar_app.events
    
    def test_delete_event_failure_cases(self, calendar_with_events):
        """Test cases where deleting events should fail"""
        # Non-existent date
        result = calendar_with_events.delete_event('2024-12-25', 12345)
        assert result is False
        
        # Non-existent event ID
        result = calendar_with_events.delete_event('2024-01-15', 99999)
        assert result is False
    
    def test_get_events_for_date(self, calendar_with_events):
        """Test retrieving events for a specific date"""
        events = calendar_with_events.get_events_for_date('2024-01-15')
        assert len(events) == 2
        
        # Non-existent date should return empty list
        events = calendar_with_events.get_events_for_date('2024-12-25')
        assert events == []
    
    def test_has_events_on_date(self, calendar_with_events):
        """Test checking if date has events"""
        assert calendar_with_events.has_events_on_date('2024-01-15') is True
        assert calendar_with_events.has_events_on_date('2024-02-20') is True
        assert calendar_with_events.has_events_on_date('2024-12-25') is False
    
    def test_get_upcoming_events(self, calendar_app):
        """Test getting upcoming events in chronological order"""
        # Add events in non-chronological order
        calendar_app.add_event('2024-03-15', 'March Event')
        calendar_app.add_event('2024-01-15', 'January Event')
        calendar_app.add_event('2024-02-15', 'February Event')
        
        upcoming = calendar_app.get_upcoming_events()
        
        # Should be sorted by date
        assert len(upcoming) == 3
        assert upcoming[0]['date'] == '2024-01-15'
        assert upcoming[1]['date'] == '2024-02-15'
        assert upcoming[2]['date'] == '2024-03-15'
    
    def test_get_upcoming_events_limit(self, calendar_app):
        """Test limiting upcoming events"""
        # Add 5 events
        for i in range(1, 6):
            calendar_app.add_event(f'2024-01-{i:02d}', f'Event {i}')
        
        upcoming = calendar_app.get_upcoming_events(limit=3)
        assert len(upcoming) == 3
    
    def test_format_date(self, calendar_app):
        """Test date formatting"""
        formatted = calendar_app.format_date('2024-01-15')
        assert 'Jan' in formatted
        assert '15' in formatted
        assert '2024' in formatted
        
        # Test invalid date
        invalid_formatted = calendar_app.format_date('invalid-date')
        assert invalid_formatted == 'invalid-date'
    
    def test_select_date_success(self, calendar_app):
        """Test successful date selection"""
        result = calendar_app.select_date('2024-01-15')
        assert result is True
        assert calendar_app.selected_date == '2024-01-15'
    
    def test_select_date_failure(self, calendar_app):
        """Test failed date selection with invalid format"""
        result = calendar_app.select_date('invalid-date')
        assert result is False
        assert calendar_app.selected_date is None
    
    def test_clear_selection(self, calendar_app):
        """Test clearing date selection"""
        calendar_app.select_date('2024-01-15')
        calendar_app.clear_selection()
        assert calendar_app.selected_date is None
    
    def test_is_today(self, calendar_app):
        """Test checking if date is today"""
        today = datetime.now().strftime('%Y-%m-%d')
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        assert calendar_app.is_today(today) is True
        assert calendar_app.is_today(tomorrow) is False
    
    def test_export_events(self, calendar_with_events):
        """Test exporting events to JSON"""
        exported = calendar_with_events.export_events()
        
        # Should be valid JSON
        parsed = json.loads(exported)
        assert isinstance(parsed, dict)
        assert '2024-01-15' in parsed
        assert '2024-02-20' in parsed
    
    def test_import_events_success(self, calendar_app):
        """Test successfully importing events from JSON"""
        test_events = {
            '2024-01-15': [{'title': 'Imported Event', 'id': 12345}]
        }
        json_string = json.dumps(test_events)
        
        result = calendar_app.import_events(json_string)
        assert result is True
        assert calendar_app.events == test_events
    
    def test_import_events_failure(self, calendar_app):
        """Test failed event import with invalid JSON"""
        # Invalid JSON
        result = calendar_app.import_events('invalid json')
        assert result is False
        
        # Valid JSON but wrong structure
        result = calendar_app.import_events('["not", "a", "dict"]')
        assert result is False
    
    def test_get_first_day_of_week(self, calendar_app):
        """Test getting first day of week for current month"""
        # January 1, 2024 was a Monday (weekday = 0)
        calendar_app.current_date = datetime(2024, 1, 15)
        first_day = calendar_app.get_first_day_of_week()
        assert isinstance(first_day, int)
        assert 0 <= first_day <= 6

# Integration tests
class TestCalendarAppIntegration:
    
    def test_full_calendar_workflow(self):
        """Test a complete calendar workflow"""
        calendar = CalendarApp()
        
        # Navigate months
        calendar.current_date = datetime(2024, 1, 15)
        calendar.next_month()
        assert calendar.current_date.month == 2
        
        # Add events
        calendar.add_event('2024-02-14', 'Valentine\'s Day')
        calendar.add_event('2024-02-14', 'Dinner Reservation')
        calendar.add_event('2024-02-20', 'Meeting')
        
        # Select a date
        calendar.select_date('2024-02-14')
        assert calendar.selected_date == '2024-02-14'
        
        # Check events
        events = calendar.get_events_for_date('2024-02-14')
        assert len(events) == 2
        
        # Delete one event
        event_id = events[0]['id']
        calendar.delete_event('2024-02-14', event_id)
        
        # Verify deletion
        remaining_events = calendar.get_events_for_date('2024-02-14')
        assert len(remaining_events) == 1
        
        # Get upcoming events
        upcoming = calendar.get_upcoming_events()
        assert len(upcoming) >= 1
        
        # Export and import
        exported = calendar.export_events()
        new_calendar = CalendarApp()
        new_calendar.import_events(exported)
        
        assert new_calendar.events == calendar.events

if __name__ == '__main__':
    pytest.main([__file__])
