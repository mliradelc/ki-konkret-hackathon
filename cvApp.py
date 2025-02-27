import gradio as gr
import requests
import json
import tempfile
import os
from datetime import datetime
import yaml
import logging
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListItem, ListFlowable, Frame, PageTemplate, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm, mm, inch


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
         "content": "You are a professional CV writer who creates well-structured CVs optimized to pass Applicant Tracking Systems (ATS). You understand how to use relevant keywords from job descriptions and format content to maximize ATS scoring while maintaining readability for human reviewers."},
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

        Key requirements:
        1. Match terminology and keywords from the job description throughout the CV
        2. Use standard section headings that ATS can easily recognize (use all-caps for main section headers)
        3. Highlight relevant skills and experiences that match the job requirements
        4. Format the CV in a clean, professional way with proper spacing
        5. Quantify achievements whenever possible
        6. Avoid tables, columns, headers/footers, or complex formatting that could confuse ATS

        Format instructions:
        - Use ALL CAPS for main section headers (like "EDUCATION", "WORK EXPERIENCE", etc.)
        - Use bullet points (- ) for listing skills and achievements
        - For work experiences and education, put the organization/school name on one line, followed by position/degree and dates

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

def create_classic_template(content, name, file_path):
    """Create a classic, clean CV template with standard formatting"""
    try:
        # Set up the document
        doc = SimpleDocTemplate(
            file_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Define styles
        styles = getSampleStyleSheet()
        
        # Create custom styles
        cv_title = ParagraphStyle(
            name='CVTitle',
            parent=styles['Heading1'],
            alignment=TA_CENTER,
            fontSize=18,
            spaceAfter=16
        )
        
        section_header = ParagraphStyle(
            name='CVSectionHeader',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=10,
            spaceBefore=15,
            textColor=colors.darkblue
        )
        
        sub_header = ParagraphStyle(
            name='CVSubHeader',
            parent=styles['Heading3'],
            fontSize=12,
            spaceAfter=8
        )
        
        normal_text = ParagraphStyle(
            name='CVNormalText',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            spaceAfter=8
        )
        
        # Create elements list
        elements = []
        
        # Add title
        elements.append(Paragraph("Curriculum Vitae", cv_title))
        elements.append(Spacer(1, 10))
        
        # Process content
        current_list_items = []
        lines = content.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            i += 1
            
            if not line:
                elements.append(Spacer(1, 5))
                if current_list_items:
                    elements.append(ListFlowable(current_list_items, bulletType='bullet', leftIndent=20))
                    current_list_items = []
                continue
            
            # Detect headers
            if line.isupper() or (line.startswith('#') and not line.startswith('##')):
                if current_list_items:
                    elements.append(ListFlowable(current_list_items, bulletType='bullet', leftIndent=20))
                    current_list_items = []
                
                header_text = line.lstrip('#').strip() if line.startswith('#') else line
                elements.append(Paragraph(header_text, section_header))
            
            # Detect subheaders
            elif line.startswith('##') or line.startswith('*') or line.startswith('**'):
                if current_list_items:
                    elements.append(ListFlowable(current_list_items, bulletType='bullet', leftIndent=20))
                    current_list_items = []
                
                subheader_text = line.lstrip('#').strip() if line.startswith('##') else line.strip('* ')
                elements.append(Paragraph(subheader_text, sub_header))
            
            # Detect list items
            elif line.startswith('-') or line.startswith('•') or line.strip().startswith('*'):
                item_text = line.lstrip('-•* ').strip()
                current_list_items.append(ListItem(Paragraph(item_text, normal_text)))
            
            # Regular text
            else:
                if current_list_items:
                    elements.append(ListFlowable(current_list_items, bulletType='bullet', leftIndent=20))
                    current_list_items = []
                
                paragraph_text = line
                while i < len(lines) and lines[i].strip() and not (
                    lines[i].strip().isupper() or
                    lines[i].strip().startswith('#') or
                    lines[i].strip().startswith('*') or
                    lines[i].strip().startswith('-') or
                    lines[i].strip().startswith('•')
                ):
                    paragraph_text += " " + lines[i].strip()
                    i += 1
                
                elements.append(Paragraph(paragraph_text, normal_text))
        
        # Add any remaining list items
        if current_list_items:
            elements.append(ListFlowable(current_list_items, bulletType='bullet', leftIndent=20))
        
        # Build the PDF
        doc.build(elements)
        return True
    except Exception as e:
        logger.error(f"Error creating classic template: {str(e)}")
        return False

def create_modern_template(content, name, file_path):
    """Create a modern CV template with colored sidebars and modern styling"""
    try:
        # Set up the document with a modern layout
        doc = SimpleDocTemplate(
            file_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72, 
            bottomMargin=72
        )
        
        # Define styles with modern aesthetics
        styles = getSampleStyleSheet()
        
        # Create custom styles with modern fonts and colors
        cv_title = ParagraphStyle(
            name='ModernCVTitle',
            parent=styles['Heading1'],
            alignment=TA_LEFT,
            fontSize=20,
            fontName='Helvetica-Bold',
            spaceAfter=16,
            textColor=colors.darkslategray
        )
        
        section_header = ParagraphStyle(
            name='ModernSectionHeader',
            parent=styles['Heading2'],
            fontSize=16,
            fontName='Helvetica-Bold',
            spaceAfter=10,
            spaceBefore=15,
            textColor=colors.teal,
            borderWidth=0,
            borderPadding=5,
            borderColor=colors.teal,
            borderRadius=3
        )
        
        sub_header = ParagraphStyle(
            name='ModernSubHeader',
            parent=styles['Heading3'],
            fontSize=14,
            fontName='Helvetica-Bold',
            textColor=colors.darkslategray,
            spaceAfter=8
        )
        
        normal_text = ParagraphStyle(
            name='ModernNormalText',
            parent=styles['Normal'],
            fontSize=11,
            fontName='Helvetica',
            leading=14,
            spaceAfter=8
        )
        
        # Process content
        elements = []
        
        # Add name as main title
        elements.append(Paragraph(name, cv_title))
        elements.append(Spacer(1, 5))
        
        # Process content
        current_list_items = []
        lines = content.split('\n')
        i = 0
        
        # Detect contact info section to format specially
        contact_info = ""
        
        while i < len(lines):
            line = lines[i].strip()
            i += 1
            
            if not line:
                elements.append(Spacer(1, 5))
                if current_list_items:
                    elements.append(ListFlowable(current_list_items, bulletType='circle', leftIndent=20))
                    current_list_items = []
                continue
            
            # Detect headers with modern styling
            if line.isupper() or (line.startswith('#') and not line.startswith('##')):
                if current_list_items:
                    elements.append(ListFlowable(current_list_items, bulletType='circle', leftIndent=20))
                    current_list_items = []
                
                header_text = line.lstrip('#').strip() if line.startswith('#') else line
                elements.append(Spacer(1, 10))
                elements.append(Paragraph(header_text, section_header))
            
            # Detect subheaders
            elif line.startswith('##') or line.startswith('*') or line.startswith('**'):
                if current_list_items:
                    elements.append(ListFlowable(current_list_items, bulletType='circle', leftIndent=20))
                    current_list_items = []
                
                subheader_text = line.lstrip('#').strip() if line.startswith('##') else line.strip('* ')
                elements.append(Paragraph(subheader_text, sub_header))
            
            # Detect list items with modern bullets
            elif line.startswith('-') or line.startswith('•') or line.strip().startswith('*'):
                item_text = line.lstrip('-•* ').strip()
                current_list_items.append(ListItem(Paragraph(item_text, normal_text)))
            
            # Regular text
            else:
                if current_list_items:
                    elements.append(ListFlowable(current_list_items, bulletType='circle', leftIndent=20))
                    current_list_items = []
                
                paragraph_text = line
                while i < len(lines) and lines[i].strip() and not (
                    lines[i].strip().isupper() or
                    lines[i].strip().startswith('#') or
                    lines[i].strip().startswith('*') or
                    lines[i].strip().startswith('-') or
                    lines[i].strip().startswith('•')
                ):
                    paragraph_text += " " + lines[i].strip()
                    i += 1
                
                elements.append(Paragraph(paragraph_text, normal_text))
        
        # Add any remaining list items
        if current_list_items:
            elements.append(ListFlowable(current_list_items, bulletType='circle', leftIndent=20))
        
        # Build the PDF
        doc.build(elements)
        return True
    except Exception as e:
        logger.error(f"Error creating modern template: {str(e)}")
        return False

def create_minimalist_template(content, name, file_path):
    """Create a minimalist CV template with clean typography and ample white space"""
    try:
        # Set up the document
        doc = SimpleDocTemplate(
            file_path,
            pagesize=A4,
            rightMargin=80,
            leftMargin=80,
            topMargin=80,
            bottomMargin=80
        )
        
        # Define styles with minimalist aesthetics
        styles = getSampleStyleSheet()
        
        # Create clean, minimalist styles
        cv_title = ParagraphStyle(
            name='MinimalistTitle',
            parent=styles['Heading1'],
            alignment=TA_CENTER,
            fontSize=20,
            fontName='Helvetica-Bold',
            spaceAfter=30,
            textColor=colors.black
        )
        
        section_header = ParagraphStyle(
            name='MinimalistSectionHeader',
            parent=styles['Heading2'],
            alignment=TA_LEFT,
            fontSize=14,
            fontName='Helvetica-Bold',
            spaceAfter=15,
            spaceBefore=20,
            textColor=colors.black,
            leading=16
        )
        
        sub_header = ParagraphStyle(
            name='MinimalistSubHeader',
            parent=styles['Heading3'],
            fontSize=12,
            fontName='Helvetica-Bold',
            textColor=colors.black,
            spaceAfter=8
        )
        
        normal_text = ParagraphStyle(
            name='MinimalistNormalText',
            parent=styles['Normal'],
            fontSize=10,
            fontName='Helvetica',
            leading=14,
            spaceAfter=8
        )
        
        # Process content
        elements = []
        
        # Add minimal header
        elements.append(Paragraph(name, cv_title))
        elements.append(Spacer(1, 20))
        
        # Process content
        current_list_items = []
        lines = content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            i += 1
            
            if not line:
                elements.append(Spacer(1, 8))
                if current_list_items:
                    elements.append(ListFlowable(current_list_items, bulletType='bullet', leftIndent=15))
                    current_list_items = []
                continue
            
            # Detect headers with minimalist styling
            if line.isupper() or (line.startswith('#') and not line.startswith('##')):
                if current_list_items:
                    elements.append(ListFlowable(current_list_items, bulletType='bullet', leftIndent=15))
                    current_list_items = []
                
                header_text = line.lstrip('#').strip() if line.startswith('#') else line
                elements.append(Paragraph(header_text, section_header))
                # Add a thin line under headers
                elements.append(Spacer(1, 2))
            
            # Detect subheaders
            elif line.startswith('##') or line.startswith('*') or line.startswith('**'):
                if current_list_items:
                    elements.append(ListFlowable(current_list_items, bulletType='bullet', leftIndent=15))
                    current_list_items = []
                
                subheader_text = line.lstrip('#').strip() if line.startswith('##') else line.strip('* ')
                elements.append(Paragraph(subheader_text, sub_header))
            
            # Detect list items with minimalist bullets
            elif line.startswith('-') or line.startswith('•') or line.strip().startswith('*'):
                item_text = line.lstrip('-•* ').strip()
                current_list_items.append(ListItem(Paragraph(item_text, normal_text)))
            
            # Regular text
            else:
                if current_list_items:
                    elements.append(ListFlowable(current_list_items, bulletType='bullet', leftIndent=15))
                    current_list_items = []
                
                paragraph_text = line
                while i < len(lines) and lines[i].strip() and not (
                    lines[i].strip().isupper() or
                    lines[i].strip().startswith('#') or
                    lines[i].strip().startswith('*') or
                    lines[i].strip().startswith('-') or
                    lines[i].strip().startswith('•')
                ):
                    paragraph_text += " " + lines[i].strip()
                    i += 1
                
                elements.append(Paragraph(paragraph_text, normal_text))
        
        # Add any remaining list items
        if current_list_items:
            elements.append(ListFlowable(current_list_items, bulletType='bullet', leftIndent=15))
        
        # Build the PDF
        doc.build(elements)
        return True
    except Exception as e:
        logger.error(f"Error creating minimalist template: {str(e)}")
        return False

def create_pdf(content, name, template_style="classic"):
    """Create a PDF file from the generated content with proper formatting using ReportLab"""
    try:
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"CV_{name.replace(' ', '_')}_{timestamp}.pdf"
        
        # Create a temporary file
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, filename)
        
        # Select the appropriate template based on style
        success = False
        if template_style == "modern":
            success = create_modern_template(content, name, file_path)
        elif template_style == "minimalist":
            success = create_minimalist_template(content, name, file_path)
        else:  # Default to classic
            success = create_classic_template(content, name, file_path)
        
        if success:
            logger.info(f"PDF created successfully: {file_path}")
            return file_path
        else:
            return None
    except Exception as e:
        error_msg = f"Error creating PDF: {str(e)}"
        logger.error(error_msg)
        return None


