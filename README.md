# FAR-survey

KU student survey parser for FAR reporting. 

## Prerequisite

```
pip install pandas flask
```

## Web app usage (local browser)

Run the local web app:

```
python webapp.py
```

Or on macOS, double-click `run_webapp.command` in Finder.

Then open:

```
http://127.0.0.1:5000
```

Upload a survey CSV file to view weighted FAR results by term, instructor, and course.

## JavaScript web app usage (no Python dependency)

The JavaScript version is fully standalone and does not import or call any Python code.
For internet-facing deployments, CSV download/export is intentionally disabled to reduce data-leak risk.

```
cd js_webapp
npm install
npm start
```

Then open:

```
http://127.0.0.1:5001
```

## CLI usage

Download the survey as CSV format from https://kusurvey.ca1.qualtrics.com. 

Run the code as follows:
```
python FAR_survey.py dashboard-export-05-19-pm-2024-01-21.csv
2023 Fall Heechul Yun EECS690/EECS700 Special Topics: Embedded ML Sect: 8001
...
weighted avg. = 0.XX  <-- this is the number that should be included in the FAR

```

## License
MIT