#!/usr/bin/env python3

"""Module containing the BoxResidues class and the command line interface."""

import argparse
import warnings
from pathlib import PurePath
from typing import Optional

import numpy as np
from Bio import BiopythonDeprecationWarning
from biobb_common.configuration import settings
from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger

from biobb_vs.utils.common import (
    _from_string_to_list,
    check_input_path,
    check_output_path,
    get_box_coordinates,
)

with warnings.catch_warnings():
    warnings.simplefilter("ignore", BiopythonDeprecationWarning)
    # try:
    #    import Bio.SubsMat.MatrixInfo
    # except ImportError:
    import Bio.Align.substitution_matrices
    import Bio.pairwise2
    import Bio.PDB


class BoxResidues(BiobbObject):
    """
    | biobb_vs BoxResidues
    | This class sets the center and the size of a rectangular parallelepiped box around a set of residues.
    | Sets the center and the size of a rectangular parallelepiped box around a selection of residues found in a given PDB. The residue identifiers that compose the selection (i.e. binding site) are provided by a property list.

    Args:
        input_pdb_path (str): PDB protein structure for which the box will be build. Its size and center will be set around the 'resid_list' property once mapped against this PDB. File type: input. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/utils/input_box_residues.pdb>`_. Accepted formats: pdb (edam:format_1476).
        output_pdb_path (str): PDB including the annotation of the box center and size as REMARKs. File type: output. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/utils/ref_output_box_residues.pdb>`_. Accepted formats: pdb (edam:format_1476).
        properties (dic - Python dictionary object containing the tool parameters, not input/output files):
            * **resid_list** (*list*) - (None) List with all the residue numbers to form a cavity or binding site. Mandatory property.
            * **offset** (*float*) - (2.0) [0.1~1000|0.1] Extra distance (Angstroms) between the last residue atom and the box boundary.
            * **box_coordinates** (*bool*) - (False) Add box coordinates as 8 ATOM records.
            * **residue_offset** (*int*) - (0) [0~1000|1] Residue id offset.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.
            * **sandbox_path** (*str*) - ("./") [WF property] Parent path to the sandbox directory.

    Examples:
        This is a use example of how to use the building block from Python::

            from biobb_vs.utils.box_residues import box_residues
            prop = {
                'resid_list': [718, 743, 745, 762, 766, 796, 790, 791, 793, 794, 788],
                'offset': 2,
                'box_coordinates': True
            }
            box_residues(input_pdb_path='/path/to/myStructure.pdb',
                        output_pdb_path='/path/to/newBox.pdb',
                        properties=prop)

    Info:
        * wrapped_software:
            * name: In house using Biopython
            * version: >=1.76
            * license: Apache-2.0
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl

    """

    def __init__(
        self, input_pdb_path, output_pdb_path, properties=None, **kwargs
    ) -> None:
        properties = properties or {}

        # Call parent class constructor
        super().__init__(properties)
        self.locals_var_dict = locals().copy()

        # Input/Output files
        self.io_dict = {
            "in": {"input_pdb_path": input_pdb_path},
            "out": {"output_pdb_path": output_pdb_path},
        }

        # Properties specific for BB
        self.resid_list = _from_string_to_list(properties.get("resid_list", []))
        self.offset = float(properties.get("offset", 2.0))
        self.box_coordinates = float(properties.get("box_coordinates", False))
        self.residue_offset = properties.get("residue_offset", 0)
        self.properties = properties

        # Check the properties
        self.check_properties(properties)
        self.check_arguments()

    def check_data_params(self, out_log, err_log):
        """Checks all the input/output paths and parameters"""
        self.io_dict["in"]["input_pdb_path"] = check_input_path(
            self.io_dict["in"]["input_pdb_path"],
            "input_pdb_path",
            self.out_log,
            self.__class__.__name__,
        )
        self.io_dict["out"]["output_pdb_path"] = check_output_path(
            self.io_dict["out"]["output_pdb_path"],
            "output_pdb_path",
            False,
            self.out_log,
            self.__class__.__name__,
        )

    @launchlogger
    def launch(self) -> int:
        """Execute the :class:`BoxResidues <utils.box_residues.BoxResidues>` utils.box_residues.BoxResidues object."""

        # check input/output paths and parameters
        self.check_data_params(self.out_log, self.err_log)

        # Setup Biobb
        if self.check_restart():
            return 0
        self.stage_files()

        # Parse structure
        fu.log(
            "Loading input PDB structure %s" % (self.io_dict["in"]["input_pdb_path"]),
            self.out_log,
            self.global_log,
        )
        structure_name = PurePath(self.io_dict["in"]["input_pdb_path"]).name
        parser = Bio.PDB.PDBParser(QUIET=True)
        structPDB = parser.get_structure(
            structure_name, self.io_dict["in"]["input_pdb_path"]
        )

        if len(structPDB):
            structPDB = structPDB[0]

        # Mapping residue structure into input structure

        fu.log(
            "Mapping residue structure into input structure",
            self.out_log,
            self.global_log,
        )

        # Listing residues to be selected from the residue structure
        residPDB_res_list = []
        for residPDB_res in self.resid_list:
            if self.residue_offset:
                residPDB_res_list.append((" ", residPDB_res + self.residue_offset, " "))
            else:
                residPDB_res_list.append((" ", residPDB_res, " "))

        selection_res_list = []
        selection_atoms_num = 0
        for struct_chain in structPDB:
            for struct_res in struct_chain:
                if struct_res.get_id() in residPDB_res_list:
                    selection_res_list.append(struct_res)
                    selection_atoms_num += len(struct_res.get_list())

        if len(selection_res_list) == 0:
            fu.log(
                self.__class__.__name__
                + ": Cannot match any of the residues listed in [%s] into %s"
                % (
                    ", ".join(str(v) for v in self.resid_list),
                    self.io_dict["in"]["input_pdb_path"],
                ),
                self.out_log,
            )
            raise SystemExit(
                self.__class__.__name__
                + ": Cannot match any of the residues listed in [%s] into %s"
                % (
                    ", ".join(str(v) for v in self.resid_list),
                    self.io_dict["in"]["input_pdb_path"],
                )
            )
        elif len(selection_res_list) != len(residPDB_res_list):
            fu.log(
                "Cannot match all the residues listed in %s into %s. Found %s out of %s"
                % (
                    ", ".join(str(v) for v in self.resid_list),
                    self.io_dict["in"]["input_pdb_path"],
                    len(selection_res_list),
                    len(residPDB_res_list),
                ),
                self.out_log,
            )
        else:
            fu.log(
                "Selection of residues successfully matched",
                self.out_log,
                self.global_log,
            )

        # Compute binding site box size

        # compute box center
        selection_box_center = (
            sum(atom.coord for res in selection_res_list for atom in res.get_atoms())
            / selection_atoms_num
        )
        fu.log(
            "Binding site center (Angstroms): %10.3f%10.3f%10.3f"
            % (
                selection_box_center[0],
                selection_box_center[1],
                selection_box_center[2],
            ),
            self.out_log,
            self.global_log,
        )

        # compute box size
        selection_coords_max = np.amax(
            [atom.coord for res in selection_res_list for atom in res.get_atoms()],
            axis=0,
        )
        selection_box_size = selection_coords_max - selection_box_center
        if self.offset:
            selection_box_size = [c + self.offset for c in selection_box_size]
        fu.log(
            "Binding site size (Angstroms):   %10.3f%10.3f%10.3f"
            % (selection_box_size[0], selection_box_size[1], selection_box_size[2]),
            self.out_log,
            self.global_log,
        )

        # compute volume
        vol = np.prod(selection_box_size) * 2**3
        fu.log("Volume (cubic Angstroms): %.0f" % (vol), self.out_log, self.global_log)

        # add box details as PDB remarks
        remarks = "REMARK BOX CENTER:%10.3f%10.3f%10.3f" % (
            selection_box_center[0],
            selection_box_center[1],
            selection_box_center[2],
        )
        remarks += " SIZE:%10.3f%10.3f%10.3f" % (
            selection_box_size[0],
            selection_box_size[1],
            selection_box_size[2],
        )

        selection_box_coords_txt = ""
        # add (optional) box coordinates as 8 ATOM records
        if self.box_coordinates:
            fu.log("Adding box coordinates", self.out_log, self.global_log)
            selection_box_coords_txt = get_box_coordinates(
                selection_box_center, selection_box_size
            )

        with open(self.io_dict["out"]["output_pdb_path"], "w") as f:
            f.seek(0, 0)
            f.write(remarks.rstrip("\r\n") + "\n" + selection_box_coords_txt)

        fu.log(
            "Saving output PDB file (with box setting annotations): %s"
            % (self.io_dict["out"]["output_pdb_path"]),
            self.out_log,
            self.global_log,
        )

        # Copy files to host
        self.copy_to_host()

        self.tmp_files.extend([self.stage_io_dict.get("unique_dir", "")])
        self.remove_tmp_files()

        return 0


