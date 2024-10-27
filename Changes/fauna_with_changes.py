# -*- coding: utf-8 -*-

"""
Contains subclasses Herbivore and Carnivore which inherits the methods from the superclass
baseclass Fauna. All methods to change the characteristics for a herbivore- or carnivore-instance is
 to be found in fauna.py.
"""

__author__ = 'Tage Andersen, Olav Vikøren Espenes'
__email__ = 'tage.andersen@nmbu.no, olaves@nmbu.no'

import random
import math as m


class Fauna:
    """
    Baseclass with methods related to both herbivores and carnivores. Common methods for both
    species are weight, aging, birth, death and weight loss. The parameters are different and are defined in the
    subclasses.
    """
    param = {
        'w_birth': None,
        'sigma_birth': None,
        'beta': None,
        'eta': None,
        'a_half': None,
        'phi_age': None,
        'w_half': None,
        'phi_weight': None,
        'mu': None,
        'gamma': None,
        'zeta': None,
        'xi': None,
        'omega': None,
        'F': None,
        'DeltaPhiMax': None
        }

    @classmethod
    def set_parameters(cls, custom_parameters):
        """
        Classmethod that sets custom animal parameters for all instances of the class.
        :params: dict: custom parameters
        """

        accepted_param_keys = ['w_birth', 'sigma_birth', 'beta', 'eta',
                               'a_half', 'phi_age', 'w_half', 'phi_weight',
                               'mu', 'lambda', 'gamma', 'zeta',
                               'xi', 'omega', 'F', 'DeltaPhiMax']
        #--------#--------#--------#--------#--------#--------#--------#
        accepted_param_keys = cls.param.keys()  # <--- Unngår unødvendig repetisjon av keys.
        #--------#--------#--------#--------#--------#--------#--------#
        for key in custom_parameters:
            if key not in accepted_param_keys:
                raise ValueError(f'{key} is not a valid parameter key')
            elif custom_parameters[key] < 0:
                raise ValueError('All parameter keys must have a non negative value')
            elif custom_parameters[key] <= 0 and key == 'DeltaPhiMax':
                raise ValueError(f'{key} shall be strictly positive (>0)')
            elif custom_parameters[key] > 1 and key == 'eta':
                raise ValueError(f'{key} can not be higher than 1')
            else:
                cls.param[key] = custom_parameters[key]
        #--------#--------#--------#--------#--------#--------#--------#
        for key, value in custom_parameters.items():    # <--- Bedre metode for denne typen dictionary iterasjon.      
            if key not in accepted_param_keys:
                raise KeyError(f'{key} is not a valid parameter key')   # <--- KeyError er mer korrekt enn ValueError
            if value < 0:
                raise ValueError(f'Value for {key} must be non-negative')
            #   .
            #   .
            #   .
            cls.param[key] = value  # <--- Unngår unødvendig else-statement.
        #--------#--------#--------#--------#--------#--------#--------#

    def __init__(self, age=0, weight=None, migrated=False, species=None):
        """
        The constructor in Fauna that allows a instance of a animal to initialize the attributes of
        the class.

        :param age: Age of the animal instance represented as a integer.
        :param weight: Weight of the animal instance represented as a float number.
        +   :param migrated: Whether the animal has migrated (bool).                <--- Tydeligere datatype
        +   :param species: Species of the animal (str).        
        """
        self.age = age
        if weight is None:
            self.weight = random.gauss(self.param['w_birth'], self.param['sigma_birth'])
        else:
            self.weight = weight
        self.fitness = None
        self.migrated = migrated
        self.species = species


    def get_fitness(self):
        """
        Calculates fitness based on current age and weight of the animal.
        The parameters 'phi_age', 'a_half', 'phi_weight', 'w_half' are specified within each
        subclass.

        :return: Updated fitness (value between 0 and 1)
        """
        q_pos = 1 / (1 + m.exp(self.param['phi_age'] * (self.age - self.param['a_half'])))
        q_neg = 1 / (1 + m.exp(-self.param['phi_weight'] * (self.weight - self.param['w_half'])))

        if self.weight <= 0:
            self.fitness = 0
        else:
            self.fitness = q_pos * q_neg

        return self.fitness
        #--------#--------#--------#--------#--------#--------#--------#
        if self.weight <= 0:    
            return 0            # <--- Unngå å regne ut det nedenfor for dyr som ikke kan ha fitness
        
        q_pos = 1 / (1 + m.exp(self.param['phi_age'] * (self.age - self.param['a_half'])))
        q_neg = 1 / (1 + m.exp(-self.param['phi_weight'] * (self.weight - self.param['w_half'])))
        self.fitness = q_pos * q_neg
        
        return self.fitness
        #--------#--------#--------#--------#--------#--------#--------#

    def ageing(self):   # <--- Litt utydelig funksjonsnavn. Kanskje age_one_year?
        """
        Used to increase the age of the animal by one year.
        """
        self.age += 1


    def get_age(self):  # <--- Legg til funksjonsbeskrivelse nedenfor. Viktig å være konsekvent
        """
        :return: int: current age
        """
        return self.age
    

    def get_weight(self):   # <--- Legg til funksjonsbeskrivelse nedenfor. Viktig å være konsekvent
        """
        :return: float: current weight
        """
        return self.weight
    

    def weight_loss(self):
        """
        Used when the animals weight decrease. Every year the weight of the animal decrease.

        :return: float: new decreased weight
        """
        self.weight -= self.param['eta'] * self.weight
        return self.weight
    

    def birth(self, num_animals):   # <--- Litt utydelig. Kanskje give_birth? Er ikke vilkårlig fødsel, men om et spesifikt dyr som skal/kan føde.
        """
        Checks if an animal has the opportunity to give birth. If this is the case,
        the weight of the newborn baby will be returned and the weight of the mother will be
        updated. The chance of giving birth is based on the number of other animals in the cell,
        the mother's weight and fitness, as well as parameter values.
        :param num_animals: int: number of animals in the same cell (gender independent)
        :return: NoneType or float: child_weight
        """
        if num_animals <= 1:
            return None
                                                                                                    # <--- La til mellomrom her og nedenfor for tydeligere lesing
        elif self.weight < self.param['zeta'] * (self.param['w_birth'] + self.param['sigma_birth']):
            return None
        #--------#--------#--------#--------#--------#--------#--------#
        required_weight = self.param['zeta'] * (self.param['w_birth'] + self.param['sigma_birth'])  # <--- Formidle hva som regnes ut her.
        if self.weight < required_weight:
            return None
        #--------#--------#--------#--------#--------#--------#--------#
        
        else:
            birth_probability = min(1, self.param['gamma'] * self.get_fitness() * (num_animals - 1))
            birth_threshold = random.random()
            if birth_probability >= birth_threshold:
                child_weight = random.gauss(self.param['w_birth'], self.param['sigma_birth'])
                if self.weight < self.param['xi'] * child_weight:
                    return None
                else:
                    self.weight = self.weight - self.param['xi'] * child_weight
                    return child_weight
            else:
                return None

    def death(self):
        """
        Check if the animal are going to die or not.
        :return: Bool (True is the animal dies)
        """
        if self.weight <= 0:
            return True
        else:
            death_probability = self.param['omega'] * (1 - self.get_fitness())
            death_threshold = random.random()
            if death_probability == 0:
                return False
            elif death_threshold <= death_probability:
                return True
            else:
                return False


