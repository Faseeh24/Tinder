# Tinder Clone - Match Making App

This project is a Tinder clone, a match-making application built using Flask, Firebase, and various other technologies. It includes features such as user registration, login, profile management, chat functionality, and a premium subscription service.

## Images
![Screenshot 2024-12-27 222428](https://github.com/user-attachments/assets/5adf7a57-ecbe-42fd-8dbd-9f8bb1fbf34d)
![Screenshot 2024-12-27 222617](https://github.com/user-attachments/assets/522510e1-19de-4c37-b0a7-e80d60eb1ba8)
![Screenshot 2024-12-27 223012](https://github.com/user-attachments/assets/bea3d87e-2a47-4d8a-a70a-ad0e51862483)
![Screenshot 2024-12-27 223102](https://github.com/user-attachments/assets/fa1ab99b-eab1-4d5c-b832-99fb49dd98c7)
![Screenshot 2024-12-27 223337](https://github.com/user-attachments/assets/f4c382db-1acb-4110-ab13-0129e46c4add)
![Screenshot 2024-12-27 223544](https://github.com/user-attachments/assets/0b5abe39-744a-455e-8808-3bc289503846)


## Features

- User Registration and Login
- Profile Management
- Match Suggestions based on Similarity
- Chat Functionality (Premium Users Only)
- Rating and Feedback System
- Admin Dashboard
- Premium Subscription

## Installation

### Prerequisites

- Python 3.8 or higher
- Firebase account and Firestore database
- Google Cloud account for Gmail API

### Clone the Repository

```sh
git clone https://github.com/Faseeh24/Tinder.git
cd tinder-clone
```

### Create a Virtual Environment

```sh
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### Install Dependencies

```sh
pip install -r requirements.txt
```

### Firebase Setup

1. Create a Firebase project and Firestore database.
2. Download the Firebase Admin SDK service account key.
3. Place the key file in the project directory and update the `.env` file with the path.

### Google Cloud Setup

1. Enable the Gmail API in your Google Cloud project.
2. Download the OAuth 2.0 Client IDs credentials file.
3. Place the key file in the project directory and update the `.env` file with the path.

### Environment Variables

Create a `.env` file in the project directory with the following content:

```
flask_secret_key=your_flask_secret_key
path_to_firestore_key=path_to_firestore_key.json
path_to_smtp_key=path_to_smtp_key.json
user_email=your_smtp_email
```

### Run the Application

```sh
flask run
```

The application will be available at `http://127.0.0.1:5000`.

## Usage

### User Registration

1. Go to the registration page at `http://127.0.0.1:5000/register`.
2. Fill in the required details and submit the form.
3. You will receive a welcome email upon successful registration.

### User Login

1. Go to the login page at `http://127.0.0.1:5000/login`.
2. Enter your email and password to log in.

### Profile Management

1. After logging in, go to the profile page at `http://127.0.0.1:5000/profile`.
2. Update your profile details and save the changes.

### Match Suggestions

1. Go to the dashboard at `http://127.0.0.1:5000/dashboard`.
2. View suggested matches based on similarity scores.

### Chat Functionality

1. Only premium users can access the chat feature.
2. Go to the premium page at `http://127.0.0.1:5000/premium` to subscribe.
3. After subscribing, go to the chat page at `http://127.0.0.1:5000/chat` to start chatting with matches.

### Rating and Feedback

1. Go to a user's profile page.
2. Submit a rating and feedback for the user.

### Admin Dashboard

1. Only the admin user can access the admin dashboard.
2. Go to the admin page at `http://127.0.0.1:5000/admin` to view user statistics.
