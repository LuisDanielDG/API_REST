from fastapi import FastAPI
import sqlite3
from datetime import datetime

app = FastAPI()


@app.get(
    "/",
    status_code=202,
    summary="Endpoint raíz",
    description="Bienvenido a la API de Agenda")
def read_root():
    response = {
        "message": "API de la Agenda",
        "datatime": "12/02/2026"
        }
    return response


@app.get(
    "/v1/contactos",
    status_code=202,
    summary="Endpoint que regresa los contactos paginados",
    description="""Endpoint que regresa los contactos paginados,
    utiliza los siguientes query params:
    limit:int -> Indica el numero de registros a regresar
    skip:int -> Indica el numero de registros a omitir
    """
)

async def get_contactos(limit: int = 10, skip: int=0):
    try:
        conn = sqlite3.connect('agenda.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM contactos LIMIT ? OFFSET ?', (limit, skip))
        rows = cursor.fetchall()
        cursor.execute('SELECT COUNT(*) FROM contactos')
        total = cursor.fetchone()[0]

        items = [
            {
                "id_contacto": row['id_contacto'],
                "nombre": row['nombre'],
                "telefono": row['telefono'],
                "email": row['email']
            }
            for row in rows
        ]
        
        conn.close()
        
        response = {
            "table":"contactos",
            "items": items,
            "count": len(items),
            "total": total,
            "datetime": "13/02/2026 12:30"
            "message":"Datos consultados exitosamente",
            "limit": limit,
            "skip": skip
        }
    return response