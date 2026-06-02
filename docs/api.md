# 📡 API Documentation

> **Status:** Stub — endpoints will be documented as they are implemented.

## Base URL

```
http://localhost:8000/api/v1
```

---

## 🔐 Authentication

| Method | Endpoint           | Description               |
| ------ | ------------------ | ------------------------- |
| POST   | `/auth/register`   | Register a new user       |
| POST   | `/auth/login`      | Log in and receive a JWT  |
| POST   | `/auth/refresh`    | Refresh an access token   |
| GET    | `/auth/me`         | Get current user profile  |

<!-- TODO: Add request/response schemas and examples -->

---

## 🌱 Plants

| Method | Endpoint           | Description                        |
| ------ | ------------------ | ---------------------------------- |
| GET    | `/plants`          | List all known medicinal plants    |
| GET    | `/plants/{id}`     | Get details for a specific plant   |
| POST   | `/plants`          | Add a new plant (admin only)       |
| PUT    | `/plants/{id}`     | Update plant information           |
| DELETE | `/plants/{id}`     | Delete a plant record              |

<!-- TODO: Add request/response schemas and examples -->

---

## 🔍 Detection

| Method | Endpoint            | Description                                 |
| ------ | ------------------- | ------------------------------------------- |
| POST   | `/detect/image`     | Upload an image and detect the plant species|
| GET    | `/detect/history`   | Get detection history for the current user  |
| GET    | `/detect/{id}`      | Get details of a specific detection result  |

<!-- TODO: Add request/response schemas, file upload details, and examples -->

---

## 💬 Chat (RAG)

| Method | Endpoint            | Description                                        |
| ------ | ------------------- | -------------------------------------------------- |
| POST   | `/chat/message`     | Send a message and receive a RAG-powered response  |
| GET    | `/chat/history`     | Get chat history for the current user               |
| DELETE | `/chat/history`     | Clear chat history                                  |

<!-- TODO: Add request/response schemas and examples -->
