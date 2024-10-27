# -*- coding: utf-8 -*-

"""
Template for BioSim class.
"""

# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2021 Hans Ekkehard Plesser / NMBU

from biosim.fauna import Herbivore, Carnivore
from biosim.cell import Water, Lowland, Highland, Desert
from biosim.island import Island

import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import colors
import os
import subprocess
import csv

_FFMPEG_BINARY = 'ffmpeg'
_MAGICK_BINARY = 'magick'

_DEFAULT_GRAPHICS_DIR = os.path.join('..', 'data')
_DEFAULT_GRAPHICS_NAME = 'dv'
_DEFAULT_MOVIE_FORMAT = 'mp4'


class BioSim:    
    # ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ #
    STANDARD_VERDIER = {'Herbivore': 50, 'Carnivore': 20}
    # ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑ #
    
    def __init__(self, island_map, ini_pop, seed,
                 vis_years=1, ymax_animals=None, cmax_animals=None, hist_specs=None,
                 img_dir=None, img_base=None, img_fmt='png', img_years=None,
                 log_file=None):

        """
        :param island_map: Multi-line string specifying island geography
        :param ini_pop: List of dictionaries specifying initial population
        :param seed: Integer used as random number seed
        :param ymax_animals: Number specifying y-axis limit for graph showing animal numbers
        :param cmax_animals: Dict specifying color-code limits for animal densities
        :param hist_specs: Specifications for histograms, see below
        :param vis_years: years between visualization updates (if 0, disable graphics)
        :param img_dir: String with path to directory for figures
        :param img_base: String with beginning of file name for figures
        :param img_fmt: String with file type for figures, e.g. 'png'
        :param img_years: years between visualizations saved to files (default: vis_years)
        :param log_file: If given, write animal counts to this file

        If ymax_animals is None, the y-axis limit should be adjusted automatically.
        If cmax_animals is None, sensible, fixed default values should be used.
        cmax_animals is a dict mapping species names to numbers, e.g.,
           {'Herbivore': 50, 'Carnivore': 20}

        hist_specs is a dictionary with one entry per property for which a histogram shall be shown.
        For each property, a dictionary providing the maximum value and the bin width must be
        given, e.g.,
            {'weight': {'max': 80, 'delta': 2}, 'fitness': {'max': 1.0, 'delta': 0.05}}
        Permitted properties are 'weight', 'age', 'fitness'.

        If img_dir is None, no figures are written to file. Filenames are formed as

            f'{os.path.join(img_dir, img_base}_{img_number:05d}.{img_fmt}'

        where img_number are consecutive image numbers starting from 0.

        img_dir and img_base must either be both None or both strings.
        """
        random.seed(seed)
        self.island_map_string = island_map
        self.island = Island(island_map)
        self.add_population(ini_pop)
        self._year = 0
        self.final_year = 0

        # Should be adjusted automatically when None
        self.ymax_animals = ymax_animals

        if cmax_animals is None:
            self.cmax_animals = {'Herbivore': 50, 'Carnivore': 20}  # <--- Definer standard verdier som del av BioSim class-en

        # ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ #
        self.cmax_animals = cmax_animals or self.STANDARD_VERDIER
        # ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑ #


        # ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ #
        """
        Gjør dette om til en metode
        """
        self.weight_hist_bins = None
        self.age_hist_bins = None
        self.fitness_hist_bins = None
        if hist_specs is not None:
            for key in hist_specs:
                n_points = int(round(hist_specs[key]['max'] / hist_specs[key]['delta'])) + 1
                if key == 'weight':
                    self.weight_hist_bins = np.linspace(0, hist_specs[key]['max'], num=n_points)
                elif key == 'age':
                    self.age_hist_bins = np.linspace(0, hist_specs[key]['max'], num=n_points)
                elif key == 'fitness':
                    self.fitness_hist_bins = np.linspace(0, hist_specs[key]['max'], num=n_points)
                else:
                    raise ValueError('hist_specs must be a dictionary with key(s) "weight", "age" '
                                     f'and/or "fitness".{hist_specs} was provided.')
        # ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑ #

        if vis_years == 0:
            self.graphics = 'Off'
        elif vis_years > 0:
            self.graphics = 'On'
            self.visualization_update_interval = vis_years
        else:
            raise ValueError('Input "vis_years" must be a positive integer (>= 0)')

        self.img_num = 0
        if img_dir is not None and img_base is not None:
            self.img_save = True
            self.img_dir = img_dir
            self.img_base = img_base
            if img_years is None:
                self.img_years = vis_years
            else:
                self.img_years = img_years
        else:
            self.img_save = False

        self.img_fmt = img_fmt

        if log_file is not None:
            self.log_file = log_file
            header = ['Year', 'Herbivore count', 'Carnivore count']
            file = open(self.log_file, 'a+', newline='')
            with file:
                write = csv.writer(file)
                write.writerow(header)
        # ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ #
        """
        Dette kan gjøres om til en metode
        """
        header = ['Year', 'Herbivore count', 'Carnivore count']
        with open(self.log_file, 'a+', newline='') as file:
            csv.writer(file).writerow(header)
        # ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑ #

        else:
            self.log_file = None    # <--- kan fjernes med endringene over

        # Plotting variables
        self.fig = None
        self.ax_year_counter = None
        self.ax_pop_counter = None
        self.ax_map = None
        self.map_rgb = None
        self.ax_pop_line = None
        self.herbi_line = None
        self.carni_line = None
        self.num_herbivores_data = np.zeros(0)
        self.num_carnivores_data = np.zeros(0)
        self.year_list = [0]
        self.ax_heatmap_herbi = None
        self.ax_cmap_herbi = None
        self.ax_heatmap_carni = None
        self.ax_cmap_carni = None
        self.ax_fitness_hist = None
        self.ax_age_hist = None
        self.ax_weight_hist = None
        self.ax_birth_and_death = None

    @staticmethod
    def set_animal_parameters(species, params):
        """
        Set parameters for animal species.

        :param species: String, name of animal species
        :param params: Dict with valid parameter specification for species
        """

        if species == 'Herbivore':
            Herbivore.set_parameters(params)

        elif species == 'Carnivore':
            Carnivore.set_parameters(params)

        else:
            raise ValueError(f'<{species}> is not an correct input for "species". '
                             f'Must be "Herbivore" or "Carnivore"')

    @staticmethod
    def set_landscape_parameters(landscape, params):
        """
        Set parameters for landscape type.

        :param landscape: String, code letter for landscape
        :param params: Dict with valid parameter specification for landscape
        """

        if landscape == 'W':
            if params['f_max'] != 0:
                raise ValueError('Water has no "f_max" value other than zero')
            else:
                Water.set_parameters(params)
        elif landscape == 'H':
            Highland.set_parameters(params)
        elif landscape == 'L':
            Lowland.set_parameters(params)
        elif landscape == 'D':
            if params['f_max'] != 0:
                raise ValueError('Desert has no "f_max" value other than zero')
            else:
                Desert.set_parameters(params)
        else:
            raise ValueError('Input landscape string is not a valid letter. '
                             'Must be "W", "H", "L" or "D".')

    def making_map(self):
        """
        Making plot for island map
        Copyright (c) Hans Ekkehard Plesser
        """
        self.island_map_string = ' '.join(self.island_map_string.split())
        self.island_map_string = self.island_map_string.replace(' ', '\n')

        rgb_value = {'W': colors.to_rgb('aqua'),  # blue
                     'L': colors.to_rgb('forestgreen'),  # dark green
                     'H': colors.to_rgb('grey'),  # light green
                     'D': colors.to_rgb('khaki')}  # light yellow

        self.map_rgb = [[rgb_value[column] for column in row]
                        for row in self.island_map_string.splitlines()]

        self.ax_map.imshow(self.map_rgb, interpolation='nearest')
        self.ax_map.set_xticks(range(len(self.map_rgb[0])))
        self.ax_map.set_xticklabels(range(1, 1 + len(self.map_rgb[0])), fontsize=8, rotation=90)
        self.ax_map.set_yticks(range(len(self.map_rgb)))
        self.ax_map.set_yticklabels(range(1, 1 + len(self.map_rgb)), fontsize=8)

        ax_lg = self.fig.add_axes([0.41, 0.75, 0.05, 0.15])  # llx, lly, w, h
        ax_lg.axis('off')
        for ix, name in enumerate(('Water', 'Lowland',
                                   'Highland', 'Desert')):
            ax_lg.add_patch(plt.Rectangle((0., ix * 0.2), 0.3, 0.1,
                                          edgecolor='none',
                                          facecolor=rgb_value[name[0]]))
            ax_lg.text(0.33, ix * 0.2, name, transform=ax_lg.transAxes, fontsize=9)

    def animal_count(self):
        """
        Setup for the two lines in the "Animal count" plot.
        """
        num_herbivores, num_carnivores = self.num_animals_per_species.values()
        y1 = np.append(self.num_herbivores_data, num_herbivores)
        y2 = np.append(self.num_carnivores_data, num_carnivores)
        self.year_list.append(self.year)

        if self.herbi_line is None:
            self.herbi_line = self.ax_pop_line.plot(self.year_list[:-1], y1,
                                                    color='b',
                                                    linewidth=2)[0]
            self.carni_line = self.ax_pop_line.plot(self.year_list[:-1], y2,
                                                    color='r',
                                                    linewidth=2)[0]
        else:
            self.herbi_line.set_xdata(self.year_list[:-1])
            herbi_ydata = self.herbi_line.get_ydata()
            new_herbi_ydata = np.append(herbi_ydata, num_herbivores)
            self.herbi_line.set_ydata(new_herbi_ydata)

            self.carni_line.set_xdata(self.year_list[:-1])
            carni_ydata = self.carni_line.get_ydata()
            new_carni_ydata = np.append(carni_ydata, num_carnivores)
            self.carni_line.set_ydata(new_carni_ydata)

        if self.ymax_animals is None:
            self.ax_pop_line.set_ylim(0, self.num_animals)
        else:
            self.ax_pop_line.set(ylim=(0, self.ymax_animals))
        self.ax_pop_line.set_xlim(0, self.final_year)
        self.ax_pop_line.legend(['Herbivore', 'Carnivore'])

    def heatmap_herbivore(self):
        """
        Setup for the density map plot for herbivores.
        """
        df_herbivore = self.animal_distribution('Herbivore')
        self.ax_cmap_herbi = self.ax_heatmap_herbi.imshow(df_herbivore,
                                                          vmax=self.cmax_animals['Herbivore'])
        # noinspection DuplicatedCode
        self.ax_heatmap_herbi.set_title('Herbivore distribution', fontsize=12)
        self.ax_heatmap_herbi.set_xticks(range(len(self.map_rgb[0])))
        self.ax_heatmap_herbi.set_xticklabels(range(1, 1 + len(self.map_rgb[0])),
                                              fontsize=8, rotation=90)
        self.ax_heatmap_herbi.set_yticks(range(len(self.map_rgb)))
        self.ax_heatmap_herbi.set_yticklabels(range(1, 1 + len(self.map_rgb)), fontsize=8)

    def heatmap_carnivore(self):
        """
        Setup for the density map plot for carnivores.
        """
        df_carnivore = self.animal_distribution('Carnivore')
        self.ax_cmap_carni = self.ax_heatmap_carni.imshow(df_carnivore,
                                                          vmax=self.cmax_animals['Carnivore'])

        self.ax_heatmap_carni.set_title('Carnivore distribution', fontsize=12)
        self.ax_heatmap_carni.set_xticks(range(len(self.map_rgb[0])))
        self.ax_heatmap_carni.set_xticklabels(range(1, 1 + len(self.map_rgb[0])),
                                              fontsize=8, rotation=90)
        self.ax_heatmap_carni.set_yticks(range(len(self.map_rgb)))
        self.ax_heatmap_carni.set_yticklabels(range(1, 1 + len(self.map_rgb)), fontsize=8)

    # ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ #
    def plot_heatmap(self, species, ax_heatmap, ...):
        """
        Generisk metode for oppsett av heatmap for en gitt art.
        """
        ax_heatmap.set_title(f'{species} distribution', fontsize=12)
        ax_heatmap.set_xticks(range(len(self.map_rgb[0])))
        ax_heatmap.set_xticklabels(range(1, 1 + len(self.map_rgb[0])),
                                   fontsize=8, rotation=90)
        ax_heatmap.set_yticks(range(len(self.map_rgb)))
        ax_heatmap.set_yticklabels(range(1, 1 + len(self.map_rgb)), fontsize=8)

    def heatmap_herbivore(self):
        """
        Enkel metode for herbivore heatmap.
        """
        self.ax_cmap_herbi = self.plot_heatmap(Herbivore, ...)

    def heatmap_carnivore(self):
        """
        Enkel metode for carnivore heatmap.
        """
        self.ax_cmap_carni = self.plot_heatmap(Carnivore, ...)
    # ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑ #

    def fitness_histogram(self):
        """
        Setup for the histogram showing the distribution of fitness values for herbivores and
        carnivores.
        """
        if self.fitness_hist_bins is None:
            self.fitness_hist_bins = np.linspace(0, 1, 5)
        self.ax_fitness_hist.cla()
        fitness_data = self.island.get_weight_age_fitness('fitness')
        self.ax_fitness_hist.hist(fitness_data['Herbivore'],
                                  bins=self.fitness_hist_bins,
                                  histtype='step')
        self.ax_fitness_hist.hist(fitness_data['Carnivore'],
                                  bins=self.fitness_hist_bins,
                                  histtype='step')
        self.ax_fitness_hist.set_title('Fitness', fontsize=10)
        self.ax_fitness_hist.legend(['Herbivore', 'Carnivore'], frameon=False)

    def age_histogram(self):
        """
        Setup for the histogram showing the distribution of age values for herbivores and
        carnivores.
        """
        if self.age_hist_bins is None:
            self.age_hist_bins = np.linspace(0, 60, 4)
        self.ax_age_hist.cla()
        age_data = self.island.get_weight_age_fitness('age')
        self.ax_age_hist.hist(age_data['Herbivore'],
                              bins=self.age_hist_bins,
                              histtype='step')
        self.ax_age_hist.hist(age_data['Carnivore'],
                              bins=self.age_hist_bins,
                              histtype='step')
        self.ax_age_hist.set_title('Age', fontsize=10)
        self.ax_age_hist.legend(['Herbivore', 'Carnivore'], frameon=False)

    def weight_histogram(self):
        """
        Setup for the histogram showing the distribution of weight values for herbivores and
        carnivores.
        """
        if self.weight_hist_bins is None:
            self.weight_hist_bins = np.linspace(0, 60, 4)
        self.ax_weight_hist.cla()
        weight_data = self.island.get_weight_age_fitness('weight')
        self.ax_weight_hist.hist(weight_data['Herbivore'],
                                 bins=self.age_hist_bins,
                                 histtype='step')
        self.ax_weight_hist.hist(weight_data['Carnivore'],
                                 bins=self.age_hist_bins,
                                 histtype='step')
        self.ax_weight_hist.set_title('Weight', fontsize=10)
        self.ax_weight_hist.legend(['Herbivore', 'Carnivore'], frameon=False)

    # ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ #
    def plot_histogram(self, data, bins, ax, title):
        """
        Generisk funksjon for å plotte histogram for både Herbivore og Carnivore
        """
        ax.cla()
        ax.hist(data['Herbivore'], bins=bins, histtype='step', label='Herbivore')
        ax.hist(data['Carnivore'], bins=bins, histtype='step', label='Carnivore')
        ax.set_title(title, fontsize=10)
        ax.legend(frameon=False)

    def fitness_histogram(self):
        """
        Setup for the histogram showing the distribution of fitness values for herbivores and
        carnivores.
        """
        if self.fitness_hist_bins is None:
            self.fitness_hist_bins = np.linspace(0, 1, 5)
        fitness_data = self.island.get_weight_age_fitness('fitness')
        self.plot_histogram(fitness_data, self.fitness_hist_bins, self.ax_fitness_hist, 'Fitness')
    
    def age_histogram(self):
        """
        Setup for the histogram showing the distribution of age values for herbivores and
        carnivores.
        """
        if self.age_hist_bins is None:
            self.age_hist_bins = np.linspace(0, 60, 4)
        age_data = self.island.get_weight_age_fitness('age')
        self.plot_histogram(age_data, self.age_hist_bins, self.ax_age_hist, 'Age')
    # ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑ #

    def birth_and_death_count(self):
        """
        Setup for the bar plots showing the numbers of births and deaths the current year for both
        herbivores and carnivores.
        """
        data = {}
        herbivore_births, carnivore_births = self.island.get_birth_and_death(
            animal_property='birth')
        herbivore_deaths, carnivore_deaths = self.island.get_birth_and_death(
            animal_property='death')
        data['Herbivore births'] = herbivore_births
        data['Herbivore deaths'] = herbivore_deaths
        data['Carnivore births'] = carnivore_births
        data['Carnivore deaths'] = carnivore_deaths
        names = list(data.keys())
        values = list(data.values())
        self.ax_birth_and_death.cla()
        self.ax_birth_and_death.bar(names, values, color=['green', 'red', 'green', 'red'])
        self.ax_birth_and_death.set_title('Births and deaths this year', fontsize=10)
        self.ax_birth_and_death.set_ylim([0, sum(values)+1])
        self.ax_birth_and_death.set_xticks(range(0, len(names)))
        self.ax_birth_and_death.set_xticklabels(names, rotation=70, size=8)

    def create_figure(self):
        """
        The method that sets up the matplolib figure with associated subplots for synchronous
        visualization.
        """
        if self.fig is None:
            self.fig = plt.figure()
            gs = self.fig.add_gridspec(nrows=4,
                                       ncols=4,
                                       width_ratios=[0.25, 0.25, 0.25, 0.25],
                                       height_ratios=[0.25, 0.25, 0.25, 0.25],
                                       wspace=0.2,
                                       hspace=0.37
                                       )
            self.fig.suptitle('Simulating the ecosystem of Rossumøya', fontsize=20)
        #   self.fig.tight_layout()

        if self.ax_year_counter is None:
            self.ax_year_counter = self.fig.text(0.55, 0.4,
                                                 f'Year:{self.year}',
                                                 fontsize=17)

        if self.ax_pop_counter is None:
            self.ax_pop_counter = self.fig.text(0.7, 0.4,
                                                f'Population: {self.num_animals}',
                                                fontsize=17)
        if self.ax_map is None:
            self.ax_map = self.fig.add_subplot(gs[:1, :2])
            self.making_map()
            self.ax_map.set_title('Island map', fontsize=12)

        if self.ax_pop_line is None:
            self.ax_pop_line = self.fig.add_subplot(gs[:2, 2:])
            self.animal_count()
            self.ax_pop_line.set_title('Animal count')

        if self.ax_heatmap_herbi is None:
            self.ax_heatmap_herbi = self.fig.add_subplot(gs[1:2, :2])
            self.heatmap_herbivore()
            colorbar_herbi = self.ax_cmap_herbi
            cax_herbi = plt.axes([0.42, 0.523, 0.02, 0.15])
            self.ax_cmap_herbi = self.fig.colorbar(colorbar_herbi, cax=cax_herbi)

        if self.ax_heatmap_carni is None:
            self.ax_heatmap_carni = self.fig.add_subplot(gs[2:3, :2])
            self.heatmap_carnivore()
            colorbar_carni = self.ax_cmap_carni
            cax_carni = plt.axes([0.42, 0.318, 0.02, 0.15])
            self.ax_cmap_carni = self.fig.colorbar(colorbar_carni, cax=cax_carni)

        if self.ax_fitness_hist is None:
            self.ax_fitness_hist = self.fig.add_subplot(gs[3:, :1])
            self.fitness_histogram()

        if self.ax_age_hist is None:
            self.ax_age_hist = self.fig.add_subplot(gs[3:, 1:2])
            self.age_histogram()

        if self.ax_weight_hist is None:
            self.ax_weight_hist = self.fig.add_subplot(gs[3:, 2:3])
            self.weight_histogram()

        if self.ax_birth_and_death is None:
            self.ax_birth_and_death = self.fig.add_subplot(gs[3:, 3:])
            self.birth_and_death_count()

    def update_plots(self):
        """
        Method for updating all plots for each year that is simulated.
        """
        self.ax_year_counter.set_text(f'Year: {self.year}')
        self.ax_pop_counter.set_text(f'Population: {int(self.num_animals)}')
        self.animal_count()
        self.heatmap_herbivore()
        self.heatmap_carnivore()
        self.fitness_histogram()
        self.age_histogram()
        self.weight_histogram()
        self.birth_and_death_count()

        plt.pause(1e-2)

    def plot_to_file(self):
        """
        The method is called each time a screenshot of a plot is to be saved. The plot is saved
        with the specified file name in the folder of your choice. If the folder does not exist,
        the method creates a new folder based on the input string.
        """
        if not os.path.exists(self.img_dir):
            os.makedirs(self.img_dir)

        directory = os.path.abspath(f'{self.img_dir}')
        filename = f'{self.img_base}_{self.img_num:05d}.{self.img_fmt}'

        plt.savefig(os.path.join(directory, filename))
        self.img_num += 1

    def write_log_file(self, data):
        """
        This method writes the number of animals per species per year on a csv file with a
        self-chosen title.
        """
        file = open(self.log_file, 'a+', newline='')
        with file:
            write = csv.writer(file)
            for row in data:
                write.writerow(row)

    def simulate(self, num_years):
        """
        Run simulation while visualizing the result.

        :param num_years: number of years to simulate
        """
        self.final_year = self.year + num_years
        self.create_figure()
        data_to_csv = []
        while self.year < self.final_year:
            if self.graphics == 'On':
                if self.year % self.visualization_update_interval == 0:
                    self.update_plots()

                if self.img_save:
                    if self.year % self.img_years == 0:
                        self.plot_to_file()
            self._year += 1
            self.island.annual_cycle()
            data_to_csv.append([self.year, int(self.num_animals_per_species['Herbivore']),
                                int(self.num_animals_per_species['Carnivore'])])

        if self.log_file:
            self.write_log_file(data=data_to_csv)

    def add_population(self, population):
        """
        Add a population to the island

        :param population: List of dictionaries specifying population
        """
        self.island.place_populations_on_island(population)

    @property
    def year(self):
        """Last year simulated."""
        return self._year

    @property
    def num_animals(self):
        """Total number of animals on island."""
        return sum(self.num_animals_per_species.values())

    @property
    def num_animals_per_species(self):
        """Number of animals per species in island, as dictionary."""
        num_animals_per_species = \
            {'Herbivore': self.animal_distribution('Herbivore').to_numpy().sum().item(),
             'Carnivore': self.animal_distribution('Carnivore').to_numpy().sum().item()}
        return num_animals_per_species

    def animal_distribution(self, species):
        """
        The method calls on animal_counter in the class Iceland and inserts the data on the number
        of animals per cell in each Panda's Dataframe. Index and columns are set to be the number
        of rows and columns. Used to make density maps for herbivores and carnivores.
        :param species: string: 'Herbivore' or 'Carnivore'
        :return: pd.Dataframe
        """
        herbivores, carnivores, rows, cols = self.island.animal_counter()
        index = []
        for row in range(1, rows+1):
            index.append(str(row).zfill(1))
        columns = []
        for col in range(1, cols+1):
            columns.append(str(col).zfill(1))
        if species == 'Herbivore':
            pop_herbivores = pd.DataFrame(data=herbivores, index=index, columns=columns)
            pop_herbivores = pop_herbivores.astype(float)
            return pop_herbivores
        elif species == 'Carnivore':
            pop_carnivores = pd.DataFrame(data=carnivores, index=index, columns=columns)
            pop_carnivores = pop_carnivores.astype(float)
            return pop_carnivores
        else:
            raise ValueError('Wrong species input')

    def make_movie(self, movie_fmt=None):
        """
        Creating MPEG4 movie from saved plot images.
        Copyright (c) Hans Ekkehard Plesser
        """
        if self.img_base is None:
            raise RuntimeError("No filename defined.")

        if movie_fmt is None:
            movie_fmt = _DEFAULT_MOVIE_FORMAT

        if movie_fmt == 'mp4':
            try:
                # Parameters chosen according to http://trac.ffmpeg.org/wiki/Encode/H.264,
                # section "Compatibility"
                subprocess.check_call([_FFMPEG_BINARY,
                                       '-i', '{}/{}_%05d.png'.format(self.img_dir, self.img_base),
                                       '-y',
                                       '-profile:v', 'baseline',
                                       '-level', '2.0',
                                       '-pix_fmt', 'yuv420p',
                                       '{}/{}.{}'.format(self.img_dir, self.img_base, movie_fmt)])
            except subprocess.CalledProcessError as err:
                raise RuntimeError('ERROR: ffmpeg failed with: {}'.format(err))
