# CivicConnect
# Community Problem Reporting and Resolution Platform

CivicConnect is a web-based platform that helps citizens report community problems and enables administrators to manage, track, and resolve complaints efficiently.

The platform uses Machine Learning to assist with complaint category prediction and improve the complaint management process.

#  Key Features

# Citizen Module
- Citizen registration and secure login.
- Submit community complaints with descriptions and images.
- Select complaint categories.
- Add complaint location using the map.
- Track complaint status.
- View submitted complaints and notifications.
- Manage user profile.

# Administrator Module
- Administrator login.
- View and manage citizen complaints.
- Update complaint status and department.
- Monitor reported community problems.
- Access complaint management features.

# Machine Learning
- Complaint category prediction.
- Text-based complaint analysis using TF-IDF.
- Logistic Regression classification model.
- Helps identify the relevant category for submitted complaints.

# Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend development |
| FastAPI | REST API |
| SQLite | Database |
| HTML | Web page structure |
| CSS | Styling |
| JavaScript | Frontend functionality |
| Bootstrap | Responsive interface |
| Scikit-learn | Machine Learning |
| TF-IDF | Text feature extraction |
| Logistic Regression | Complaint classification |

# Project Structure

```text
CivicConnect/
│
├── backend/
│   ├── routes/
│   ├── models.py
│   ├── database.py
│   └── main.py
│
├── client/
│   ├── js/
│   ├── css/
│   ├── images/
│   └── HTML pages
│
├── dataset/
│
├── ml/
│
├── README.md
└── .gitignore
```

# Installation and Execution

# 1. Clone the repository

```bash
git clone https://github.com/Sushmita-naik/CivicConnect.git
```

# 2. Open the project folder

```bash
cd CivicConnect
```

# 3. Install required dependencies

Install the Python packages required by the project.

# 4. Start the backend server

```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

# 5. Start the frontend server

Open another terminal and execute:

```bash
python -m http.server 5500 --bind 127.0.0.1 --directory client
```

# 6. Open the application

Visit:

http://127.0.0.1:5500/

# 7. API Documentation

Visit:

http://127.0.0.1:8000/docs

# 🎯 Project Objective

The main objective of CivicConnect is to provide a centralized digital platform for reporting and managing community problems. It aims to improve communication between citizens and administrators, support efficient complaint tracking, and use Machine Learning to assist in complaint classification.

# 🔮 Future Enhancements

- Real-time complaint status updates.
- Improved ML classification performance.
- Advanced analytics and visual dashboards.
- Mobile application support.
- Integration with municipal services.

# 👩‍💻 Project Information

**Project Name:** CivicConnect

**Domain:** Web Development and Machine Learning

**Project Type:** Community Problem Reporting and Resolution Platform

**GitHub Repository:** https://github.com/Sushmita-naik/CivicConnect

---

*Developed as an engineering project to support smarter community problem reporting and resolution.*
