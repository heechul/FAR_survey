# %%
# This script reads a CSV file containing survey results from the FAR survey
# and calculates the weighted average of the responses to the questions.
#
# Installation:
# $ pip install pandas
# 
# Usage:
# $ python FAR_survey.py <input csv file> 
# 
# Example:
# $ python FAR_survey.py dashboard-export-05-19-pm-2024-01-21.csv
# 2023 Fall Heechul Yun EECS690/EECS700 Special Topics: Embedded ML Sect: 8001
# ...
# weighted avg. = 0.XX  <-- this is the number that should be included in the FAR
#

from pandas import read_csv
import sys


QUESTION_ALIASES = [
    (
        "[NUM] Instructor Q1_1 - The instructor helped me understand what I was expected to learn",
        "[NUM] I knew what I was expected to learn and do in this course.",
    ),
    (
        "[NUM] Instructor Q1_2 - The instructor explained the purpose of work I did in the course (things like discussions, assignments, exams, class activities)",
        "[NUM] I understood the purpose of the work I did in the course (things like discussions, assignments, exams, class activities).",
    ),
    (
        "[NUM] Instructor Q1_3 - The instructor made deadlines clear",
        "[NUM] The course policies (attendance, late work, etc.) and deadlines were clear.",
    ),
    (
        "[NUM] Instructor Q1_4 - The instructor was clear about how I would be graded",
        "[NUM] The grading criteria were clear.",
    ),
    (
        "[NUM] Instructor Q1_5 - The instructor provided feedback that helped me learn",
        "[NUM] The instructor provided feedback that helped me learn.",
    ),
    (
        "[NUM] Instructor Q2_1 - The instructor helped create an environment in the class (whether in person or online) that motivated me to learn",
        "[NUM] The class climate was respectful, open, and welcoming.",
    ),
    (
        "[NUM] Instructor Q2_2 - The instructor responded respectfully if I had  questions",
        "[NUM] The instructor was available to answer questions or provide assistance.",
    ),
    (
        "[NUM] Instructor Q2_3 - The instructor helped me feel that I could succeed in the class",
        "[NUM] The instructor helped me feel that I could succeed in the class.",
    ),
    (
        "[NUM] Instructor Q2_4 - The instructor helped me understand different ways to apply what I learned",
        "[NUM] I acquired knowledge and skills that I can use in the future (in other courses, work, life).",
    ),
    (
        "[NUM] Instructor Q2_5 - The instructor used approaches that encouraged me to participate in class activities (in person or online)",
        "[NUM] The instructor’s approach encouraged me to participate and engage in class meetings or activities.",
    ),
]


def populated_column(df, aliases):
    for column in aliases:
        if column in df.columns and df[column].notna().any():
            return column
    for column in aliases:
        if column in df.columns:
            return column
    raise ValueError(f"Could not find any of these CSV columns: {', '.join(aliases)}")


def calculate_results(df):
    term_column = populated_column(df, ("Term Name", "Term Name*"))
    instructor_column = populated_column(df, ("Instructor Name", "Instructor Name*"))
    course_column = populated_column(
        df, ("Course Code Dashboard", "Course Code Dashboard*")
    )
    survey_source_column = populated_column(
        df, ("Survey Source", "Survey Source*")
    )
    question_columns = [
        populated_column(df, aliases) for aliases in QUESTION_ALIASES
    ]
    four_point_scale = any(
        column == aliases[1]
        for column, aliases in zip(question_columns, QUESTION_ALIASES)
    )
    results = []

    for term in df[term_column].drop_duplicates().values:
        for instructor in df[instructor_column].drop_duplicates().values:
            for course in df[course_column].drop_duplicates().values:
                instructor_survey = df[
                    (df[term_column] == term)
                    & (df[instructor_column] == instructor)
                    & (df[course_column] == course)
                    & df[survey_source_column].str.contains("Instructor", na=False)
                ]

                qq = instructor_survey[question_columns]
                n_total = len(qq)
                if n_total == 0:
                    continue

                question_breakdown = []
                weighted_sum = 0

                for i in range(len(QUESTION_ALIASES)):
                    responses = qq.iloc[:, i]
                    if four_point_scale:
                        question_score = sum(
                            (value - 1) / 3
                            for value in responses.dropna()
                            if value in (1, 2, 3, 4)
                        )
                        question_breakdown.append(
                            {
                                "question_number": i + 1,
                                "score_pct": round(question_score / n_total * 100),
                            }
                        )
                        weighted_sum += question_score
                    else:
                        n_all = len(responses[responses == 3])
                        n_some = len(responses[responses == 2])

                        pct_all = round(n_all / n_total * 100)
                        pct_some = round(n_some / n_total * 100)

                        question_breakdown.append(
                            {
                                "question_number": i + 1,
                                "pct_all": pct_all,
                                "pct_some": pct_some,
                            }
                        )
                        weighted_sum += pct_all + 0.5 * pct_some

                weighted_avg = (
                    weighted_sum / (n_total * len(QUESTION_ALIASES))
                    if four_point_scale
                    else weighted_sum / (len(QUESTION_ALIASES) * 100)
                )

                results.append(
                    {
                        "term": term,
                        "instructor": instructor,
                        "course": course,
                        "total_response_count": n_total,
                        "weighted_avg": weighted_avg,
                        "score_scale": "four_point" if four_point_scale else "legacy",
                        "question_breakdown": question_breakdown,
                    }
                )

    return results


def print_results(results):
    for result in results:
        print("-------")
        print(result["term"], result["instructor"], result["course"])
        print("total response count =", result["total_response_count"])
        if result["score_scale"] == "four_point":
            print("q# \t score %")
            for row in result["question_breakdown"]:
                print("q%d \t %d" % (row["question_number"], row["score_pct"]))
        else:
            print("q# \t all \t some")
            for row in result["question_breakdown"]:
                print(
                    "q%d \t %d \t %d"
                    % (row["question_number"], row["pct_all"], row["pct_some"])
                )
        print("weighted avg. = %.2f" % result["weighted_avg"])


def main():
    if len(sys.argv) < 2:
        print("Usage: python FAR_survey.py <input csv file>")
        return 1

    csv_file_path = sys.argv[1]
    df = read_csv(csv_file_path)
    results = calculate_results(df)
    print_results(results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


