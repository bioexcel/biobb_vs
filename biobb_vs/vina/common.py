"""Common functions for package biobb_vs.vina"""

from pathlib import Path, PurePath

from biobb_common.tools import file_utils as fu

# CHECK PARAMETERS


def check_input_path(path, argument, out_log, classname):
    """Checks input file"""
    if not Path(path).exists():
        fu.log(classname + ": Unexisting %s file, exiting" % argument, out_log)
        raise SystemExit(classname + ": Unexisting %s file" % argument)
    file_extension = PurePath(path).suffix
    if not is_valid_file(file_extension[1:], argument):
        fu.log(
            classname
            + ": Format %s in %s file is not compatible"
            % (file_extension[1:], argument),
            out_log,
        )
        raise SystemExit(
            classname
            + ": Format %s in %s file is not compatible"
            % (file_extension[1:], argument)
        )
    return path


def check_output_path(path, argument, optional, out_log, classname):
    """Checks output file"""
    if optional and not path:
        return None
    if PurePath(path).parent and not Path(PurePath(path).parent).exists():
        fu.log(classname + ": Unexisting  %s folder, exiting" % argument, out_log)
        raise SystemExit(classname + ": Unexisting  %s folder" % argument)
    file_extension = PurePath(path).suffix
    if not is_valid_file(file_extension[1:], argument):
        fu.log(
            classname
            + ": Format %s in  %s file is not compatible"
            % (file_extension[1:], argument),
            out_log,
        )
        raise SystemExit(
            classname
            + ": Format %s in  %s file is not compatible"
            % (file_extension[1:], argument)
        )
    return path


def is_valid_file(ext, argument):
    """Checks if file format is compatible"""
    formats = {
        "input_ligand_path": ["pdb"],
        "output_ligand_path": ["pdbqt"],
        "input_receptor_path": ["pdb"],
        "output_receptor_path": ["pdbqt"],
        "input_ligand_pdbqt_path": ["pdbqt"],
        "input_receptor_pdbqt_path": ["pdbqt"],
        "input_box_path": ["pdb"],
        "output_pdbqt_path": ["pdbqt"],
        "output_log_path": ["log"],
    }
    return ext in formats[argument]


def check_mgltools_path(mgltools_path, out_log, classname):
    """Checks the path of mgltools"""
    if not Path(mgltools_path).exists():
        fu.log(classname + ": Unexisting mgltools_path, exiting", out_log)
        raise SystemExit(classname + ": Unexisting mgltools_path, exiting")
    return mgltools_path


'''def check_input_autodock(structure, out_log):
    """ if structure ends with END, remove last line """
    lines_new = []
    with open(structure, 'r') as f:
        lines = f.read().splitlines()
        for item in lines:
            #if not item.startswith('END'):
            if not item.strip() == 'END':
                lines_new.append(item)
            else:
                fu.log('%s file ends with END, cleaning' % structure, out_log)

    with open(structure, 'w') as f:
        for item in lines_new:
            f.write("%s\n" % item)'''
