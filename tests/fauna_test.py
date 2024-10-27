# -*- coding: utf-8 -*-

"""
Pytest for fauna.py file.
"""

__author__ = 'Olav Vikøren Espenes, Tage Andersen'
__email__ = 'olaves@nmbu.no, tage.andersen@nmbu.no'

import pytest
import random

from biosim.fauna import Herbivore
from biosim.fauna import Carnivore


def test_set_parameters_wrong_key():
    """
    Check that set_parameters method raises ValueError when a not accepted key is used.
    """
    animal = Herbivore()
    parameters = {'sigma_death': 0.5}
    with pytest.raises(ValueError):
        animal.set_parameters(custom_parameters=parameters)


@pytest.mark.parametrize('wrong_parameters',
                         [{'w_birth': -1},
                          {'DeltaPhiMax': 0},
                          {'eta': 1.1}])
def test_set_parameters_errors(wrong_parameters):
    """
    Test 1: checks that set_parameters raises ValueError when a parameter is set to a negative
            number.
    Test 2: checks that set_parameters raises ValueError when 'DeltaPhiMax' parameter is not set to
            a strictly positive number.
    Test 3: check that set_parameters raises ValueError when 'eta' is set to a value higher then 1.
    """
    animal = Herbivore(age=5)
    with pytest.raises(ValueError):
        animal.set_parameters(wrong_parameters)


@pytest.fixture()
def test_set_parameters_correct_param():
    """
    Test that set_parameters sets the input value to correct subclass parameters when input value
    key is legal. (THIS TEST ARE NOT RUNNING)
    """
    animal = Herbivore(age=5)
    parameters = {'a_half': 55.5}
    animal.set_parameters(custom_parameters=parameters)
    assert animal.param['a_half'] == 55.5


@pytest.fixture()
def reset_animals_parameters():
    """
    Set back the parameters for Herbivore subclass to default. (THIS IS NOT RUNNING)
    """
    # No setup
    yield

    Herbivore.set_parameters(Herbivore.param)


def test_fitness_weight_zero_herbivore():
    """
    Check if fitness returns zero when weight of herbivore is zero. Random age.
    """
    herbi = Herbivore(5, 0)
    assert herbi.get_fitness() == 0


def test_fitness_weight_zero_carnivores():
    """
    Check if fitness returns zero when weight of carnivore is zero. Random age.
    """
    carni = Carnivore(5, 0)
    assert carni.get_fitness() == 0


def test_fitness_weight_positive_herbivores():
    """
    Check if herbivore with a given age and weight (>0) will compute the right fitness.
    """
    herbi = Herbivore(5, 5)
    assert herbi.get_fitness() == 0.3775406685118729


def test_fitness_weight_positive_carnivores():
    """
    Check if carnivore with a given age and weight (>0) will compute the right fitness.
    """
    carni = Carnivore(7, 10)
    assert carni.get_fitness() == 0.9167813042956195


def test_age_increase():
    """
    Testing the ageing method. Check if self.age is 10 after 10 years.
    """
    num_years = 10
    animal = Herbivore()
    for _ in range(num_years):
        animal.ageing()
    assert animal.get_age() == num_years


def test_get_age():
    """
    Test that get_age method returns the correct age.
    """
    age = random.randint(1, 20)
    animal = Herbivore(age, 30)
    assert animal.get_age() == age


def test_get_weight():
    """
    Check if method get_weight() returns the correct value of current weight. Random age.
    """
    age = random.randint(1, 20)
    animal = Herbivore(age, 14)
    assert animal.get_weight() == 14


@pytest.mark.parametrize("from_weight, to_weight",
                         [[24, 22.8],
                          [16.3, 15.485],
                          [9.23, 8.7685]])
def test_weight_loss_herbivore(from_weight, to_weight):
    """
    Test weight_loss method with different weights for herbivore with belonging
    eta-parameter. Random age from 1 to 20.
    """
    age = random.randint(1, 20)
    herbi = Herbivore(age, from_weight)
    assert herbi.weight_loss() == pytest.approx(to_weight)


