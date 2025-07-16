# # import mysql.connector
# # import csv

# # # 1. Connect to MySQL
# # conn = mysql.connector.connect(
# #     host="localhost",
# #     user="root",
# #     password="0000",
# #     database="irt"
# # )
# # cursor = conn.cursor()

# # # 2. Read the correct CSV file
# # with open('C:\\Users\\asus\\Desktop\\IRT_Training\\random_user_answers.csv', 'r', encoding='utf-8') as file:
# #     reader = csv.DictReader(file)
# #     print("Headers found:", reader.fieldnames)  
# #     for row in reader:
# #         cursor.execute("""
# #             INSERT INTO user_details (username, email, roll_number, answers)
# #             VALUES (%s, %s, %s, %s)
# #         """, (
# #             row['username'],
# #             row['email'],
# #             row['roll_number'],
# #             row['answers']
# #         ))

# # # 3. Commit and close
# # conn.commit()
# # cursor.close()
# # conn.close()

# import mysql.connector
# import json

# # Ask for user details
# username = input("Enter your name: ")
# email = input("Enter your email: ")
# roll_number = input("Enter your roll number: ")

# # Connect to the MySQL database
# conn = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="0000",
#     database="irt"
# )
# cursor = conn.cursor(dictionary=True)

# # Get 20 random questions
# cursor.execute("SELECT * FROM questions ORDER BY RAND() LIMIT 10")
# questions = cursor.fetchall()

# # Dictionary to hold answers
# user_answers = {}

# print("=== Welcome to the Assessment ===\nPlease answer the following questions:\n")
# question_number = 0
# # Collect answers from user
# for q in questions:
#     question_number = question_number+1
#     print(f"Q{question_number}: {q['Questions']}")
#     print(f"A. {q['Option A']}")
#     print(f"B. {q['Option B']}")
#     print(f"C. {q['Option C']}")
#     print(f"D. {q['Option D']}")
    
#     answer = input("Your answer (A/B/C/D or leave blank to skip): ").strip().upper()
#     if answer not in ['A', 'B', 'C', 'D']:
#         answer = None
#     user_answers[q['number']] = answer
#     print()


# # Calculate score
# score = 0
# for q in questions:
#     q_no = q['number']
#     if user_answers[q_no] and user_answers[q_no] == q['Correct_Option']:
#         score += 1

# print(f"\nYour score is: {score}/20")

# # Store answers and user data
# answers_json = json.dumps(user_answers)

# insert_query = """
# INSERT INTO user_details (username, email, roll_number, answers, score)
# VALUES (%s, %s, %s, %s, %s)
# """
# cursor.execute(insert_query, (username, email, roll_number, answers_json, score))
# conn.commit()

# print("Your answers and score have been recorded.")

# # Clean up
# cursor.close()
# conn.close()
