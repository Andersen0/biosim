# -*- coding: utf-8 -*-

"""
Island controls all the cells on the map through an annual cycle.
"""

__author__ = 'Tage Andersen, Olav Vikøren Espenes'
__email__ = 'tage.andersen@nmbu.no, olaves@nmbu.no'

import textwrap
import random
import numpy as np
import collections
import itertools

from biosim.cell import Water, Lowland, Highland, Desert


class Island:
    """
    Island contains all the instances of cells that are created by the input string map. The
    "communication" between the various cells and the movement of animals in connection with
    migration takes place in Island. Here is also the method that is called when an annual cycle on
    Rossumøya is carried out.
    """
    def __init__(self, map_as_string):
        """
        The constructor in Island that allows a instance of a an Island to initialize the
        attributes of the class. The map with Cell instances is also created through creating_map
         method based on the input string at the same time a Island instance is created.
        :param map_as_string: string containing letters representing landscape types.
        """
        self.island_map = None
        self.creating_map(map_as_string)

    def creating_map(self, map_as_string):
        """
        Method that creates a 2d numpy.vdarray based on the input map string. The correct instance
        of the cell is called and ValueError is raised if an element in the input string is
        incorrect.
        :param map_as_string: string with letter codes for landscape types
        :return: numpy.ndarray
        """
        map_as_string = textwrap.dedent(map_as_string)
        self.check_input_map_string(map_as_string)
        split_map = map_as_string.split('\n')
        reformat_map = []
        for line in split_map:
            reformat_map.append(line.strip())

        rows = len(split_map)
        cols = len(reformat_map[0])

        self.island_map = np.empty((rows, cols)).astype(object)
        for n, line in enumerate(reformat_map):
            for m, char in enumerate(line):
                if char == 'W':
                    self.island_map[n, m] = Water()
                elif char == 'L':
                    self.island_map[n, m] = Lowland()
                elif char == 'H':
                    self.island_map[n, m] = Highland()
                elif char == 'D':
                    self.island_map[n, m] = Desert()
                else:
                    raise ValueError('Input "map_as_string" contains one or more symbols that are '
                                     'not approved. "map_as_string" must only consist of "W" and '
                                     '"H", "L" and / or "D"')
        return self.island_map

    @staticmethod
    def check_input_map_string(map_as_string):
        """
        Raises ValueError if the string input is not a valid landscape type. Edges
        must of the island must be water. Letters in string must be of a correct landscape type.
        Controls that all rows must have the same length.
        """
        rows = map_as_string.split('\n')
        for row in itertools.chain(rows[0], rows[-1]):
            if row != 'W':
                raise ValueError('All the edges of the island map string must be "W" (Water)')
        for a_cell in rows:
            if a_cell[0] != 'W':
                raise ValueError('All the edges of the island map string must be "W" (Water)')
            elif a_cell[-1] != 'W':
                raise ValueError('All the edges of the island map string must be "W" (Water)')

        num_cells_first_row = len(rows[0])
        for ind, val in enumerate(rows):
            if len(rows[ind]) != num_cells_first_row:
                raise ValueError('Input string must be the same length on all rows.')

    def place_populations_on_island(self, population_list):
        """
        Method takes a list of dictionaries with lists of animals in a cell and please them in the
        correct place on the island.
        :param population_list: list of dictionaries
        """
        for cell_location in population_list:
            row = cell_location['loc'][0] - 1
            col = cell_location['loc'][1] - 1

            self.island_map[row, col].add_new_population(cell_location['pop'])

    @staticmethod
    def get_neighbors_to_cell(a_cell):
        """
        Staticmethod used to get the neighbors to the cell in input. The method is called in
        migration().
        """
        neighbors = [[a_cell[0] - 1, a_cell[1]],  # North
                     [a_cell[0], a_cell[1] + 1],  # East
                     [a_cell[0] + 1, a_cell[1]],  # South
                     [a_cell[0], a_cell[1] - 1]]  # West
        return neighbors

    def migration(self):
        """
        The method that takes care of the migration of animals between the cells. Goes through each
        cell and find the animals that will migrate. Finds the neighboring cells of the cell and
        then goes through all the animals to see if they move to a randomly selected cell or not.
        If the randomly selected cell is of the Water type, the animal does not migrate.
        """
        for row in self.island_map:
            for a_cell in row:
                n, m = np.where(self.island_map == a_cell)
                cell_loc = np.concatenate((n, m))
                neighbor_cells = self.get_neighbors_to_cell(cell_loc)
                animal_migrating = a_cell.migrating_or_not()
                for animal in animal_migrating:
                    chosen_cell = random.choice(neighbor_cells)
                    current_migration_cell = self.island_map[chosen_cell[0], chosen_cell[1]]
                    if current_migration_cell.hospitable is True:
                        a_cell.mark_as_migrated(animal)
                        current_migration_cell.add_immigrating_animal(animal)
                        a_cell.remove_emigrated_animal(animal)
                    else:
                        continue

    def annual_cycle(self):
        """
        The annual cycle for the island where all methods associated with this are called on in the
        correct order.
        """
        for row in self.island_map:
            for a_cell in row:
                a_cell.herbivores_eating()  # <--- Eating funksjon kan være en ide
                a_cell.carnivores_eating()  #
                a_cell.procreation_herbivore()  # <--- Procreation funksjon kan være en ide
                a_cell.procreation_carnivore()  #
        self.migration()
        for row in self.island_map:
            for a_cell in row:
                a_cell.yearly_ageing_and_weight_loss()
                a_cell.yearly_death()
                a_cell.reset_migrated_parameter()
                a_cell.fodder_regrowth()

    def animal_counter(self):
        """
        The method counts the number of animals per species in each cell and returns this in two
        numpy.ndarrey. The number of rows and columns on the island is also returned.
        :return: two numpy.ndarray, two integers
        """
        pop_herbivores_per_cell = np.full_like(self.island_map, int(0))
        pop_carnivores_per_cell = np.full_like(self.island_map, int(0))
        rows = self.island_map.shape[0]
        cols = self.island_map.shape[1]
        for row in self.island_map:
            for a_cell in row:
                n, m = np.where(self.island_map == a_cell)
                pop_herbivores_per_cell[n, m] = int(a_cell.number_of_herbivores())
                pop_carnivores_per_cell[n, m] = int(a_cell.number_of_carnivores())

        return pop_herbivores_per_cell, pop_carnivores_per_cell, rows, cols

    def get_weight_age_fitness(self, animal_property):
        """
        Method used for making histograms in simulation.py file. Based on input the method returns
        either fitness, age or weight for both herbivores and carnivores on the entire island.
        :param animal_property: string: 'weight', 'age' or 'fitness'
        :return: dictionary with keys 'Herbivore' and 'Carnivore'
        """
        weight = collections.defaultdict(list)
        age = collections.defaultdict(list)
        fitness = collections.defaultdict(list)
        for row in self.island_map:
            for a_cell in row:
                for animal in itertools.chain(a_cell.pop_herbivores, a_cell.pop_carnivores):
                    if animal.species == 'Herbivore':
                        weight['Herbivore'].append(animal.get_weight())
                        age['Herbivore'].append(animal.get_age())
                        fitness['Herbivore'].append(animal.get_fitness())
                    elif animal.species == 'Carnivore':
                        weight['Carnivore'].append(animal.get_weight())
                        age['Carnivore'].append(animal.get_age())
                        fitness['Carnivore'].append(animal.get_fitness())
        if animal_property == 'weight':
            return weight
        elif animal_property == 'age':
            return age
        elif animal_property == 'fitness':
            return fitness
        else:
            raise ValueError('Input parameter "animal_property" must be a string named <weight>, '
                             '<age> or <fitness>')

    def get_birth_and_death(self, animal_property):
        """
        Used to create birth / death plot in simulation.py. Based on string input, the method
        returns two lists with the number of births / deaths per cell for both herbivores and
        carnivores.
        :param animal_property: string: 'birth' or 'death'
        :return: two lists
        """
        herbivore_tot = 0
        carnivore_tot = 0
        for row in self.island_map:
            for a_cell in row:
                if animal_property == 'birth':
                    herbivore_tot += a_cell.num_newborns['Herbivore']
                    carnivore_tot += a_cell.num_newborns['Carnivore']
                elif animal_property == 'death':
                    herbivore_tot += a_cell.num_deaths['Herbivore']
                    carnivore_tot += a_cell.num_deaths['Carnivore']
                else:
                    raise ValueError('Input "animal_property" must be either "birth" or "death"')
        return herbivore_tot, carnivore_tot
