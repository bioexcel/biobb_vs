#!/usr/bin/env python3

"""Module containing the AutoDockVinaRun class and the command line interface."""
import argparse
import os
from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.configuration import  settings
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger
from biobb_common.command_wrapper import cmd_wrapper
from biobb_vs.vina.common import *


class AutoDockVinaRun(BiobbObject):
    """
    | biobb_vs AutoDockVinaRun
    | Wrapper of the AutoDock Vina software.
    | This class performs docking of the ligand to a set of grids describing the target protein via the `AutoDock Vina <http://vina.scripps.edu/index.html>`_ software.

    Args:
        input_ligand_pdbqt_path (str): Path to the input PDBQT ligand. File type: input. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/vina/vina_ligand.pdbqt>`_. Accepted formats: pdbqt (edam:format_1476).
        input_receptor_pdbqt_path (str): Path to the input PDBQT receptor. File type: input. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/vina/vina_receptor.pdbqt>`_. Accepted formats: pdbqt (edam:format_1476).
        input_box_path (str): Path to the PDB containig the residues belonging to the binding site. File type: input. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/vina/vina_box.pdb>`_. Accepted formats: pdb (edam:format_1476).
        output_pdbqt_path (str): Path to the output PDBQT file. File type: output. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/vina/ref_output_vina.pdbqt>`_. Accepted formats: pdbqt (edam:format_1476).
        output_log_path (str) (Optional): Path to the log file. File type: output. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/vina/ref_output_vina.log>`_. Accepted formats: log (edam:format_2330).
        properties (dic - Python dictionary object containing the tool parameters, not input/output files):
            * **vina_path** (*string*) - ('vina') path to vina in your local computer.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.

    Examples:
        This is a use example of how to use the building block from Python::

            from biobb_vs.vina.autodock_vina_run import autodock_vina_run
            prop = { 
                'vina_path': 'vina'
            }
            autodock_vina_run(input_ligand_pdbqt_path='/path/to/myLigand.pdbqt', 
                            input_receptor_pdbqt_path='/path/to/myReceptor.pdbqt', 
                            input_box_path='/path/to/myBox.pdb', 
                            output_pdbqt_path='/path/to/newStructure.pdbqt', 
                            output_log_path='/path/to/newLog.log', 
                            properties=prop)

    Info:
        * wrapped_software:
            * name: Autodock Vina
            * version: >=1.1.2
            * license: Apache-2.0
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl

    """

    def __init__(self, input_ligand_pdbqt_path, input_receptor_pdbqt_path, input_box_path, output_pdbqt_path, 
                output_log_path=None, properties=None, **kwargs) -> None:
        properties = properties or {}

        # Call parent class constructor
        super().__init__(properties)

        # Input/Output files
        self.io_dict = { 
            "in": { "input_ligand_pdbqt_path": input_ligand_pdbqt_path, "input_receptor_pdbqt_path": input_receptor_pdbqt_path, "input_box_path": input_box_path }, 
            "out": { "output_pdbqt_path": output_pdbqt_path, "output_log_path": output_log_path } 
        }

        # Properties specific for BB
        self.vina_path = properties.get('vina_path', 'vina')
        self.properties = properties

        # Check the properties
        self.check_properties(properties)

    def check_data_params(self, out_log, err_log):
        """ Checks all the input/output paths and parameters """
        self.io_dict["in"]["input_ligand_pdbqt_path"] = check_input_path(self.io_dict["in"]["input_ligand_pdbqt_path"], "input_ligand_pdbqt_path", self.out_log, self.__class__.__name__)
        self.io_dict["in"]["input_receptor_pdbqt_path"] = check_input_path(self.io_dict["in"]["input_receptor_pdbqt_path"], "input_receptor_pdbqt_path", self.out_log, self.__class__.__name__)
        self.io_dict["in"]["input_box_path"] = check_input_path(self.io_dict["in"]["input_box_path"], "input_box_path", self.out_log, self.__class__.__name__)
        self.io_dict["out"]["output_pdbqt_path"] = check_output_path(self.io_dict["out"]["output_pdbqt_path"],"output_pdbqt_path", False, self.out_log, self.__class__.__name__)
        self.io_dict["out"]["output_log_path"] = check_output_path(self.io_dict["out"]["output_log_path"],"output_log_path", True, self.out_log, self.__class__.__name__)

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
        """Execute the :class:`AutoDockVinaRun_run <vina.autodock_vina_run.AutoDockVinaRun_run>` vina.autodock_vina_run.AutoDockVinaRun_run object."""

        # check input/output paths and parameters
        self.check_data_params(self.out_log, self.err_log)

        # Setup Biobb
        if self.check_restart(): return 0
        self.stage_files()

        # calculating box position and size
        x0, y0, z0, sidex, sidey, sidez = self.calculate_box(self.io_dict["in"]["input_box_path"])

        # in case ligand or receptor end with END, remove last line
        #check_input_autodock(self.io_dict["in"]["input_ligand_pdbqt_path"], self.out_log)
        #check_input_autodock(self.io_dict["in"]["input_receptor_pdbqt_path"], self.out_log)

        # create cmd
        self.cmd = [self.vina_path,
               '--ligand', self.io_dict["in"]["input_ligand_pdbqt_path"],
               '--receptor', self.io_dict["in"]["input_receptor_pdbqt_path"],
               '--center_x=' + x0, '--center_y=' + y0, '--center_z=' + z0,
               '--size_x=' + sidex, '--size_y=' + sidey, '--size_z=' + sidez,
               '--out', self.io_dict["out"]["output_pdbqt_path"],
               '--log', self.io_dict["out"]["output_log_path"]]

        fu.log('Executing AutoDock Vina', self.out_log, self.global_log)

        # Run Biobb block
        self.run_biobb()

        # Copy files to host
        self.copy_to_host()

        return self.return_code

def autodock_vina_run(input_ligand_pdbqt_path: str, input_receptor_pdbqt_path: str, input_box_path: str, output_pdbqt_path:str, output_log_path: str = None, properties: dict = None, **kwargs) -> int:
    """Execute the :class:`AutoDockVinaRun <vina.autodock_vina_run.AutoDockVinaRun>` class and
    execute the :meth:`launch() <vina.autodock_vina_run.AutoDockVinaRun.launch>` method."""

    return AutoDockVinaRun(input_ligand_pdbqt_path=input_ligand_pdbqt_path,
                input_receptor_pdbqt_path=input_receptor_pdbqt_path,
                input_box_path=input_box_path,
                output_pdbqt_path=output_pdbqt_path,
                output_log_path=output_log_path,
                properties=properties, **kwargs).launch()

def main():
    """Command line execution of this building block. Please check the command line documentation."""
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
    autodock_vina_run(input_ligand_pdbqt_path=args.input_ligand_pdbqt_path, 
                    input_receptor_pdbqt_path=args.input_receptor_pdbqt_path, 
                    input_box_path=args.input_box_path,
                    output_pdbqt_path=args.output_pdbqt_path, 
                    output_log_path=args.output_log_path, 
                    properties=properties)

if __name__ == '__main__':
    main()
