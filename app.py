import os
import uuid
from flask import Flask, render_template, request, send_from_directory, after_this_request

# Import the function from your other file
from pdf_generator import create_pdf

app = Flask(__name__)

# Configure a folder to temporarily save the generated PDFs
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    """Serves the main page with the textarea form."""
    return render_template('index.html')


@app.route('/create-pdf', methods=['POST'])
def generate_pdf_from_text():
    """
    Handles the form submission, generates the PDF, and sends it for download.
    """
    # 1. Get the text content from the form
    text_content = request.form['text_content']
    if not text_content:
        return "Error: No text provided.", 400

    # 2. Generate a unique filename to avoid conflicts
    unique_filename = f"output_{uuid.uuid4().hex}.pdf"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

    try:
        # 3. Call your PDF generation function
        create_pdf(text_content, output_path)

        # 4. Use a callback to delete the file from the server after it's been sent
        @after_this_request
        def cleanup(response):
            try:
                os.remove(output_path)
            except Exception as error:
                app.logger.error("Error removing or closing downloaded file handle", error)
            return response

        # 5. Send the generated file to the user for download
        return send_from_directory(
            directory=app.config['UPLOAD_FOLDER'],
            path=unique_filename,
            as_attachment=True,
            download_name='generated_booklet.pdf' # The name the user will see
        )

    except Exception as e:
        # Handle any errors that might occur during PDF generation
        return f"An error occurred: {e}", 500


if __name__ == '__main__':
    app.run(debug=True)