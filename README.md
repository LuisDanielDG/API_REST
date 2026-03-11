# API_REST
## Plantilla para modelar la API

|NO.|PROPIEDAD|DETALLE|
|--|--|--|
|1|Description|Endpoint de bienvenida|
|2 |Summary|Endpoint de bienvenida a la agenda|
|3|Method|GET|
|4|Endpoint|/|
|5|Authentication|NA|
|6|Query param|NA|
|7|Path param|NA|
|8|Data|NA|
|9|Status code|202|
|10|Response|{"message","Agenda","datetime""9/2/26 11:17"}|
|11|Response type|application/json|
|12|Status code(error)|NA|
|13|Response type(error)|NA|
|14|Response(error)|NA|
|15|cURL|curl -X http://127.0.0.1:8000/|

### 2. Contactos

|No.|Propiedad|Detalle|
|:---:|:---------:|:-------:|
|1|Description|Obtiene la lista completa de contactos de la agenda|
|2|Summary|Endpoint para consultar todos los contactos registrados|
|3|Method|GET|
|4|Endpoint|/v1/contactos|
|5|Authentication|NA|
|6|Query param|limit:int&skip:int|
|7|Path param|NA|
|8|Data|NA|
|9|Status code|200|
|10|Response|{"table": "contactos", "items": [{"id_contacto": int, "nombre": str, "email": str, "telefono": str}], "count": int, "datetime": timestamp, "message": "Datos cargados exitosamente"}|
|11|Response Type|application/json|
|12|Status code (Error)|500|
|13|Response Type (Error)|application/json|
|14|Response (Error)|{"table": None, "items": [], "count": int, "datetime": timestamp, "message": "Ocurrio un error al cargar los datos"}|
|15|cURL|curl -X GET https://127.0.0.1:8000/contactos|

### 3. Buscar contacto

|No.|Propiedad|Detalle|
|:---:|:---------:|:-------:|
|1|Description||
|2|Summary|Endpoint para buscar un contacto|
|3|Version|v1|
|4|Method|POST|
|5|Endpoint|/v1/contactos/{id_contacto}|
|6|Authentication|NA|
|7|Query param|NA|
|8|Path param|id_contacto|
|9|Data|NA|
|10|Status code|202|
|11|Response|{"table": "contactos", "item": {"id_contacto": int, "nombre": str, "telefono": int, "email": str} , "count":1, "datetime": timestamp, "message": "Contacto encontrado"}, {"table":"contactos", "item":{}, "count":0, "datetime": timestamp, "message": "Contacto no encontrado"}|
|12|Response Type|application/json|
|13|Status code (Error)|400|
|14|Response Type (Error)|application/json|
|15|Response (Error)|{"error":"Error al buscar el registro"}|
|15|cURL|curl -X GET https://127.0.0.1:8000/v1/contactos/3|