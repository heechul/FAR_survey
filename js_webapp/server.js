const express = require("express");
const multer = require("multer");
const { parse } = require("csv-parse/sync");

const app = express();
const upload = multer({ storage: multer.memoryStorage() });
const PORT = 5001;

const QUESTIONS = [
  "[NUM] Instructor Q1_1 - The instructor helped me understand what I was expected to learn",
  "[NUM] Instructor Q1_2 - The instructor explained the purpose of work I did in the course (things like discussions, assignments, exams, class activities)",
  "[NUM] Instructor Q1_3 - The instructor made deadlines clear",
  "[NUM] Instructor Q1_4 - The instructor was clear about how I would be graded",
  "[NUM] Instructor Q1_5 - The instructor provided feedback that helped me learn",
  "[NUM] Instructor Q2_1 - The instructor helped create an environment in the class (whether in person or online) that motivated me to learn",
  "[NUM] Instructor Q2_2 - The instructor responded respectfully if I had  questions",
  "[NUM] Instructor Q2_3 - The instructor helped me feel that I could succeed in the class",
  "[NUM] Instructor Q2_4 - The instructor helped me understand different ways to apply what I learned",
  "[NUM] Instructor Q2_5 - The instructor used approaches that encouraged me to participate in class activities (in person or online)",
];

function normalizeSpaces(value) {
  return String(value || "").replace(/\s+/g, " ").trim();
}

function valueFromAliases(row, aliases) {
  for (const alias of aliases) {
    if (row[alias] !== undefined && row[alias] !== null && String(row[alias]).trim() !== "") {
      return row[alias];
    }
  }
  return "";
}

function buildQuestionColumnMap(rows) {
  const availableKeys = new Set();
  for (const row of rows) {
    for (const key of Object.keys(row)) {
      availableKeys.add(key);
    }
  }

  const normalizedKeyMap = new Map();
  for (const key of availableKeys) {
    normalizedKeyMap.set(normalizeSpaces(key), key);
  }

  return QUESTIONS.map((question) => normalizedKeyMap.get(normalizeSpaces(question)) || question);
}

function toIntOrNull(value) {
  const parsed = Number.parseInt(String(value), 10);
  return Number.isNaN(parsed) ? null : parsed;
}

