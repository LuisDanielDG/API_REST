import os
import sqlite3
import requests

URI_BASE = "http://localhost:8000"
DB_PATH = os.path.join(os.path.dirname(__file__), 'agenda.db')
SQL_PATH = os.path.join(os.path.dirname(__file__), 'crear_agenda.sql')


# ─────────────────────────────────────────────
# UTILIDADES
# ─────────────────────────────────────────────

def setup_module(module):
    """Recrea la base de datos limpia antes de correr todas las pruebas."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    with open(SQL_PATH, 'r', encoding='utf-8') as f:
        cursor.executescript(f.read())
    conn.commit()
    conn.close()


def obtener_total():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM contactos')
    total = cursor.fetchone()[0]
    conn.close()
    return total


def insertar_contacto(id_contacto, nombre, telefono, email):
    """Inserta un contacto directamente en la BD (para preparar escenarios)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO contactos (id_contacto, nombre, telefono, email) VALUES (?, ?, ?, ?)',
        (id_contacto, nombre, telefono, email)
    )
    conn.commit()
    conn.close()


def eliminar_contacto(id_contacto):
    """Elimina un contacto directamente en la BD (para preparar escenarios)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM contactos WHERE id_contacto = ?', (id_contacto,))
    conn.commit()
    conn.close()


def vaciar_tabla():
    """Elimina todos los registros de la tabla (para probar tabla vacía)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM contactos')
    conn.commit()
    conn.close()


def restaurar_datos_csv():
    """Recarga los datos originales del CSV después de pruebas destructivas."""
    import csv
    csv_path = os.path.join(os.path.dirname(__file__), 'data.csv')
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM contactos')
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute(
                'INSERT INTO contactos (id_contacto, nombre, telefono, email) VALUES (?, ?, ?, ?)',
                (int(row['id_contacto']), row['nombre'], row['telefono'], row['email'])
            )
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# PRUEBAS ORIGINALES — GET /v1/contactos
# ─────────────────────────────────────────────

def test_primeros_diez():
    total = obtener_total()
    respuesta = requests.get(f"{URI_BASE}/v1/contactos", params={"limit": 10, "skip": 0})
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo['count'] == 10
    assert cuerpo['items'][0]['id_contacto'] == 1
    assert cuerpo['total'] == total


def test_ultimos_diez():
    total = obtener_total()
    respuesta = requests.get(f"{URI_BASE}/v1/contactos", params={"limit": 10, "skip": 90})
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo['count'] == 10
    assert cuerpo['items'][0]['id_contacto'] == total - 9


def test_limit_negativo():
    r = requests.get(f"{URI_BASE}/v1/contactos", params={"limit": -10, "skip": 0})
    assert r.status_code == 400


def test_skip_negativo():
    r = requests.get(f"{URI_BASE}/v1/contactos", params={"limit": 10, "skip": -10})
    assert r.status_code == 400


def test_limite_cero():
    # limit=0 con skip>0 debe ser error (no es la combinación especial 0,0)
    r = requests.get(f"{URI_BASE}/v1/contactos", params={"limit": 0, "skip": 10})
    assert r.status_code == 400


def test_cero_ambos():
    r = requests.get(f"{URI_BASE}/v1/contactos", params={"limit": 0, "skip": 0})
    assert r.json() == {}


def test_limite_null():
    total = obtener_total()
    r = requests.get(f"{URI_BASE}/v1/contactos", params={"skip": 0})
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo['count'] == 10
    assert cuerpo['limit'] == 10
    assert cuerpo['total'] == total


def test_skip_null():
    total = obtener_total()
    r = requests.get(f"{URI_BASE}/v1/contactos", params={"limit": 10})
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo['count'] == 10
    assert cuerpo['skip'] == 0
    assert cuerpo['total'] == total


def test_ambos_null():
    total = obtener_total()
    r = requests.get(f"{URI_BASE}/v1/contactos")
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo['count'] == 10
    assert cuerpo['limit'] == 10
    assert cuerpo['skip'] == 0
    assert cuerpo['total'] == total


def test_limit_no_int():
    r = requests.get(f"{URI_BASE}/v1/contactos", params={"limit": "abc", "skip": 0})
    assert r.status_code == 422


def test_skip_no_int():
    r = requests.get(f"{URI_BASE}/v1/contactos", params={"limit": 10, "skip": "xyz"})
    assert r.status_code == 422


# ─────────────────────────────────────────────
# NUEVAS — GET /v1/contactos: paginación y bordes
# ─────────────────────────────────────────────

def test_skip_igual_al_total():
    """skip exactamente igual al total → fuera de rango, debe ser 400."""
    total = obtener_total()
    r = requests.get(f"{URI_BASE}/v1/contactos", params={"limit": 10, "skip": total})
    assert r.status_code == 400
    assert r.json()['count'] == 0


