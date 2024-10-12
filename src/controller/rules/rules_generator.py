from controller.rules.const import INITIAL_POPULATION
from controller.fuzzy.fuzzy_controller import FuzzyController
from collections import Counter
import random
import sys
import math
import numpy as np
import pandas as pd

sys.path.append('/home/matheus/Documentos/GIT/FuzzyLogicExp/subscriber/src')


class GeneticAlgorithm:
    @staticmethod
    def top_selection(population, fitness_scores, num_select=5):
        # Sort the population based on fitness scores in ascending order
        sorted_population = [x for _, x in sorted(zip(fitness_scores, population))]
        # Select the top individuals with the smallest fitness scores
        return sorted_population[:num_select]


    @staticmethod
    def crossover_multiple(parents):
        if not all(len(parents[0]) == len(parent) for parent in parents):
            raise ValueError("All parent rule sets must have the same length")

        offspring1 = []
        offspring2 = []
        length = len(parents[0])

        for i in range(length):
            # Collect the ith property of each parent
            properties = [parent[i] for parent in parents]
            # Find the most common and the second most common properties
            most_common_properties = Counter(properties).most_common(2)
            most_common_property = most_common_properties[0][0]
            second_most_common_property = most_common_properties[1][0] if len(most_common_properties) > 1 else most_common_property

            offspring1.append(most_common_property)
            offspring2.append(second_most_common_property)

        return offspring1, offspring2
    

    @staticmethod
    def crossover(parent1, parent2):
        # Ensure the parents have the same length
        if len(parent1) != len(parent2):
            raise ValueError("Parent rule sets must have the same length")

        # Choose a random crossover point
        crossover_point = random.randint(1, len(parent1) - 1)

        # Create offspring by combining rules from parents at the crossover point
        offspring1 = parent1[:crossover_point] + parent2[crossover_point:]
        offspring2 = parent2[:crossover_point] + parent1[crossover_point:]

        return offspring1, offspring2

    @staticmethod
    def roulette_wheel_selection(population, fitness_scores):
        total_fitness = sum(fitness_scores)
        selection_probs = [f / total_fitness for f in fitness_scores]

        # Generate cumulative probabilities
        cumulative_probs = []
        cumulative_sum = 0.0
        for prob in selection_probs:
            cumulative_sum += prob
            cumulative_probs.append(cumulative_sum)

        def select_one():
            r = random.random()
            for i, cum_prob in enumerate(cumulative_probs):
                if r <= cum_prob:
                    return population[i]

        # Select two parents
        parent1 = select_one()
        parent2 = select_one()

        return parent1, parent2

    @staticmethod
    def mutate(parent, mutation_rate):
        pca_labels = ['higher_decrease', 'medium_decrease', 'small_decrease',
                      'zero', 'small_increase', 'medium_increase', 'higher_increase']
        mutated = parent.copy()
        for i in range(len(mutated)):
            if random.random() < mutation_rate:
                antecedent, consequent = mutated[i].split(' THEN ')
                error_level = antecedent.split('= ')[1].strip()
                pca_level = consequent.split('= ')[1].strip()
                error_index = ['negative_large', 'negative_medium', 'negative_small', 'zero',
                               'positive_small', 'positive_medium', 'positive_large'].index(error_level)
                pca_index = pca_labels.index(pca_level)
                error_index = (error_index + random.randint(-1, 1)) % 7
                pca_index = (pca_index + random.randint(-1, 1)) % 7
                mutated[i] = f"IF ERROR = {error_level} THEN PCA = {pca_labels[pca_index]}"
        return mutated

    @staticmethod
    def calculate_fitness_from_df(rule_set, df, df_reference, lower_bound, upper_bound, setpoints):
        total_nrmse = 0

        for setpoint in setpoints:
            df['error'] = df['arrival_rate'] - setpoint
            controller = FuzzyController(setpoint)
            controller.update_rules(rule_set)

            # Extract necessary data from DataFrame as NumPy arrays
            errors = df['error'].values
            prefetch_counts = df['prefetch_count'].values
            df_reference_arrival_rate = df_reference['arrival_rate'].values
            df_reference_prefetch_count = df_reference.index.values

            # Simulate controller output and calculate new prefetch counts
            controller_outputs = controller.simulate(errors)
            new_prefetch_counts = np.clip(
                np.round(controller_outputs + prefetch_counts), lower_bound, upper_bound)

            # Interpolate new arrival rates
            new_arrival_rates = np.interp(
                new_prefetch_counts, df_reference_prefetch_count, df_reference_arrival_rate)

            # Calculate deviations and MSE
            deviations = new_arrival_rates - setpoint
            mse = np.mean(deviations ** 2)

            # Calculate RMSE and NRMSE
            rmse = np.sqrt(mse)
            max_arrival_rate = np.max(df_reference_arrival_rate)
            min_arrival_rate = np.min(df_reference_arrival_rate)
            nrmse = rmse / (max_arrival_rate - min_arrival_rate)

            total_nrmse += nrmse

        # Average NRMSE over all setpoints
        average_nrmse = total_nrmse / len(setpoints)
        return average_nrmse

    def improve_rules(self, setpoints=[2000, 3000, 4000]):
        df = pd.read_csv('results.csv')
        df_reference = df.groupby('prefetch_count').mean().drop(
            columns=['sample_number', 'setpoint'])
        lower_bound = df['prefetch_count'].min()
        upper_bound = df['prefetch_count'].max()

        initial_population = INITIAL_POPULATION
        best_fitness = math.inf
        best_rule_set = []
        has_been_changed = False
        i = 0

        for generation in range(100):
            # Calculate the fitness of each individual in the population
            fitness_scores = []
            for rule_set in initial_population:
                fitness = self.calculate_fitness_from_df(
                    rule_set, df, df_reference, lower_bound, upper_bound, setpoints)
                fitness_scores.append(fitness)

            # Find the best individual in the population
            best_index = np.argmin(fitness_scores)
            best_rule_set = initial_population[best_index]
            has_been_changed = best_fitness != fitness_scores[best_index]
            best_fitness = fitness_scores[best_index]

            # Check if the best fitness is less than 0.2 or fitness no changed in past 10 generations
            if (best_fitness < 0.2) or (not has_been_changed and i == 10):
                return best_rule_set

            # Select parents for crossover
            top_individuals = self.top_selection(initial_population, fitness_scores)

            # Perform crossover to generate offspring
            offspring1, offspring2 = self.crossover_multiple(top_individuals)

            # Mutate the offspring
            offspring1 = self.mutate(offspring1, 0.5)
            offspring2 = self.mutate(offspring2, 0.5)

            # Replace the worst individuals in the population with the offspring
            worst_index = np.argmax(fitness_scores)
            initial_population[worst_index] = offspring1
            worst_index = np.argmax(fitness_scores)
            initial_population[worst_index] = offspring2
            if has_been_changed:
                i = 0
            else:
                i += 1

            print(f"Generation {generation}: Best Fitness = {best_fitness}")

        return best_rule_set