@pytest.mark.parametrize('from_weight, to_weight',
                         [[24, 21],
                          [16.3, 14.2625],
                          [9.23, 8.07625]])
def test_weight_loss_carnivore(from_weight, to_weight):
    """
    Test weight_loss method with different weights for carnivore with belonging
    eta-parameter. Random age from 1 to 20.
    """
    age = random.randint(1, 20)
    carni = Carnivore(age, from_weight)
    assert carni.weight_loss() == pytest.approx(to_weight)


@pytest.mark.parametrize('age, weight, num_animals, returned',
                         [[20, 30, 1, None],  # Test 1
                          [20, 33.24, 5, None],  # Test 2
                          [35, 33.25, 5, None]])  # Test 3
def test_birth_herbivore(age, weight, num_animals, returned):
    """
    Check that birth_herbivore returns None when:
     Test 1: There is just one animal in the cell.ag
     Test 2: When weight is lower then weight <= zeta*(w_birth+sigma_birth) (default parameters)
     Test 3: When weight is high enough, but the fitness is to low.
    """
    herbi = Herbivore(age, weight)
    random.seed(24)
    assert herbi.birth(num_animals) is returned


def test_birth_herbivore_newborn():
    """
    Check that birth method in Fauna do not return NoneType when a animal is born.
    With seed = 24 the birth_threshold is 0.712 and the birth_probability is 0.729 (Default
    herbivore parameters, num_animals = 5 and fitness calculated from age = 20 and weight = 33.25).
    Since birth_probability >= birth_threshold is fulfilled, and the weight of herbivore in test
    will be higher than the multiplication between 'xi' and child_weight (standard parameters),
    then birth should return child_weight and not a NoneType.
    """
    herbi = Herbivore(20, 33.25)
    random.seed(24)
    assert herbi.birth(5) is not None


def test_death_zero_weight():
    """
    Test that death-method return True if the weight of the animal is zero.
    """
    carni = Carnivore(25, 0)
    assert carni.death() is True


@pytest.mark.parametrize('age, weight, seed, boolean_return',
                         [[25, 0, 1, True],  # Test 1
                          [50, 20, 3, True],  # Test 2
                          [50, 20, 5, False]])  # Test 3
def test_death_not_zero_weight(age, weight, seed, boolean_return):
    """
    Test 1: death-method should return True if the weight of the animal is zero.
    Test 2: death_method should return True when death_threshold has a lower value than
            death_probability. death_probability is 0.399 (sta. parameters) and random.random with
            seed(3) is 0.238.
    Test 3: Same animal as in Test 2, but this time more lucky. death_threshold (seed(5): 0.622)
            has now a higher value than death_probability and therefore the death_method should
            return False.
    """
    herbi = Herbivore(age, weight)
    random.seed(seed)
    assert herbi.death() is boolean_return


@pytest.fixture()
def test_death_not_zero_omega(mocker):
    """
    Test that setting 'omega' parameter to zero will make method return False (not dies) even
    tho the animal is very old and got very low fitness, at the same time death_probability is set
    to 0.999 by mocker.
    (THIS TEST IS NOT RUNNING)
    """
    mocker.patch('random.random', return_value=0.999)
    herbi = Herbivore(age=80, weight=1)
    parameters = {'omega': 0}
    herbi.set_parameters(parameters)
    assert herbi.death() is False

    yield


def test_eating_herbivore():
    """
    Test eating method for Herbivores. Checking the self.weight is set to correct weight before
    herbivore is eating. After the herbivore eats, the weight is also checked to see that it has
    been updated correctly.
    """
    age = random.randint(1, 20)
    fodder = 10
    weight_before_eating = 20
    weight_after_eating = weight_before_eating + (0.9*fodder)  # Standard parameter for "beta"

    animal = Herbivore(age, weight_before_eating)
    assert animal.get_weight() == weight_before_eating
    animal.eating(fodder)
    assert animal.get_weight() == weight_after_eating