function calculateResults(rows) {
  const terms = [];
  const instructors = [];
  const courses = [];

  for (const row of rows) {
    const term = String(valueFromAliases(row, ["Term Name", "Term Name*"]));
    const instructor = String(valueFromAliases(row, ["Instructor Name", "Instructor Name*"]));
    const course = String(valueFromAliases(row, ["Course Code Dashboard", "Course Code Dashboard*"]));

    if (!terms.includes(term)) terms.push(term);
    if (!instructors.includes(instructor)) instructors.push(instructor);
    if (!courses.includes(course)) courses.push(course);
  }

  const questionColumns = buildQuestionColumnMap(rows);
  const results = [];

  for (const term of terms) {
    for (const instructor of instructors) {
      for (const course of courses) {
        const instructorSurvey = rows.filter((row) => {
          const rowTerm = String(valueFromAliases(row, ["Term Name", "Term Name*"]));
          const rowInstructor = String(valueFromAliases(row, ["Instructor Name", "Instructor Name*"]));
          const rowCourse = String(valueFromAliases(row, ["Course Code Dashboard", "Course Code Dashboard*"]));
          const surveySource = String(valueFromAliases(row, ["Survey Source", "Survey Source*"]));

          return (
            rowTerm === term &&
            rowInstructor === instructor &&
            rowCourse === course &&
            surveySource.includes("Instructor")
          );
        });

        const nTotal = instructorSurvey.length;
        if (nTotal === 0) {
          continue;
        }

        const questionBreakdown = [];
        let weightedSum = 0;

        for (let index = 0; index < questionColumns.length; index += 1) {
          const questionColumn = questionColumns[index];
          let nAll = 0;
          let nSome = 0;

          for (const row of instructorSurvey) {
            const value = toIntOrNull(row[questionColumn]);
            if (value === 3) nAll += 1;
            if (value === 2) nSome += 1;
          }

          const pctAll = Math.round((nAll / nTotal) * 100);
          const pctSome = Math.round((nSome / nTotal) * 100);

          questionBreakdown.push({
            questionNumber: index + 1,
            pctAll,
            pctSome,
          });

          weightedSum += pctAll + 0.5 * pctSome;
        }

        const weightedAvg = weightedSum / (QUESTIONS.length * 100);

        results.push({
          term,
          instructor,
          course,
          totalResponseCount: nTotal,
          weightedAvg,
          questionBreakdown,
        });
      }
    }
  }

  return results;
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function renderPage(results = [], error = "") {
  const hasResults = results.length > 0;

  const resultRows = hasResults
    ? results
        .map((result) => {
          const questionRows = result.questionBreakdown
            .map(
              (q) => `
                <tr>
                  <td>${q.questionNumber}</td>
                  <td>${q.pctAll}</td>
                  <td>${q.pctSome}</td>
                </tr>`
            )
            .join("");

          return `
            <tr>
              <td>${escapeHtml(result.term)}</td>
              <td>${escapeHtml(result.instructor)}</td>
              <td>${escapeHtml(result.course)}</td>
              <td>${result.totalResponseCount}</td>
              <td>${result.weightedAvg.toFixed(2)}</td>
              <td>
                <details>
                  <summary>View q1–q10 percentages</summary>
                  <table>
                    <thead>
                      <tr>
                        <th>Q#</th>
                        <th>% All</th>
                        <th>% Some</th>
                      </tr>
                    </thead>
                    <tbody>
                      ${questionRows}
                    </tbody>
                  </table>
                </details>
              </td>
            </tr>`;
        })
        .join("")
    : "";

  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>FAR Survey JavaScript Web App</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 2rem; }
    h1 { margin-bottom: 1rem; }
    form { margin-bottom: 1.5rem; }
    table { border-collapse: collapse; width: 100%; margin-bottom: 1rem; }
    th, td { border: 1px solid #ccc; padding: 0.5rem; text-align: left; vertical-align: top; }
    th { background: #f5f5f5; }
    .error { color: #b00020; margin-bottom: 1rem; }
    .muted { color: #666; }
    details { margin-top: 0.25rem; }
  </style>
</head>
<body>
  <h1>FAR Survey Calculator (JavaScript)</h1>
  <form method="post" enctype="multipart/form-data" action="/analyze">
    <input type="file" name="csv_file" accept=".csv" required />
    <button type="submit">Analyze</button>
  </form>

  ${error ? `<div class="error">${escapeHtml(error)}</div>` : ""}

  ${
    hasResults
      ? `<table>
            <thead>
              <tr>
                <th>Term</th>
                <th>Instructor</th>
                <th>Course</th>
                <th>Total Responses</th>
                <th>Weighted Avg.</th>
                <th>Question Breakdown</th>
              </tr>
            </thead>
            <tbody>
              ${resultRows}
            </tbody>
          </table>`
      : '<p class="muted">Upload a FAR survey CSV to see results.</p>'
  }
</body>
</html>`;
}

app.get("/", (_req, res) => {
  res.type("html").send(renderPage([], ""));
});

app.post("/analyze", upload.single("csv_file"), (req, res) => {
  const uploadedFile = req.file;

  if (!uploadedFile) {
    res.type("html").status(400).send(renderPage([], "Please choose a CSV file."));
    return;
  }

  try {
    const rows = parse(uploadedFile.buffer.toString("utf8"), {
      columns: true,
      skip_empty_lines: true,
      relax_column_count: true,
    });

    const results = calculateResults(rows);

    if (results.length === 0) {
      res.type("html").send(renderPage([], "No instructor survey rows were found in this file."));
      return;
    }

    res.type("html").send(renderPage(results, ""));
  } catch (error) {
    res
      .type("html")
      .status(400)
      .send(renderPage([], `Could not parse CSV: ${error.message || String(error)}`));
  }
});

app.listen(PORT, () => {
  console.log(`FAR JavaScript web app running at http://127.0.0.1:${PORT}`);
});
