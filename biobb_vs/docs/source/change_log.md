# Biobb Virtual Screening changelog

## [Unreleased]

## What's new in version [5.4.0](https://github.com/bioexcel/biobb_vs/releases/tag/v5.4.0)?

### Changes

* [UPDATE] Update to biobb_common 5.4.0.
* [FEATURE](gnina): New gnina_run building block, wrapping the gnina docking software with optional CNN rescoring. gnina is not bundled with this package, install it separately from its binary release or use its container image.
* [FEATURE](gnina): New gnina_select_pose building block, extracting a single pose out of the multi record SDF file written by gnina_run.
* [FIX] box, box_residues: the SIZE field of the `REMARK BOX CENTER` line is now the full box edge length, matching what AutoDock Vina reads from `--size_x/y/z`. It was previously written as a half-extent (centre-to-face distance), so `box` -> `autodock_vina_run` workflows searched a box with half the intended edge in each dimension, i.e. 1/8 of the intended volume.
* [FIX] autodock_vina_run: raise an error instead of silently using a 0x0x0 box when the input box file has no `REMARK BOX CENTER` line.
* [FIX](gnina): removed the `box_definition` property from gnina_run. The `SIZE` field of the input box file is now passed to gnina unchanged, exactly as autodock_vina_run does, since box and box_residues write it as the full box edge length. The property only existed to work around the half-extent convention fixed above, and its `half_extent` default would now double an already correct value.
* [FIX] fpocket_select: the `pocket` property defaults to 1, as documented. It had no default, so without it the block selected no pocket and wrote no output files. The pocket files are now matched by name: `pocket: 1` no longer also takes the files of pockets 10 to 19, which made the output depend on the order of the files in the zip. A pocket that is not in the input zip raises an error.
* [UPDATE] autodock_vina_run also writes the missing `REMARK BOX CENTER` error in its log. fpocket_run keeps its temporary folder when fpocket fails, as every block keeps its sandbox after an error.
* [DOCS] box, box_residues: document that the box is centred on the mean of the selected coordinates, so an asymmetric set of points may extend slightly beyond the box faces, and `offset` should be chosen to absorb it.
* [FIX] box: the coordinates are read from the PDB columns 31-38, 39-46 and 47-54. The first column of each was skipped, so a coordinate of -100.000 or less, or 1000.000 or more, lost its sign or its first digit.
* [FIX] bindingsite: with several chains, the first chain of the input structure and of each cluster member is used, as the log says (it used the last one). A residue whose CA atom is in the cluster member but not in the input structure is skipped in both atom lists; it was added to one of them only, and the superimposition failed.
* [FIX] autodock_vina_run: `output_log_path` is optional, as documented; the block failed without it.
* [FIX] fpocket_run: in containers, an input PDB file of any name works; the block looked for the outputs of an input named `fpocket_input.pdb` and failed otherwise.
* [UPDATE] `container_working_dir` removed from the docs and the JSON schemas: the commands run in the sandbox, mounted in `container_volume_path` in containers.
* [DOCS] bindingsite, box_residues: `input_pdb_path` also accepts PQR files, as the path checks already did.
* [UPDATE] Python 3.11 to 3.13.

## What's new in version [5.3.0](https://github.com/bioexcel/biobb_amber/releases/tag/v5.3.0)?

### Changes

* [UPDATE] Update to biobb_common 5.3.1

## What's new in version [5.2.1](https://github.com/bioexcel/biobb_amber/releases/tag/v5.2.1)?

### Changes

* [UPDATE] Update to biobb_common 5.2.2

## What's new in version [5.2.0](https://github.com/bioexcel/biobb_amber/releases/tag/v5.2.0)?

### Changes

* [UPDATE] Update to biobb_common 5.2.0

## What's new in version [5.1.0](https://github.com/bioexcel/biobb_vs/releases/tag/v5.1.0)?

### Changes

* [UPDATE]: Update to biobb_common 5.1.0

## What's new in version [5.0.0](https://github.com/bioexcel/biobb_vs/releases/tag/v5.0.0)?

### Changes

