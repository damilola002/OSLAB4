# OSLAB4
# Secure Cloud Storage System

**Course:** CSE 3320 — Operating Systems  
**Assignment:** Lab 4 — Secure Cloud Storage  
**Student:** Damilola Adesina
**Student ID:** 1002283276  
**University:** University of Texas at Arlington 
**Date:** 10/31/2026

---

## 1. Project Overview

Secure Cloud Storage is a Python-based client-server application that allows users to securely upload, store, retrieve, and download files.

The system uses AES-256-GCM encryption to encrypt files on the client before transmitting them to the server. The server stores the encrypted files without needing access to the client's encryption key.

The application also includes user authentication, password hashing, and file ownership controls to prevent unauthorized access.

## 2. Features

- User registration and login
- Secure password hashing using Argon2
- JWT-based authentication
- AES-256-GCM client-side file encryption
- Upload files of different types
- List files belonging to the logged-in user
- Download and decrypt individual files
- Download multiple files
- Automatically rename duplicate downloaded filenames
- File ownership and access control
- SQLite database for user and file metadata
- FastAPI REST API

## 3. Technologies Used

| Technology | Purpose |
|---|---|
| Python 3 | Application development |
| FastAPI | Backend REST API |
| Uvicorn | ASGI web server |
| SQLite | Database |
| Cryptography | AES-256-GCM encryption |
| Argon2 / pwdlib | Password hashing |
| PyJWT | Authentication tokens |
| Requests | Client-server HTTP communication |
| Python pathlib | File management |

## 4. System Architecture

The project follows a client-server architecture.

**Client:**
1. Accepts user input through a terminal menu.
2. Authenticates users through the server.
3. Encrypts files locally before uploading.
4. Sends encrypted files to the server using HTTP requests.
5. Downloads and decrypts files locally.

**Server:**
1. Processes registration and login requests.
2. Verifies JWT authentication tokens.
3. Stores encrypted files.
4. Maintains user and file metadata in SQLite.
5. Restricts file access to the authenticated owner.

**Data flow:**

```text
User
  |
  v
Python Terminal Client
  |
  | AES-256-GCM Encryption
  v
Encrypted File
  |
  | HTTP Request + JWT
  v
FastAPI Server
  |
  +---- SQLite Database
  |       - Users
  |       - File Ownership
  |
  +---- Encrypted File Storage
```

## 5. Project Structure

```text
LAB 4/
|
|-- client/
|   |-- main.py
|   |-- encryption.py
|   |-- downloads/
|   |-- secret.key (local only)
|
|-- server/
|   |-- main.py
|   |-- auth.py
|   |-- database.py
|   |-- uploads/
|   |-- securecloud.db (local runtime data)
|
|-- requirements.txt
|-- README.md
```

The application may also contain a legacy `metadata.json` file from an earlier implementation.

## 6. Installation

### Prerequisites

- Python 3.10 or later
- pip
- Terminal or VS Code

### Step 1: Open the project

```bash
cd "LAB 4"
```

### Step 2: Create a virtual environment

```bash
python3 -m venv .venv
```

Activate the environment on macOS/Linux:

```bash
source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

### Step 3: Install dependencies

```bash
python -m pip install -r requirements.txt
```

Ensure `requirements.txt` includes:

```text
fastapi
uvicorn
python-multipart
requests
cryptography
pwdlib[argon2]
PyJWT
```

## 7. Running the Application

### Step 1: Initialize the database

```bash
python server/database.py
```

### Step 2: Configure the JWT secret

On macOS/Linux:

```bash
export SECURECLOUD_JWT_SECRET="$(python -c 'import secrets; print(secrets.token_hex(32))')"
```

Keep this secret private.

### Step 3: Start the server

```bash
python -m uvicorn server.main:app --host 127.0.0.1 --port 8000
```

The API will be available at:

http://127.0.0.1:8000

API documentation:

http://127.0.0.1:8000/docs

### Step 4: Start the client

Open another terminal, activate the virtual environment, and run:

```bash
python client/main.py
```

## 8. Using the Application

When the client starts, users can:

```text
================================
      SECURE CLOUD STORAGE
