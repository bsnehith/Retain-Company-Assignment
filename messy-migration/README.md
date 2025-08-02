# Refactoring Summary

## Issues Fixed
- SQL Injection vulnerability from f-strings → replaced with parameterized queries.
- Passwords stored in plain text → now hashed using `werkzeug.security`.
- Global DB connection removed → replaced with per-request connection using `get_db()`.
- Added JSON responses with appropriate HTTP status codes.
- Added input validation for missing or invalid fields.
- Better error handling and code readability.

## Improvements
- Production-safe password storage
- Secure input handling
- Consistent and structured responses

## What I’d Do With More Time
- Add token-based authentication (e.g., JWT)
- Move DB logic to a separate service layer or use SQLAlchemy ORM
- Add automated tests using `pytest` or `unittest`
