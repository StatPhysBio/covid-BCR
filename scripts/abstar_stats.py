#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to get sequence statistics of filtered lineages and nonsingletons.
    Copyright (C) 2020 Montague, Zachary

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from utils import *
import numpy as np
import operator
import collections
import numpy as np
from abstar_pipeline import merge_replicates, get_lineage_progenitor_cdr3, get_lineage_progenitor

def initialize_stats_dict() -> dict:
    """Creates dictionary that will contain sequence statistics for lineage progentiors and nonsingletons

    Parameters
    ----------
    None

    Returns
    -------
    stats_dict : dict
        Dictionary containing a list for each observable to be filled by examining
        the annotation for a lineage progenitor and all nonsingletons in a lineage.
     """

    stats_dict = {'nonsingletons': {'v gene': [],
                                    'j gene': [],
                                    'd gene': [],
                                    'cdr3 length': [],
                                    'vd ins': [],
                                    'dj ins': [],
                                    'vd del': [],
                                    'dj del': []},
                  'progenitors': {'v gene': [],
                                  'j gene': [],
                                  'd gene': [],
                                  'cdr3 length': [],
                                  'vd ins': [],
                                  'dj ins': [],
                                  'vd del': [],
                                  'dj del': []}}
    return stats_dict

def fill_dict(in_dict: dict, annotation: dict) -> None:
    """Examines a single annotation and adds the values of the observables to the dictionary lists.

    Parameters
    ----------
    in_dict : dict
        Dictionary either for lineage progenitors or nonsingletons of a lineage
        containing lists for each observable. See initialize_stats_dict()
    annotation : dict
        Dictionary containing annotation output for a sequence.

    Returns
    -------
    None
    """

    #  Gene statistics
    in_dict['v gene'].append(annotation['v_gene']['gene'])
    in_dict['j gene'].append(annotation['j_gene']['gene'])
    in_dict['d gene'].append(annotation['d_gene']['gene'])

    #  CDR3 statistics
    in_dict['cdr3 length'].append(len(annotation['junc_nt']))

    #  Insertion statistics
    in_dict['vd ins'].append(len(annotation['junc_nt_breakdown']['n1_nt']))
    in_dict['dj ins'].append(len(annotation['junc_nt_breakdown']['n2_nt']))

    #  Deletion statistics
    in_dict['vd del'].append(annotation['exo_trimming']['var_3']
                             + annotation['exo_trimming']['div_5'])
    in_dict['dj del'].append(annotation['exo_trimming']['div_3']
                             + annotation['exo_trimming']['join_5'])

def get_stats(stats_dict: dict, lineage: list):
    """Records statistics of annotations in a lineage.

    Parameters
    ----------
    stats_dict : dict
        Dictionary containing statistics of sequence observables for lineage
        progenitors and nonsingletons.
    lineage : list
        List of annotations.
    Returns
    -------
    None
    """

    progenitor_cdr3 = get_lineage_progenitor_cdr3(lineage)
    if progenitor_cdr3 == '' or len(lineage) < 3:
        return
    progenitor_sequence = get_lineage_progenitor(lineage)
    progenitor_stats_recorded = False

    for j, annotation in enumerate(lineage):
        #  Get statistics for the lineage progenitor. The lineage progenitor annotation
        #  might come from a singleton or nonsingleton.
        if progenitor_stats_recorded == False and annotation['vdj_germ_nt'] == progenitor_sequence:
            fill_dict(stats_dict['progenitors'], annotation)
            progenitor_stats_recorded = True
        #  Get statistics for nonsingletons only.
        if get_abundance(annotation['seq_id']) == 1:
            continue
        fill_dict(stats_dict['nonsingletons'], annotation)

def create_stats_file(infile: str) -> None:
    """Obtains lineages from the file and obtains the statistics.

    Parameters
    ----------
    infile : str
        String to path of lineage json file.
    Returns
    -------
    None
    """

    file_name = infile.split("/")[-1]
    patient = file_name.split("_")[0]
    save_dir = '/gscratch/stf/zachmon/covid/stats/'
    save_name = save_dir + patient + "_final_stats.json"
    lineages = merge_replicates(json_open(in_file)['productive'], productive=True)
    stats_dict = initialize_stats_dict()

    #  Loop over all lineages.
    for key in lineages:
       get_stats(stats_dict, lineages[key])
    json_save(save_name, stats_dict)

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Gets relevant stats of productive lineage progenitors '
                    'and nonsingletons in productive lineages')
    parser.add_argument('--infile', type=str, help='path to abstar lineage json file')
    args = parser.parse_args()
    create_stats_file(args.infile)

if __name__ == '__main__':
    main()