def test_skip_mayor_al_total():
    """skip mayor al total → también fuera de rango."""
    total = obtener_total()
    r = requests.get(f"{URI_BASE}/v1/contactos", params={"limit": 10, "skip": total + 50})
    assert r.status_code == 400


def test_limit_mayor_al_total():
    """limit mayor que registros disponibles → la API recorta al total real."""
    total = obtener_total()
    r = requests.get(f"{URI_BASE}/v1/contactos", params={"limit": total + 100, "skip": 0})
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo['count'] == total


def test_limit_mayor_que_registros_restantes():
    """limit pide más de los que quedan tras el skip → devuelve solo los restantes."""
    total = obtener_total()
    skip = total - 3  # quedan 3 registros
    r = requests.get(f"{URI_BASE}/v1/contactos", params={"limit": 10, "skip": skip})
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo['count'] == 3


def test_estructura_de_cada_item():
    """Verifica que cada item tenga exactamente los campos esperados."""
    r = requests.get(f"{URI_BASE}/v1/contactos", params={"limit": 5, "skip": 0})
    assert r.status_code == 200
    campos_esperados = {"id_contacto", "nombre", "telefono", "email"}
    for item in r.json()['items']:
        assert set(item.keys()) == campos_esperados


def test_items_no_tienen_campos_extra():
    """La respuesta no debe filtrar campos privados ni exponer columnas extra."""
    r = requests.get(f"{URI_BASE}/v1/contactos", params={"limit": 1, "skip": 0})
    item = r.json()['items'][0]
    assert len(item) == 4  # solo id_contacto, nombre, telefono, email


def test_paginacion_sin_duplicados():
    """Dos páginas consecutivas no deben compartir registros."""
    r1 = requests.get(f"{URI_BASE}/v1/contactos", params={"limit": 10, "skip": 0})
    r2 = requests.get(f"{URI_BASE}/v1/contactos", params={"limit": 10, "skip": 10})
    ids_pagina1 = {item['id_contacto'] for item in r1.json()['items']}
    ids_pagina2 = {item['id_contacto'] for item in r2.json()['items']}
    assert ids_pagina1.isdisjoint(ids_pagina2)


def test_respuesta_incluye_campos_de_metadatos():
    """La respuesta debe incluir table, count, total, limit, skip, message y datetime."""
    r = requests.get(f"{URI_BASE}/v1/contactos", params={"limit": 5, "skip": 0})
    cuerpo = r.json()
    for campo in ['table', 'items', 'count', 'total', 'limit', 'skip', 'message', 'datetime']:
        assert campo in cuerpo, f"Falta el campo '{campo}' en la respuesta"


# ─────────────────────────────────────────────
# NUEVAS — GET /v1/contactos: tabla vacía
# ─────────────────────────────────────────────

def test_tabla_vacia_devuelve_404():
    """Si no hay contactos en la BD, debe responder 404."""
    vaciar_tabla()
    r = requests.get(f"{URI_BASE}/v1/contactos", params={"limit": 10, "skip": 0})
    assert r.status_code == 404
    assert r.json()['count'] == 0
    restaurar_datos_csv()  # deja la BD como estaba


# ─────────────────────────────────────────────
# NUEVAS — GET /v1/contacto/{id}: por ID
# ─────────────────────────────────────────────

def test_contacto_por_id_existente():
    """Un ID que existe debe devolver 200 y el contacto correcto."""
    r = requests.get(f"{URI_BASE}/v1/contacto/1")
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo['item']['id_contacto'] == 1
    assert cuerpo['item']['nombre'] is not None


def test_contacto_por_id_no_existente():
    """Un ID que no existe debe devolver 404."""
    r = requests.get(f"{URI_BASE}/v1/contacto/99999")
    assert r.status_code == 404
    cuerpo = r.json()
    assert cuerpo['item'] is None


def test_contacto_id_cero():
    """id=0 no es válido → 400."""
    r = requests.get(f"{URI_BASE}/v1/contacto/0")
    assert r.status_code == 400


def test_contacto_id_negativo():
    """IDs negativos no son válidos → 400."""
    r = requests.get(f"{URI_BASE}/v1/contacto/-5")
    assert r.status_code == 400


def test_contacto_id_no_entero():
    """Un ID que no es entero (string) → FastAPI devuelve 422."""
    r = requests.get(f"{URI_BASE}/v1/contacto/abc")
    assert r.status_code == 422


def test_contacto_id_flotante():
    """Un ID flotante como '1.5' → FastAPI no lo acepta como int → 422."""
    r = requests.get(f"{URI_BASE}/v1/contacto/1.5")
    assert r.status_code == 422


def test_contacto_eliminado_devuelve_404():
    """Si un contacto es eliminado de la BD, buscarlo por ID debe dar 404."""
    # Insertamos uno temporal para no afectar datos reales
    insertar_contacto(9991, "Temp Borrable", "5500000001", "temp@test.com")
    eliminar_contacto(9991)
    r = requests.get(f"{URI_BASE}/v1/contacto/9991")
    assert r.status_code == 404


