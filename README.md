# Ingeniería de Software

Sistema de gestión para un restaurante.

## Stack

- **Backend:** FastAPI + SQLAlchemy + Pydantic + SQLite
- **Frontend:** React + TypeScript (Vite)

## Estructura

```
.
├── Backend/
│   ├── .env.example
│   ├── requirements.txt
│   └── src/
│       ├── __init__.py
│       ├── main.py
│       ├── database.py
│       ├── models.py
│       ├── schemas.py
│       └── exceptions.py
└── Frontend/
    ├── package.json
    ├── vite.config.ts
    ├── index.html
    ├── README.md              # Guía de la base visual y de trabajo por equipos
    └── src/
        ├── ui/                # Kit compartido (ui.tsx + ui.css)
        ├── app/               # Rutas y navegación por hash
        ├── layout/            # Shell de la aplicación
        ├── features/          # Una carpeta por funcionalidad/equipo
        ├── main.tsx
        └── App.tsx
```

La base del frontend, las rutas, los componentes vacíos y las convenciones para completarlos están documentados en [`Frontend/README.md`](Frontend/README.md).

## Requisitos

- Python 3.11+
- Node.js (LTS)

## Instalación

### Backend

```bash
cd Backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # Windows: copy .env.example .env
fastapi dev src/main.py
```

API en http://localhost:8000 · Documentación en http://localhost:8000/docs

### Frontend

```bash
cd Frontend
npm install
npm run dev
```

App en http://localhost:5173
