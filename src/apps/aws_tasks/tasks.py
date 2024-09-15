from .utils import lambda_task

@lambda_task
def send_email(user_id, subject, message):
    # Logic to send email
    print(f"Sending email to user {user_id} with subject '{subject}'")


@lambda_task
def generate_report(report_id):
    # Logic to generate a report
    print(f"Generating report {report_id}")
