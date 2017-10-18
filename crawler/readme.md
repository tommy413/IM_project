# law-project

## Usage
* `./law-project -fs path [input (see below)]`
  * `path` is somewhere to store downloaded data in the filesystem
  * this is the default mode and stores in `downloaded` if the argument is not provided
* `./law-project -db user:password@host/db [input (see below)]`
  * db is a postgres login string
  * see below for the 2 input methods
  * if `db` is not given, the downloaded html is stored in the filesystem
* `./law-project courtName startDate endDate`
  * `courtName` is name+caseType, like `TPDM`
  * `startDate` and `endDate` are in the form `YYYYMMDD`
* `./law-project -f fileName`
  * `fileName` is the name of a space separated file where each line has the form `courtName startDate endDate`

## Other
[courts.md](courts.md) is a list of court / type combinations
