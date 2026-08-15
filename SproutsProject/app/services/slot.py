"""
Time slot management system for availability tracking.
Adapted from the original Slot.py to work with the Flask application.
"""

class Slot:
    """Represents a time slot with start and end times in 24-hour format."""
    
    def __init__(self, string="Unavailable"):
        self.start = 0
        self.end = 0
        self.from_string(string)

    def __str__(self):
        return f"{self.start}-{self.end}"

    def __repr__(self):
        return f"{self.start}-{self.end}"

    @staticmethod
    def to_24_hour(string_am_pm):
        """Convert AM/PM time string to 24-hour format."""
        string_am_pm = string_am_pm.strip()
        
        if 'AM' in string_am_pm:
            hour = int(string_am_pm.replace('AM', ''))
            return 12 if hour == 12 else hour
        elif string_am_pm == '12PM':
            return 12
        else:
            hour = int(string_am_pm.replace('PM', ''))
            return 12 + hour if hour != 12 else 12

    @staticmethod
    def combine_slots(day_slots_string):
        """
        Combine multiple time slots for a day into optimized slots.
        Input: "9AM-12PM,1PM-5PM,6PM-9PM"
        Output: List of Slot objects
        """
        if not day_slots_string or day_slots_string.strip() in ['', 'Unavailable']:
            return []
            
        slots = []
        individual_slots = day_slots_string.split(',')
        prev_slot = Slot()
        
        for slot_string in individual_slots:
            slot_string = slot_string.strip()
            if not slot_string:
                continue
                
            new_slot = Slot(slot_string)
            
            # If it's an all-day slot, just return it
            if new_slot.is_all_day():
                return [new_slot]
            
            # If slots are adjacent, combine them
            if prev_slot.is_adjacent(new_slot):
                prev_slot.add_and_combine(new_slot)
                continue
            
            # Only keep slots that are at least 4 hours long
            if prev_slot.duration() >= 4:
                slots.append(prev_slot)
            
            prev_slot = new_slot
        
        # Add the last slot if it's long enough
        if prev_slot.duration() >= 4:
            slots.append(prev_slot)
            
        return slots

    def from_string(self, string):
        """Parse time slot from string format."""
        string = string.strip()
        
        if string == 'All Day (9AM-9PM)' or string == 'All Day':
            self.start = 9
            self.end = 21
        elif string in ['', 'Unavailable']:
            self.start = 0
            self.end = 0
        else:
            try:
                start_end = string.split('-')
                if len(start_end) == 2:
                    self.start = self.to_24_hour(start_end[0])
                    self.end = self.to_24_hour(start_end[1])
            except (ValueError, IndexError):
                # If parsing fails, mark as unavailable
                self.start = 0
                self.end = 0

    def is_adjacent(self, other):
        """Check if this slot is adjacent to another slot."""
        if not isinstance(other, Slot):
            return False
        return self.start == other.end or self.end == other.start

    def add_and_combine(self, other):
        """Combine this slot with an adjacent slot."""
        if not self.is_adjacent(other):
            raise ValueError("Cannot combine slots that are not adjacent")
        
        if self.start == other.end:
            self.start = other.start
        else:
            self.end = other.end

    def duration(self):
        """Get the duration of the slot in hours."""
        return max(0, self.end - self.start)

    def is_all_day(self):
        """Check if this is an all-day slot (9AM-9PM)."""
        return self.start == 9 and self.end == 21

    def get_overlap(self, other_slot):
        """Get the overlapping time between this slot and another."""
        if not isinstance(other_slot, Slot):
            return Slot('')
        
        overlap = Slot('')
        overlap.start = max(self.start, other_slot.start)
        overlap.end = min(self.end, other_slot.end)
        
        # If there's no actual overlap, return empty slot
        if overlap.start >= overlap.end:
            overlap.start = 0
            overlap.end = 0
            
        return overlap

    def is_available(self):
        """Check if this slot represents available time."""
        return self.duration() > 0

    def to_dict(self):
        """Convert slot to dictionary for JSON serialization."""
        return {
            'start': self.start,
            'end': self.end,
            'duration': self.duration()
        }

    @classmethod
    def from_dict(cls, data):
        """Create slot from dictionary."""
        slot = cls('')
        slot.start = data.get('start', 0)
        slot.end = data.get('end', 0)
        return slot

    def to_display_string(self):
        """Convert to human-readable time format."""
        if not self.is_available():
            return "Unavailable"
        
        def hour_to_display(hour):
            if hour == 0:
                return "12AM"
            elif hour < 12:
                return f"{hour}AM"
            elif hour == 12:
                return "12PM"
            else:
                return f"{hour - 12}PM"
        
        return f"{hour_to_display(self.start)}-{hour_to_display(self.end)}"
