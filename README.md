# "KI konkret" - ZKI-Workshop für IT-Leitungen/CIO und Entwickler:innen

Dieses Repository enthält Code für den Workshop: Entwickler - Hackathon zur Erstellung von Schnittstellen für KI-Modelle mit Gradio


CV Automatic creation Web-App using Gradio.

With Gradio connected to a LLM model that is set in the 'settings.yml' file the app should have and do:

- An UI where the user can add different attributes about themselves and the job he/she wants to apply to.
  -  Job Description
  - Contact Information
  - Professional Summary
  - Education
  - Skills
  - Achievements
  - References
- The app use this information to send a prompt to a LLM who will generate a CV from the input data
- The App has to receive this information, make the proper formating and save it in a PDF that the user is able to download it
- The goal is that the CV be optimized to pass automated CV tools that check the CVs


Other considerations:
- The 'settings.yml' file is already configured and should use only the information contained in it.