def generate_cv(name, contact, summary, education, work_experience,
                skills, achievements, references, job_description, template_style="classic"):
    """Main function to generate CV PDF"""

    # Generate the CV content
    cv_content = generate_cv_content(
        name, contact, summary, education, work_experience,
        skills, achievements, references, job_description
    )

    # Check if content generation failed
    if cv_content.startswith("Error:"):
        return None, cv_content

    # Create PDF with the specified template style
    pdf_path = create_pdf(cv_content, name, template_style)

    if pdf_path:
        return pdf_path, f"CV generated successfully with {template_style} template! Click to download."
    else:
        return None, "Error: Failed to create PDF file."


# Create Gradio interface
with gr.Blocks(title="CV Generator") as app:
    gr.Markdown("# Professional CV Generator - ATS Optimized")
    gr.Markdown("Fill in the fields below to generate a customized CV for your job application. Your CV will be optimized to pass Applicant Tracking Systems (ATS) while maintaining a professional appearance.")

    with gr.Row():
        with gr.Column(scale=2):
            # First Column: Personal Information and Summary
            name = gr.Textbox(label="Full Name")
            contact = gr.Textbox(label="Contact Information", placeholder="Email, Phone, LinkedIn, Address, etc.",
                                lines=3)
            summary = gr.Textbox(label="Professional Summary", lines=5,
                                placeholder="Brief overview of your professional background and goals")
            
            # Template Selection with HTML/CSS preview
            gr.Markdown("### Choose CV Template")
            with gr.Row():
                # Using HTML to create visual templates with CSS styling
                with gr.Column(scale=1):
                    classic_html = """
                    <div style="border: 1px solid #ccc; padding: 10px; border-radius: 5px; height: 150px; background-color: white; position: relative; cursor: pointer;">
                        <div style="text-align: center; font-weight: bold; font-size: 1.2em; margin-bottom: 10px; color: navy;">Classic</div>
                        <div style="height: 10px; background-color: navy; margin-bottom: 5px;"></div>
                        <div style="height: 5px; background-color: navy; width: 80%; margin-bottom: 10px;"></div>
                        <div style="height: 5px; background-color: #ddd; margin-bottom: 5px;"></div>
                        <div style="height: 5px; background-color: #ddd; margin-bottom: 5px;"></div>
                        <div style="height: 5px; background-color: #ddd; margin-bottom: 5px;"></div>
                        <div style="position: absolute; bottom: 5px; right: 10px; color: #666; font-size: 0.8em;">Traditional</div>
                    </div>
                    """
                    gr.HTML(classic_html)
                
                with gr.Column(scale=1):
                    modern_html = """
                    <div style="border: 1px solid #ccc; padding: 10px; border-radius: 5px; height: 150px; background-color: white; position: relative; cursor: pointer;">
                        <div style="text-align: left; font-weight: bold; font-size: 1.2em; margin-bottom: 10px; color: teal;">Modern</div>
                        <div style="height: 2px; background-color: teal; margin-bottom: 10px;"></div>
                        <div style="height: 5px; background-color: #eee; margin-bottom: 5px;"></div>
                        <div style="height: 5px; background-color: #eee; margin-bottom: 5px;"></div>
                        <div style="height: 5px; background-color: #eee; margin-bottom: 5px;"></div>
                        <div style="position: absolute; bottom: 5px; right: 10px; color: teal; font-size: 0.8em;">Contemporary</div>
                    </div>
                    """
                    gr.HTML(modern_html)
                
                with gr.Column(scale=1):
                    minimalist_html = """
                    <div style="border: 1px solid #ccc; padding: 10px; border-radius: 5px; height: 150px; background-color: white; position: relative; cursor: pointer;">
                        <div style="text-align: center; font-weight: bold; font-size: 1.2em; margin-bottom: 15px; color: black;">Minimalist</div>
                        <div style="height: 1px; background-color: black; margin-bottom: 15px;"></div>
                        <div style="height: 3px; background-color: #f5f5f5; margin-bottom: 8px;"></div>
                        <div style="height: 3px; background-color: #f5f5f5; margin-bottom: 8px;"></div>
                        <div style="height: 3px; background-color: #f5f5f5; margin-bottom: 8px;"></div>
                        <div style="position: absolute; bottom: 5px; right: 10px; color: #888; font-size: 0.8em;">Clean & Simple</div>
                    </div>
                    """
                    gr.HTML(minimalist_html)
            
            # Template dropdown for actual selection
            template_dropdown = gr.Dropdown(
                choices=["classic", "modern", "minimalist"],
                value="classic",
                label="Select Template"
            )
            
            # Model selection if multiple models are available
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
            
        with gr.Column(scale=3):
            # Second Column: Experience and History
            with gr.Row():
                with gr.Column(scale=1):
                    education = gr.Textbox(label="Education", lines=5,
                                    placeholder="List your educational qualifications with institutions and dates")
                    work_experience = gr.Textbox(label="Work Experience", lines=10,
                                        placeholder="Detail your work history with roles, companies, dates, and responsibilities")
                
                with gr.Column(scale=1):
                    skills = gr.Textbox(label="Skills", lines=5, 
                                placeholder="List your technical and soft skills")
                    achievements = gr.Textbox(label="Achievements", lines=5,
                                    placeholder="Notable accomplishments, awards, certifications")
                    references = gr.Textbox(label="References", lines=3,
                                    placeholder="Professional references or 'Available upon request'")
            
            job_description = gr.Textbox(label="Job Description", lines=8,
                                    placeholder="Paste the job description you're applying for")

    # Template description based on selection
    template_description = gr.HTML(
        """
        <div style="padding: 10px; border-radius: 5px; background-color: #f9f9f9; margin-top: 10px;">
            <h4 style="margin-top: 0;">Classic Template</h4>
            <p>A traditional CV template with a clean, professional layout. Features standard sections with blue headers and conventional formatting.</p>
        </div>
        """
    )
    
    # Update template description when selection changes
    def update_template_info(template):
        if template == "modern":
            return """
            <div style="padding: 10px; border-radius: 5px; background-color: #f9f9f9; margin-top: 10px;">
                <h4 style="margin-top: 0; color: teal;">Modern Template</h4>
                <p>A contemporary CV design with teal accents and modern typography. Features clean layouts with subtle styling.</p>
            </div>
            """
        elif template == "minimalist":
            return """
            <div style="padding: 10px; border-radius: 5px; background-color: #f9f9f9; margin-top: 10px;">
                <h4 style="margin-top: 0;">Minimalist Template</h4>
                <p>A clean, simple design with ample white space and minimal styling. Perfect for a sleek, uncluttered appearance.</p>
            </div>
            """
        else:  # classic
            return """
            <div style="padding: 10px; border-radius: 5px; background-color: #f9f9f9; margin-top: 10px;">
                <h4 style="margin-top: 0; color: navy;">Classic Template</h4>
                <p>A traditional CV template with a clean, professional layout. Features standard sections with blue headers and conventional formatting.</p>
            </div>
            """
    
    template_dropdown.change(fn=update_template_info, inputs=[template_dropdown], outputs=[template_description])

    # Submit button and output
    submit_btn = gr.Button("Generate CV", size="large")
    output = gr.File(label="Download Your CV")
    status_output = gr.Textbox(label="Status", visible=True)


    def process_submission(name, contact, summary, education, work_experience,
                           skills, achievements, references, job_description, 
                           template_style="classic", model=None):
        if not name:
            return None, "Error: Name is required"

        # Update the model if a different one was selected
        global MODEL
        if model and model != MODEL and model in MODELS:
            MODEL = model
            logger.info(f"Using model: {MODEL}")

        logger.info(f"Using template style: {template_style}")

        pdf_path, status = generate_cv(
            name, contact, summary, education, work_experience,
            skills, achievements, references, job_description, 
            template_style
        )

        return pdf_path, status


    # Connect the interface with template selection
    if isinstance(MODELS, list) and len(MODELS) > 1:
        submit_btn.click(
            fn=process_submission,
            inputs=[name, contact, summary, education, work_experience,
                    skills, achievements, references, job_description, 
                    template_dropdown, model_dropdown],
            outputs=[output, status_output]
        )
    else:
        submit_btn.click(
            fn=process_submission,
            inputs=[name, contact, summary, education, work_experience,
                    skills, achievements, references, job_description,
                    template_dropdown],
            outputs=[output, status_output]
        )

