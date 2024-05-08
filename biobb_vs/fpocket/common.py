""" Common functions for package biobb_vs.fpocket """
from pathlib import Path, PurePath
import json
import re
from biobb_common.tools import file_utils as fu


# CHECK PARAMETERS

def check_input_path(path, argument, out_log, classname):
    """ Checks input file """
    if not Path(path).exists():
        fu.log(classname + ': Unexisting %s file, exiting' % argument, out_log)
        raise SystemExit(classname + ': Unexisting %s file' % argument)
    file_extension = PurePath(path).suffix
    if not is_valid_file(file_extension[1:], argument):
        fu.log(classname + ': Format %s in %s file is not compatible' % (file_extension[1:], argument), out_log)
        raise SystemExit(classname + ': Format %s in %s file is not compatible' % (file_extension[1:], argument))
    return path


def check_output_path(path, argument, optional, out_log, classname):
    """ Checks output file """
    if optional and not path:
        return None
    if PurePath(path).parent and not Path(PurePath(path).parent).exists():
        fu.log(classname + ': Unexisting  %s folder, exiting' % argument, out_log)
        raise SystemExit(classname + ': Unexisting  %s folder' % argument)
    file_extension = PurePath(path).suffix
    if not is_valid_file(file_extension[1:], argument):
        fu.log(classname + ': Format %s in  %s file is not compatible' % (file_extension[1:], argument), out_log)
        raise SystemExit(classname + ': Format %s in  %s file is not compatible' % (file_extension[1:], argument))
    return path


def is_valid_file(ext, argument):
    """ Checks if file format is compatible """
    formats = {
        'input_pdb_path': ['pdb'],
        'output_pockets_zip': ['zip'],
        'output_summary': ['json'],
        'input_pockets_zip': ['zip'],
        'input_summary': ['json'],
        'output_filter_pockets_zip': ['zip'],
        'output_pocket_pdb': ['pdb'],
        'output_pocket_pqr': ['pqr']
    }
    return ext in formats[argument]


# CHECK PROPERTIES

def check_range(name, property, values, out_log, classname):
    """ Checks the format of a range for fpocket_filter """

    if not isinstance(property, list) or len(property) != 2 or not all(isinstance(n, (int, float)) for n in property):
        fu.log(classname + ': Incorrect format for %s property, exiting' % name, out_log)
        raise SystemExit(classname + ': Incorrect format for %s property, exiting' % name)

    if property[0] < values[0] or property[1] > values[1]:
        fu.log(classname + ': %s is out of [%s] range, exiting' % (name, ', '.join(str(v) for v in values)), out_log)
        raise SystemExit(classname + ': %s is out of [%s] range, exiting' % (name, ', '.join(str(v) for v in values)))

    return property


# PROCESS OUTPUTS

def process_output_fpocket(tmp_folder, output_pockets_zip, output_summary, sort_by, remove_tmp, container_path, out_log, classname):
    """ Creates the output_pockets_zip and generates the  output_summary """

    if container_path:
        path = str(PurePath(tmp_folder).joinpath('fpocket_input_out'))
    else:
        path = str(PurePath(tmp_folder).joinpath('input_out'))

    if not Path(path).is_dir():
        if remove_tmp:
            # remove temporary folder
            fu.rm(tmp_folder)
            fu.log('Removing temporary folder: %s' % tmp_folder, out_log)

        fu.log(classname + ': Error executing fpocket, please check your properties', out_log)
        raise SystemExit(classname + ': Error executing fpocket, please check your properties')

    # summary
    # read input_info.txt file
    if container_path:
        info = PurePath(path).joinpath('fpocket_input_info.txt')
    else:
        info = PurePath(path).joinpath('input_info.txt')
    with open(info, 'r') as info_text:
        lines = info_text.readlines()
        lines = [x for x in lines if x != '\n']

    data = {}

    # parse input_info.txt file to python object
    pocket = ''
    for line in lines:
        if not line.startswith('\t'):
            # first level: pocket
            num = re.findall('\\d+', line)[0]
            pocket = 'pocket' + num
            data[pocket] = {}
        else:
            # second level: pocket properties
            groups = re.findall('(.*)(?:\\ *\\:\\ *)(.*)', line)[0]
            key = groups[0].lower().strip()
            key = re.sub(r'\-|\.', '', key)
            key = re.sub(r'\s+', '_', key)
            value = float(groups[1]) if '.' in groups[1] else int(groups[1])
            data[pocket][key] = value

    # get number of pockets
    fu.log('%d pockets found' % (len(data)), out_log)

    # sort data by sort_by property
    fu.log('Sorting output data by %s' % (sort_by), out_log)
    data = dict(sorted(data.items(), key=lambda item: float(item[1][sort_by]), reverse=True))

    # compress pockets
    pockets = PurePath(path).joinpath('pockets')
    files_list = [str(i) for i in Path(pockets).iterdir()]
    fu.zip_list(zip_file=output_pockets_zip, file_list=files_list, out_log=out_log)

    # save summary
    fu.log('Saving summary to %s file' % (output_summary), out_log)
    with open(output_summary, 'w') as outfile:
        json.dump(data, outfile, indent=4)

    '''if remove_tmp:
        # remove temporary folder
        fu.rm(tmp_folder)
        fu.log('Removed temporary folder: %s' % tmp_folder, out_log)'''


def process_output_fpocket_filter(search_list, tmp_folder, input_pockets_zip, output_filter_pockets_zip, remove_tmp, out_log):
    """ Creates the output_filter_pockets_zip """

    # decompress the input_pockets_zip file to tmp_folder
    fu.unzip_list(zip_file=input_pockets_zip, dest_dir=tmp_folder, out_log=out_log)

    # list all files of tmp_folder
    pockets_list = [str(i) for i in Path(tmp_folder).iterdir()]

    # select search_list items from pockets_list
    sel_pockets_list = [p for p in pockets_list for s in search_list if s + '_' in p]

    fu.log('Creating %s output file' % output_filter_pockets_zip, out_log)

    # compress output to output_filter_pockets_zip
    fu.zip_list(zip_file=output_filter_pockets_zip, file_list=sel_pockets_list, out_log=out_log)

    '''if remove_tmp:
        # remove temporary folder
        fu.rm(tmp_folder)
        fu.log('Removed temporary folder: %s' % tmp_folder, out_log)'''