def box_residues(
    input_pdb_path: str,
    output_pdb_path: str,
    properties: Optional[dict] = None,
    **kwargs,
) -> int:
    """Execute the :class:`BoxResidues <utils.box_residues.BoxResidues>` class and
    execute the :meth:`launch() <utils.box_residues.BoxResidues.launch>` method."""

    return BoxResidues(
        input_pdb_path=input_pdb_path,
        output_pdb_path=output_pdb_path,
        properties=properties,
        **kwargs,
    ).launch()


def main():
    """Command line execution of this building block. Please check the command line documentation."""
    parser = argparse.ArgumentParser(
        description="Sets the center and the size of a rectangular parallelepiped box around a selection of residues found in a given PDB.",
        formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999),
    )
    parser.add_argument("--config", required=False, help="Configuration file")

    # Specific args of each building block
    required_args = parser.add_argument_group("required arguments")
    required_args.add_argument(
        "--input_pdb_path",
        required=True,
        help="PDB protein structure for which the box will be build. Its size and center will be set around the 'resid_list' property once mapped against this PDB. Accepted formats: pdb.",
    )
    required_args.add_argument(
        "--output_pdb_path",
        required=True,
        help="PDB including the annotation of the box center and size as REMARKs. Accepted formats: pdb.",
    )

    args = parser.parse_args()
    args.config = args.config or "{}"
    properties = settings.ConfReader(config=args.config).get_prop_dic()

    # Specific call of each building block
    box_residues(
        input_pdb_path=args.input_pdb_path,
        output_pdb_path=args.output_pdb_path,
        properties=properties,
    )


if __name__ == "__main__":
    main()
