# Biobb Virtual Screening changelog

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
