# User Registration Web Application

This is a web application that allows users to register, login, and manage their personal details, including changing their name and password. The application follows the given use cases and handles error scenarios. It is implemented using Node.js, ReactJS, and MongoDB.


## Sign up page
![Sign up Page](https://github-production-user-asset-6210df.s3.amazonaws.com/108184610/245683795-a0b660c9-3a81-429d-b6b2-a577268d6bd7.png)
## Login page
![Login Page](https://github-production-user-asset-6210df.s3.amazonaws.com/108184610/245683784-92feec6e-b02f-41d7-946f-6bad5c4f6b31.png)

## Features

- User registration via email, name, and password.
- User login via email and password.
- Display of personal details on the main page after login.
- Ability to change name and password details.
- User logout functionality.
- Proper error handling, including handling wrong password scenarios.

## Technology Stack

- Frontend: ReactJS, Material-UI
- Backend: Node.js, Express.js
- Database: MongoDB
- Authentication: JWT (JSON Web Tokens)
- Password Encryption: bcrypt.js

## Demo

Check out the live demo of the website: [User-registration Website](https://user-registration-somnath000.vercel.app/)

## Installation

1. Clone the repository: `git clone https://github.com/SomnathKar000/User-registration`
2. Navigate to the project directory: `cd User-registration`
3. Change the directory to the backend folder: `cd backend`
4. Install the backend dependencies: `npm install`
5. Return to the previous directory: `cd ..`
6. Install the frontend dependencies: `npm install`

## Environment Variables

1. Create an `.env` file in the root directory of the project.
2. Define the following environment variables in the `.env` file:
   - `DB_URL=<your-db-url>` : The MongoDB URL for connecting to the database.
   - `JWT_SECRET_KEY=<your-secret-key>` : The secret key used for authentication.

## Usage

1. Start the backend server: `npm start` (from the project backend directory)
2. Start the frontend server: `npm start` (from the project root directory)
3. Open the application in your browser: `http://localhost:3000`

## Contributing

Contributions are welcome! If you have any suggestions, bug reports, or feature requests, please open an issue or submit a pull request.




