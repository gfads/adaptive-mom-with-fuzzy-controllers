import math
import sys
from utils.core_functions import logging_pc_changes

class HPA:
    def __init__(self, max_value, min_value):
        self.max_value = max_value
        self.min_value = min_value

    def evaluate_new_prefetch_count(self, current_prefetch_count, arrival_rate, setpoint):
        error_value = setpoint - arrival_rate

        new_prefetch_count = current_prefetch_count * setpoint / arrival_rate
        new_prefetch_count = round(new_prefetch_count)
 
        if new_prefetch_count < self.min_value:
            new_prefetch_count = self.min_value
        elif new_prefetch_count > self.max_value:
            new_prefetch_count = self.max_value

        logging_pc_changes(setpoint, arrival_rate,
                           error_value, current_prefetch_count, new_prefetch_count)

        return new_prefetch_count
