import os
import pandas as pd
import openai
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Load the data
file_path = 'D:\\Downlode\\OneDrive\\Documents\\Downloads\\chatbot copy-20240603T070249Z-001\\chatbot copy\\student_info.xlsx'

try:
    df = pd.read_excel(file_path)
except Exception as e:
    print(f"Error loading Excel file: {e}")

# Set your OpenAI API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')  # Ensure this environment variable is set

def query_gpt(prompt):
    try:
        response = openai.Completion.create(
            engine="davinci",
            prompt=prompt,
            max_tokens=100,
            n=1,
            stop=None,
            temperature=0.5,
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"Error querying GPT: {e}")
        return "Error processing your request."

def find_student(query):
    query_lower = query.lower()

    fields = {
        "mobile number of student": 'Mobile No(student)',
        "mobile number of parent": 'Mobile No(parent)',
        "email of student": 'Email id(Student)',
        "personal email": 'Personal Email',
        "instagram": 'instagram id',
        "linkedin id": 'Linkedin Iink',
        "address": 'Permanent Address',
        "identification mark": 'Identifivation Mark',
        "blood group": 'Blood Group',
        "date of birth": 'Date OF Birth',
        "registration number": 'Registration No'
    }

    requested_field = None
    for key, value in fields.items():
        if key in query_lower:
            requested_field = value
            break

    if "roll number" in query_lower:
        try:
            roll_no = int(query_lower.split("roll number")[1].strip().split()[0])
            student_data = df[df['Roll No'] == roll_no].to_dict('records')
        except (ValueError, IndexError) as e:
            return f"Invalid roll number format: {e}"
    elif "name" in query_lower:
        try:
            name = query_lower.split("name")[1].strip()
            student_data = df[df['Name of Student'].str.contains(name, case=False, na=False)].to_dict('records')
        except IndexError as e:
            return f"Name not found in the query: {e}"
    else:
        return "Please provide either a roll number or a name."

    if not student_data:
        return "Student not found."

    student_info = student_data[0]

    if requested_field:
        return student_info.get(requested_field, f"Information '{requested_field}' not found.")
    return student_info

def handle_query(query):
    return find_student(query)

def chatbot_response(user_input):
    response = handle_query(user_input)
    return response

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_input = request.json.get('message')
        response = chatbot_response(user_input)
        return jsonify({"response": response})
    except Exception as e:
        print(f"Error in /chat endpoint: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0')