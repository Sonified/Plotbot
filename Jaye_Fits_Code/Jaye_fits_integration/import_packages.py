

#🧹 Clean this up
# Standard libraries
import numpy as np
import numpy.ma as ma
from datetime import timezone, timedelta
from collections import defaultdict
import warnings

# Data handling and parsing
import cdflib
from dateutil.parser import parse
import pandas as pd
from datetime import datetime

# Scientific computing
from scipy import constants, interpolate, stats

# Plotting and visualization
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.dates as mdates
from matplotlib.colors import Normalize, TwoSlopeNorm
from matplotlib.dates import num2date


# Space physics specific libraries
import pyspedas
from pyspedas import tinterpol
from pytplot import get_data, split_vec, time_datetime, time_double, time_string, cdf_to_tplot, tplot_rename, divide, store_data

# Suppress warnings
warnings.filterwarnings("ignore")
from warnings import simplefilter 
simplefilter(action='ignore', category=DeprecationWarning)

import pickle

import hashlib
import json