================================
1. Register
2. Login
3. Exit
```

After successful login:

```text
================================
      WELCOME, USER
================================
1. Upload a file
2. List my files
3. Download and decrypt a file
4. Download all my files
5. Logout
6. Exit
```

### Uploading a File

1. Log in.
2. Select option 1.
3. Enter the path of the file.
4. The client encrypts the file using AES-256-GCM.
5. The encrypted file is uploaded to the server.
6. The server returns a unique file ID.

### Downloading a File

1. Select option 2 to view stored files.
2. Copy the file ID.
3. Select option 3.
4. Enter the file ID.
5. The client downloads and decrypts the file.
6. The decrypted file is saved in `client/downloads/`.

If a filename already exists, the application automatically generates a unique filename.

## 9. Security Implementation

### AES-256-GCM Encryption

Files are encrypted locally using AES-GCM with a 256-bit key and a randomly generated 12-byte nonce.

AES-GCM provides confidentiality and integrity protection for encrypted file contents.

The encryption key is stored locally in `client/secret.key` and is not transmitted to the server.

### Password Security

Passwords are hashed using Argon2 before being stored in SQLite. Plaintext passwords are not saved in the database.

### JWT Authentication

After successful login, the server generates a JWT access token. The client includes this token in requests to protected endpoints.

Tokens expire after 30 minutes.

### File Access Control

The server associates each uploaded file with the authenticated user's account.

Users can list and download only files belonging to their account. Unauthorized requests are rejected.

## 10. API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Check server status |
| POST | `/register` | Register a new user |
| POST | `/login` | Authenticate and obtain a JWT |
| POST | `/upload` | Upload an encrypted file |
| GET | `/files` | List authenticated user's files |
| GET | `/download/{file_id}` | Download an owned encrypted file |

## 11. Testing

The following functionality was tested during development:

| Test | Result |
|---|---|
| User registration | Passed |
| User login | Passed |
| Encrypted file upload | Passed |
| List stored files | Passed |
| Download and decryption | Passed |
| Duplicate filename handling | Passed |
| Download multiple files | Passed |
| Reject unauthenticated file listing | Passed — HTTP 401 |

### Screenshots


## Project Screenshots


## Project Screenshots

### 1. User Login
![User Login](screenshots/Screenshot%202026-10-31%20at%2010.23.48%20PM.png)

### 2. Encrypted File Upload
![Encrypted File Upload](screenshots/Screenshot%202026-10-31%20at%2010.24.32%20PM.png)

### 3. Stored Files
![Stored Files](screenshots/Screenshot%202026-10-31%20at%2010.24.56%20PM.png)

### 4. File Download and Decryption
![File Download](screenshots/Screenshot%202026-10-31%20at%2010.25.29%20PM.png)


1. Successful user registration and login.
2. Terminal client menu.
3. Successful encrypted file upload.
4. Listing stored files.
5. Successful download and decryption.
6. HTTP 401 Unauthorized response in Swagger UI.

## 12. Limitations

- The application currently runs locally on `127.0.0.1`.
- The terminal client uses a locally stored encryption key.
- Separate per-user encryption keys are not yet implemented.
- Direct file sharing between users is not yet implemented.
- HTTPS is not configured for public deployment.
- Large files are currently encrypted and decrypted in memory.
- There is no password recovery system.

## 13. Future Improvements

Possible improvements include:

- Secure file sharing between registered users
- Separate encryption keys for each user
- Browser-based frontend
- HTTPS and public server deployment
- File deletion and storage quotas
- Password recovery
- Audit logging and improved error handling

## 14. Conclusion

This project demonstrates the implementation of a client-server file storage application using Python, FastAPI, SQLite, and AES-256-GCM encryption.

The system successfully combines client-side file encryption, authenticated file uploads and downloads, password hashing, and file ownership controls.

It provides a functional foundation for a secure cloud storage system, with additional security and sharing capabilities identified for future development.
