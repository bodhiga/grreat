# GRREAT midline quant

### Dependencies
Install docker.

### Before running

Place the raw data files in the root directory of this repository

* Adolescent Survey_2022_20_09_10_37.sav
* Community_2022_22_09_10_51.sav
* Customer Satisfaction_2022_20_09_10_29.xlsx
* Customer Satisfaction_2022_22_09_10_52.sav
* Health Facility_2022_22_09_10_52.sav

And the baseline data:

* GIRLS EMPOWEMENT.dta

## Build the docker image

`docker build -t quant .`

## Running

To run interactively:

`docker run -it --name grreat --rm --volume $(pwd):/usr/src/app --net=host quant bash`

Then:

`python3 quant.py`
