CiteRight - An Intelligent Academic Research Hub
CiteRight is a modern, full-stack web application designed to be a central hub for researchers to upload, discover, and discuss academic papers. It moves beyond a simple document manager by integrating social networking features and leveraging AI to automate content analysis and summarization.

🎯 Core Concept
The goal of CiteRight is to create a dynamic, collaborative environment where research meets social media. Users can build their own library, follow other researchers, engage in discussions directly on paper pages, and discover new work through an intelligent, searchable interface.

✨ Key Features
This project is currently under active development. The following features have been implemented:

👤 User Authentication: Secure and simple user onboarding using Google Accounts (django-allauth).

📄 Paper Upload & Management:

Upload research papers (PDF format).

Automatic Thumbnail Generation: The first page of every uploaded PDF is converted into a visual thumbnail using PyMuPDF.

Ability to delete uploaded papers, which also removes the associated files from storage.

🤖 AI-Powered Content Analysis:

Automatic Tagging: An NLP model (scikit-learn & NLTK) extracts relevant keywords from the PDF content to automatically tag papers.

AI-Generated Abstracts: A background task (Celery) sends the PDF text to the Google Gemini API to generate a formal summary or article.

Editable Content: Users can edit the AI-generated abstract or replace it with their own.

🔍 Search & Discovery:

A global search engine to find papers by title, author, or the uploader's username.

Filter papers by clicking on tags in the sidebar.

🌐 Social Networking:

User Profiles: Every user has a profile page that showcases their uploaded papers and social stats.

Follow System: Users can follow and unfollow other researchers.

Public Discussions: A full commenting system under each paper to facilitate peer discussion.

🛠️ Tech Stack
This project is built with a modern, scalable tech stack:

Backend: Django

Frontend: HTML5, Custom CSS (No CSS Framework)

Database: SQLite (for development), PostgreSQL (recommended for production)

Authentication: django-allauth for Google OAuth2

Background Tasks: Celery with Redis as the message broker

File Processing: PyMuPDF (thumbnails), PyPDF2 (text extraction)

AI & NLP:

scikit-learn & NLTK for keyword extraction.

Google Gemini API for abstract generation.

Frontend Libraries: Select2.js for the scalable, searchable author selection form.

🚀 Getting Started
To get a local copy up and running, follow these simple steps.

Prerequisites
Python 3.8+

Pip

Redis (for Celery)

Installation
Clone the repository:

git clone [https://github.com/your-username/citeright.git](https://github.com/your-username/citeright.git)
cd citeright

Create and activate a virtual environment:

# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate

Install dependencies:
(First, create a requirements.txt file by running pip freeze > requirements.txt in your current project terminal.)

pip install -r requirements.txt

Set up environment variables:
You will need to get API credentials for Google OAuth2 and the Google Gemini API. Rename the .env.example file to .env and add your keys:

# in .env
GOOGLE_CLIENT_ID="your-google-client-id"
GOOGLE_SECRET="your-google-secret"
GEMINI_API_KEY="your-gemini-api-key"

You will then need to update settings.py to read these variables instead of hardcoding the keys.

Run database migrations:

python manage.py makemigrations
python manage.py migrate

Running the Application
To run the full application, you need to start both the Django development server and the Celery background worker. You will need two separate terminals for this.

Terminal 1: Start the Django Server

python manage.py runserver

Terminal 2: Start the Celery Worker

celery -A citeright worker --loglevel=info
