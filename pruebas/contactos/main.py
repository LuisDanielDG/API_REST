from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import sqlite3
from datetime import datetime

app = FastAPI()

@app.get("/", status_code=200)
def read_root():
    return {
        "message": "API de la Agenda",
        "datetime": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }

@app.get("/v1/contactos")
async def get_contactos(
    limit: int = Query(10),
    skip: int = Query(0)
):
    if limit == 0 and skip == 0:
        return {}

    if limit <= 0:
        return JSONResponse(
            status_code=400,
            content={
                "table": "contactos",
                "items": [],
                "count": 0,
                "message": "El parámetro limit debe ser mayor a 0",
                "datetime": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }
        )

    if skip < 0:
        return JSONResponse(
            status_code=400,
            content={
                "table": "contactos",
                "items": [],
                "count": 0,
                "message": "El parámetro skip no puede ser negativo",
                "datetime": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }
        )

    conn = None

    try:
        conn = sqlite3.connect('agenda.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM contactos')
        total = cursor.fetchone()[0]

        if total == 0:
            return JSONResponse(
                status_code=404,
                content={
                    "table": "contactos",
                    "items": [],
                    "count": 0,
                    "total": 0,
                    "message": "No existen contactos registrados",
                    "datetime": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                }
            )

        if skip >= total:
            return JSONResponse(
                status_code=400,
                content={
                    "table": "contactos",
                    "items": [],
                    "count": 0,
                    "total": total,
                    "message": "El parámetro skip excede el total de registros",
                    "datetime": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                }
            )

        if limit > total:
            limit = total

        if limit > (total - skip):
            limit = total - skip

        cursor.execute(
            'SELECT * FROM contactos LIMIT ? OFFSET ?',
            (limit, skip)
        )
        rows = cursor.fetchall()

        items = [
            {
                "id_contacto": row['id_contacto'],
                "nombre": row['nombre'],
                "telefono": row['telefono'],
                "email": row['email']
            }
            for row in rows
        ]

        return JSONResponse(
            status_code=200,
            content={
                "table": "contactos",
                "items": items,
                "count": len(items),
                "total": total,
                "limit": limit,
                "skip": skip,
                "message": "Datos consultados exitosamente",
                "datetime": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }
        )

    except sqlite3.Error as e:
        return JSONResponse(
            status_code=500,
            content={
                "table": "contactos",
                "items": [],
                "count": 0,
                "message": f"Error en base de datos: {str(e)}",
                "datetime": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }
        )

    finally:
        if conn:
            conn.close()

@app.get("/v1/contacto/{id_contacto}")
async def get_contacto_by_id(id_contacto: int):

    if id_contacto <= 0:
        return JSONResponse(
            status_code=400,
            content={
                "table": "contactos",
                "item": None,
                "message": "El id_contacto debe ser mayor a 0",
                "datetime": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }
        )

    conn = None

    try:
        conn = sqlite3.connect('agenda.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            'SELECT * FROM contactos WHERE id_contacto = ?',
            (id_contacto,)
        )
        row = cursor.fetchone()

        if row is None:
            return JSONResponse(
                status_code=404,
                content={
                    "table": "contactos",
                    "item": None,
                    "message": f"Contacto con ID {id_contacto} no encontrado",
                    "datetime": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                }
            )

        item = {
            "id_contacto": row['id_contacto'],
            "nombre": row['nombre'],
            "telefono": row['telefono'],
            "email": row['email']
        }

        return JSONResponse(
            status_code=200,
            content={
                "table": "contactos",
                "item": item,
                "message": "Contacto consultado exitosamente",
                "datetime": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }
        )

    except sqlite3.Error as e:
        return JSONResponse(
            status_code=500,
            content={
                "table": "contactos",
                "item": None,
                "message": f"Error en base de datos: {str(e)}",
                "datetime": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }
        )

    finally:
        if conn:
            conn.close()
