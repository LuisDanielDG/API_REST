import os
import sqlite3
import requests

URI_BASE = "http://localhost:8000"

def setup_module(module):
    db_path = os.path.join(os.path.dirname(__file__), 'agenda.db')
    sql_path = os.path.join(os.path.dirname(__file__), 'crear_agenda.sql')
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    with open(sql_path, 'r', encoding='utf-8') as f:
        cursor.executescript(f.read())
    conn.commit()
    conn.close()


def obtener_total():
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'agenda.db'))
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM contactos')
    total = cursor.fetchone()[0]
    conn.close()
    return total


def test_primeros_diez():
    total = obtener_total()
    url = f"{URI_BASE}/v1/contactos"
    params = {"limit": 10, "skip": 0}
    respuesta = requests.get(url, params=params)
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo['count'] == 10
    assert cuerpo['items'][0]['id_contacto'] == 1
    assert cuerpo['total'] == total

def test_ultimos_diez():
    total = obtener_total()
    url = f"{URI_BASE}/v1/contactos"
    params = {"limit": 10, "skip": 90}
    respuesta = requests.get(url, params=params)
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo['count'] == 10
    assert cuerpo['items'][0]['id_contacto'] == total - 9

def test_limit_negativo():
    url = f"{URI_BASE}/v1/contactos"
    response = requests.get(url, params={"limit": -10, "skip": 0})
    assert response.status_code == 400
    
def test_skip_negativo():
    url = f"{URI_BASE}/v1/contactos"
    response = requests.get(url, params={"limit": 10, "skip": -10})
    assert response.status_code == 400

def test_limite_cero():
    url = f"{URI_BASE}/v1/contactos"
    r = requests.get(url, params={"limit": 0, "skip": 10})
    assert r.status_code == 400

def test_cero_ambos():
    url = f"{URI_BASE}/v1/contactos"
    r = requests.get(url, params={"limit": 0, "skip": 0})
    assert r.json() == {}


def test_limite_null():
    total = obtener_total()
    url = f"{URI_BASE}/v1/contactos"
    r = requests.get(url, params={"skip": 0})
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo['count'] == 10
    assert cuerpo['limit'] == 10
    assert cuerpo['total'] == total


def test_skip_null():
    total = obtener_total()
    url = f"{URI_BASE}/v1/contactos"
    r = requests.get(url, params={"limit": 10})
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo['count'] == 10
    assert cuerpo['skip'] == 0
    assert cuerpo['total'] == total


def test_ambos_null():
    total = obtener_total()
    url = f"{URI_BASE}/v1/contactos"
    r = requests.get(url)
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo['count'] == 10
    assert cuerpo['limit'] == 10
    assert cuerpo['skip'] == 0
    assert cuerpo['total'] == total


def test_limit_no_int():
    url = f"{URI_BASE}/v1/contactos"
    r = requests.get(url, params={"limit": "abc", "skip": 0})
    assert r.status_code == 422


def test_skip_no_int():
    url = f"{URI_BASE}/v1/contactos"
    r = requests.get(url, params={"limit": 10, "skip": "xyz"})
    assert r.status_code == 422

