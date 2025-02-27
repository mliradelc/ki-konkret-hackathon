import gradio as gr
import requests
import json
import tempfile
from fpdf import FPDF
import os
from datetime import datetime
import yaml
import logging


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config():
    try:
        with open("settings.yml", "r") as file:
            meta_data = yaml.safe_load(file)
    except Exception as e:
        logger.info(f"Failed to read config file settings.yml \nException was:")
        logger.error(e)
        raise e

    # Extract models as a list
    models = meta_data["models"]

    # Extract API key as a string (remove list if present)
    api_key = meta_data['api_key']
    if isinstance(api_key, list) and len(api_key) > 0:
        api_key = api_key[0]

    # Extract base URL as a string (remove list if present)
    base_url = meta_data['base_url']
    if isinstance(base_url, list) and len(base_url) > 0:
        base_url = base_url[0]

    return models, api_key, base_url


# Load configuration
try:
    MODELS, API_KEY, BASE_URL = load_config()
    # Default to the first model if multiple are available
    MODEL = MODELS[0] if isinstance(MODELS, list) and MODELS else "gpt-3.5-turbo"

    # Remove any placeholder text or quotes from API key
    if API_KEY and (API_KEY.startswith('<') or API_KEY.endswith('>')):
        logger.warning("API key appears to be a placeholder. Please update with your actual API key.")

    logger.info(f"Configuration loaded successfully. Using model: {MODEL}")
    logger.info(f"Base URL: {BASE_URL}")
except Exception as e:
    logger.error(f"Failed to load configuration: {e}")
    # Set default values that will trigger error messages when used
    MODEL = "CONFIG_NOT_LOADED"
    API_KEY = "CONFIG_NOT_LOADED"
    BASE_URL = "CONFIG_NOT_LOADED"


def generate_cv_content(name, contact, summary, education, work_experience,
                        skills, achievements, references, job_description):
    """Generate formatted CV content using LLM"""

    # Check if API configuration is loaded
    if API_KEY == "CONFIG_NOT_LOADED" or BASE_URL == "CONFIG_NOT_LOADED":
        error_msg = "Error: API configuration not loaded. Please check your settings.yml file."
        logger.error(error_msg)
        return error_msg

    # Construct the messages for the chat completion API
    messages = [
        {"role": "system",
         "content": "You are a professional CV writer who creates well-structured, professional CVs."},
        {"role": "user", "content": f"""
        Create a professional CV for {name} who is applying for the following job:

        {job_description}

        Use the following information to create a well-structured, professional CV:

        CONTACT INFORMATION:
        {contact}

        PROFESSIONAL SUMMARY:
        {summary}

        EDUCATION:
        {education}

        WORK EXPERIENCE:
        {work_experience}

        SKILLS:
        {skills}

        ACHIEVEMENTS:
        {achievements}

        REFERENCES:
        {references}

        Format the CV in a clean, professional way that highlights the candidate's strengths relevant to the job description.
        Return the content in plain text with clear section headers. Do not comment before and after the content.
        """}
    ]

    # Properly set up headers with Bearer token
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    # Construct the payload according to chat completions API format
    data = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1500
    }

    try:
        # Construct the full endpoint URL for chat completions
        endpoint_url = f"{BASE_URL.rstrip('/')}/chat/completions"
        logger.info(f"Sending request to {endpoint_url}")

        # Log the request details for debugging (omit sensitive info)
        logger.debug(
            f"Request headers: {json.dumps({k: v for k, v in headers.items() if k.lower() != 'authorization'})}")
        logger.debug(f"Request model: {MODEL}")

        # Make the API request
        response = requests.post(endpoint_url, headers=headers, json=data)

        # Check for HTTP errors
        if response.status_code != 200:
            logger.error(f"API request failed with status code {response.status_code}: {response.text}")
            return f"Error: API request failed with status code {response.status_code}. Details: {response.text}"

        # Parse the response
        result = response.json()

        # Safe logging of response structure - convert dict_keys to list
        logger.debug(f"Response keys: {list(result.keys())}")

        # Extract the generated text from the response
        if "choices" in result and len(result["choices"]) > 0:
            choice = result["choices"][0]
            if "message" in choice and "content" in choice["message"]:
                cv_content = choice["message"]["content"].strip()
            else:
                logger.error(f"Unexpected response structure in choice: {str(choice)}")
                return "Error: Unexpected API response structure"
        else:
            logger.error(f"No choices in API response")
            return "Error: No content generated by the API"

        logger.info("Successfully generated CV content")
        return cv_content
    except Exception as e:
        error_msg = f"Error generating CV content: {str(e)}"
        logger.error(error_msg)
        return error_msg

def create_pdf(content, name):
    """Create a PDF file from the generated content using markdown conversion"""
    try:
        # Convert markdown to HTML
        from mistletoe import markdown
        html_content = markdown(content)

        # Create a PDF object
        pdf = FPDF()
        pdf.add_page()

        # Add title
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="Curriculum Vitae", ln=True, align='C')
        pdf.ln(10)

        # Write the HTML content
        pdf.write_html(html_content)

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"CV_{name.replace(' ', '_')}_{timestamp}.pdf"

        # Create a temporary file
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, filename)

        # Save the pdf
        pdf.output(file_path)

        logger.info(f"PDF created successfully: {file_path}")
        return file_path
    except Exception as e:
        error_msg = f"Error creating PDF: {str(e)}"
        logger.error(error_msg)
        return None