* [FIX](all): Accept lists in different formats on input properties.
* [CI/CD](env.yaml): Update biobb_common version.
* [CI/CD](linting_and_testing.yml): Update set-up micromamba.
* [CI/CD](linting_and_testing): Update GA test workflow to Python >3.9
* [DOCS](.readthedocs.yaml): Updating to Python 3.9
* [CI/CD](GITIGNORE): Update .gitignore to include the new file extensions to ignore
* [FEATURE](__init__): Importing submodules when a module is loaded
* [CI/CD](conf.yml): Change test conf.yml to adapt to new settings configuration
* [FEATURE] New sandbox_path property

## What's new in version [4.2.0](https://github.com/bioexcel/biobb_vs/releases/tag/v4.2.0)?
In version 4.2.0 the dependency biobb_common has been updated to 4.2.0 version.

### New features

* Update to biobb_common 4.2.0 (general)

## What's new in version [4.1.2](https://github.com/bioexcel/biobb_vs/releases/tag/v4.1.2)?
In version 4.1.2 the code has been updated for being compatible with biopython 1.83 and fpocket version dependency has been fixed to 4.1.

### New features

* Compatibility with biopython 1.83.
* Fpocket fixed to 4.1 version.

## What's new in version [4.1.1](https://github.com/bioexcel/biobb_vs/releases/tag/v4.1.1)?
In version 4.1.1 some minor bugs have been fixed.

### New features

* Minor bug fixes in Utils

## What's new in version [4.1.0](https://github.com/bioexcel/biobb_vs/releases/tag/v4.1.0)?
In version 4.1.0 the dependency biobb_common has been updated to 4.1.0 version.

### New features

* Update to biobb_common 4.1.0 (general)

## What's new in version [4.0.0](https://github.com/bioexcel/biobb_vs/releases/tag/v4.0.0)?
In version 4.0.0 the dependency biobb_common has been updated to 4.0.0 version. Also Autodock Vina has been updated from 1.1.2 to 1.2.3.

### New features

* Update to biobb_common 4.0.0 (general)
* Update to Vina 1.2.3 (vina module)

## What's new in version [3.9.0](https://github.com/bioexcel/biobb_vs/releases/tag/v3.9.0)?
In version 3.9.0 the dependency biobb_common has been updated to 3.9.0 version.

### New features

* Update to biobb_common 3.9.0 (general)
* All inputs/outputs are checked for correct file format, extension and type (general)

## What's new in version [3.8.1](https://github.com/bioexcel/biobb_vs/releases/tag/v3.8.1)?
In version 3.8.1 the AutoDockVinaRun and FPocketRun tools have added the ability to be executed through docker.

### New features

* Added docker containers for AutoDockVinaRun and FPocketRun tools

## What's new in version [3.8.0](https://github.com/bioexcel/biobb_vs/releases/tag/v3.8.0)?
In version 3.8.0 the dependency biobb_common has been updated to 3.8.1 version.

### New features

* Update to biobb_common 3.8.0 (general)

## What's new in version [3.7.1](https://github.com/bioexcel/biobb_vs/releases/tag/v3.7.1)?
In version 3.7.1 some minor bugs have been fixed.

### Other changes

* Minor bug fixes in AutoDockVinaRun

## What's new in version [3.7.0](https://github.com/bioexcel/biobb_vs/releases/tag/v3.7.0)?
In version 3.7.0 the dependency biobb_common has been updated to 3.7.0 version.

### New features

* Update to biobb_common 3.7.0 (general)

## What's new in version [3.6.0](https://github.com/bioexcel/biobb_vs/releases/tag/v3.6.0)?
In version 3.6.0 the dependency biobb_common has been updated to 3.6.0 version.

### New features

* Update to biobb_common 3.6.0 (general)

## What's new in version [3.5.1](https://github.com/bioexcel/biobb_vs/releases/tag/v3.5.1)?
In version 3.5.1 the tools fpocket and autodock_vina have been renamed to fpocket_run and autodock_vina_run in order to avoid conflicts with the wrapped softwares.

### New features

* Tools fpocket and autodock_vina renamed to fpocket_run and autodock_vina_run

## What's new in version [3.5.0](https://github.com/bioexcel/biobb_vs/releases/tag/v3.5.0)?
The version 3.5.0 is the first release of biobb_vs. There have been added the fpocket and autodock-vina tools as well as utilities for getting a binding site, calculate box or extract a desired model from a PDBQT file.

### New features

* First release
* Fpocket module: FPocket, FPocketFilter and FPocketSelect tools
* Vina module: AutoDockVina tool
* Utils module: BindingSite, Box, BoxResidues and ExtractModelPDBQT tools
