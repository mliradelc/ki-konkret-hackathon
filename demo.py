#!/usr/bin/env python
"""
Demo script to test CV Generator functionality with sample data.
Run with: python demo.py
"""

import os
import sys
from cvApp import generate_cv, load_config

# Sample data for CV generation
SAMPLE_DATA = {
    "name": "Max Mustermann",
    "contact": "Email: max.mustermann@example.com\nPhone: +49 123 456789\nAddress: Musterstraße 1, 12345 Berlin\nLinkedIn: linkedin.com/in/maxmustermann",
    "summary": "Erfahrener Softwareentwickler mit über 5 Jahren Erfahrung in der Entwicklung von Webanwendungen mit Python, Django und JavaScript. Spezialisiert auf Backend-Entwicklung und API-Design mit einem starken Fokus auf Code-Qualität und Testautomatisierung.",
    "education": "Technische Universität Berlin\nMaster of Science in Informatik, 2016-2018\nNote: 1,3\n\nHochschule für Technik und Wirtschaft Berlin\nBachelor of Science in Angewandte Informatik, 2012-2016\nNote: 1,7",
    "work_experience": "Digitale Lösungen GmbH, Berlin\nSenior Backend-Entwickler, 2020-heute\n- Entwurf und Implementierung von RESTful APIs mit Django REST Framework\n- Optimierung der Datenbankabfragen, was zu einer 40% schnelleren Anwendung führte\n- Einführung von CI/CD-Pipelines, die die Deploymentzeit um 60% reduzierten\n\nTech Innovationen AG, München\nSoftwareentwickler, 2018-2020\n- Entwicklung von Microservices mit Python und Flask\n- Integration von Drittanbieter-APIs für Zahlungsabwicklung und Authentifizierung\n- Implementierung automatisierter Tests, die die Fehlerrate um 30% reduzierten",
    "skills": "Programmiersprachen: Python, JavaScript, SQL, HTML, CSS\nFrameworks: Django, Flask, React, Vue.js\nDatenbanken: PostgreSQL, MongoDB, Redis\nTools: Git, Docker, Kubernetes, Jenkins\nSprachen: Deutsch (Muttersprache), Englisch (fließend), Französisch (Grundkenntnisse)",
    "achievements": "- Sprecher auf der PyCon DE 2019 zum Thema 'Skalierbare Backend-Architekturen mit Django'\n- Gewinner des Hackathon Berlin 2020 für ein Projekt zur COVID-19-Kontaktverfolgung\n- Veröffentlichung von 3 Open-Source-Paketen im Python Package Index mit über 50.000 Downloads",
    "references": "Auf Anfrage verfügbar",
    "job_description": "Wir suchen einen erfahrenen Python-Entwickler für unser wachsendes Backend-Team. Sie werden an der Entwicklung und Wartung unserer Cloud-basierten Plattform arbeiten, die Big Data-Analyse und maschinelles Lernen nutzt.\n\nAnforderungen:\n- Mindestens 3 Jahre Erfahrung mit Python-Entwicklung\n- Erfahrung mit Django oder ähnlichen Web-Frameworks\n- Solide Kenntnisse in SQL und NoSQL-Datenbanken\n- Vertrautheit mit Docker und Kubernetes\n- Kenntnisse in CI/CD und automatisierten Tests\n- Gute Teamfähigkeit und Kommunikationskompetenz\n- Deutsch- und Englischkenntnisse\n\nWir bieten:\n- Flexible Arbeitszeiten und Remote-Arbeit\n- Wettbewerbsfähiges Gehalt\n- Kontinuierliche Weiterbildungsmöglichkeiten\n- Modernes Arbeitsumfeld mit aktueller Technologie"
}

def run_demo():
    """Run a demonstration of the CV generator with sample data."""
    print("=" * 80)
    print("CV Generator Demo".center(80))
    print("=" * 80)
    
    # Check if settings.yml exists
    if not os.path.exists("settings.yml"):
        print("Error: settings.yml not found. Please create it first.")
        sys.exit(1)
    
    # Load config to verify it's working
    try:
        models, api_key, base_url = load_config()
        print(f"✓ Configuration loaded successfully")
        print(f"✓ Using model: {models[0]}")
        print(f"✓ API URL: {base_url}")
        
        # Basic validation of API key
        if api_key.startswith('<') or api_key.endswith('>') or api_key == "YOUR_API_KEY_HERE":
            print("⚠ Warning: API key appears to be a placeholder")
            print("  Please update settings.yml with a valid API key")
            sys.exit(1)
        else:
            print(f"✓ API key looks valid (starts with: {api_key[:4]}...)")
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)
    
    print("\nGenerating CV with sample data...")
    print("This may take a minute...\n")
    
    # Let user choose a template
    print("\nChoose a CV template:")
    print("1. Classic - Traditional format with blue headers")
    print("2. Modern - Contemporary design with teal accents")
    print("3. Minimalist - Clean, simple design with ample white space")
    
    # Try to get user input, but handle non-interactive environments (like Claude's bash tool)
    template_style = "classic"  # default
    try:
        template_choice = input("\nEnter choice (1-3) [default=1]: ").strip()
        
        # Map user input to template style
        if template_choice == "2":
            template_style = "modern"
        elif template_choice == "3":
            template_style = "minimalist"
    except (EOFError, KeyboardInterrupt):
        print("\nUsing default template (Classic) in non-interactive mode")
    
    print(f"\nGenerating CV with {template_style} template...")
    
    # Generate CV with sample data and selected template
    pdf_path, status = generate_cv(
        SAMPLE_DATA["name"],
        SAMPLE_DATA["contact"],
        SAMPLE_DATA["summary"],
        SAMPLE_DATA["education"],
        SAMPLE_DATA["work_experience"],
        SAMPLE_DATA["skills"],
        SAMPLE_DATA["achievements"],
        SAMPLE_DATA["references"],
        SAMPLE_DATA["job_description"],
        template_style
    )
    
    if pdf_path:
        print(f"✓ Success! CV generated at: {pdf_path}")
        print("  You can open this PDF to view the generated CV")
        
        # Try to open the PDF with the default viewer
        try:
            if sys.platform == 'win32':
                os.startfile(pdf_path)
            elif sys.platform == 'darwin':  # macOS
                os.system(f'open "{pdf_path}"')
            else:  # Linux
                os.system(f'xdg-open "{pdf_path}" &')
            print("  (Attempting to open the PDF with your default viewer)")
        except:
            pass
    else:
        print(f"✗ Failed to generate CV: {status}")

if __name__ == "__main__":
    run_demo()