# Launch the app
if __name__ == "__main__":
    # Create a settings.yml file from example if it doesn't exist
    if not os.path.exists("settings.yml"):
        if os.path.exists("settings.yml.example"):
            try:
                # Copy the example file
                with open("settings.yml.example", "r") as example_file:
                    template = yaml.safe_load(example_file)
                
                # Ask user for API key
                print("\n" + "="*80)
                print("CV Generator Setup".center(80))
                print("="*80)
                print("\nNo settings.yml file found. Creating one from the example template.")
                
                # Get API key from user
                api_key = input("\nPlease enter your API key: ").strip()
                if api_key:
                    if isinstance(template["api_key"], list):
                        template["api_key"] = [api_key]
                    else:
                        template["api_key"] = api_key
                    
                    # Write to settings.yml
                    with open("settings.yml", "w") as file:
                        yaml.dump(template, file, default_flow_style=False)
                    print("\n✓ Settings file created successfully!")
                    print("✓ Your API key has been saved to settings.yml (which is gitignored)")
                else:
                    print("\n⚠ No API key provided. You'll need to edit settings.yml manually.")
                    
                    # Just copy the example file
                    with open("settings.yml", "w") as file:
                        yaml.dump(template, file, default_flow_style=False)
            except Exception as e:
                logger.error(f"Failed to create settings.yml from example: {e}")
                # Fall back to creating a basic template
                template = {
                    "models": ["meta-llama-3.1-8b-instruct", "mistral-large-instruct"],
                    "api_key": "YOUR_API_KEY_HERE",
                    "base_url": "https://chat-ai.academiccloud.de/v1"
                }
                with open("settings.yml", "w") as file:
                    yaml.dump(template, file, default_flow_style=False)
                logger.info("Created basic settings.yml file. Please update with your actual API details.")
        else:
            # Create a basic template if example doesn't exist
            template = {
                "models": ["meta-llama-3.1-8b-instruct", "mistral-large-instruct"],
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
