# 📚 CiteRight - An Intelligent Academic Research Hub

CiteRight is a modern, full-stack web application designed to be a central hub for researchers to upload, discover, and discuss academic papers.  
It moves beyond a simple document manager by integrating social networking features and leveraging AI to automate content analysis and summarization.

---

## 🎯 Core Concept
The goal of CiteRight is to create a dynamic, collaborative environment where research meets social media.  
Users can build their own library, follow other researchers, engage in discussions directly on paper pages, and discover new work through an intelligent, searchable interface.

---

## ✨ Key Features

### 👤 User Authentication
- Secure and simple user onboarding using **Google Accounts (django-allauth)**.

### 📄 Paper Upload & Management
- Upload research papers (**PDF format**).
- **Automatic Thumbnail Generation**: The first page of every uploaded PDF is converted into a visual thumbnail using *PyMuPDF*.
- Ability to **delete uploaded papers**, which also removes the associated files from storage.

### 🤖 AI-Powered Content Analysis
- **Automatic Tagging**: An NLP model (*scikit-learn & NLTK*) extracts relevant keywords from the PDF content.
- **AI-Generated Abstracts**: A background task (*Celery*) sends the PDF text to the **Google Gemini API** to generate a formal summary.
- **Editable Content**: Users can edit the AI-generated abstract or replace it with their own.

### 🔍 Search & Discovery
- Global search engine to find papers by title, author, or uploader's username.
- Filter papers by clicking on tags in the sidebar.

### 🌐 Social Networking
- **User Profiles**: Every user has a profile page that showcases their uploaded papers and social stats.
- **Follow System**: Users can follow/unfollow other researchers.
- **Public Discussions**: Full commenting system under each paper to facilitate peer discussion.

---

## 🛠️ Tech Stack

- **Backend**: Django  
- **Frontend**: HTML5, Custom CSS (No CSS Framework)  
- **Database**: SQLite (development), PostgreSQL (production)  
- **Authentication**: django-allauth (Google OAuth2)  
- **Background Tasks**: Celery + Redis  
- **File Processing**: PyMuPDF (thumbnails), PyPDF2 (text extraction)  
- **AI & NLP**:  
  - scikit-learn & NLTK for keyword extraction  
  - Google Gemini API for abstract generation  
- **Frontend Libraries**: Select2.js for scalable, searchable author selection form  

---

## 🚀 Getting Started

### ✅ Prerequisites
- Python 3.8+  
- pip  
- Redis (for Celery)  

### 📥 Installation

Clone the repository:
```bash
git clone https://github.com/your-username/citeright.git
cd citeright