class Herbivore(Fauna):
    """
    Subclass based on class Fauna for making Herbivores. Inherits the methods from the Fauna class.
    Has its own method of eating based on herbivore requirements.
    """
    param = {
        'w_birth': 8.0,
        'sigma_birth': 1.5,
        'beta': 0.9,
        'eta': 0.05,
        'a_half': 40.0,
        'phi_age': 0.6,
        'w_half': 10.0,
        'phi_weight': 0.1,
        'mu': 0.25,
        'gamma': 0.2,
        'zeta': 3.5,
        'xi': 1.2,
        'omega': 0.4,
        'F': 10.0
        }

    def __init__(self, age=0, weight=None, migrated=False, species='Herbivore'):
        super().__init__(age, weight, migrated, species)

    def eating(self, fodder):
        """
        Eating method specified for herbivores.
        Weight increase for herbivore depends on amount of fodder and parameter "beta".
        :param fodder: float
        """
        self.weight += self.param['beta'] * fodder


class Carnivore(Fauna):
    """
    Carnivore subclass which is based on class Fauna. Inherits methods from Fauna, same as Herbivore
     subclass. Has its own method for checking if carnivore are going to eat or not based on
     conditions. Also has its own eating method which can affect the number of herbivores in the
     cell after the carnivores have eaten.
    """
    param = {
        'w_birth': 6.0,
        'sigma_birth': 1.0,
        'beta': 0.75,
        'eta': 0.125,
        'a_half': 40.0,
        'phi_age': 0.3,
        'w_half': 4.0,
        'phi_weight': 0.4,
        'mu': 0.4,
        'gamma': 0.8,
        'zeta': 3.5,
        'xi': 1.1,
        'omega': 0.8,
        'F': 50.0,
        'DeltaPhiMax': 10.0
        }

    def __init__(self, age=0, weight=None, migrated=False, species='Carnivore'):
        super().__init__(age, weight, migrated, species)

    def eating_or_not(self, herbivore):
        """
        Method of checking if a given carnivore has the ability to eat a given herbivore.
        Used as a method in Carnivore.eat. A carnivores fitness must be higher than the fitness of
        herbivores in order for it to have a chance to eat the herbivore.
        :param herbivore: instance of subclass Herbivore
        :return: bool (True if carnivores eats the herbivore)
        """
        self.get_fitness()
        herbivore.get_fitness()

        if self.fitness <= herbivore.fitness:
            return False
        
        elif 0 < self.fitness < self.param['DeltaPhiMax']:
            eat_probability = (self.fitness - herbivore.fitness) / self.param['DeltaPhiMax']
            eat_threshold = random.random()
            if eat_probability < eat_threshold:
                return False
            else:
                return True
        else:
            return True
        
        #--------#--------#--------#--------#--------#--------#--------#
        fitness_difference = self.fitness - herbivore.fitness
        if 0 < self.fitness < self.param['DeltaPhiMax']:
            eat_probability = fitness_difference / self.param['DeltaPhiMax']
            eat_threshold = random.random()
            return eat_probability >= eat_threshold
        
        return True
        #--------#--------#--------#--------#--------#--------#--------#

    def eat(self, population_herbivores):
        """
        Method of eating for carnivores where it tries to eat each herbivore given in the input if
        given the chance to do so, based on the eating_or_not method. A carnivore eats herbivores
        until it has reached its stated maximum level of food intake. The weight of the carnivore
        is updated as it eats. Herbivores that have been eaten, or partially eaten, are removed from
        the input list and returned when the carnivore has finished eating.
        :param population_herbivores: list of instances of Herbivore before carnivore eats
        :return: population_herbivores: list of instances of Herbivore after carnivore have eaten
        """

        tot_eaten_weight = 0
        tot_herbivores_eaten = []
        for herbi in population_herbivores:
            herbi.get_weight()
            if self.eating_or_not(herbi):
                tot_eaten_weight += herbi.weight
                if tot_eaten_weight < self.param['F']:
                    self.weight += self.param['beta'] * herbi.weight
                    tot_herbivores_eaten.append(herbi)
                else:
                    self.weight += self.param['beta'] * herbi.weight
                    tot_herbivores_eaten.append(herbi)
                    break  # Stopping the for-loop and goes to next statement

        for dead_herbi in tot_herbivores_eaten:
            population_herbivores.remove(dead_herbi)
        return population_herbivores
        #--------#--------#--------#--------#--------#--------#--------#
        total_eaten_weight = 0                                                  # <--- Fullstendige variabelnavn
        total_herbivores_eaten = []                                             #
                                                                                # <--- Mellomrom
        for herbivore in herbivore_population:                                  # 
            herbivore_weight = herbivore.get_weight()
            
            if self.eating_or_not(herbivore):
                total_food_consumed += herbivore_weight
                
                if total_food_consumed < self.param['F']:
                    self.weight += self.param['beta'] * herbivore_weight
                    eaten_herbivores.append(herbivore)
                else:
                    self.weight += self.param['beta'] * herbivore_weight
                    eaten_herbivores.append(herbivore)
                    break  # Stop eating after reaching the food intake limit

        # Remove all eaten herbivores from the population
        for eaten_herbivore in eaten_herbivores:
            herbivore_population.remove(eaten_herbivore)

        return herbivore_population
        #--------#--------#--------#--------#--------#--------#--------#