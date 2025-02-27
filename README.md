# "KI konkret" - ZKI-Workshop für IT-Leitungen/CIO und Entwickler:innen

Dieses Repository enthält Code für den Workshop: Entwickler - Hackathon zur Erstellung von Schnittstellen für KI-Modelle mit Gradio

## CV Generator - ATS Optimized

This application automatically creates professional CVs optimized for Applicant Tracking Systems (ATS) using Gradio and LLMs.

### Features

- User-friendly interface for inputting personal and professional information:
  - Full Name
  - Contact Information
  - Professional Summary
  - Education
  - Work Experience
  - Skills
  - Achievements
  - References
  - Job Description
- AI-powered CV generation optimized for ATS screening tools
- Formatted PDF download with proper styling and layout
- Multiple LLM model selection

### Getting Started

1. Set up the environment:
   ```
   conda env create -f environment.yml
   conda activate ki-konkret-hackathon
   ```

2. Configure the `settings.yml` file with your API key and preferred models.

3. Run the application:
   ```
   python cvApp.py
   ```

4. Try the demo (with sample data):
   ```
   python demo.py
   ```

### Configuration

1. The app uses a gitignored `settings.yml` file that contains your API credentials.
2. On first run, it will:
   - Copy from `settings.yml.example` if available
   - Ask you for your API key via console input
   - Save it to the gitignored `settings.yml` file

Configuration parameters:
- `models`: List of available LLM models
- `api_key`: Your API key for accessing the LLM service (never committed to git)
- `base_url`: API endpoint for the LLM service

### Requirements

- Python 3.x
- Gradio
- FPDF
- Other dependencies listed in environment.yml

The goal of this application is to generate CVs that are optimized to pass automated CV screening tools while maintaining a professional appearance for human reviewers.