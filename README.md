# FAR-survey

KU student survey parser for FAR reporting. 

## Prerequisite

```
pip install pandas
```

## Pure client-side single HTML app (no Node/Python)

Open this file directly in your browser:

```
client_webapp/index.html
```

It runs completely in-browser and works from `file://` without any server process.

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