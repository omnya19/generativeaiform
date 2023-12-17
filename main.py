from flask import Flask, render_template, request, redirect, flash, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import google.generativeai as palm
from datetime import datetime
from io import BytesIO

import secrets

app = Flask(__name__)
app.secret_key = 'omnya'
palm.configure(api_key="AIzaSyAKnWwc0R1eamUpSTTT_LKkB34E9K-Yl90")

defaults = {
    'model': 'models/text-bison-001',
    'temperature': 0.7,
    'candidate_count': 1,
    'top_k': 40,
    'top_p': 0.95,
    'max_output_tokens': 1024,
    'stop_sequences': [],
    'safety_settings': [
        {"category": "HARM_CATEGORY_DEROGATORY", "threshold": 1},
        {"category": "HARM_CATEGORY_TOXICITY", "threshold": 1},
        {"category": "HARM_CATEGORY_VIOLENCE", "threshold": 2},
        {"category": "HARM_CATEGORY_SEXUAL", "threshold": 2},
        {"category": "HARM_CATEGORY_MEDICAL", "threshold": 2},
        {"category": "HARM_CATEGORY_DANGEROUS", "threshold": 2},
    ]
}

doctor_answers = []
student_answers = []
students_info = []  # Initialize the list to store student information


@app.route('/')
def login():
    return render_template('login.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/doctor', methods=['POST'])
def doctor():
    return render_template('doctor.html')


@app.route('/create', methods=['POST'])
def prepare_exam():
    num_questions = int(request.form['num_questions'])
    exam_duration = int(request.form['exam_duration'])
    questions = [request.form[f'question_{i}']
                 for i in range(1, num_questions + 1)]
    answers = [request.form[f'answer_{i}']
               for i in range(1, num_questions + 1)]

    global doctor_questions, doctor_answers, exam_duration_global
    doctor_questions = questions
    doctor_answers = answers
    exam_duration_global = exam_duration

    return redirect('/student')


@app.route('/student')
def student():
    global start_time, exam_duration_global, doctor_questions
    start_time = datetime.now()

    return render_template('student.html', questions=doctor_questions, start_time=start_time, exam_duration=exam_duration_global)


@app.route('/submit_answers', methods=['POST'])
def submit_answers():
    student_name = request.form.get('student_name')
    student_answers = [request.form.get(
        f'answer_{i}', '') for i in range(1, len(doctor_answers) + 1)]
    num_correct_answers, similarity_score = compare_answers(
        doctor_answers, student_answers)

    # Save student information
    student_info = {
        'name': student_name,
        'num_correct_answers': num_correct_answers,
        'similarity_score': similarity_score,
    }
    students_info.append(student_info)

    # Generate PDF report
    pdf_report = generate_pdf_report(doctor_answers, students_info)

    # Save the PDF report on the server
    pdf_report_filename = save_pdf_report(pdf_report)

    # Provide the doctor with a link to download the report
    flash(f'PDF report generated. Download your report: {request.url_root}download/{pdf_report_filename}', 'success')

    return render_template('result.html', num_correct_answers=num_correct_answers, similarity_score=similarity_score)

def generate_pdf_report(doctor_answers, students_info):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)

    # Add content to the PDF
    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, 800, "Exam Results Summary")

    # Display information for each student
    y_position = 780
    for i, student_info in enumerate(students_info):
        pdf.drawString(100, y_position, f"Student Name: {student_info['name']}")
        pdf.drawString(100, y_position - 20, f"Number of Correct Answers: {student_info['num_correct_answers']}")
        pdf.drawString(100, y_position - 40, f"Similarity Score: {student_info['similarity_score']}%")

        # Display answers
        for j, (doctor, student) in enumerate(zip(doctor_answers, student_answers)):
            question_number = j + 1
            pdf.drawString(100, y_position - 60 - j * 20, f"Question {question_number}")
            pdf.drawString(250, y_position - 60 - j * 20, f"Doctor Answer: {doctor}")
            pdf.drawString(250, y_position - 70 - j * 20, f"Student Answer: {student}")

        y_position -= 100

    # Save the PDF
    pdf.save()

    # Move the buffer cursor to the beginning
    buffer.seek(0)

    return buffer


def save_pdf_report(pdf_report):
    # Save the PDF report on the server (you may want to use a dedicated folder)
    pdf_report_filename = f'exam_results_report_{datetime.now().strftime("%Y%m%d%H%M%S")}.pdf'
    
    with open(pdf_report_filename, 'wb') as file:
        file.write(pdf_report.read())

    return pdf_report_filename

@app.route('/download/<filename>')
def download_pdf_report(filename):
    # Provide a route for the doctor to download the PDF report
    return send_file(filename, as_attachment=True)


def compare_answers(doctor_answers, student_answers):
    prompt = f"Do the doctor and student answers have the same meaning?\n"
    num_correct_answers = 0

    for doctor, student in zip(doctor_answers, student_answers):
        prompt += f"Doctor Answer: {doctor}\nStudent Answer: {student}\n"

        response = palm.generate_text(
            **defaults,
            prompt=prompt
        )
        similarity_score = 0

        if response.result:
            similarity_text = response.result.lower()
            if 'yes' in similarity_text:
                similarity_score = 2
                num_correct_answers += 1
            elif 'no' in similarity_text:
                similarity_score = 0

    total_questions = len(doctor_answers)
    similarity_score_percentage = (
        num_correct_answers / total_questions) * 100 if total_questions > 0 else 0

    return num_correct_answers, similarity_score_percentage


if __name__ == '__main__':
    app.run(debug=True)
