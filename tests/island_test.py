# -*- coding: utf-8 -*-

"""
Pytest for island.py file.
"""

__author__ = 'Olav Vikøren Espenes, Tage Andersen'
__email__ = 'olaves@nmbu.no, tage.andersen@nmbu.no '

import pytest

from biosim.island import Island


class TestIsland:

    def test_creating_map(self):
        """
        Test that the class makes a instance of Island when input a correct map string.
        """
        a_map_string = """\
                          WWW
                          WLW
                          WWW"""
        Island(a_map_string)

    def test_creating_map_raise_error(self):
        """
        Test that creating_map raises ValueError when a input string contains letter that are not
        representing a valid landscape type.
        :return:
        """
        a_map_string = """\
                          WWWW
                          WTDW
                          WHLW
                          WWWW"""
        with pytest.raises(ValueError):
            Island(a_map_string)

    def test_check_input_map_string_not_water_edges(self):
        """
        Test that check_input_map_string raises ValueError when a input string contains edges that
        are not of type 'W' (water).
        """
        a_map_string = """\
                          WWWWW
                          WDDDD
                          WLLHW
                          WWWWW"""
        with pytest.raises(ValueError):
            Island(a_map_string)

    def test_check_input_map_string_not_water_edges_2(self):
        """
        Test that check_input_map_string raises ValueError when a input string contains edges that
        are not of type 'W' (water).
        """
        a_map_string = """\
                          WWLWW
                          WDDDW
                          WLLHW
                          WWWWW"""
        with pytest.raises(ValueError):
            Island(a_map_string)

    def test_check_input_map_string_not_same_length(self):
        """
        Test that check_input_map_string raises ValueError when not all rows are in the same length.
        """
        a_map_string = """\
                          WWWWW
                          WDDDW
                          WLLHW
                          WWWWWW"""
        with pytest.raises(ValueError):
            Island(a_map_string)

    def test_place_animals_on_island(self):
        """
        Test that a population of herbivores and a population of carnivores is put in its proper
        cell on island.
        """
        test_map = """\
                       WWWWW
                       WLLLW
                       WHHHW
                       WWWWW"""

        test_island = Island(test_map)
        population = self.herbs + self.carns

        test_island.place_populations_on_island(population)
        assert test_island.island_map[1, 1].number_of_herbivores() == 10 and \
               test_island.island_map[2, 2].number_of_carnivores() == 5

    @pytest.fixture(autouse=True)
    def create_island(self):
        map = """\
                  WWWWW
                  WLLLW
                  WHHHW
                  WWWWW"""

        self.herbs = [{'loc': (2, 2),
                       'pop': [{'species': 'Herbivore',
                                'age': 5,
                                'weight': 20}
                               for _ in range(10)]}]
        self.carns = [{'loc': (3, 3),
                       'pop': [{'species': 'Carnivore',
                                'age': 5,
                                'weight': 20}
                               for _ in range(5)]}]
        self.an_island = Island(map)
        self.an_island.place_populations_on_island(self.herbs)
        self.an_island.place_populations_on_island(self.carns)

        yield

    def test_get_neighbors_to_cell(self):
        """
        Test that test_get_neighbors_to_cell method returns the correct list of neighbors to a input
        cell.
        """
        a_cell_location = [2, 2]
        neighbors = self.an_island.get_neighbors_to_cell(a_cell_location)
        assert neighbors == [[1, 2],
                             [2, 3],
                             [3, 2],
                             [2, 1]]

    def test_migration(self, mocker):
        """
        Test that no animal migrating to cell of type Water.
        Set two mockers:
            - One to be sure that chosen random migration cell is a water cell.
            - One to be sure that all animals will be set as they get the opportunity to migrate.
        Since no animals have migrated, the number of animals in the population list must be the
        same before and after migration () is called.
        """
        mocker.patch('random.choice', return_value=[0, 1])
        mocker.patch('random.random', return_value=0.001)
        length_pop_before = self.an_island.island_map[1, 1].number_of_herbivores()
        for animals in self.an_island.island_map[1, 1].pop_herbivores:
            animals.migrated = False
            animals.get_fitness()
        self.an_island.migration()
        length_pop_after = self.an_island.island_map[1, 1].number_of_herbivores()
        assert length_pop_after == length_pop_before

    def test_migration_2(self, mocker):
        """
        Choose migration cell to be of type Lowland and that every animal can migrate to it by
        setting random.random mocker (migrating_threshold) to 0.001. But for half of the animals,
        migrated = True is set so these animals do not get migrated anyway. The test checks if the
        correct number of animals are left in the cell after migration () is called.
        """
        mocker.patch('random.choice', return_value=[1, 2])
        mocker.patch('random.random', return_value=0.001)
        for animals in self.an_island.island_map[1, 1].pop_herbivores[:5]:
            animals.migrated = True
            animals.get_fitness()
        self.an_island.migration()

        length_pop_after = self.an_island.island_map[1, 1].number_of_herbivores()
        assert length_pop_after == 5

    def test_annual_cycle(self):
        """
        Test to check if annual_cycle runs as it should without raising any error.
        """
        for _ in range(10):
            self.an_island.annual_cycle()

    def test_animal_counter_pop_lists(self):
        """
        Method that checks that animal_counter () counts the correct number of animals of the same
        species in their respective numpy.array.
        """
        pop_herbivores_per_cell, pop_carnivores_per_cell, rows, cols = \
            self.an_island.animal_counter()

        assert pop_herbivores_per_cell[1, 1] == \
               self.an_island.island_map[1, 1].number_of_herbivores() and \
               pop_carnivores_per_cell[2, 2] == \
               self.an_island.island_map[2, 2].number_of_carnivores()

    def test_animal_counter_shape(self):
        """
        Test to control that the shape of numpy.array pop_herbivores_per_cell and
        pop_carnivores_per_cell is the same as the island instance they benn made from.
        """
        pop_herbivores_per_cell, pop_carnivores_per_cell, rows, cols = \
            self.an_island.animal_counter()

        assert pop_herbivores_per_cell.shape[0] == rows and \
               pop_herbivores_per_cell.shape[1] == cols

    def test_weight_in_get_weight_age_fitness(self):
        """
        Check that get_weight_age_fitness returns correct weights when input
        animal_property='weight'.
        """
        first_herbi_weight = self.an_island.island_map[1, 1].pop_herbivores[0].get_weight()
        first_carni_weight = self.an_island.island_map[2, 2].pop_carnivores[0].get_weight()
        weight = self.an_island.get_weight_age_fitness('weight')
        assert weight['Herbivore'][0] == first_herbi_weight and \
               weight['Carnivore'][0] == first_carni_weight

    def test_age_in_get_weight_age_fitness(self):
        """
        Check that get_weight_age_fitness returns correct ages when input
        animal_property='age'.
        """
        first_herbi_age = self.an_island.island_map[1, 1].pop_herbivores[0].get_age()
        first_carni_age = self.an_island.island_map[2, 2].pop_carnivores[0].get_age()
        weight = self.an_island.get_weight_age_fitness('age')
        assert weight['Herbivore'][0] == first_herbi_age and \
               weight['Carnivore'][0] == first_carni_age

    def test_fitness_in_get_weight_age_fitness(self):
        """
        Check that get_weight_age_fitness returns correct fitness when input
        animal_property='fitness'.
        """
        first_herbi_age = self.an_island.island_map[1, 1].pop_herbivores[0].get_age()
        first_carni_age = self.an_island.island_map[2, 2].pop_carnivores[0].get_age()
        weight = self.an_island.get_weight_age_fitness('age')
        assert weight['Herbivore'][0] == first_herbi_age and \
               weight['Carnivore'][0] == first_carni_age

    def test_error_get_weight_age_fitness(self):
        """
        Check that get_weight_age_fitness method raises ValueError if input string is typed
        incorrect.
        """
        with pytest.raises(ValueError):
            self.an_island.get_weight_age_fitness('ages')
