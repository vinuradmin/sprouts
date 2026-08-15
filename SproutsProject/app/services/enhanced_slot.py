"""
Enhanced Slot class with 1-hour discontinuity tolerance for merging
"""

class EnhancedSlot:
    """Enhanced Slot class with improved merging logic"""
    
    def __init__(self, string="Unavailable"):
        self.start = 0
        self.end = 0
        self.fromString(string)
    
    def __str__(self):
        return f"{self.start}-{self.end}"
    
    def __repr__(self):
        return f"EnhancedSlot({self.start}-{self.end})"
    
    @staticmethod
    def to24(stringAmPm):
        """Convert AM/PM time to 24-hour format"""
        if 'AM' in stringAmPm:
            return int(stringAmPm.replace('AM', ''))
        elif stringAmPm.strip() == '12PM':
            return 12
        else:
            return 12 + int(stringAmPm.replace('PM', ''))
    
    def fromString(self, string):
        """Parse time string into slot"""
        if string == 'All Day (9AM-9PM)':
            self.start = 9
            self.end = 21
        elif string == '' or string.strip() == 'Unavailable':
            return
        else:
            startEnd = string.split('-')
            self.start = self.to24(startEnd[0])
            self.end = self.to24(startEnd[1])
    
    def duration(self):
        """Get slot duration in hours"""
        return max(0, self.end - self.start)
    
    def isAllDay(self):
        """Check if this is an all-day slot"""
        return self.start == 9 and self.end == 21
    
    def isAdjacent(self, other):
        """Check if two slots are adjacent (no gap)"""
        return self.start == other.end or self.end == other.start
    
    def isWithin1Hour(self, other):
        """Check if two slots are within 1 hour of each other"""
        gap_start = min(self.end, other.end)
        gap_end = max(self.start, other.start)
        gap = gap_end - gap_start
        return 0 <= gap <= 1
    
    def canMergeWith(self, other, max_gap_hours=1):
        """Check if two slots can be merged with allowed gap"""
        return self.isWithin1Hour(other) and max_gap_hours >= 1
    
    def mergeWith(self, other):
        """Merge this slot with another (assuming they can be merged)"""
        if not self.canMergeWith(other):
            raise ValueError(f"Cannot merge slots {self} and {other} - gap > 1 hour")
        
        # Create merged slot that spans both slots
        merged = EnhancedSlot()
        merged.start = min(self.start, other.start)
        merged.end = max(self.end, other.end)
        return merged
    
    def getOverlap(self, other):
        """Get overlap between this slot and another"""
        overlap = EnhancedSlot()
        overlap.start = max(self.start, other.start)
        overlap.end = min(self.end, other.end)
        return overlap
    
    @staticmethod
    def combineSlots(daySlots, max_gap_hours=1, min_duration_hours=4):
        """
        Combine slots with 1-hour discontinuity tolerance
        
        Args:
            daySlots: String of comma-separated time slots
            max_gap_hours: Maximum gap allowed between slots for merging (default: 1)
            min_duration_hours: Minimum duration for final slots (default: 4)
        
        Returns:
            List of merged slots that meet minimum duration requirement
        """
        if not daySlots or daySlots.strip() == '' or daySlots.strip() == 'Unavailable':
            return []
        
        slots = []
        individualSlots = daySlots.split(',')
        
        # Parse individual slots
        parsed_slots = []
        for slot_str in individualSlots:
            slot_str = slot_str.strip()
            if slot_str:
                slot = EnhancedSlot(slot_str)
                
                # Handle All Day case
                if slot.isAllDay():
                    return [slot]
                
                parsed_slots.append(slot)
        
        if not parsed_slots:
            return []
        
        # Sort slots by start time
        parsed_slots.sort(key=lambda s: s.start)
        
        # Group slots by proximity (within max_gap_hours)
        slot_groups = []
        current_group = [parsed_slots[0]]
        
        for i in range(1, len(parsed_slots)):
            current_slot = parsed_slots[i]
            last_slot = current_group[-1]
            
            # Check if current slot is close enough to the last slot in the group
            gap_start = last_slot.end
            gap_end = current_slot.start
            gap = gap_end - gap_start
            
            if gap <= max_gap_hours:
                # Add to current group
                current_group.append(current_slot)
            else:
                # Start new group
                slot_groups.append(current_group)
                current_group = [current_slot]
        
        # Add the last group
        slot_groups.append(current_group)
        
        # Merge each group into a single slot
        merged_slots = []
        for group in slot_groups:
            if group:
                # Create merged slot that spans the entire group
                merged = EnhancedSlot()
                merged.start = min(s.start for s in group)
                merged.end = max(s.end for s in group)
                
                # Only include if meets minimum duration
                if merged.duration() >= min_duration_hours:
                    merged_slots.append(merged)
        
        return merged_slots
    
    @staticmethod
    def mergeGroup(slot_group, max_gap_hours=1):
        """Merge a group of slots into a single slot"""
        if not slot_group:
            return None
        
        if len(slot_group) == 1:
            return slot_group[0]
        
        # Sort by start time
        slot_group.sort(key=lambda s: s.start)
        
        # Create merged slot that spans the entire group
        merged = EnhancedSlot()
        merged.start = slot_group[0].start
        merged.end = slot_group[-1].end
        
        return merged
    
    @staticmethod
    def calculateTotalOverlap(slots1, slots2):
        """Calculate total overlap hours between two lists of slots"""
        total_hours = 0
        
        for slot1 in slots1:
            for slot2 in slots2:
                overlap = slot1.getOverlap(slot2)
                total_hours += overlap.duration()
        
        return total_hours

def test_enhanced_merging():
    """Test the enhanced merging logic"""
    print("=== TESTING ENHANCED SLOT MERGING ===")
    
    # Test case 1: Snail Bar Saturday (should be valid)
    snail_saturday = "10AM-11AM, 11AM-12PM, 12PM-1PM, 2PM-3PM, 3PM-4PM, 4PM-5PM, 5PM-6PM"
    merged = EnhancedSlot.combineSlots(snail_saturday, max_gap_hours=1, min_duration_hours=4)
    
    print(f"Snail Bar Saturday: {snail_saturday}")
    print(f"Merged slots: {[str(s) for s in merged]}")
    print(f"Total duration: {sum(s.duration() for s in merged)} hours")
    
    # Test case 2: Snail Bar with 2-hour gap (should be invalid)
    snail_with_gap = "10AM-11AM, 11AM-12PM, 12PM-1PM, 3PM-4PM, 4PM-5PM, 5PM-6PM"
    merged_gap = EnhancedSlot.combineSlots(snail_with_gap, max_gap_hours=1, min_duration_hours=4)
    
    print(f"\nSnail Bar with 2-hour gap: {snail_with_gap}")
    print(f"Merged slots: {[str(s) for s in merged_gap]}")
    print(f"Total duration: {sum(s.duration() for s in merged_gap)} hours")
    
    # Test case 3: Ollie's availability
    ollie_saturday = "All Day (9AM-9PM)"
    ollie_merged = EnhancedSlot.combineSlots(ollie_saturday, max_gap_hours=1, min_duration_hours=4)
    
    print(f"\nOllie Saturday: {ollie_saturday}")
    print(f"Merged slots: {[str(s) for s in ollie_merged]}")
    
    # Test overlap calculation
    if merged and ollie_merged:
        total_overlap = EnhancedSlot.calculateTotalOverlap(ollie_merged, merged)
        print(f"Total overlap: {total_overlap} hours")

if __name__ == "__main__":
    test_enhanced_merging()
