from flask import Flask, render_template, request
import smtplib

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def contact_form():
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        phone = request.form["phone"]
        email = request.form["email"]
        subject = f"New Inquiry from {first_name} {last_name} - Phone: {phone}"
        message = request.form["message"]

        # Validate the data (you can add more validation if needed)
        if not first_name or not last_name or not email or not message:
            return "Please fill out all the fields."

        # Set up email parameters
        to_email = "dcornelius@basecampcodingacademy.org"  # Change this to your recipient's email address
        sender_email = email  # Update with your sender email address

        # Send the email using SMTP
        try:
            smtp_server = "smtp.gmail.com"  # Update with your SMTP server
            smtp_port = 587  # Update with your SMTP port

            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()

            email_body = f"Name: {first_name} {last_name}\nEmail: {email}\nPhone: {phone}\nMessage:\n{message}"
            server.sendmail(sender_email, to_email, email_body)

            server.quit()  # Close the SMTP connection after sending the email

            return "Thank you! Your inquiry has been sent."

        except Exception as e:
            print(f"Error sending email: {e}")
            return "Oops! Something went wrong. Please try again later."

    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True)
