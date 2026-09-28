# Copa Santa Fe — Gestión de Facturación y Cartera

Aplicativo web interno del Departamento de Tesorería de Independiente Santa Fe S.A. para administrar los equipos invitados de la Copa Santa Fe, su facturación, la cartera y la plantilla de importación a **World Office**.

Reemplaza progresivamente el archivo `3. Copa_SantaFe_2026_Cartera.xlsm`, conservando su lógica y los nombres de sus campos.

**Estado actual: Fase 1 terminada** (proyecto, base de datos, inicio y módulo Equipos). Ver [docs/FASES.md](docs/FASES.md).

## Documentación

| Documento | Contenido |
|---|---|
| [docs/ANALISIS_EXCEL.md](docs/ANALISIS_EXCEL.md) | Cómo funciona el Excel actual, sus fórmulas y los problemas encontrados |
| [docs/MODELO_DATOS.md](docs/MODELO_DATOS.md) | Tablas, campos, relaciones y correspondencia con cada columna del Excel |
| [docs/FASES.md](docs/FASES.md) | Qué se construyó, qué falta y decisiones pendientes |

## Tecnología

Python 3.12 · Django 5.1 · PostgreSQL (producción) / SQLite (desarrollo) · HTML + CSS sin dependencias de compilación.

## Instalación en un computador (Windows)

Requisitos: [Python 3.12](https://www.python.org/downloads/) (marcar «Add Python to PATH» al instalar) y [Git](https://git-scm.com/download/win).

```powershell
git clone https://github.com/SU-USUARIO/copa-santafe.git
cd copa-santafe
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Abra http://127.0.0.1:8000 e ingrese con el usuario creado. La configuración de World Office y de cartera se edita en **Administración → Configuración**.

En macOS/Linux cambie `.venv\Scripts\activate` por `source .venv/bin/activate` y `copy` por `cp`.

## Pruebas

```powershell
python manage.py test
```

GitHub ejecuta las mismas pruebas automáticamente (contra PostgreSQL) en cada cambio subido a `main`.

## Producción

1. Cree una base PostgreSQL y defina `DATABASE_URL`.
2. Defina `SECRET_KEY` (larga y aleatoria), `DEBUG=False`, `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS`.
3. Ejecute `python manage.py migrate` y `python manage.py collectstatic --noinput`.
4. Inicie con `gunicorn config.wsgi`.

## Seguridad de la información

- El repositorio debe ser **privado**.
- **Los datos reales no se suben a GitHub.** El `.gitignore` excluye `.env`, la base de datos y todos los archivos Excel/CSV. El `.xlsm` original se guarda en `datos_privados/` (carpeta ignorada) o fuera del proyecto.
- La información contable no se elimina desde la interfaz: los equipos se desactivan y los pagos quedan en el historial.
