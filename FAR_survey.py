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

if len(sys.argv) < 2:
    print("Usage: python FAR_survey.py <input csv file>")
    exit(1)
csv_file_path = sys.argv[1]

df = read_csv(csv_file_path)

for term in df["Term Name"].drop_duplicates().values:
    print("-------")
    for instructor in df["Instructor Name"].drop_duplicates().values:
        for course in df["Course Code Dashboard"].drop_duplicates().values:

            instructor_survey = df[(df["Term Name"]==term) & (df["Instructor Name"]==instructor) & (df["Course Code Dashboard"]==course) & (df["Survey Source"].str.contains("Instructor"))]
            questions=[
                "[NUM] Instructor Q1_1 - The instructor helped me understand what I was expected to learn",
                "[NUM] Instructor Q1_2 - The instructor explained the purpose of work I did in the course (things like discussions, assignments, exams, class activities)",
                "[NUM] Instructor Q1_3 - The instructor made deadlines clear",
                "[NUM] Instructor Q1_4 - The instructor was clear about how I would be graded",
                "[NUM] Instructor Q1_5 - The instructor provided feedback that helped me learn",
                "[NUM] Instructor Q2_1 - The instructor helped create an environment in the class (whether in person or online) that motivated me to learn",
                "[NUM] Instructor Q2_2 - The instructor responded respectfully if I had  questions",
                "[NUM] Instructor Q2_3 - The instructor helped me feel that I could succeed in the class",
                "[NUM] Instructor Q2_4 - The instructor helped me understand different ways to apply what I learned",
                "[NUM] Instructor Q2_5 - The instructor used approaches that encouraged me to participate in class activities (in person or online)"
            ]
            qq = instructor_survey[questions]
            n_total = len(qq)
            if n_total > 0:
                print(term, instructor, course)
                print("total response count =", n_total)

                weighted_sum = 0
                print ("q# \t all \t some")
                for i in range(len(questions)):
                    n_all  = len(qq[qq.iloc[:,i] == 3])
                    n_some = len(qq[qq.iloc[:,i] == 2])
                    n_not  = len(qq[qq.iloc[:,i] == 1])

                    pct_all = round(n_all/n_total*100)
                    pct_some = round(n_some/n_total*100)
                    print("q%d \t %d \t %d" % (i+1, pct_all, pct_some))

                    weighted_sum += (pct_all + 0.5*pct_some)
                    
                print("weighted avg. = %.2f" % (weighted_sum / (len(questions)*100)))


