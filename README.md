# 🌩️ AWS Serverless Terraria Server Manager

A fully serverless web application built on AWS that allows users to register, log in, and manage their own preconfigured Terraria game servers through a simple and secure interface.

## 🎮 Features

- Static frontend hosted on Amazon S3
- User registration and login via AWS Lambda + API Gateway
- Each user can:
  - View their profile
  - Start a personal EC2 instance with a preconfigured Terraria server (AMI)
  - View server details: Instance ID, IP address, CPU usage, and current status
- Custom domain routing with Route 53
- Responses are handled client-side with plain JavaScript

## 🧱 Architecture Overview

- **Frontend:**  
  Static HTML/CSS/JavaScript pages hosted on **Amazon S3**  
  Pages: `index.html`, `login.html`, `register.html`, `profile.html`

- **Backend:**  
  - **Lambda Functions** for all backend logic (auth, EC2 operations, monitoring)
  - **API Gateway** exposing RESTful endpoints
  - **Amazon EC2** instances launched using a **custom AMI** with Terraria pre-installed and configured
  - **Route 53** for custom domain and DNS routing
  - Optional: **DynamoDB or S3** to associate EC2 instances to user accounts

## 🚀 How It Works

1. Users register and log in via frontend pages using API Gateway + Lambda.
2. After login, the profile page allows:
   - Launching a new EC2 instance from a prebuilt AMI
   - Viewing instance metadata and real-time stats
3. Each instance is tied to a specific user and monitored through AWS APIs.

## 🌐 Pages

- `index.html`: Welcome / landing page  
- `register.html`: Sign-up form  
- `login.html`: User authentication  
- `profile.html`: Server control dashboard (status, start/stop, metrics)

## 🛠️ Technologies Used

- HTML, CSS, Vanilla JavaScript
- AWS S3 (static hosting)
- AWS Lambda (backend logic)
- AWS API Gateway (API access)
- AWS EC2 (Terraria servers via AMI)
- AWS Route 53 (custom domain and DNS)
- AWS IAM (secure roles and permissions)

## 🗂️ Folder Structure
```
aws-terraria-server-manager/

├── frontend/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── profile.html

├── lambdas/
│   ├── loginHandler.py
│   ├── registerHandler.py
│   ├── startFinishInstance.py
│   ├── getInstanceStatus.py

├── diagrams/
│   └── architecture.pdf
│   └── flow-diagram.png

├── docs/
│   ├── project-details.pdf
│   ├── test-cases.pdf

├── README.md
```

