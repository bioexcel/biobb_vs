#!/usr/bin/env python3

"""Module containing the BindingSite class and the command line interface."""
import argparse
import os
from biobb_common.configuration import  settings
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger
from biobb_common.command_wrapper import cmd_wrapper
from biobb_vs.utils.common import *

class BindingSite():
    """Finds the binding site of the input_pdb file based on the ligands' location of similar structures (members of the sequence identity cluster)

    Args:
        output_pdb_path (str): Path to the PDB containig the residues belonging to the binding site. File type: output. `Sample file <>`_. Accepted formats: pdb.
        properties (dic):
            * **pdb_code** (*str*) - ('2VGB') PDB code for the protein structure where the binding site is to be found
            * **pdb_chain** (*str*) - ('A') Chain id for the pdb_code where to binding site is to be find
            * **ligand** (*str*) - ('PGA') Ligand to be found in the protein structure
            * **radius** (*float*) - (5.0) Cut-off distance(Amstrongs) around ligand atoms to consider a protein atom as a binding site atom.
            * **identity_cluster** (*int*) - (90) Minimal sequence identity (%) of the cluster members shared with the input_pdb. Values: 95, 90, 75, 50.
            * **max_num_ligands** (*int*) - (15) Total number of superimposed ligands to be extracted from the identity cluster. For populated clusters, the restriction avoids to superimpose redundant structures. If 0, all ligands extracted will be considered.
            * **matrix_name** (*str*) - ('blosum62') Substitution matrices for use in alignments. Values: 'benner6', 'benner22', 'benner74', 'blosum100', 'blosum30', 'blosum35', 'blosum40', 'blosum45', 'blosum50', 'blosum55', 'blosum60', 'blosum62', 'blosum65', 'blosum70', 'blosum75', 'blosum80', 'blosum85', 'blosum90', 'blosum95', 'feng', 'fitch', 'genetic', 'gonnet', 'grant', 'ident', 'johnson', 'levin', 'mclach', 'miyata', 'nwsgappep', 'pam120', 'pam180', 'pam250', 'pam30', 'pam300', 'pam60', 'pam90', 'rao', 'risler', 'structure'.
            * **gap_open** (*float*) - (-10.0) Gap open penalty.
            * **gap_extend** (*float*) - (-0.5) Gap extend penalty.
            * **trim_ends** (*bool*) - (True) Cut unaligned sequence ends.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.
    """

    def __init__(self, output_pdb_path, properties=None, **kwargs) -> None:
        properties = properties or {}

        # Input/Output files
        self.io_dict = { 
            "out": { "output_pdb_path": output_pdb_path } 
        }

        # Properties specific for BB
        self.vina_path = properties.get('vina_path', 'vina')
        self.properties = properties

        # Properties common in all BB
        self.can_write_console_log = properties.get('can_write_console_log', True)
        self.global_log = properties.get('global_log', None)
        self.prefix = properties.get('prefix', None)
        self.step = properties.get('step', None)
        self.path = properties.get('path', '')
        self.remove_tmp = properties.get('remove_tmp', True)
        self.restart = properties.get('restart', False)

    def check_data_params(self, out_log, err_log):
        """ Checks all the input/output paths and parameters """
        self.io_dict["out"]["output_pdb_path"] = check_output_path(self.io_dict["out"]["output_pdb_path"],"output_pdb_path", False, out_log, self.__class__.__name__)


    @launchlogger
    def launch(self) -> int:
        """Launches the execution of the BindingSite module."""

        # Get local loggers from launchlogger decorator
        out_log = getattr(self, 'out_log', None)
        err_log = getattr(self, 'err_log', None)

        # check input/output paths and parameters
        self.check_data_params(out_log, err_log)

        # Check the properties
        fu.check_properties(self, self.properties)

        if self.restart:
            output_file_list = [self.io_dict["out"]["output_pdb_path"]]
            if fu.check_complete_files(output_file_list):
                fu.log('Restart is enabled, this step: %s will the skipped' % self.step, out_log, self.global_log)
                return 0

        

        #return returncode
        return 0

def main():
    parser = argparse.ArgumentParser(description="Finds the binding site of the input_pdb file based on the ligands' location of similar structures (members of the sequence identity cluster)", formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('--config', required=False, help='Configuration file')

    # Specific args of each building block
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--output_pdb_path', required=True, help='Path to the PDB containig the residues belonging to the binding site. Accepted formats: pdb.')

    args = parser.parse_args()
    args.config = args.config or "{}"
    properties = settings.ConfReader(config=args.config).get_prop_dic()

    # Specific call of each building block
    BindingSite(output_pdb_path=args.output_pdb_path, 
                   properties=properties).launch()

if __name__ == '__main__':
    main()
