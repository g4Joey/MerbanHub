# MerbanHub Backend

This is the backend service for the **MerbanHub Capital Document Management System** – a prototype built using **Java Spring Boot**. It powers user authentication, document upload, and OCR-based indexing features.

---

## 🚀 Features

### ✅ Authentication & Authorization
- **JWT-based authentication** with login and signup endpoints
- Role-based access control (`ADMIN`, `USER`, etc.)
- Secure password encryption using `BCryptPasswordEncoder`
- Stateless session policy using Spring Security
- Custom filter chain for separating public vs protected APIs

### ✅ User Management
- User roles stored in MySQL and automatically assigned during signup
- Unique checks for username and email
- Sign-in returns JWT and user details

### ✅ File Upload System
- Upload endpoint saves files to a local folder `incoming-scan`
- Automatically creates the folder on any system if it doesn’t exist
- Fully supports cross-platform local setups
- Ready for future integration with OCR pipeline

### ✅ API Design
- Clean RESTful API with endpoints like:
    - `POST /api/auth/signup`
    - `POST /api/auth/signin`
    - `POST /api/files/upload`
- All public endpoints are configured with open access
- Protected endpoints secured via JWT filter

### ✅ Docker & Environment Setup
- Connected to MySQL using Docker Compose
- All credentials securely managed using a `.env` file
- Uses dynamic Spring Boot property mapping for DB and JWT config
- Health checks and container orchestration handled via `docker-compose.yml`

---

## 🛠 Tech Stack

| Tech              | Description                                 |
|-------------------|---------------------------------------------|
| Java              | Backend language                            |
| Spring Boot       | Backend framework                           |
| Spring Security   | Authentication and authorization            |
| JWT               | Secure token generation and validation      |
| MySQL             | Database                                    |
| Docker            | Containerization for DB and app             |
| Docker Compose    | Service orchestration                       |
| Postman           | API testing                                 |

---

## 🧪 Testing

- All endpoints tested using **Postman**
- Signup and login tested with valid and invalid payloads
- File upload tested with both existing and new local directory setups
- Logs verified in Docker container for proper functionality

---

## 📂 Folder Structure (Key)

backend/
├── src/
│ ├── main/
│ │ ├── java/
│ │ │ └── com/merbancapital/backend/
│ │ │ ├── dto/
│ │ │ ├── config/
│ │ │ ├── controller/
│ │ │ ├── model/
│ │ │ ├── repository/
│ │ │ ├── security/
│ │ │ └── service/
│ │ └── resources/
│ │ ├── application.properties
│ │ └── .env
├── docker-compose.yml
└── Dockerfile

---

## ✅ Getting Started

### 1. Clone the repo

```bash
- git clone https://github.com/<your-username>/merbanhub-backend.git
cd merbanhub-backend
```
### ✅ Run Docker Compose
```bash
docker-compose up --build
```

### ✅ Test APIs
* Use Postman or cURL to test the following endpoints:
* 
* POST /api/auth/signup
* 
* POST /api/auth/signin
* 
* POST /api/files/upload (requires JWT token)


### ✅ 🔒 Future Improvements (for production)
* Role-based access validation at method level
* Cloud file storage (e.g. AWS S3)
* Token refresh mechanism
* Advanced exception handling
* Logging and monitoring with Actuator
* HTTPS and CORS hardening
* Full OAuth2 or LDAP integration

### ✅ 👨‍💻 Author
Kenny Kwasi Otumayin Idan
First-year IT student @ University of Ghana
Backend Developer | Java | Spring Boot
Passionate about learning, building, and launching software


Let me know if you want me to also generate the `.env.example` file or Swagger documentation setup

