#!/usr/bin/env python3

"""Module containing the Box class and the command line interface."""
import argparse
from biobb_common.configuration import  settings
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger
from biobb_common.command_wrapper import cmd_wrapper
from biobb_vs.utils.common import *

class Box():
    """Sets the center and the size of a rectangular parallelepiped box around a selection of residues found in a given PDB. The residue identifiers that compose the selection (i.e. binding site) are extracted from a second PDB.

    Args:
        input_pdb_path (str): PDB protein structure for which the box will be build. Its size and center will be set around the 'resid_pdb_path' residues once mapped against this PDB. File type: input. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/utils/box.pdb>`_. Accepted formats: pdb.
        resid_pdb_path (str): PDB file containing a selection of residue numbers mappable to 'input_pdb_path'. File type: input.  `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/utils/resid_box.pdb>`_. Accepted formats: pdb.
        output_pdb_path (str): PDB protein structure coordinates including the annotation of the box center and size as REMARKs. File type: output. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/utils/ref_output_box.pdb>`_. Accepted formats: pdb.
        properties (dic):
            * **offset** (*float*) - (2.0) Extra distance (Angstroms) between the last residue atom and the box boundary.
            * **residue_offset** (*int*) - (0) Residue id offset.
            * **box_coordinates** (*bool*) - (False) Add box coordinates as 8 ATOM records.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.
    """

    def __init__(self, input_pdb_path, resid_pdb_path,
                output_pdb_path, properties=None, **kwargs) -> None:
        properties = properties or {}

        # Input/Output files
        self.io_dict = { 
            "in": { "input_pdb_path": input_pdb_path, "resid_pdb_path": resid_pdb_path },
            "out": { "output_pdb_path": output_pdb_path } 
        }

        # Properties specific for BB
        self.offset = float(properties.get('offset', 2.0))
        self.residue_offset = properties.get('residue_offset', 0)
        self.box_coordinates = float(properties.get('box_coordinates', False))
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
        self.io_dict["in"]["input_pdb_path"] = check_input_path(self.io_dict["in"]["input_pdb_path"],"input_pdb_path", out_log, self.__class__.__name__)
        self.io_dict["in"]["resid_pdb_path"] = check_input_path(self.io_dict["in"]["resid_pdb_path"],"resid_pdb_path", out_log, self.__class__.__name__)
        self.io_dict["out"]["output_pdb_path"] = check_output_path(self.io_dict["out"]["output_pdb_path"],"output_pdb_path", False, out_log, self.__class__.__name__)


    @launchlogger
    def launch(self) -> int:
        """Launches the execution of the Box module."""

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

        # Parse structure
        fu.log('Loading input PDB structure %s' % (self.io_dict["in"]["input_pdb_path"]), out_log, self.global_log)
        structure_name = PurePath(self.io_dict["in"]["input_pdb_path"]).name
        parser      = Bio.PDB.PDBParser(QUIET = True)
        structPDB   = parser.get_structure(structure_name, self.io_dict["in"]["input_pdb_path"])

        if len(structPDB):
            structPDB = structPDB[0]

        # Parse residue structure
        fu.log('Loading residue PDB selection %s' % (self.io_dict["in"]["resid_pdb_path"]), out_log, self.global_log)
        resid_name   = PurePath(self.io_dict["in"]["resid_pdb_path"]).name
        residPDB     = parser.get_structure(resid_name,self.io_dict["in"]["resid_pdb_path"])

        if len(residPDB):
            residPDB = residPDB[0]

        ## Mapping residue structure into input structure

        fu.log('Mapping residue structure into input structure', out_log, self.global_log)

        # Listing residues to be selected from the residue structure
        residPDB_res_list = []
        p = re.compile('H_|W_|W')
        for residPDB_res in residPDB.get_residues():
            m_het = p.match(residPDB_res.get_id()[0])
            if not m_het:
                if self.residue_offset:
                    residPDB_res_list.append((residPDB_res.get_id()[0],residPDB_res.get_id()[1]+self.residue_offset,residPDB_res.get_id()[2]))
                else:
                    residPDB_res_list.append(residPDB_res.get_id())

        selection_res_list   = []
        selection_atoms_num  = 0
        for struct_chain in structPDB:
            for struct_res in struct_chain:
                if struct_res.get_id() in residPDB_res_list:
                    selection_res_list.append(struct_res)
                    selection_atoms_num += len(struct_res.get_list())

        if len(selection_res_list) == 0:
            fu.log(self.__class__.__name__ + ': Cannot match any of the residues listed in %s into %s' % (self.io_dict["in"]["resid_pdb_path"],self.io_dict["in"]["input_pdb_path"]), out_log)
            raise SystemExit(self.__class__.__name__ + ': Cannot match any of the residues listed in %s into %s' % (self.io_dict["in"]["resid_pdb_path"],self.io_dict["in"]["input_pdb_path"]))
        elif len(selection_res_list) !=  len(residPDB_res_list):
            fu.log('Cannot match all the residues listed in %s into %s. Found %s out of %s' % (self.io_dict["in"]["resid_pdb_path"],self.io_dict["in"]["input_pdb_path"], len(selection_res_list),len(residPDB_res_list)), out_log)
        else:
            fu.log('Selection residues successfully matched', out_log, self.global_log)

        ## Compute binding site box size

        # compute box center
        selection_box_center = sum(atom.coord for res in selection_res_list for atom in res.get_atoms()) / selection_atoms_num
        fu.log('Binding site center (Angstroms): %8.3f%8.3f%8.3f' % (selection_box_center[1],selection_box_center[1],selection_box_center[2]), out_log, self.global_log)

        # compute box size
        selection_coords_max = np.amax([atom.coord for res in selection_res_list for atom in res.get_atoms()],axis=0)
        selection_box_size   = selection_coords_max - selection_box_center
        if self.offset:
            selection_box_size = [c + self.offset for c in selection_box_size]
        fu.log('Binding site size (Angstroms):   %8.3f%8.3f%8.3f' % (selection_box_size[0],selection_box_size[1],selection_box_size[2]), out_log, self.global_log)

        vol = np.prod(selection_box_size) * 2**3
        fu.log('Volume (cubic Angstroms): %.0f' % (vol), out_log, self.global_log)

        # add box details as PDB remarks
        remarks = "REMARK BOX CENTER:%8.3f%8.3f%8.3f" % (selection_box_center[1],selection_box_center[1],selection_box_center[2])
        remarks += " SIZE:%8.3f%8.3f%8.3f" % (selection_box_size[0],selection_box_size[1],selection_box_size[2])

        selection_box_coords_txt   = ""
        # add (optional) box coordinates as 8 ATOM records
        if self.box_coordinates:
            fu.log('Adding box coordinates', out_log, self.global_log)
            selection_box_coords_txt  = get_box_coordinates(selection_box_center,selection_box_size)

        shutil.copy2(self.io_dict["in"]["input_pdb_path"], self.io_dict["out"]["output_pdb_path"])

        with open(self.io_dict["out"]["output_pdb_path"], 'r+') as f:
            content = f.read()
            if "END" in content:
                content = content.replace("END", selection_box_coords_txt + "END")
            else:
                content += selection_box_coords_txt
            f.seek(0, 0)
            f.write(remarks.rstrip('\r\n') + '\n' + content)

        fu.log('Saving output PDB file (with box setting annotations): %s' % (self.io_dict["out"]["output_pdb_path"]), out_log, self.global_log)

        return 0

def main():
    parser = argparse.ArgumentParser(description="Sets the center and the size of a rectangular parallelepiped box around a selection of residues found in a given PDB. The residue identifiers that compose the selection (i.e. binding site) are extracted from a second PDB.", formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('--config', required=False, help='Configuration file')

    # Specific args of each building block
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--input_pdb_path', required=True, help='Path to the PDB structure where the binding site is to be found. Accepted formats: pdb.')
    required_args.add_argument('--resid_pdb_path', required=True, help='PDB file containing a selection of residue numbers mappable to \'input_pdb_path\'. Accepted formats: pdb.')
    required_args.add_argument('--output_pdb_path', required=True, help='Path to the PDB containig the residues belonging to the binding site. Accepted formats: pdb.')

    args = parser.parse_args()
    args.config = args.config or "{}"
    properties = settings.ConfReader(config=args.config).get_prop_dic()

    # Specific call of each building block
    Box(input_pdb_path=args.input_pdb_path, resid_pdb_path=args.resid_pdb_path, 
                    output_pdb_path=args.output_pdb_path, 
                    properties=properties).launch()

if __name__ == '__main__':
    main()