@pytest.mark.parametrize('herbivore, carnivore, seed, boolean_return',
                         [[Herbivore(15, 30), Carnivore(35, 20), 1, False],  # Test 1
                          [Herbivore(40, 5), Carnivore(10, 40), 91, False],  # Test 2
                          [Herbivore(40, 5), Carnivore(10, 40), 32, True]])  # Test 3
def test_eating_or_not(herbivore, carnivore, seed, boolean_return):
    """
    Test 1: eating_or_not-method should return False if carnivores fitness is the same or less
            then herbivores fitness.
    Test 2: Carnivores fitness is above zero, but lower then DeltaPhiMax (std. parameter: 10).
            Therefore it can eat the
            input herbivore if eat_probability is higher then the eat_threshold. In this test, the
            carnivore does not have luck with eating (0.0811 against 0.0835 (seed(91)) and the
            method should therefore return False.
    Test 3: Same herbivore and carnivore as in Test 2, but this time the carnivore eat_probability
            value are higher then the eat_threshold value (seed(32): 0.0774). In this case the
            method should return True.
    Test 4 (NOT MADE YET) : Changing the parameter "DeltaPhiMax" to a lower value than the
                            carnivore fitness. In such a case, the method will in any case return
                            True if the fitness of the carnivore is higher than the fitness of the
                            herbivore.
    """
    herbi = herbivore
    carni = carnivore
    random.seed(seed)
    assert carni.eating_or_not(herbi) is boolean_return


@pytest.mark.parametrize('herbivore, num_herbivores, returned_list_length',
                         [[Herbivore(40, 5), 15, 5],  # Test 1
                          [Herbivore(40, 5), 5, 0],  # Test 2
                          [Herbivore(40, 4), 20, 7]])  # Test 3
def test_eat_return_list(herbivore, num_herbivores, returned_list_length, mocker):
    """
    Three different tests to check if carnivore.eat() are removing the right number of herbivores
    (eaten animals) before it returns the list. A mocker is used to to make sure that the
    eaten_or_not method always returns True when it is called inside eat().
    Test 1: 15 herbivores with a weight of 5. With parameter F set to 50 for carnivores (standard),
            10 herbivores will be removed from the return list.
    Test 2: Check that all herbivores are removed when the total weight of eaten herbivores is less
            than the F-value.
    Test 3: Check that the carnivore also eats the herbivore which causes the total weight of the
            eaten herbivores to exceed the F-value but stops eating after that.
    """
    mocker.patch('random.random', return_value=0.001)
    list_of_herbivores = [herbivore for _ in range(num_herbivores)]
    carni = Carnivore(10, 40)
    assert len(carni.eat(list_of_herbivores)) == returned_list_length


@pytest.mark.parametrize('herbivore, num_herbivores, added_weight',
                         [[Herbivore(30, 1), 100, 37.5],  # Test 1
                          [Herbivore(30, 20), 100, 45.0]])  # Test 2
def test_eat_updated_weight(herbivore, num_herbivores, added_weight, mocker):
    """
    Three different tests to check if carnivore.eat() are updating correct weight for the carnivore
    eating. A mocker is used to to make sure that the eaten_or_not method always returns True when
    it is called inside eat().
    Test 1: 100 herbivores with a weight of 1. With std. parameters for F- and beta-value the
            carnivore should put on 37.5.
    Test 2: 100 herbivores with a weight of 20. The carnivore will eat 3 herbivores and put on 45.0
            in weight.
    """
    mocker.patch('random.random', return_value=0.001)
    list_of_herbivores = [herbivore for _ in range(num_herbivores)]
    carni = Carnivore(10, 40)
    old_weight = carni.get_weight()
    carni.eat(list_of_herbivores)
    new_weight = old_weight + added_weight
    assert carni.get_weight() == new_weight
