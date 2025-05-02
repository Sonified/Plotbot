from datetime import datetime
from datetime import timedelta, time
from .print_manager import print_manager
from dateutil.parser import parse

def str_to_datetime(date_str):
    """
    Convert a string date/time to a datetime object using dateutil.parser.
    
    Parameters:
    date_str (str): Date/time string in any standard format
    
    Returns:
    datetime: A datetime object
    """
    try:
        return parse(date_str)
    except (ValueError, TypeError):
        print_manager.warning(f"Could not parse date string: {date_str}")
        return None

#====================================================================
# FUNCTION: daterange, Generates sequence of dates between two endpoints
#====================================================================
def daterange(start_date, end_date):
    """
    Yield dates between start_date and end_date, inclusive.
    If end_date has any hours/minutes/seconds, include that full day.
    If end_time is exactly at midnight, do not include that day.
    """
    print_manager.debug(f"daterange called with start_date={start_date}, end_date={end_date}")
    
    if isinstance(end_date, datetime):
        if (end_date.hour == 0 and end_date.minute == 0 and
            end_date.second == 0 and end_date.microsecond == 0):
            # Do not include the end date
            end_date = (end_date - timedelta(days=1)).date()
            print_manager.debug(f"End date is midnight, adjusting to previous day: {end_date}")
        else:
            # Include the end date
            end_date = end_date.date()
            print_manager.debug(f"End date has time component, using full day: {end_date}")
    
    if isinstance(start_date, datetime):
        start_date = start_date.date()
        print_manager.debug(f"Converted start_date to date: {start_date}")
    
    total_days = int((end_date - start_date).days + 1)
    print_manager.debug(f"Will generate {total_days} dates")
    
    for n in range(total_days):
        date = start_date + timedelta(n)
        print_manager.debug(f"Yielding date: {date}")
        yield date
        
def get_needed_6hour_blocks(start_time, end_time):
    """
    Generate a list of (date, block) tuples needed for 6-hour files.
    Each block is an integer from 0 to 3, representing hours 0-5, 6-11, 12-17, 18-23.
    """
    print_manager.debug(f"get_needed_6hour_blocks called with start_time={start_time}, end_time={end_time}")
    
    blocks = []
    # Round down start_time to nearest 6-hour block
    start_block_hour = (start_time.hour // 6) * 6
    print_manager.debug(f"Rounded start hour {start_time.hour} down to {start_block_hour}")
    
    # Make current_time timezone-aware to match end_time
    current_time = datetime.combine(start_time.date(), time(start_block_hour)).replace(tzinfo=start_time.tzinfo)
    print_manager.debug(f"Initial current_time: {current_time}")
    
    while current_time < end_time:
        current_date = current_time.date()
        block = current_time.hour // 6
        print_manager.debug(f"Adding block {block} for date {current_date}")
        blocks.append((current_date, block))
        current_time += timedelta(hours=6)
        print_manager.debug(f"Advanced to {current_time}")
    
    print_manager.debug(f"Returning {len(blocks)} blocks: {blocks}")
    return blocks