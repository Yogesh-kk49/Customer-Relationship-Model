# 🚀 CRM Web Application (Django)

A fully functional **Customer Relationship Management (CRM)** web application built using **Django**, designed to manage customers, leads, and documents efficiently with a clean and structured backend.

---

## 📌 Project Overview

This CRM system allows businesses or users to:

* Manage customer data
* Track leads
* Upload and manage documents
* Handle user authentication securely

The project follows **Django best practices**, with modular apps and scalable architecture, making it ideal for learning and real-world usage.

---

## ✨ Features

* 🔐 User Authentication (Login / Logout)
* 👥 Customer Management System
* 📊 Lead Tracking
* 📁 File & Document Uploads
* 🛠️ Django Admin Panel
* 🧩 Modular App Structure
* 🌐 Server-side Rendering with Templates
* ⚙️ Environment Variable Configuration

---

## 🛠️ Tech Stack

* **Backend:** Django (Python)
* **Frontend:** HTML, CSS (Django Templates)
* **Database:** SQLite (Development)
* **Server:** Gunicorn
* **Version Control:** Git & GitHub
* **Deployment:** Render

---

## 📂 Project Structure

```bash
crm_project/
│── manage.py
│── crm/                # Main project settings
│── accounts/           # Authentication module
│── customers/          # Customer management
│── leads/              # Lead tracking
│── documents/          # File uploads
│── templates/          # HTML templates
│── static/             # CSS, JS, assets
│── media/              # Uploaded files
│── db.sqlite3
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/crm-project.git
cd crm-project
```

### 2️⃣ Create virtual environment

```bash
python -m venv env
```

### 3️⃣ Activate environment

```bash
env\Scripts\activate     # Windows
```

### 4️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 5️⃣ Apply migrations

```bash
python manage.py migrate
```

### 6️⃣ Run the server

```bash
python manage.py runserver
```

👉 Open in browser:

```
http://127.0.0.1:8000/
```

---

## 🔑 Default Admin Access

Create superuser:

```bash
python manage.py createsuperuser
```

Then login at:

```
/admin
```

---

## 🚀 Future Improvements

* REST API integration (Django REST Framework)
* Role-based access control
* Dashboard analytics & charts
* Email notifications
* Search & filtering improvements

---

## 🌐 Deployment

This project can be deployed on:

* Render
* Railway
* AWS / DigitalOcean

---

## 📌 Use Cases

* Academic projects
* Portfolio showcase
* CRM system prototype
* Django learning project

---

## 🤝 Contributing

Contributions are welcome!
Feel free to fork the repository and submit a pull request.

---

## 👨‍💻 Author

**Yogesh**

---

⭐ If you like this project, give it a star on GitHub!
