import math
import sys
from utils.core_functions import logging_pc_changes
sys.path.append('/home/matheus/Documentos/GIT/FuzzyLogicExp/subscriber/src')


class AsTAR:
    def __init__(self, max_value, min_value, hysteresis_band):
        self.max_value = max_value
        self.min_value = min_value
        self.hysteresis_band = hysteresis_band
        self.previous_rate = 0
        self.previous_output = 0
       
    def evaluate_new_prefetch_count(self, current_prefetch_count, arrival_rate, setpoint):
        error_value = setpoint - arrival_rate
        if arrival_rate < (setpoint - self.hysteresis_band):
            adjustment = 1 if arrival_rate > self.previous_rate else 2
            new_prefetch_count = self.previous_output + adjustment if arrival_rate > self.previous_rate else self.previous_output * adjustment
        elif arrival_rate > (setpoint + self.hysteresis_band):
            adjustment = -1 if arrival_rate < self.previous_rate else 0.5
            new_prefetch_count = self.previous_output + adjustment if arrival_rate < self.previous_rate else self.previous_output * adjustment
        else:
            new_prefetch_count = self.previous_output

        self.previous_rate = arrival_rate
        new_prefetch_count = min(max(new_prefetch_count, self.min_value), self.max_value)
        self.previous_output = new_prefetch_count
        
        logging_pc_changes(setpoint, arrival_rate,
                           error_value, current_prefetch_count, new_prefetch_count)
        
        return round(new_prefetch_count)
            
