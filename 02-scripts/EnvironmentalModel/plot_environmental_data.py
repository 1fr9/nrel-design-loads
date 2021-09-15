# %%
# Load data, preprocess them, plot them

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import csv, math


dpi_for_printing_figures = 300

paths = ['Data/DForNREL.txt', 'Data/artificial_time_series_50years.txt']
suffixes = ['coastdat', 'artificial50']
for path, suffix in zip(paths, suffixes):
    v = list()
    hs = list()
    tz = list()
    tp = list()
    with open(path, newline='') as csv_file:
        reader = csv.reader(csv_file, delimiter=';')
        idx = 0
        for row in reader:
            if idx == 0:
                v_label = row[1][1:] # Ignore first char (is a white space).
                hs_label = row[2][1:] # Ignore first char (is a white space).
                tz_label = row[3][1:] # Ignore first char (is a white space).
            if idx > 0: # Ignore the header
                v.append(float(row[1]))
                hs.append(float(row[2]))
                tz.append(float(row[3]))
            idx = idx + 1
    v_label = '1-hour mean wind speed at hub height (m s$^{-1}$)'
    tp_label = 'Spectral peak period (s)'

    hs = np.array(hs)
    v = np.array(v) # This is the 1-h wind speed at hub height, see IEC 61400-1:2019 p. 34
    tz = np.array(tz)
    tp = 1.2796 * tz # Assuming a JONSWAP spectrum with gamma = 3.3

    g = 9.81
    steepness = 2 * math.pi * hs / ( g * tp ** 2)
    steepness_label = 'Steepness (-)'

    fig_rawdata, axs = plt.subplots(1, 2, figsize=(9.8, 4), dpi=300, sharey=True)
    h0 = axs[0].scatter(v, hs, c=steepness, s=5, rasterized=True, cmap='jet')
    axs[0].set_xlabel(v_label)
    axs[0].set_ylabel(hs_label)
    axs[0].spines['right'].set_visible(False)
    axs[0].spines['top'].set_visible(False)
    
    h1 = axs[1].scatter(tp, hs, c=steepness, s=5, rasterized=True, cmap='jet')

    # Calculate a constant steepness curves
    hs_s = np.arange(0.1, 11, 0.2)
    const_ss =  1 / np.array([15, 20, 30, 40, 50])
    for const_s in const_ss:
        tp_s = np.sqrt((2 * math.pi * hs_s) / (g * const_s))
        axs[1].plot(tp_s, hs_s, c='k')
    axs[1].text(8, 8, 'Steepness = 1/15', fontsize=8, rotation=71,
        horizontalalignment='center', verticalalignment='center',
        c='k')
    axs[1].text(11.5, 11.1, '1/20', fontsize=8, horizontalalignment='center', 
        c='k')
    axs[1].text(14.2, 11.1, '1/30', fontsize=8, horizontalalignment='center', 
        c='k')
    axs[1].text(16.7, 11.1, '1/40', fontsize=8, horizontalalignment='center', 
        c='k')
    axs[1].text(18.9, 11.1, '1/50', fontsize=8, horizontalalignment='center', 
        c='k')
    axs[1].set_xlabel(tp_label)
    axs[1].set_ylabel(hs_label)
    axs[1].spines['right'].set_visible(False)
    axs[1].spines['top'].set_visible(False)
    h0.set_clim(1/60, 1/17)
    h1.set_clim(1/60, 1/17)
    c = fig_rawdata.colorbar(h1, ax=axs, orientation='vertical', fraction=.1)
    c.set_label(steepness_label)

    axs[0].set_xlim(0, 41)
    axs[1].set_xlim(0, 19)
    axs[0].set_ylim(0, 12.5)
    axs[1].set_ylim(0, 12.5)

    fname = 'gfx/EnvironmentalDataset_' + suffix
    fig_rawdata.savefig(fname + '.png', bbox_inches='tight')
    fig_rawdata.savefig(fname + '.pdf', bbox_inches='tight')

fig_sim_points, axs = plt.subplots(1, 2, figsize=(9.2, 4), dpi=300, sharey=True)
inc = 2
hs_sim = np.append(0, np.arange(1, 15 + inc, inc))
inc = 2
v_sim = np.arange(1, 25 + inc, inc)
v_sim = np.append(v_sim, np.array([26, 30, 35, 40, 45]))
vgrid, hsgrid = np.meshgrid(v_sim, hs_sim)
axs[0].scatter(v, hs, c='black', s=5, alpha=0.5, rasterized=True)
axs[0].scatter(vgrid, hsgrid, c='red', s=9, marker='D')

verts = [(-0.5, 8), (10, 8), (10, 10), (16, 10), (16, 12), (20, 12), (20, 15.5), (-0.5, 15.5)]
poly = Polygon(verts, facecolor='1', edgecolor='1')
axs[0].add_patch(poly)

axs[0].set_xlabel(v_label)
axs[0].set_ylabel(hs_label)
axs[0].spines['right'].set_visible(False)
axs[0].spines['top'].set_visible(False)
axs[1].scatter(tp, hs, c='black', s=5, alpha=0.5, rasterized=True)
hs_s = np.arange(0, 15, 0.1)
sps = [1/15, 1/20]
for i in range(2):
    sp = sps[i]
    tp_s = np.sqrt((2 * math.pi * hs_s) / (g * sp))
    axs[1].plot(tp_s, hs_s, c='blue', zorder=9)
    tp_sim = np.sqrt((2 * math.pi * hs_sim) / (g * sp))
    axs[1].scatter(tp_sim, hs_sim, c='red', s=9, marker='D', zorder=10)
    tpid = str(i + 1)
    plt.text(tp_s[-1], hs_s[-1] + 0.6, r'$t_{p' + tpid + r'}$', horizontalalignment='center')
add_to_tp = [8, 20]
for i in range(2):
    tp_splus = tp_s + 1 / (1 + np.power(hs_s + 2, 0.5)) * add_to_tp[i]
    axs[1].plot(tp_splus, hs_s, c='blue', zorder=9)
    axs[1].scatter(tp_sim + 1 / (1 + np.power(hs_sim + 2, 0.5)) * add_to_tp[i], hs_sim, c='red',  s=9, marker='D', zorder=10)
    tpid = str(i + 3)
    plt.text(tp_splus[-1], hs_s[-1] + 0.6, r'$t_{p' + tpid + r'}$', horizontalalignment='center')

axs[1].set_xlabel(tp_label)
axs[1].set_ylabel(hs_label)
axs[1].spines['right'].set_visible(False)
axs[1].spines['top'].set_visible(False)
fig_sim_points.savefig('gfx/SimulationPoints.pdf', bbox_inches='tight')
fig_sim_points.savefig('gfx/SimulationPoints.jpg', bbox_inches='tight')