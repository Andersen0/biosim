# -*- coding: utf-8 -*-

"""
Pytest for cell.py file.
"""

__author__ = 'Tage Andersen, Olav Vikøren Espenes'
__email__ = 'tage.andersen@nmbu.no, olaves@nmbu.no '

import pytest
import random
import itertools

from biosim.fauna import Fauna
from biosim.fauna import Herbivore
from biosim.fauna import Carnivore
from biosim.cell import Water, Lowland, Highland, Desert


class TestCell:

    def test_set_parameters_wrong_key(self):
        """
        Test if set_parameters raises ValueError if the input dictionary has a wrong spelled key.
        :return: ValueError
        """
        with pytest.raises(ValueError):
            Lowland.set_parameters({'f_min': 400})

    def test_set_parameters_negative_number(self):
        """
        Test if set_parameters raises ValueError if the input key f_max is set to a negative number.
        :return: ValueError
        """
        with pytest.raises(ValueError):
            Highland.set_parameters({'f_max': -10})

    def test_set_parameters_water(self):
        """
        Test to check if the @classmethod works considering that the parameter 'f_max' is changed
        at class level so that all new instances of Highland will have 'f_max' of 150 after
        set_parameters is called.
        """
        custom_parameters = {'f_max': 150}
        Highland.set_parameters(custom_parameters)
        a_cell = Highland()
        assert a_cell.landscape_param == custom_parameters

    @pytest.fixture()
    def reset_landscape_parameters(self):
        """
        Set all landscape parameters to default after tests.
        """
        # no setup
        yield
        Water.set_parameters({'f_max': 0})
        Lowland.set_parameters({'f_max': 800})
        Highland.set_parameters({'f_max': 300})
        Desert.set_parameters({'f_max': 0})

    @pytest.fixture(autouse=True)
    def create_cell(self):
        """
        Create a cell with 10 herbivores and 12 carnivores of type Lowland. This is a starting
        point for all the tests that belong to this fixture.
        """
        self.new_herbivores = [{'species': 'Herbivore',
                                'age': 50,
                                'weight': 5},
                               {'species': 'Herbivore',
                                'age': 20,
                                'weight': 60}]
        self.new_carnivores = [{'species': 'Carnivore',
                                'age': 25,
                                'weight': 60}]

        self.a_cell = Lowland()
        self.population_herbivore = [{'species': 'Herbivore',
                                      'age': 5,
                                      'weight': 20} for _ in range(10)]
        self.population_carnivore = [{'species': 'Carnivore',
                                      'age': 5,
                                      'weight': 20} for _ in range(12)]
        for animal in self.population_herbivore:
            self.a_cell.pop_herbivores.append(Herbivore(age=animal['age'],
                                                        weight=animal['weight']))
        for animal in self.population_carnivore:
            self.a_cell.pop_carnivores.append(Carnivore(age=animal['age'],
                                                        weight=animal['weight']))
        yield

    def test_number_of_herbivores(self):
        """
        Check that a instance of Cell (type Lowland) returns the right number for herbivore
        population when calling number_of_herbivores method.
        """
        assert self.a_cell.number_of_herbivores() == 10

    def test_number_of_carnivores(self):
        """
        Same conditions as in test_number_of_herbvores, but this time testing the total number of
        carnivores.
        """
        assert self.a_cell.number_of_carnivores() == 12

    def test_number_of_animals(self):
        """
        Testing that number_of_animals returns the correct total number of animals in "a_cell" cell
        instance.
        """
        assert self.a_cell.number_of_animals() == 22

    def test_population_in_cell(self):
        """
        Test that population_in_cell method returns the pop_herbivores and pop_carnivores with
        animals instances
        together.
        """
        current_pop_herbivore = self.a_cell.pop_herbivores
        current_pop_carnivore = self.a_cell.pop_carnivores

        assert self.a_cell.population_in_cell() == current_pop_herbivore + current_pop_carnivore

    def test_add_new_population_adding_animals(self):
        """
        Test that add_new_population append new animals to their proper list based on 'species'
        """
        population = self.new_herbivores + self.new_carnivores
        self.a_cell.add_new_population(population)
        assert self.a_cell.number_of_herbivores() == 12 and self.a_cell.number_of_carnivores() == 13

    def test_add_new_population_wrong_species(self):
        """
        Test that add_new_population raises ValueError when input a list with a dictionary where
        'species' is not 'Herbivore' or 'Carnivore'.
        """
        new_animal = [{'species': 'Carnivores',
                       'age': 25,
                       'weight': 60}]
        with pytest.raises(ValueError):
            self.a_cell.add_new_population(new_animal)

    def test_sort_by_fitness_high_low(self):
        """
        Test to check if test_sort_by_fitness works when method 'high-low' is used. Adding two
        herbivores (no 1 with low fitness, no 2 with high fitness) to end of pop_herbivores list in
        a_cell. Make a copy of pop_herbivores list called "pop". Uses sort_by_fitness to sort the
        pop list so that the animal with highest fitness is the first element in the list, and the
        animal with the lowest fitness is the last. Then check if the two instances have been
        sorted correctly in pop.
        """
        self.a_cell.add_new_population(self.new_herbivores)
        pop = self.a_cell.pop_herbivores.copy()
        self.a_cell.sort_by_fitness(population=pop, method='high-low')
        assert self.a_cell.pop_herbivores[-2] == pop[-1] and \
               self.a_cell.pop_herbivores[-1] == pop[0]

    def test_sort_by_fitness_low_high(self):
        """
        Tests in the same way as test_sort_by_fitness_high_low, but this time the method='low-high'
        so the first element in "pop" will be the animal with lowest fitness.
        """
        self.a_cell.add_new_population(self.new_herbivores)
        pop = self.a_cell.pop_herbivores.copy()
        self.a_cell.sort_by_fitness(population=pop, method='low-high')
        assert self.a_cell.pop_herbivores[-2] == pop[0] and \
               self.a_cell.pop_herbivores[-1] == pop[-1]

    def test_sort_by_fitness_wrong_string_input(self):
        """
        Test that sort_by_fitness raises ValueError when string input for "method" is wrong.
        """
        with pytest.raises(ValueError):
            self.a_cell.sort_by_fitness(self.a_cell.pop_carnivores, method='highest-lowest')

    def test_add_immigrating_animal(self):
        """
        Check that add_immigrating_animal adds an immigrant animal to its correct population list.
        """
        one_herbivore = Herbivore(age=30, weight=31)
        one_carnivore = Carnivore(age=20, weight=21)
        self.a_cell.add_immigrating_animal(one_herbivore)
        self.a_cell.add_immigrating_animal(one_carnivore)
        assert self.a_cell.pop_herbivores[-1] == one_herbivore and \
               self.a_cell.pop_carnivores[-1] == one_carnivore

    def test_add_immigrating_animal_no_species(self):
        """
        Check if an instance which is not Herbivore or Carnivore will not be added to either
        pop_herbivores or pop_carnivores.
        """
        animal = Fauna(age=15, weight=16)
        with pytest.raises(ValueError):
            self.a_cell.add_immigrating_animal(animal)

    def test_remove_emigrated_animal(self):
        """
        Check if an animal instance who have been determined to emigrate will be removed from their
        respective population lists.
        """
        number = random.randint(1, 9)
        herbivore_from_pop_list = self.a_cell.pop_herbivores[number]
        carnivore_from_pop_list = self.a_cell.pop_carnivores[number]
        self.a_cell.remove_emigrated_animal(herbivore_from_pop_list)
        self.a_cell.remove_emigrated_animal(carnivore_from_pop_list)
        assert herbivore_from_pop_list not in self.a_cell.pop_herbivores and \
               carnivore_from_pop_list not in self.a_cell.pop_carnivores

    def test_remove_emigrated_herbivore_not_in_list(self):
        """
        Test that herbivore that is not a part of the population list will raise a ValueError when
        attempted to remove.
        """
        one_herbivore = Herbivore(age=10, weight=20)
        with pytest.raises(ValueError):
            self.a_cell.remove_emigrated_animal(one_herbivore)

    def test_remove_emigrated_carnivore_not_in_list(self):
        """
        Test that carnivore that is not a part of the population list will raise a ValueError when
        attempted to remove.
        """
        one_carnivore = Carnivore(age=30, weight=40)
        with pytest.raises(ValueError):
            self.a_cell.remove_emigrated_animal(one_carnivore)

    def test_herbivore_eating_fodder_redused(self):
        """
        Check that all fodder is eaten when fodder is set to 100 and the population of herbivores
        is 10 animals.
        """
        self.a_cell.fodder = 100
        self.a_cell.herbivores_eating()
        assert self.a_cell.fodder == 0

    def test_herbivores_eating_weight_gain(self):
        """
        In this test, there is enough food to achieve the maximum desired amount of food for 9 out
        of 10 herbivores. The last herbivore in the list has to settle for 5 fodder and therefore
        gets a lower weight gain than the second last herbivore on the list. Checks that the new
        weight is correct and that the fodder is now set to 0.
        """

        self.a_cell.fodder = 95
        for animal in self.a_cell.pop_herbivores:
            animal.weight = 20
        self.a_cell.herbivores_eating()
        weight_second_last_herbi_after = 10 * 0.9 + 20
        weight_last_herbi_after = 5 * 0.9 + 20
        assert self.a_cell.pop_herbivores[-2].get_weight() == weight_second_last_herbi_after and \
               self.a_cell.pop_herbivores[-1].get_weight() == weight_last_herbi_after and \
               self.a_cell.fodder == 0

    def test_carnivore_eating(self, mocker):
        """
        Checks that when carnivores eat herbivores they are removed from "pop_herbivores".
        Guarantees that at least one herbivore is eaten by setting "eat_threshold" to 0.001 in
        eat() method.
        """

        mocker.patch('random.random', return_value=0.001)
        for animal in self.a_cell.pop_herbivores:
            animal.weight = 20
        self.a_cell.carnivores_eating()
        assert self.a_cell.number_of_herbivores() < 10

    def test_mark_as_migrated(self):
        """
        Check that mark_as_migrated method set the input animals "migrated" parameter to True.
        """
        animal = self.a_cell.pop_herbivores[0]
        animal.migrated = False
        self.a_cell.mark_as_migrated(animal)
        assert animal.migrated is True

    def test_procreation_herbivore_list_extend(self, mocker):
        """
        Checks if pop_herbivore contains more herbivores than originally before procreation.
        Guarantees that animals are born by setting the weight high enough and setting low
        birth_threshold by using mocker.
        """
        mocker.patch('random.random', return_value=0.001)
        for animal in self.a_cell.pop_herbivores:
            animal.weight = 40
        self.a_cell.procreation_herbivore()
        assert self.a_cell.number_of_herbivores() > 10

    def test_procreation_herbivore_one_animal(self, mocker):
        """
        Checks that no new animals are added to pop_herbivores even though the weight is high
        enough and the birth_threshold is low since there is only one herbivore in the cell.
        """
        mocker.patch('random.random', return_value=0.001)
        self.a_cell.pop_herbivores[-1].weight = 40
        for animal in self.a_cell.pop_herbivores[0:-1]:
            self.a_cell.pop_herbivores.remove(animal)
        self.a_cell.procreation_herbivore()
        assert self.a_cell.number_of_herbivores() == 1

    def test_procreation_herbivore_birth_weight(self, mocker):
        """
        Check that the weight of the newborn herbivore instance is the same as the birth() method
        in Fauna returns.
        """
        mocker.patch('random.gauss', return_value=8.0)
        mocker.patch('random.random', return_value=0.001)
        for animal in self.a_cell.pop_herbivores:
            animal.weight = 40
        self.a_cell.procreation_herbivore()
        assert self.a_cell.pop_herbivores[-1].get_weight() == 8

    def test_procreation_carnivore_list_extend(self, mocker):
        """
        Same test as "test_procreation_herbivore_list_extend", but with carnivores instead of
        herbivores. The test is described in the above test.
        """
        mocker.patch('random.random', return_value=0.001)
        for animal in self.a_cell.pop_carnivores:
            animal.weight = 40
        self.a_cell.procreation_carnivore()
        assert self.a_cell.number_of_carnivores() > 12

    def test_procreation_carnivore_one_animal(self, mocker):
        """
        Same test as "test_procreation_herbivore_one_animal", but with carnivores instead of
        herbivores. The test is described in the above test.
        """
        mocker.patch('random.random', return_value=0.001)
        self.a_cell.pop_carnivores[-1].weight = 40
        for animal in self.a_cell.pop_carnivores[0:-1]:
            self.a_cell.pop_carnivores.remove(animal)
        self.a_cell.procreation_carnivore()
        assert self.a_cell.number_of_carnivores() == 1

    def test_procreation_carnivore_birth_weight(self, mocker):
        """
        Same test as "test_procreation_herbivore_birth_weight", but with carnivores instead of
        herbivores. The test is described in the above test.
        """
        mocker.patch('random.gauss', return_value=8.0)
        mocker.patch('random.random', return_value=0.001)
        for animal in self.a_cell.pop_carnivores:
            animal.weight = 40
        self.a_cell.procreation_carnivore()
        assert self.a_cell.pop_carnivores[-1].get_weight() == 8

    def test_migrating_or_not_migrated_as_true(self):
        """
        Check that migrating_or_not() are returning a empty list when all the animals has migrated
        = True.
        """
        for animal in itertools.chain(self.a_cell.pop_herbivores, self.a_cell.pop_carnivores):
            animal.migrated = True
        assert self.a_cell.migrating_or_not() == []

    def test_migrating_or_not_half_pop_migrating(self, mocker):
        """
        Check that the number of animals in the animals_migrating list is correct in relation to
        how many animals have been migrated. Half of the animals are set to migrated = True, while
        the other half are guaranteed to migrate since migrating_threshold is set artificially low
        so that the outcome is that all animals that have not migrated before migrate now.
        """
        mocker.patch('random.random', return_value=0.001)
        for animal in itertools.chain(self.a_cell.pop_herbivores[:5],
                                      self.a_cell.pop_carnivores[:6]):
            animal.migrated = True
        assert len(self.a_cell.migrating_or_not()) == 11

    def test_yearly_ageing_and_weight_loss_ageing_check(self):
        """
        Check that both herbivores and carnivores is ageing by one year when calling
        yearly_ageing_and_weight_loss()
        """
        self.a_cell.yearly_ageing_and_weight_loss()
        assert self.a_cell.pop_herbivores[1].get_age() == 6 and \
               self.a_cell.pop_carnivores[5].get_age() == 6

    def test_yearly_ageing_and_weight_loss_check_ageing(self):
        """
        Check that both herbivores and carnivores is ageing by one year when calling
        yearly_ageing_and_weight_loss()
        """
        for animal in itertools.chain(self.a_cell.pop_herbivores,
                                      self.a_cell.pop_carnivores):
            animal.age = 25
        self.a_cell.yearly_ageing_and_weight_loss()
        assert self.a_cell.pop_herbivores[1].get_age() == 26 and \
               self.a_cell.pop_carnivores[5].get_age() == 26

    def test_yearly_ageing_and_weight_loss_check_weight_loss(self):
        """
        Check that both herbivores and carnivores is getting the right amount of weight loss when
        calling yearly_ageing_and_weight_loss method.
        """
        for animal in itertools.chain(self.a_cell.pop_herbivores,
                                      self.a_cell.pop_carnivores):
            animal.weight = 20
        herbi_new_weight = 20 - 0.05*20
        carni_new_weight = 20 - 0.125*20
        self.a_cell.yearly_ageing_and_weight_loss()
        assert self.a_cell.pop_herbivores[3].get_weight() == herbi_new_weight and \
               self.a_cell.pop_carnivores[9].get_weight() == carni_new_weight

    def test_yearly_death(self, mocker):
        """
        Check that only the animals that are going to die are removed from their respective
        population lists. Sets some animals to have weight 0 (dead) and some animals that are
        guaranteed not to die (through the use of mocker).
        """
        mocker.patch('random.random', return_value=0.999)
        for herbi in self.a_cell.pop_herbivores[:7]:
            herbi.weight = 0
        for carni in self.a_cell.pop_carnivores[:3]:
            carni.weight = 0

        self.a_cell.yearly_death()
        assert self.a_cell.number_of_herbivores() == 3 and \
               self.a_cell.number_of_carnivores() == 9

    def test_reset_migrated_parameter(self):
        """
        Set all animals in pop_herbivores to migrated=True, and after called
        reset_migrated_parameter all the animals should have migrated=False.
        """
        for animal in self.a_cell.pop_herbivores:
            animal.migrated = True
        self.a_cell.reset_migrated_parameter()
        for animal in self.a_cell.pop_herbivores:
            assert animal.migrated is False

    def test_fodder_regrowth(self):
        """Set fodder to be zero. Since a_cell is a instance of Lowland the fodder should be set to
        default (800) after calling fodder_regrowth method.
        """
        self.a_cell.fodder = 0
        self.a_cell.fodder_regrowth()
        assert self.a_cell.fodder == 800

    def test_hospitable(self):
        """
        Test that a instance of Water returns False on hospitable call, and instance of Desert
        returns True on the same call.
        """
        a_water_cell = Water()
        a_desert_cell = Desert()
        assert a_water_cell.hospitable is False and a_desert_cell.hospitable is True

    def test_landscape_type(self):
        """
        Test that a instance of Lowland and Highland returns the right landscape type when it is
        called.
        """
        a_lowland_cell = Lowland()
        a_highland_cell = Highland()
        assert a_lowland_cell.landscape == 'L' and a_highland_cell.landscape == 'H'
