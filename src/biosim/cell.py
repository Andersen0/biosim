# -*- coding: utf-8 -*-

"""
Cell does anything that happens inn a landscape cell.
"""

__author__ = 'Tage Andersen, Olav Vikøren Espenes'
__email__ = 'tage.andersen@nmbu.no, olaves@nmbu.no'

import random
import itertools

from biosim.fauna import Herbivore
from biosim.fauna import Carnivore


class Cell:
    """
    This class contains methods for everything that happens in a given cell on the map. An instance
    of Cell is of a landscape type Water, Lowland, Highland or Desert which contains a population
    of herbivores and carnivores (not Water). The class also takes care of which animals are to
    migrate, and adds/removes animals that immigrate/emigrate.
    """
    landscape_param = {'f_max': None}

    @classmethod
    def set_parameters(cls, custom_parameters):
        """
        Class method that allows the user to set their own landscape parameters, such as choosing
        how much fodder to grow for each year.
        :param custom_parameters: dictionary with correct parameter key
        """
        accepted_param_keys = ['f_max']

        for key in custom_parameters:
            if key not in accepted_param_keys:
                raise ValueError(f'{key} is not a valid parameter key')
            elif custom_parameters[key] < 0:
                raise ValueError('All parameter keys must have a non negative value')
            else:
                cls.landscape_param[key] = custom_parameters[key]

    def __init__(self, landscape=None):
        """
        The constructor in Cell that allows a instance of a landscape type to initialize the
        attributes of the class.
        :param landscape: Cells type represented as a one character string
        """
        self.landscape = landscape
        self.pop_herbivores = []
        self.pop_carnivores = []
        self.num_newborns = {'Herbivore': 0, 'Carnivore': 0}
        self.num_deaths = {'Herbivore': 0, 'Carnivore': 0}
        self.fodder = self.landscape_param['f_max']

    def number_of_herbivores(self):
        """
        :return: int: The total number of herbivores in the cell
        """
        return len(self.pop_herbivores)

    def number_of_carnivores(self):
        """
        :return: int: The total number of carnivores in the cell
        """
        return len(self.pop_carnivores)

    def number_of_animals(self):
        """
        :return: int: The total number of animals in the cell
        """
        return len(self.pop_herbivores + self.pop_carnivores)

    def population_in_cell(self):
        """
        :return: list that contains all the animals in the cell
        """
        return self.pop_herbivores + self.pop_carnivores

    @staticmethod
    def mark_as_migrated(animal):
        """
        Method used when an animal has migrated to set the "migrated" parameter to True for the
        animal. Acts as a link between Fauna class and Island class.
        :param animal: instance of animal
        :return: same animal instance with migrated = True
        """
        animal.migrated = True
        return animal

    @staticmethod
    def sort_by_fitness(population, method):
        """
        Sorting list of input animals by their fitness. Sorting method is required to sort the
        animals in the correct order.
        :param population: list of animal instances
        :param method: str ("high-low" or "low-high")
        :return: sorted population list
        """
        if method == 'high-low':
            reverse_parameter = True
        elif method == 'low-high':
            reverse_parameter = False
        else:
            raise ValueError('method-input must be string <high-low> or <low-high>')

        for animal in population:
            animal.get_fitness()
        population.sort(key=lambda a_animal: a_animal.fitness, reverse=reverse_parameter)
        return population

    def add_new_population(self, population):
        """
        When a new population, which not have been placed on the map before (not instances yet),
        are added to the cell this method is called. The method checks the "species" key, creates
        either an herbivore or carnivore instance, and places it in its respective list.
        :param population: list of dictionaries
        """
        for animal in population:
            if animal['species'] == 'Herbivore':
                herbivore_instance = Herbivore(age=animal['age'],
                                               weight=animal['weight'])
                self.pop_herbivores.append(herbivore_instance)
            elif animal['species'] == 'Carnivore':
                carnivore_instance = Carnivore(age=animal['age'],
                                               weight=animal['weight'])
                self.pop_carnivores.append(carnivore_instance)
            else:
                raise ValueError('Key "species" must have value "Herbivore" or "Carnivore"')

    def add_immigrating_animal(self, immigrant):
        """
        Adds animal that have emigrated to the cell in its respective population list. Checks the
        type of instance the animal is to add it to the correct list.
        :param immigrant: animal instance
        """
        if immigrant.species == 'Herbivore':
            self.pop_herbivores.append(immigrant)
        elif immigrant.species == 'Carnivore':
            self.pop_carnivores.append(immigrant)
        else:
            raise ValueError('Input should only be a instance of Herbivore or Carnivore.')

    def remove_emigrated_animal(self, emigrant):
        """
        Removes emigrated animal from its respective list. Works like add_immigrated_animal, but
        removes the animal instead of adding it.
        :param emigrant: animal instance
        """
        if emigrant.species == 'Herbivore':
            if emigrant in self.pop_herbivores:
                self.pop_herbivores.remove(emigrant)
            else:
                raise ValueError('This herbivore instance is not in the s population list')
        elif emigrant.species == 'Carnivore':
            if emigrant in self.pop_carnivores:
                self.pop_carnivores.remove(emigrant)
            else:
                raise ValueError('This carnivore instance is not in the carnivores population list')
        else:
            raise ValueError('Input should only be of a instance of Herbivore or Carnivore.')

    def herbivores_eating(self):
        """
        Method for herbivores that are allowed to eat in a cell based on available food.
        The eating order is randomly sorted among all herbivores in advance, regardless of weight
        and age.
        """
        random.shuffle(self.pop_herbivores)
        for animal in self.pop_herbivores:
            if self.fodder >= animal.param['F']:
                animal.eating(animal.param['F'])
                self.fodder -= animal.param['F']
            else:
                animal.eating(self.fodder)
                self.fodder = 0
                break

    def carnivores_eating(self):
        """
        Feeding of carnivores in a cell. The carnivores with the highest fitness eat first, and go
        after herbivores from worst to best fitness. The list of herbivores is updated, as well as
        the weight of the carnivore who is given the opportunity to eat.
        """
        self.sort_by_fitness(self.pop_herbivores, method='low-high')
        self.sort_by_fitness(self.pop_carnivores, method='high-low')
        for animal in self.pop_carnivores:
            not_eaten_herbivores = animal.eat(self.pop_herbivores)
            self.pop_herbivores = not_eaten_herbivores

    def procreation_herbivore(self):
        """
        In this method, all herbivores in the cell try to give birth if the conditions are right.
        Calls the birth method in the Fauna class. Newborns become an instance of Herbivore and are
        added to the list of herbivores in the cell.
        """
        all_newborn_herbivores = []
        for herbivore in self.pop_herbivores:
            birth_check = herbivore.birth(self.number_of_herbivores())
            if birth_check is None:
                continue
            else:
                newborn_weight = birth_check
                newborn_herbivore = Herbivore(weight=newborn_weight)
                all_newborn_herbivores.append(newborn_herbivore)
        self.pop_herbivores.extend(all_newborn_herbivores)
        self.num_newborns['Herbivore'] = len(all_newborn_herbivores)

    def procreation_carnivore(self):
        """
        Same method as procreation_herbivore except that here it is carnivores that give birth. New
        carnivores are added to the total list of carnivores in the cell.
        """
        all_newborn_carnivores = []
        for carnivore in self.pop_carnivores:
            birth_check = carnivore.birth(self.number_of_carnivores())
            if birth_check is None:
                continue
            else:
                newborn_weight = birth_check
                newborn_carnivore = Carnivore(weight=newborn_weight)
                all_newborn_carnivores.append(newborn_carnivore)
        self.pop_carnivores.extend(all_newborn_carnivores)
        self.num_newborns['Carnivore'] = len(all_newborn_carnivores)

    def migrating_or_not(self):
        """
        Method that goes through all the animals in the cell, checks if the animals have migrated
        before the same year, and if not then it is checked if the animal has the opportunity to
        migrate. The method returns a list of all animals that are ready to migrate.
        :return animals_migrating: list with migrating animals
        """
        animals_migrating = []
        for animal in self.population_in_cell():
            if animal.migrated is False:
                migrating_probability = animal.param['mu']*animal.get_fitness()
                migrating_threshold = random.random()
                if migrating_probability > migrating_threshold:
                    animals_migrating.append(animal)
        return animals_migrating

    def yearly_ageing_and_weight_loss(self):
        """
        Method called every year when all the animals in the cell are to age and lose weight.
        """
        for animal in itertools.chain(self.pop_herbivores, self.pop_carnivores):
            animal.ageing()
            animal.weight_loss()

    def yearly_death(self):
        """
        Checks if an animal dies or not at the end of an annual cycle. If the animal dies, it is
        removed from its respective population list.
        """
        dead_herbivores = []
        dead_carnivores = []
        self.num_deaths['Herbivore'] = 0
        self.num_deaths['Carnivore'] = 0
        for animal in itertools.chain(self.pop_herbivores, self.pop_carnivores):
            animal.get_fitness()
            if animal.death() is True:
                if animal.species == 'Herbivore':
                    dead_herbivores.append(animal)
                    self.num_deaths['Herbivore'] += 1
                elif animal.species == 'Carnivore':
                    dead_carnivores.append(animal)
                    self.num_deaths['Carnivore'] += 1
                else:
                    raise ValueError('There are one or more animals in the cell population that '
                                     'are not instances of "Herbivore" or "Carnivore"')
        for animal in dead_herbivores:
            if animal in self.pop_herbivores:
                self.pop_herbivores.remove(animal)
        for animal in dead_carnivores:
            if animal in self.pop_carnivores:
                self.pop_carnivores.remove(animal)

    def reset_migrated_parameter(self):
        """
        Set "migrated" parameter to False in the end of the year
        """
        for animal in itertools.chain(self.pop_herbivores, self.pop_carnivores):
            animal.migrated = False

    def fodder_regrowth(self):
        """
        Sets "fodder" to maximum level as specified in the landscape parameters.
        :return:
        """
        self.fodder = self.landscape_param['f_max']


