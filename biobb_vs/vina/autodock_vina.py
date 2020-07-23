#!/usr/bin/env python3

"""Module containing the AutoDockVina class and the command line interface."""
import argparse
import os
from biobb_common.configuration import  settings
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger
from biobb_common.command_wrapper import cmd_wrapper
from biobb_vs.vina.common import *

class AutoDockVina():
    """Docking of the ligand to a set of grids describing the target protein.
    Wrapper of the AutoDock Vina software
    Visit the `AutoDock official website <http://vina.scripps.edu/index.html>`_. 

    Args:
        input_ligand_pdbqt_path (str): Path to the input PDBQT ligand. File type: input. `Sample file <>`_. Accepted formats: pdbqt.
        input_receptor_pdbqt_path (str): Path to the input PDBQT receptor. File type: input. `Sample file <>`_. Accepted formats: pdbqt.
        input_box_path (str): Path to the PDB containig the residues belonging to the binding site. File type: input. `Sample file <>`_. Accepted formats: pdb.
        output_pdbqt_path (str): Path to the output PDBQT file. File type: output. `Sample file <>`_. Accepted formats: pdbqt.
        output_log_path (str) (Optional): Path to the log file. File type: output. `Sample file <>`_. Accepted formats: log.
        properties (dic):
            * **vina_path** (*string*) - ('vina') path to vina in your local computer.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.
    """

    def __init__(self, input_ligand_pdbqt_path, input_receptor_pdbqt_path, input_box_path,
                 output_pdbqt_path, output_log_path=None, properties=None, **kwargs) -> None:
        properties = properties or {}

        # Input/Output files
        self.io_dict = { 
            "in": { "input_ligand_pdbqt_path": input_ligand_pdbqt_path, "input_receptor_pdbqt_path": input_receptor_pdbqt_path, "input_box_path": input_box_path }, 
            "out": { "output_pdbqt_path": output_pdbqt_path, "output_log_path": output_log_path } 
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
        self.io_dict["in"]["input_ligand_pdbqt_path"] = check_input_path(self.io_dict["in"]["input_ligand_pdbqt_path"], "input_ligand_pdbqt_path", out_log, self.__class__.__name__)
        self.io_dict["in"]["input_receptor_pdbqt_path"] = check_input_path(self.io_dict["in"]["input_receptor_pdbqt_path"], "input_receptor_pdbqt_path", out_log, self.__class__.__name__)
        self.io_dict["in"]["input_box_path"] = check_input_path(self.io_dict["in"]["input_box_path"], "input_box_path", out_log, self.__class__.__name__)
        self.io_dict["out"]["output_pdbqt_path"] = check_output_path(self.io_dict["out"]["output_pdbqt_path"],"output_pdbqt_path", False, out_log, self.__class__.__name__)
        self.io_dict["out"]["output_log_path"] = check_output_path(self.io_dict["out"]["output_log_path"],"output_log_path", True, out_log, self.__class__.__name__)

    def calculate_box(self, box_file_path):
        with open(box_file_path, 'r') as box_file:
            for line in box_file:
                line = line.rstrip(os.linesep)
                if line.startswith("REMARK BOX CENTER"):
                    fields = line.split()
                    center = fields[3:6]
                    size = fields[-3:]
                    return list(map(str, [center[0], center[1], center[2], size[0], size[1], size[2]]))
            return list(map(str, [0, 0 ,0, 0, 0, 0]))

    @launchlogger
    def launch(self) -> int:
        """Launches the execution of the AutoDockVina module."""

        # Get local loggers from launchlogger decorator
        out_log = getattr(self, 'out_log', None)
        err_log = getattr(self, 'err_log', None)

        # check input/output paths and parameters
        self.check_data_params(out_log, err_log)

        # Check the properties
        fu.check_properties(self, self.properties)

        if self.restart:
            output_file_list = [self.io_dict["out"]["output_pdbqt_path"],self.io_dict["out"]["output_log_path"]]
            if fu.check_complete_files(output_file_list):
                fu.log('Restart is enabled, this step: %s will the skipped' % self.step, out_log, self.global_log)
                return 0

        # calculating box position and size
        x0, y0, z0, sidex, sidey, sidez = self.calculate_box(self.io_dict["in"]["input_box_path"])

        # create cmd
        cmd = [self.vina_path,
               '--ligand', self.io_dict["in"]["input_ligand_pdbqt_path"],
               '--receptor', self.io_dict["in"]["input_receptor_pdbqt_path"],
               '--center_x=' + x0, '--center_y=' + y0, '--center_z=' + z0,
               '--size_x=' + sidex, '--size_y=' + sidey, '--size_z=' + sidez,
               '--out', self.io_dict["out"]["output_pdbqt_path"],
               '--log', self.io_dict["out"]["output_log_path"]]

        fu.log('Executing AutoDock Vina', out_log, self.global_log)

        cmd = fu.create_cmd_line(cmd, out_log=out_log, global_log=self.global_log)
        returncode = cmd_wrapper.CmdWrapper(cmd, out_log, err_log, self.global_log).launch()

        return returncode

def main():
    parser = argparse.ArgumentParser(description="Prepares input ligand for an Autodock Vina Virtual Screening.", formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('--config', required=False, help='Configuration file')

    # Specific args of each building block
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--input_ligand_pdbqt_path', required=True, help='Path to the input PDBQT ligand. Accepted formats: pdbqt.')
    required_args.add_argument('--input_receptor_pdbqt_path', required=True, help='Path to the input PDBQT receptor. Accepted formats: pdbqt.')
    required_args.add_argument('--input_box_path', required=True, help='Path to the PDB containig the residues belonging to the binding site. Accepted formats: pdb.')
    required_args.add_argument('--output_pdbqt_path', required=True, help='Path to the output PDBQT file. Accepted formats: pdbqt.')
    parser.add_argument('--output_log_path', required=False, help='Path to the log file. Accepted formats: log.')

    args = parser.parse_args()
    args.config = args.config or "{}"
    properties = settings.ConfReader(config=args.config).get_prop_dic()

    # Specific call of each building block
    AutoDockVina(input_ligand_pdbqt_path=args.input_ligand_pdbqt_path, input_receptor_pdbqt_path=args.input_receptor_pdbqt_path, input_box_path=args.input_box_path,
                   output_pdbqt_path=args.output_pdbqt_path, output_log_path=args.output_log_path, 
                   properties=properties).launch()

if __name__ == '__main__':
    main()
