"""Common functions for package biobb_vs.vina"""

from pathlib import Path

from biobb_common.tools import file_utils as fu

# CHECK PARAMETERS


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
