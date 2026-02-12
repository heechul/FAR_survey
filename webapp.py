import csv
from io import StringIO

from flask import Flask, Response, render_template, request
from pandas import read_csv

from FAR_survey import calculate_results


app = Flask(__name__)
LAST_RESULTS = []


@app.route("/", methods=["GET", "POST"])
def index():
    global LAST_RESULTS
    results = []
    error = None

    if request.method == "POST":
        uploaded_file = request.files.get("csv_file")
        if not uploaded_file or uploaded_file.filename == "":
            error = "Please choose a CSV file."
        else:
            try:
                df = read_csv(uploaded_file)
                results = calculate_results(df)
                LAST_RESULTS = results
                if not results:
                    error = "No instructor survey rows were found in this file."
            except Exception as exc:
                error = f"Could not parse CSV: {exc}"

    return render_template("index.html", results=results, error=error)


@app.route("/download")
def download_results():
    if not LAST_RESULTS:
        return Response("No results available to download.", status=400)

    output = StringIO()
    writer = csv.writer(output)

    header = [
        "Term",
        "Instructor",
        "Course",
        "Total Responses",
        "Weighted Avg",
    ]
    for question_num in range(1, 11):
        header.append(f"Q{question_num} % All")
        header.append(f"Q{question_num} % Some")
    writer.writerow(header)

    for result in LAST_RESULTS:
        row = [
            result["term"],
            result["instructor"],
            result["course"],
            result["total_response_count"],
            f"{result['weighted_avg']:.2f}",
        ]

        question_map = {
            q["question_number"]: (q["pct_all"], q["pct_some"])
            for q in result["question_breakdown"]
        }
        for question_num in range(1, 11):
            pct_all, pct_some = question_map.get(question_num, ("", ""))
            row.extend([pct_all, pct_some])

        writer.writerow(row)

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=far_results.csv"},
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
