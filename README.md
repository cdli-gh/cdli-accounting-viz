# Numerals & Commodity Visualization

Utilities and visualizations for CDLI accounting corpora. Included are an API for retrieving information about numerals and counted objects, and a web interface which allows for exploratory visualization of this data. 

## Installation

This project runs as part of the CDLI framework. Standalone installation is not supported, as access to the CDLI database is required for the project to work.

1. Install the CDLI framework following [these instructions](https://gitlab.com/cdli/framework/-/blob/phoenix/develop/FRAMEWORK_INSTALL.md). Ensure you have a recent copy of the database, as this project fetches data from the `inscriptions` and `artifact_languages` tables.
2. Ensure that this project is enabled in `framework/dev/config.json.dist`:
<!-- although this is json, use javascript syntax highlighting 
     so comments render nicely -->
```javascript 
"commodity-viz": {
  "is_default" : false,
  "enabled": true, /* set this to true */
  "scale" : 1
},
"commodity-api": {
  "is_default" : false,
  "enabled": true, /* set this to true */
  "scale" : 1
}
```
3. Launch the framework using `cdlidev.py`. If this is the first time you are running the project, this should build two docker containers.
```
cd framework/dev
./cdlidev.py up
```
If the containers do not (re)build automatically, force them with 
```
./cdlidev up --build
```
4. Once the docker containers have launched, access the web interface at http://127.0.0.1:4001/cdli-accounting-viz/ or query the API directly at http://127.0.0.1:8087.

(Optional)
5. The `commodity-api` image already contains a static copy of all of the commodity data extracted from the CDLI's Sumerian corpora. To manually update this data, launch the container and run
```
python3 generate.py
```
Ensure that the framework's `mariadb` container is running at the same time, as this script requires database access.

## User Guide
Available [here](https://github.com/MrLogarithm/cdli-accounting-viz/blob/master/docs/UserGuide.md).

## API Documentation
When the application is running, access the documentation at http://127.0.0.1:8087/docs/
