from flask import Flask, render_template, request
from pandas import read_csv

from FAR_survey import calculate_results


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
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
                if not results:
                    error = "No instructor survey rows were found in this file."
            except Exception as exc:
                error = f"Could not parse CSV: {exc}"

    return render_template("index.html", results=results, error=error)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