class Water(Cell):
    """
    Subclass of Cell that represents the areas that are "W" (water). Cells of this type are
    uninhabitable for animals and do not contain any fodder.
    """
    landscape_param = {'f_max': 0}

    def __init__(self, landscape='W'):
        self.hospitable = False
        super().__init__(landscape)


class Lowland(Cell):
    """
    Subclass of Cell that represents the areas that are "L" (lowland). Cells of this type are
    habitable for all animals and contain 800 fodder for herbivores as default.
    """
    landscape_param = {'f_max': 800}

    def __init__(self, landscape='L'):
        super().__init__(landscape)
        self.hospitable = True


class Highland(Cell):
    """
    Subclass of Cell that represents the areas that are "H" (highland). Cells of this type are
    habitable for all animals, but generally contains less fodder than lowland. Highland contain
    300 fodder for herbivores as default.
    """
    landscape_param = {'f_max': 300}

    def __init__(self, landscape='H'):
        super().__init__(landscape)
        self.hospitable = True


class Desert(Cell):
    """
    Subclass of Cell that represents the areas that are "D" (desert). Cells of this type are
    habitable for all animals, but contains no food for herbivores. Fodder are therefore set to 0
    as the default value for desert.
    """
    landscape_param = {'f_max': 0}

    def __init__(self, landscape='D'):
        super().__init__(landscape)
        self.hospitable = True
