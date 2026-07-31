"""Common functions for package biobb_vs.gnina"""

import gzip
import json
import re
from pathlib import Path, PurePath

from biobb_common.tools import file_utils as fu

# Matches an SDF data field header, e.g. "> <minimizedAffinity>"
SDF_TAG_PATTERN = re.compile(r">\s*<([^>]+)>")
# Record terminator of the SDF format
SDF_TERMINATOR = "$$$$"


# CHECK PARAMETERS


def check_input_path(path, argument, out_log, classname):
    """Checks input file"""
    if not Path(path).exists():
        fu.log(classname + ': Unexisting %s file, exiting' % argument, out_log)
        raise SystemExit(classname + ': Unexisting %s file' % argument)
    file_extension = PurePath(path).suffix
    if not is_valid_file(file_extension[1:], argument):
        fu.log(classname + ': Format %s in %s file is not compatible' % (file_extension[1:], argument), out_log)
        raise SystemExit(classname + ': Format %s in %s file is not compatible' % (file_extension[1:], argument))
    check_gzip_extension(path, argument, out_log, classname)
    return path


def check_output_path(path, argument, optional, out_log, classname):
    """Checks output file"""
    if optional and not path:
        return None
    if PurePath(path).parent and not Path(PurePath(path).parent).exists():
        fu.log(classname + ': Unexisting  %s folder, exiting' % argument, out_log)
        raise SystemExit(classname + ': Unexisting  %s folder' % argument)
    file_extension = PurePath(path).suffix
    if not is_valid_file(file_extension[1:], argument):
        fu.log(classname + ': Format %s in  %s file is not compatible' % (file_extension[1:], argument), out_log)
        raise SystemExit(classname + ': Format %s in  %s file is not compatible' % (file_extension[1:], argument))
    check_gzip_extension(path, argument, out_log, classname)
    return path


def is_valid_file(ext, argument):
    """Checks if file format is compatible"""
    formats = {
        'input_ligand_path': ['sdf', 'mol2', 'pdb', 'pdbqt'],
        'input_receptor_path': ['pdb', 'pdbqt'],
        'input_box_path': ['pdb'],
        'input_autobox_path': ['sdf', 'mol2', 'pdb', 'pdbqt', 'pqr'],
        'input_sdf_path': ['sdf', 'gz'],
        'output_sdf_path': ['sdf', 'gz'],
        'output_summary_path': ['json'],
        'output_log_path': ['log']
    }
    return ext in formats[argument]


def check_gzip_extension(path, argument, out_log, classname):
    """Checks that a gzip compressed file also declares the format it wraps

    gnina and Open Babel take the molecular format from the file extension, and
    a bare .gz gives them nothing to work with. Only .sdf.gz is accepted.
    """
    suffixes = PurePath(path).suffixes
    if suffixes[-1:] == ['.gz'] and suffixes[-2:-1] != ['.sdf']:
        fu.log(classname + ': %s must use a .sdf.gz extension to be gzip compressed' % argument, out_log)
        raise SystemExit(classname + ': %s must use a .sdf.gz extension to be gzip compressed' % argument)
    return path


# READ / WRITE SDF


def open_sdf(path, mode='rt'):
    """Opens a plain or gzip compressed SDF file, transparently"""
    if PurePath(path).suffix == '.gz':
        return gzip.open(path, mode, newline='')
    return open(path, mode, newline='')


def read_sdf_records(path):
    """Splits a multi record SDF file into its records

    Returns a list of dictionaries, one per record, each holding:
        * **text**: the raw record text, terminator included, so that a record
          can be written back out verbatim.
        * **name**: the molecule name, that is the first line of the record.
        * **data**: the SD data fields of the record, as a tag to value mapping.
        * **ligand_index**: 1 based index of the ligand the record belongs to.
        * **pose**: 1 based rank of the record within its ligand.

    gnina writes the poses of every input ligand consecutively and does not tag
    them with a ligand identifier, so records are grouped into ligands whenever
    the molecule name changes. Consecutive ligands sharing the same name are
    therefore reported as a single ligand.
    """
    with open_sdf(path, 'rt') as sdf_file:
        content = sdf_file.read()

    records = []
    record_lines = []
    for line in content.splitlines(keepends=True):
        record_lines.append(line)
        if line.strip() == SDF_TERMINATOR:
            records.append(parse_sdf_record(record_lines))
            record_lines = []

    # keep a trailing record that is missing its terminator instead of losing it
    if any(line.strip() for line in record_lines):
        records.append(parse_sdf_record(record_lines))

    # group the records into ligands, gnina writes each ligand's poses together
    ligand_index = 0
    previous_name = None
    pose = 0
    for record in records:
        if record['name'] != previous_name:
            ligand_index += 1
            previous_name = record['name']
            pose = 0
        pose += 1
        record['ligand_index'] = ligand_index
        record['pose'] = pose

    return records


def parse_sdf_record(record_lines):
    """Parses a single SDF record into its name, data fields and raw text"""
    name = record_lines[0].strip() if record_lines else ''
    data = {}
    tag = None
    values = []

    for line in record_lines:
        if line.strip() == SDF_TERMINATOR:
            break
        match = SDF_TAG_PATTERN.match(line)
        if match:
            if tag is not None:
                data[tag] = '\n'.join(values)
            tag = match.group(1)
            values = []
            continue
        if tag is not None:
            if not line.strip():
                data[tag] = '\n'.join(values)
                tag = None
                values = []
            else:
                values.append(line.strip())

    if tag is not None:
        data[tag] = '\n'.join(values)

    return {'text': ''.join(record_lines), 'name': name, 'data': data}


def to_number(value):
    """Converts an SD data value to a float, leaving it untouched if it is not numeric"""
    try:
        return float(value)
    except (TypeError, ValueError):
        return value


# PROCESS OUTPUTS


def process_output_gnina(output_sdf_path, output_summary_path, out_log, classname):
    """Generates the output_summary_path JSON file from the poses written by gnina

    Every pose becomes one entry holding the ligand it belongs to, its rank
    within that ligand and every score gnina attached to it as an SD data field
    (minimizedAffinity, CNNscore, CNNaffinity, CNN_VS and, for model ensembles,
    CNNvariance). Which scores are present depends on the cnn_scoring property.
    """
    if not Path(output_sdf_path).exists():
        fu.log(classname + ': %s not found, skipping the summary' % output_sdf_path, out_log)
        raise SystemExit(classname + ': Error executing gnina, %s was not created' % output_sdf_path)

    records = read_sdf_records(output_sdf_path)

    data = {}
    for index, record in enumerate(records, start=1):
        entry = {
            'ligand_name': record['name'],
            'ligand_index': record['ligand_index'],
            'pose': record['pose']
        }
        for tag, value in record['data'].items():
            entry[tag] = to_number(value)
        data['pose' + str(index)] = entry

    ligands = len({record['ligand_index'] for record in records})
    fu.log('%d poses found for %d ligand(s)' % (len(records), ligands), out_log)

    fu.log('Saving summary to %s file' % output_summary_path, out_log)
    with open(output_summary_path, 'w') as outfile:
        json.dump(data, outfile, indent=4)

    return data
