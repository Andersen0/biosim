# -*- coding: utf-8 -*-

"""
Script used to simulate ideas from check_cell.py
"""
import random
import matplotlib.pyplot as plt
import numpy as np
from biosim.fauna import Fauna
from biosim.fauna import Herbivore
from biosim.fauna import Carnivore
from biosim.cell import Lowland

if __name__ == '__main__':

    ini_herbs = [{'loc': (2, 2),
                  'pop': [{'species': 'Herbivore',
                           'age': 5,
                           'weight': 20}
                          for _ in range(50)]}]

    ini_carns = [{'loc': (2, 2),
                  'pop': [{'species': 'Carnivore',
                           'age': 5,
                           'weight': 20}
                          for _ in range(20)]}]

    the_cell = Lowland()
    population = ini_herbs[0]['pop'] # + ini_carns[0]['pop']
    the_cell.add_new_population(population)
    # graph = plt.plot(the_cell.number_of_herbivores())

    num_years = 200

    for years in range(num_years):
        the_cell.annual_cycle()

    print("Nr of Herbivores: ", the_cell.number_of_herbivores())
    print("Nr of Carnivores: ", the_cell.number_of_carnivores())

    # def update(num_years):
    #     fig = plt.figure()
    #     ax = fig.add_subplot(1, 1, 1)
    #     ax.set_xlim(0, num_years)
    #     ax.set_ylim(0, 1)
    #
    #     line = ax.plot(np.arange(num_years),
    #                    np.full(num_years, np.nan), 'b-')[0]
    #
    #     for n in range(num_years):
    #         ydata = line.get_ydata(the_cell.number_of_herbivores())
    #         ydata[n] = np.random.random()
    #         line.set_ydata(ydata)
    #         fig.canvas.flush_events()
    #         plt.pause(1e-6)

    # plt.show()

    # the_cell.update(num_years)
