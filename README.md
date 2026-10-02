# Online Students' Result Forwarding Management System

A focused FastAPI + MySQL + SQLModel + Jinja2 + HTMX + Tailwind CSS v4 + daisyUI application for digitizing the result-forwarding workflow:

**Lecturer → Examination Officer → HOD → Dean → Academic Planning Unit**

## Stack

- FastAPI
- SQLModel / SQLAlchemy
- MySQL + PyMySQL
- Jinja2 server-rendered templates
- HTMX progressive interactions
- Tailwind CSS v4
- daisyUI
- Iconify Tailwind v4
- Argon2 password hashing via pwdlib
- Alembic migrations

## Local setup

1. Start local MySQL with `docker compose up -d mysql` (or create the `result_forwarding` database manually).
2. Copy `.env.example` to `.env` and update the database URL and secret key.
3. Create and activate a Python 3.12+ virtual environment.
4. Install Python dependencies: `pip install -e ".[dev]"`.
5. Install frontend dependencies: `npm install`.
6. Build CSS: `npm run build:css`.
7. Seed demo data: `python -m app.seed`.
8. Start the server: `uvicorn app.main:app --reload`.
9. Open `http://127.0.0.1:8000`.

## Demo credentials are printed by the seed command.

# 📄 License

This project is developed for academic/research purposes.

Add an appropriate open-source license such as MIT if the project is intended to be distributed publicly.

---

# 👨‍💻 Author

- **Selim Adekola**
- 📧 [salimdotpy@gmail.com](mailto:salimdotpy@gmail.com)
- 📞 [+2348076738293](https://wa.me/+2348076738293)