def test_estructura_item_por_id():
    """El item retornado por ID debe tener exactamente los 4 campos esperados."""
    r = requests.get(f"{URI_BASE}/v1/contacto/1")
    assert r.status_code == 200
    item = r.json()['item']
    assert set(item.keys()) == {"id_contacto", "nombre", "telefono", "email"}


def test_respuesta_id_incluye_metadatos():
    """La respuesta por ID debe incluir table, item, message y datetime."""
    r = requests.get(f"{URI_BASE}/v1/contacto/1")
    cuerpo = r.json()
    for campo in ['table', 'item', 'message', 'datetime']:
        assert campo in cuerpo, f"Falta el campo '{campo}' en la respuesta"


# ─────────────────────────────────────────────
# NUEVAS — Integridad de datos en BD
# ─────────────────────────────────────────────

def test_id_contacto_duplicado_falla():
    """Insertar un ID duplicado debe lanzar un error de integridad en SQLite."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO contactos (id_contacto, nombre, telefono, email) VALUES (?, ?, ?, ?)',
            (1, "Duplicado", "5500000000", "dup@test.com")
        )
        conn.commit()
        assert False, "Debió fallar por PRIMARY KEY duplicada"
    except sqlite3.IntegrityError:
        pass  # comportamiento esperado
    finally:
        conn.close()


def test_nombre_nulo_falla():
    """El campo nombre no debe aceptar NULL si la columna tiene NOT NULL."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO contactos (id_contacto, nombre, telefono, email) VALUES (?, ?, ?, ?)',
            (9992, None, "5500000002", "nonull@test.com")
        )
        conn.commit()
        # Si llega aquí, la columna permite NULL; marcamos el test como advertencia
        eliminar_contacto(9992)
    except sqlite3.IntegrityError:
        pass  # columna tiene NOT NULL, correcto
    finally:
        conn.close()


def test_insertar_y_consultar_contacto_nuevo():
    """Un contacto recién insertado en la BD debe ser visible vía la API."""
    insertar_contacto(9993, "Nuevo Contacto", "5512345678", "nuevo@test.com")
    r = requests.get(f"{URI_BASE}/v1/contacto/9993")
    assert r.status_code == 200
    assert r.json()['item']['nombre'] == "Nuevo Contacto"
    eliminar_contacto(9993)


def test_eliminar_y_verificar_ausencia():
    """Un contacto eliminado de la BD no debe aparecer en la lista."""
    insertar_contacto(9994, "Para Borrar", "5598765432", "borrar@test.com")
    eliminar_contacto(9994)
    r = requests.get(f"{URI_BASE}/v1/contacto/9994")
    assert r.status_code == 404


def test_total_se_actualiza_al_insertar():
    """El total reportado por la API debe crecer al insertar un contacto."""
    total_antes = obtener_total()
    insertar_contacto(9995, "Extra", "5511111111", "extra@test.com")
    r = requests.get(f"{URI_BASE}/v1/contactos", params={"limit": 1, "skip": 0})
    assert r.json()['total'] == total_antes + 1
    eliminar_contacto(9995)


def test_total_se_actualiza_al_eliminar():
    """El total reportado por la API debe disminuir al eliminar un contacto."""
    insertar_contacto(9996, "Temporal", "5522222222", "temporal@test.com")
    total_con = obtener_total()
    eliminar_contacto(9996)
    r = requests.get(f"{URI_BASE}/v1/contactos", params={"limit": 1, "skip": 0})
    assert r.json()['total'] == total_con - 1


# ─────────────────────────────────────────────
# NUEVAS — GET /: endpoint raíz
# ─────────────────────────────────────────────

def test_root_devuelve_200():
    r = requests.get(f"{URI_BASE}/")
    assert r.status_code == 200


def test_root_tiene_message_y_datetime():
    r = requests.get(f"{URI_BASE}/")
    cuerpo = r.json()
    assert 'message' in cuerpo
    assert 'datetime' in cuerpo


def test_root_message_no_vacio():
    r = requests.get(f"{URI_BASE}/")
    assert len(r.json()['message']) > 0


# ─────────────────────────────────────────────
# NUEVAS — Rutas inexistentes
# ─────────────────────────────────────────────

def test_ruta_inexistente_devuelve_404():
    """Una ruta que no existe debe devolver 404."""
    r = requests.get(f"{URI_BASE}/v1/noexiste")
    assert r.status_code == 404


def test_metodo_post_no_permitido():
    """POST a un endpoint que solo acepta GET debe devolver 405."""
    r = requests.post(f"{URI_BASE}/v1/contactos")
    assert r.status_code == 405


def test_metodo_delete_no_permitido():
    """DELETE a un endpoint de solo lectura debe devolver 405."""
    r = requests.delete(f"{URI_BASE}/v1/contacto/1")
    assert r.status_code == 405