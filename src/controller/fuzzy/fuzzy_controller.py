import math
from utils.core_functions import logging_pc_changes
from controller.fuzzy.sigma_optimization import estimate_best_sigma
import sys
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


class FuzzyController:
    def __init__(self, type: int, defuzzification_method: str = 'centroid'):
        """
        Define the fuzzy variables and membership functions.
        The error is the input variable, and the prefetch count adjustment (pca) is the output variable.
        """
        self.error = ctrl.Antecedent(np.arange(-2500, 2500, 1), 'error')
        self.pca = ctrl.Consequent(np.arange(-6, 6, 1), 'pca')
        self.pca.defuzzify_method = defuzzification_method
        self.fuzzy_number = type
        
        if self.fuzzy_number == 1:
            self.error['negative_large'] = fuzz.trimf(self.error.universe, [-2500, -2500, -1500])
            self.error['negative_medium'] = fuzz.trimf(self.error.universe, [-2500, -1500, -500])
            self.error['negative_small'] = fuzz.trimf(self.error.universe, [-1500, -500, 0])
            self.error['zero'] = fuzz.trimf(self.error.universe, [-500, 0, 500])
            self.error['positive_small'] = fuzz.trimf(self.error.universe, [0, 500, 1500])
            self.error['positive_medium'] = fuzz.trimf(self.error.universe, [500, 1500, 2500])
            self.error['positive_large'] = fuzz.trimf(self.error.universe, [1500, 2500, 2500])
        elif self.fuzzy_number == 2:
            self.error['negative_large'] = fuzz.gaussmf(self.error.universe, -2500, 500)
            self.error['negative_medium'] = fuzz.gaussmf(self.error.universe, -1500, 400)
            self.error['negative_small'] = fuzz.gaussmf(self.error.universe, -500, 300)
            self.error['zero'] = fuzz.gaussmf(self.error.universe, 0, 150)
            self.error['positive_small'] = fuzz.gaussmf(self.error.universe, 500, 300)
            self.error['positive_medium'] = fuzz.gaussmf(self.error.universe, 1500, 400)
            self.error['positive_large'] = fuzz.gaussmf(self.error.universe, 2500, 500)
        elif self.fuzzy_number == 3:
            # Labels of each error
            error_labels = [
                'negative_large',
                'negative_medium',
                'negative_small',
                'zero',
                'positive_small',
                'positive_medium',
                'positive_large'
            ]
            estimated_mean_values = estimate_best_sigma()
            sigma_values = [500, 400, 300, 150, 300, 400, 500]
            # Iterate over both error_labels and estimated_sigma_values in parallel
            for label, estimated_values, sigma in zip(error_labels, estimated_mean_values, sigma_values):
                optimized_mean = estimated_values[0]
                optimized_sigma = sigma
                print(f"Best mu = {optimized_mean}. Best sigma = {optimized_sigma}.")
                self.error[label] = fuzz.gaussmf(self.error.universe, optimized_mean, optimized_sigma)
        elif self.fuzzy_number == 4:
            # Bell-shaped membership functions (gbellmf)
            self.error['negative_large'] = fuzz.gbellmf(self.error.universe, 500, 2, -2500)
            self.error['negative_medium'] = fuzz.gbellmf(self.error.universe, 400, 2, -1500)
            self.error['negative_small'] = fuzz.gbellmf(self.error.universe, 300, 2, -500)
            self.error['zero'] = fuzz.gbellmf(self.error.universe, 150, 2, 0)
            self.error['positive_small'] = fuzz.gbellmf(self.error.universe, 300, 2, 500)
            self.error['positive_medium'] = fuzz.gbellmf(self.error.universe, 400, 2, 1500)
            self.error['positive_large'] = fuzz.gbellmf(self.error.universe, 500, 2, 2500)
        elif self.fuzzy_number == 5:
            # Pi-shaped membership functions (pimf)
            self.error['negative_large'] = fuzz.pimf(self.error.universe, -2500, -2000, -1500, -1000)
            self.error['negative_medium'] = fuzz.pimf(self.error.universe, -2000, -1500, -1000, -500)
            self.error['negative_small'] = fuzz.pimf(self.error.universe, -1000, -500, 0, 500)
            self.error['zero'] = fuzz.pimf(self.error.universe, -100, 0, 0, 100)
            self.error['positive_small'] = fuzz.pimf(self.error.universe, 0, 500, 1000, 1500)
            self.error['positive_medium'] = fuzz.pimf(self.error.universe, 500, 1000, 1500, 2000)
            self.error['positive_large'] = fuzz.pimf(self.error.universe, 1000, 1500, 2000, 2500)
        elif self.fuzzy_number == 6:
            # Sigmoidal membership functions (sigmf)
            self.error['negative_large'] = fuzz.sigmf(self.error.universe, -2500, -0.001)
            self.error['negative_medium'] = fuzz.sigmf(self.error.universe, -1500, -0.001)
            self.error['negative_small'] = fuzz.sigmf(self.error.universe, -500, -0.001)
            self.error['zero'] = fuzz.sigmf(self.error.universe, 0, -0.05)  
            self.error['positive_small'] = fuzz.sigmf(self.error.universe, 500, 0.001)
            self.error['positive_medium'] = fuzz.sigmf(self.error.universe, 1500, 0.001)
            self.error['positive_large'] = fuzz.sigmf(self.error.universe, 2500, 0.001)
        elif self.fuzzy_number == 7:
            # Z-shaped membership functions (zmf)
            self.error['negative_large'] = fuzz.zmf(self.error.universe, -2500, -1500)
            self.error['negative_medium'] = fuzz.zmf(self.error.universe, -1500, -500)
            self.error['negative_small'] = fuzz.zmf(self.error.universe, -500, 0)
            self.error['zero'] = fuzz.zmf(self.error.universe, -500, 500)
            self.error['positive_small'] = fuzz.zmf(self.error.universe, 0, 500)
            self.error['positive_medium'] = fuzz.zmf(self.error.universe, 500, 1500)
            self.error['positive_large'] = fuzz.zmf(self.error.universe, 1500, 2500)        

        # Define the membership functions for prefetch count adjustment (pca)
        self.pca['higher_decrease'] = fuzz.trimf(self.pca.universe, [-6, -5, -4])
        self.pca['medium_decrease'] = fuzz.trimf(self.pca.universe, [-4, -3, -2])
        self.pca['small_decrease'] = fuzz.trimf(self.pca.universe, [-3, -2, -1])
        self.pca['zero'] = fuzz.trimf(self.pca.universe, [0, 0, 0])
        self.pca['small_increase'] = fuzz.trimf(self.pca.universe, [1, 2, 3])
        self.pca['medium_increase'] = fuzz.trimf(self.pca.universe, [2, 3, 4])
        self.pca['higher_increase'] = fuzz.trimf(self.pca.universe, [4, 5, 6])

        # Define the fuzzy rules based on error
        self.rule1 = ctrl.Rule(self.error['negative_large'], self.pca['higher_decrease'])
        self.rule2 = ctrl.Rule(self.error['negative_medium'], self.pca['medium_decrease'])
        self.rule3 = ctrl.Rule(self.error['negative_small'], self.pca['small_decrease'])
        self.rule4 = ctrl.Rule(self.error['zero'], self.pca['zero'])
        self.rule5 = ctrl.Rule(self.error['positive_small'], self.pca['small_increase'])
        self.rule6 = ctrl.Rule(self.error['positive_medium'], self.pca['medium_increase'])
        self.rule7 = ctrl.Rule(self.error['positive_large'], self.pca['higher_increase'])

        # Create the fuzzy system
        self.control_system = ctrl.ControlSystem(
            [self.rule1, self.rule2, self.rule3, self.rule4, self.rule5, self.rule6, self.rule7])
        self.controller = ctrl.ControlSystemSimulation(self.control_system)

    def evaluate_new_prefetch_count(self, current_prefetch, arrival_rate_value, setpoint):
        """
        The error is the difference between the setpoint and the current value of the arrival rate.
        - If the error is positive, it means that the arrival rate is lower than the setpoint, and PC must be increased.
        - Otherwise, the error negative means that the arrival rate is higher than the setpoint, and PC must be decreased.
        """
        error_value = round(setpoint - arrival_rate_value)
        print(f"Error: {error_value}")
        try:
            self.controller.input['error'] = error_value
            self.controller.compute()
            pca_adjustment = self.controller.output['pca']
        except ValueError as e:
            print(f"Failed to compute a new prefetch count for error: {error_value}")
            pca_adjustment = 0

        # Save logs to file
        new_prefetch_count = math.ceil(current_prefetch + pca_adjustment)
        new_prefetch_count = max(1, min(new_prefetch_count, 25))
        logging_pc_changes(setpoint, arrival_rate_value,
                           error_value, current_prefetch, new_prefetch_count)
        
        return new_prefetch_count

    def update_rules(self, rule_list):
        """
        Define fuzzy rules based on the given rule_list.
        Expected format: ['IF ERROR = negative_large THEN PCA = higher_decrease', ...]
        """
        self.control_system = None
        self.controller = None
        rules = []
        for rule in rule_list:
            antecedent, consequent = rule.split(' THEN ')
            error_level = antecedent.split('= ')[1].strip()
            pca_level = consequent.split('= ')[1].strip()
            rules.append(
                ctrl.Rule(self.error[error_level], self.pca[pca_level]))

        # Create the fuzzy control system
        self.control_system = ctrl.ControlSystem(rules)
        self.controller = ctrl.ControlSystemSimulation(self.control_system)

    def simulate(self, error_values):
        outputs = []
        for error in error_values:
            self.controller.input['error'] = error
            self.controller.compute()
            outputs.append(self.controller.output['pca'])
        return outputs
