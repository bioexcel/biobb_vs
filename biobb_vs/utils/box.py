#!/usr/bin/env python3

"""Module containing the Box class and the command line interface."""

import argparse
from pathlib import PurePath
from typing import Optional

import numpy as np
from biobb_common.configuration import settings
from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger

from biobb_vs.utils.common import (
    check_input_path,
    check_output_path,
    get_box_coordinates,
)


class Box(BiobbObject):
    """
    | biobb_vs Box
    | This class sets the center and the size of a rectangular parallelepiped box around a set of residues or a pocket.
    | Sets the center and the size of a rectangular parallelepiped box around a set of residues from a given PDB or a pocket from a given PQR.

    Args:
        input_pdb_path (str): PDB file containing a selection of residue numbers or PQR file containing the pocket. File type: input.  `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/utils/input_box.pqr>`_. Accepted formats: pdb (edam:format_1476), pqr (edam:format_1476).
        output_pdb_path (str): PDB including the annotation of the box center and size as REMARKs. File type: output. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/utils/ref_output_box.pdb>`_. Accepted formats: pdb (edam:format_1476).
        properties (dic - Python dictionary object containing the tool parameters, not input/output files):
            * **offset** (*float*) - (2.0) [0.1~1000|0.1] Extra distance (Angstroms) between the last residue atom and the box boundary.
            * **box_coordinates** (*bool*) - (False) Add box coordinates as 8 ATOM records.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.
            * **sandbox_path** (*str*) - ("./") [WF property] Parent path to the sandbox directory.

    Examples:
        This is a use example of how to use the building block from Python::

            from biobb_vs.utils.box import box
            prop = {
                'offset': 2,
                'box_coordinates': True
            }
            box(input_pdb_path='/path/to/myPocket.pqr',
                output_pdb_path='/path/to/newBox.pdb',
                properties=prop)

    Info:
        * wrapped_software:
            * name: In house
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
        self.offset = float(properties.get("offset", 2.0))
        self.box_coordinates = float(properties.get("box_coordinates", False))
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
        """Execute the :class:`Box <utils.box.Box>` utils.box.Box object."""

        # check input/output paths and parameters
        self.check_data_params(self.out_log, self.err_log)

        # Setup Biobb
        if self.check_restart():
            return 0
        self.stage_files()

        # check if cavity (pdb) or pocket (pqr)
        input_type = PurePath(self.io_dict["in"]["input_pdb_path"]).suffix.lstrip(".")
        if input_type == "pdb":
            fu.log(
                "Loading residue PDB selection from %s"
                % (self.io_dict["in"]["input_pdb_path"]),
                self.out_log,
                self.global_log,
            )
        else:
            fu.log(
                "Loading pocket PQR selection from %s"
                % (self.io_dict["in"]["input_pdb_path"]),
                self.out_log,
                self.global_log,
            )

        # get input_pdb_path atoms coordinates
        selection_atoms_num = 0
        x_coordslist = []
        y_coordslist = []
        z_coordslist = []
        with open(self.io_dict["in"]["input_pdb_path"]) as infile:
            for line in infile:
                if line.startswith("HETATM") or line.startswith("ATOM"):
                    x_coordslist.append(float(line[31:38].strip()))
                    y_coordslist.append(float(line[39:46].strip()))
                    z_coordslist.append(float(line[47:54].strip()))
                    selection_atoms_num = selection_atoms_num + 1

        # Compute binding site box size

        # compute box center
        selection_box_center = [
            np.average(x_coordslist),
            np.average(y_coordslist),
            np.average(z_coordslist),
        ]
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
            [x_coordslist, y_coordslist, z_coordslist], axis=1
        )
        selection_box_size = selection_coords_max - selection_box_center
        if self.offset:
            fu.log(
                "Adding %.1f Angstroms offset" % (self.offset),
                self.out_log,
                self.global_log,
            )
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

        self.check_arguments(output_files_created=True, raise_exception=False)

        return 0


def box(
    input_pdb_path: str,
    output_pdb_path: str,
    properties: Optional[dict] = None,
    **kwargs,
) -> int:
    """Execute the :class:`Box <utils.box.Box>` class and
    execute the :meth:`launch() <utils.box.Box.launch>` method."""

    return Box(
        input_pdb_path=input_pdb_path,
        output_pdb_path=output_pdb_path,
        properties=properties,
        **kwargs,
    ).launch()


def main():
    """Command line execution of this building block. Please check the command line documentation."""
    parser = argparse.ArgumentParser(
        description="Sets the center and the size of a rectangular parallelepiped box around a set of residues from a given PDB or a pocket from a given PQR.",
        formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999),
    )
    parser.add_argument("--config", required=False, help="Configuration file")

    # Specific args of each building block
    required_args = parser.add_argument_group("required arguments")
    required_args.add_argument(
        "--input_pdb_path",
        required=True,
        help="PDB file containing a selection of residue numbers or PQR file containing the pocket. Accepted formats: pdb, pqr.",
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
    box(
        input_pdb_path=args.input_pdb_path,
        output_pdb_path=args.output_pdb_path,
        properties=properties,
    )


if __name__ == "__main__":
    main()
