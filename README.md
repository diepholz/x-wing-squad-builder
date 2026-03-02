
## X-Wing Squad Builder

---
## Description

To build installer, run the following commands in your local environment:
```
pip install -r requirements/base.txt
python setup.py build_qt
python setup.py build_installer
```

---
## Features

- Filter cards by faction, ship, and pilot to assemble your squad
- Search through all available pilots, upgrades, and current squad in the viewer
- Export and import squad list to tweak at a later date

---
## Web App

A browser-based squad builder with account support, squad saving, and sharing.

### Development

```bash
# Backend (FastAPI, runs on http://localhost:8000)
cd web/backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (React + Vite, runs on http://localhost:5173)
cd web/frontend
npm install
npm run dev
```

The Vite dev server proxies `/api` requests to the backend automatically.

### Docker (production)

```bash
cd web
docker compose up --build
```

- Frontend served by nginx on **port 80**
- Backend API on **port 8000**
- SQLite database persisted via a named Docker volume
- Set `SECRET_KEY` env var for production deployments:
  ```bash
  SECRET_KEY=your-secret-key docker compose up -d
  ```

---
## Credits

This package was created with [Cookiecutter](https://github.mmm.com/a4t5gzz/pyside-cookiecutter)