def generate_cv(name, contact, summary, education, work_experience,
                skills, achievements, references, job_description):
    """Main function to generate CV PDF"""

    # Generate the CV content
    cv_content = generate_cv_content(
        name, contact, summary, education, work_experience,
        skills, achievements, references, job_description
    )

    # Check if content generation failed
    if cv_content.startswith("Error:"):
        return None, cv_content

    # Create PDF
    pdf_path = create_pdf(cv_content, name)

    if pdf_path:
        return pdf_path, "CV generated successfully! Click to download."
    else:
        return None, "Error: Failed to create PDF file."


# Create Gradio interface
with gr.Blocks(title="CV Generator") as app:
    gr.Markdown("# Professional CV Generator")
    gr.Markdown("Fill in the fields below to generate a customized CV for your job application.")

    with gr.Row():
        with gr.Column():
            name = gr.Textbox(label="Full Name")
            contact = gr.Textbox(label="Contact Information", placeholder="Email, Phone, LinkedIn, Address, etc.",
                                 lines=3)
            summary = gr.Textbox(label="Professional Summary", lines=5,
                                 placeholder="Brief overview of your professional background and goals")
            education = gr.Textbox(label="Education", lines=5,
                                   placeholder="List your educational qualifications with institutions and dates")
            work_experience = gr.Textbox(label="Work Experience", lines=10,
                                         placeholder="Detail your work history with roles, companies, dates, and responsibilities")

        with gr.Column():
            skills = gr.Textbox(label="Skills", lines=5, placeholder="List your technical and soft skills")
            achievements = gr.Textbox(label="Achievements", lines=5,
                                      placeholder="Notable accomplishments, awards, certifications")
            references = gr.Textbox(label="References", lines=5,
                                    placeholder="Professional references or 'Available upon request'")
            job_description = gr.Textbox(label="Job Description", lines=10,
                                         placeholder="Paste the job description you're applying for")

    # Add model selection dropdown if multiple models are available
    if isinstance(MODELS, list) and len(MODELS) > 1:
        model_dropdown = gr.Dropdown(
            choices=MODELS,
            value=MODEL,
            label="Select AI Model"
        )
    else:
        model_dropdown = gr.Textbox(
            value=MODEL,
            label="AI Model",
            interactive=False
        )

    submit_btn = gr.Button("Generate CV")
    output = gr.File(label="Download Your CV")
    status_output = gr.Textbox(label="Status", visible=True)


    def process_submission(name, contact, summary, education, work_experience,
                           skills, achievements, references, job_description, model=None):
        if not name:
            return None, "Error: Name is required"

        # Update the model if a different one was selected
        global MODEL
        if model and model != MODEL and model in MODELS:
            MODEL = model
            logger.info(f"Using model: {MODEL}")

        pdf_path, status = generate_cv(
            name, contact, summary, education, work_experience,
            skills, achievements, references, job_description
        )

        return pdf_path, status


    # Connect the interface
    if isinstance(MODELS, list) and len(MODELS) > 1:
        submit_btn.click(
            fn=process_submission,
            inputs=[name, contact, summary, education, work_experience,
                    skills, achievements, references, job_description, model_dropdown],
            outputs=[output, status_output]
        )
    else:
        submit_btn.click(
            fn=process_submission,
            inputs=[name, contact, summary, education, work_experience,
                    skills, achievements, references, job_description],
            outputs=[output, status_output]
        )

# Launch the app
if __name__ == "__main__":
    # Create a template settings.yml file if it doesn't exist
    if not os.path.exists("settings.yml"):
        template = {
            "models": ["meta-llama-3.1-8b-instruct", "codestral-22b"],
            "api_key": "YOUR_API_KEY_HERE",
            "base_url": "https://chat-ai.academiccloud.de/v1"
        }
        try:
            with open("settings.yml", "w") as file:
                yaml.dump(template, file, default_flow_style=False)
            logger.info("Created template settings.yml file. Please update with your actual API details.")
        except Exception as e:
            logger.error(f"Failed to create template settings.yml file: {e}")

    # Add settings.yml to .gitignore if it doesn't already contain it
    gitignore_path = ".gitignore"
    gitignore_entry = "settings.yml"

    try:
        # Check if .gitignore exists
        if os.path.exists(gitignore_path):
            with open(gitignore_path, "r") as file:
                content = file.read()

            # Add settings.yml to .gitignore if not already there
            if gitignore_entry not in content:
                with open(gitignore_path, "a") as file:
                    file.write(f"\n# API Configuration\n{gitignore_entry}\n")
                logger.info(f"Added {gitignore_entry} to .gitignore")
        else:
            # Create .gitignore if it doesn't exist
            with open(gitignore_path, "w") as file:
                file.write(f"# API Configuration\n{gitignore_entry}\n")
            logger.info(f"Created .gitignore with {gitignore_entry}")
    except Exception as e:
        logger.error(f"Failed to update .gitignore: {e}")

    # Launch the app
    app.launch()
