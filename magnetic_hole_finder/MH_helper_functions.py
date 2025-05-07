#file: MH_helper_functions.py

from datetime import datetime, timedelta
import pandas as pd



current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print(f'{current_time} - 🧲 MH Helpers initialized')