
class CalendarApp {
    constructor() {
        this.currentDate = new Date();
        this.selectedDate = null;
        this.events = JSON.parse(localStorage.getItem('calendarEvents')) || {};
        this.monthNames = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ];
        
        this.initializeElements();
        this.attachEventListeners();
        this.renderCalendar();
        this.renderEvents();
    }
    
    initializeElements() {
        this.monthYearElement = document.getElementById('monthYear');
        this.calendarDaysElement = document.getElementById('calendarDays');
        this.prevMonthBtn = document.getElementById('prevMonth');
        this.nextMonthBtn = document.getElementById('nextMonth');
        this.eventDateInput = document.getElementById('eventDate');
        this.eventTitleInput = document.getElementById('eventTitle');
        this.addEventBtn = document.getElementById('addEvent');
        this.eventsContainer = document.getElementById('eventsContainer');
    }
    
    attachEventListeners() {
        this.prevMonthBtn.addEventListener('click', () => this.previousMonth());
        this.nextMonthBtn.addEventListener('click', () => this.nextMonth());
        this.addEventBtn.addEventListener('click', () => this.addEvent());
        this.eventTitleInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.addEvent();
        });
    }
    
    previousMonth() {
        this.currentDate.setMonth(this.currentDate.getMonth() - 1);
        this.renderCalendar();
    }
    
    nextMonth() {
        this.currentDate.setMonth(this.currentDate.getMonth() + 1);
        this.renderCalendar();
    }
    
    renderCalendar() {
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        
        this.monthYearElement.textContent = `${this.monthNames[month]} ${year}`;
        
        // Clear previous calendar
        this.calendarDaysElement.innerHTML = '';
        
        // Get first day of the month and number of days
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const daysInMonth = lastDay.getDate();
        const startingDayOfWeek = firstDay.getDay();
        
        // Get days from previous month
        const prevMonth = new Date(year, month, 0);
        const daysInPrevMonth = prevMonth.getDate();
        
        // Add days from previous month
        for (let i = startingDayOfWeek - 1; i >= 0; i--) {
            const dayElement = this.createDayElement(
                daysInPrevMonth - i, 
                true, 
                year, 
                month - 1
            );
            this.calendarDaysElement.appendChild(dayElement);
        }
        
        // Add days of current month
        for (let day = 1; day <= daysInMonth; day++) {
            const dayElement = this.createDayElement(day, false, year, month);
            this.calendarDaysElement.appendChild(dayElement);
        }
        
        // Add days from next month
        const totalCells = this.calendarDaysElement.children.length;
        const remainingCells = 42 - totalCells; // 6 rows × 7 days
        
        for (let day = 1; day <= remainingCells; day++) {
            const dayElement = this.createDayElement(day, true, year, month + 1);
            this.calendarDaysElement.appendChild(dayElement);
        }
    }
    
    createDayElement(day, isOtherMonth, year, month) {
        const dayElement = document.createElement('div');
        dayElement.className = 'day';
        dayElement.textContent = day;
        
        if (isOtherMonth) {
            dayElement.classList.add('other-month');
        }
        
        // Check if this is today
        const today = new Date();
        const actualMonth = isOtherMonth ? (month < 0 ? 11 : month > 11 ? 0 : month) : month;
        const actualYear = isOtherMonth ? (month < 0 ? year - 1 : month > 11 ? year + 1 : year) : year;
        
        if (actualYear === today.getFullYear() && 
            actualMonth === today.getMonth() && 
            day === today.getDate() && 
            !isOtherMonth) {
            dayElement.classList.add('today');
        }
        
        // Check for events
        const dateKey = `${actualYear}-${String(actualMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        if (this.events[dateKey]) {
            dayElement.classList.add('has-event');
            const eventDot = document.createElement('div');
            eventDot.className = 'event-dot';
            dayElement.appendChild(eventDot);
        }
        
        // Add click event to select date
        dayElement.addEventListener('click', () => {
            // Remove previous selection
            document.querySelectorAll('.day.selected').forEach(el => {
                el.classList.remove('selected');
            });
            
            // Add selection to clicked day
            dayElement.classList.add('selected');
            this.selectedDate = dateKey;
            this.eventDateInput.value = dateKey;
        });
        
        return dayElement;
    }
    
    addEvent() {
        const date = this.eventDateInput.value;
        const title = this.eventTitleInput.value.trim();
        
        if (!date || !title) {
            alert('Please enter both date and event title');
            return;
        }
        
        if (!this.events[date]) {
            this.events[date] = [];
        }
        
        this.events[date].push({
            title: title,
            id: Date.now()
        });
        
        this.saveEvents();
        this.eventTitleInput.value = '';
        this.renderCalendar();
        this.renderEvents();
    }
    
    deleteEvent(date, eventId) {
        if (this.events[date]) {
            this.events[date] = this.events[date].filter(event => event.id !== eventId);
            if (this.events[date].length === 0) {
                delete this.events[date];
            }
            this.saveEvents();
            this.renderCalendar();
            this.renderEvents();
        }
    }
    
    saveEvents() {
        localStorage.setItem('calendarEvents', JSON.stringify(this.events));
    }
    
    renderEvents() {
        this.eventsContainer.innerHTML = '';
        
        // Get all events and sort by date
        const allEvents = [];
        for (const [date, events] of Object.entries(this.events)) {
            events.forEach(event => {
                allEvents.push({ ...event, date });
            });
        }
        
        allEvents.sort((a, b) => new Date(a.date) - new Date(b.date));
        
        // Show only upcoming events (next 10)
        const upcomingEvents = allEvents
            .filter(event => new Date(event.date) >= new Date().setHours(0, 0, 0, 0))
            .slice(0, 10);
        
        if (upcomingEvents.length === 0) {
            this.eventsContainer.innerHTML = '<p style="color: #a0aec0; font-style: italic;">No upcoming events</p>';
            return;
        }
        
        upcomingEvents.forEach(event => {
            const eventElement = document.createElement('div');
            eventElement.className = 'event-item';
            eventElement.innerHTML = `
                <div class="event-date">${this.formatDate(event.date)}</div>
                <div class="event-title">${event.title}</div>
                <button onclick="calendar.deleteEvent('${event.date}', ${event.id})" 
                        style="background: #e53e3e; color: white; border: none; padding: 2px 6px; 
                               border-radius: 3px; font-size: 10px; margin-top: 5px; cursor: pointer;">
                    Delete
                </button>
            `;
            this.eventsContainer.appendChild(eventElement);
        });
    }
    
    formatDate(dateString) {
        const date = new Date(dateString);
        const options = { 
            weekday: 'short', 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric' 
        };
        return date.toLocaleDateString('en-US', options);
    }
}

// Initialize the calendar when the page loads
let calendar;
document.addEventListener('DOMContentLoaded', () => {
    calendar = new CalendarApp();
});
