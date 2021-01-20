""" Common functions for package biobb_vs.fpocket """
from pathlib import Path, PurePath
import shutil
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
		'output_summary': ['json']
	}
	return ext in formats[argument]

def process_output_fpocket(tmp_folder, output_pockets_zip, output_summary, remove_tmp, out_log, classname):
	""" Creates the output_pockets_zip and generates the  output_summary """

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
			num = re.findall('\d+', line)[0]
			pocket = 'pocket' + num
			data[pocket] = {}
		else:
			# second level: pocket properties
			groups = re.findall('(.*)(?:\ *\:\ *)(.*)', line)[0]
			key = groups[0].lower().strip()
			key = re.sub(r'\-|\.', '', key)
			key = re.sub(r'\s+', '_', key)
			value = float(groups[1]) if '.' in groups[1] else int(groups[1])
			data[pocket][key] = value

	# get number of pockets
	fu.log('%d pockets found' % (len(data)), out_log)

	# compress pockets
	fu.log('Compressing all pockets to %s file' % (output_pockets_zip), out_log)
	pockets = PurePath(path).joinpath('pockets')
	file_name = PurePath(output_pockets_zip).parent.joinpath(PurePath(output_pockets_zip).stem)
	shutil.make_archive(file_name, 'zip', pockets)

	# save summary
	fu.log('Saving summary to %s file' % (output_summary), out_log)
	with open(output_summary, 'w') as outfile:
		json.dump(data, outfile, indent=4)

	if remove_tmp:
		# remove temporary folder
		fu.rm(tmp_folder)
		fu.log('Removed temporary folder: %s' % tmp_folder, out_log)
	



