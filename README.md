# KIRI — Backend de Gestión con FastAPI y SQLModel

## Descripción general

KIRI cuenta con un backend desarrollado en Python utilizando **FastAPI** y **SQLModel**. La aplicación proporciona una API REST para administrar usuarios y manejar información relacionada con refrigeradores y alimentos.

El sistema incorpora autenticación mediante **JWT**, almacenamiento de contraseñas utilizando **Argon2** y conexión con una base de datos PostgreSQL. Para facilitar el desarrollo local también se contempla el uso de SQLite como alternativa.

---

## Herramientas y tecnologías

El proyecto utiliza las siguientes tecnologías principales:

* **Python:** lenguaje utilizado para el desarrollo del backend.
* **FastAPI:** framework empleado para construir los servicios y endpoints de la API.
* **SQLModel:** herramienta utilizada para definir los modelos y trabajar con la información almacenada en la base de datos.
* **PostgreSQL:** motor de base de datos utilizado mediante Docker.
* **SQLite:** alternativa local mediante el archivo `mikedb.db`.
* **Alembic:** herramienta utilizada para controlar los cambios y versiones del esquema de la base de datos.
* **JWT:** mecanismo utilizado para la generación de tokens de autenticación.
* **Argon2:** algoritmo empleado para proteger las contraseñas.
* **OAuth2:** utilizado en el proceso de autenticación mediante usuario y contraseña.
* **Docker y Docker Compose:** utilizados para ejecutar y configurar el servicio de PostgreSQL.

---

# Organización del proyecto

La aplicación está dividida en diferentes carpetas, donde cada una concentra una responsabilidad determinada. Esta separación permite mantener por separado las rutas, modelos, configuración, seguridad y acceso a la base de datos.

## Archivos principales

En la carpeta principal del proyecto se encuentran los archivos necesarios para iniciar y configurar la aplicación.

### `main.py`

Es el punto de entrada de la aplicación FastAPI.

Entre sus responsabilidades se encuentran:

* Inicializar la base de datos y sus tablas mediante el ciclo de vida `lifespan`.
* Configurar el middleware de CORS.
* Incorporar las rutas correspondientes a la API.
* Proporcionar el endpoint `/` como respuesta inicial.
* Proporcionar `/health` para comprobar el estado de la aplicación.

Las rutas de usuarios se encuentran disponibles mediante:

`/api/v1/users`

### `docker-compose.yml`

Contiene la configuración utilizada para levantar PostgreSQL mediante Docker.

El proyecto utiliza la imagen:

`postgres:15-alpine`

El servicio se expone localmente mediante el puerto `5435` y utiliza el volumen `postgres_data3` para conservar los datos.

### `alembic.ini`

Archivo de configuración principal utilizado por Alembic para ejecutar y administrar las migraciones de la base de datos.

### `requerimientos.txt`

Contiene las dependencias de Python necesarias para ejecutar el proyecto.

### `script.py`

Funciona como cliente de prueba para consumir los endpoints que requieren autenticación. Para realizar las solicitudes protegidas utiliza el token mediante la cabecera HTTP correspondiente.

### `mikedb.db`

Archivo de base de datos SQLite utilizado como alternativa para trabajar con una base de datos local durante el desarrollo.

---

# Migraciones — `alembic`

La carpeta `alembic` se encarga del control de cambios realizados sobre la estructura de la base de datos.

### `env.py`

Configura el entorno de Alembic. Obtiene la conexión con la base de datos y utiliza los metadatos de SQLModel para permitir la generación de migraciones.

### `script.py.mako`

Plantilla utilizada por Alembic como base para crear los archivos correspondientes a nuevas migraciones.

### `versions/`

Aquí se almacenan las diferentes migraciones generadas a lo largo del desarrollo del proyecto.

Un ejemplo de archivo almacenado en esta carpeta es:

`ad8c96673972_relacion.py`

---

# API — `api`

Esta sección contiene las rutas que puede utilizar el cliente para comunicarse con el backend.

Actualmente las rutas se encuentran organizadas bajo la versión `v1`.

## `api/v1/user_api.py`

Este archivo concentra las operaciones relacionadas con los usuarios.

Las operaciones disponibles son:

| Método   | Ruta         | Función                                  |
| -------- | ------------ | ---------------------------------------- |
| `POST`   | `/`          | Registrar un usuario                     |
| `POST`   | `/token`     | Autenticar al usuario y generar un token |
| `GET`    | `/`          | Consultar los usuarios                   |
| `GET`    | `/{user_id}` | Obtener un usuario específico            |
| `PUT`    | `/{user_id}` | Actualizar información del usuario       |
| `DELETE` | `/{user_id}` | Eliminar un usuario                      |

Durante el registro se verifica que no exista un usuario duplicado y la contraseña se almacena utilizando un hash.

El endpoint `/token` utiliza `OAuth2PasswordRequestForm` para recibir las credenciales, comprobarlas y generar el JWT correspondiente.

Las consultas protegidas requieren que el usuario se encuentre autenticado mediante dicho token.

---

## `api/v1/todo_api.py`

Este router contiene las operaciones relacionadas con los refrigeradores y los alimentos almacenados en ellos.

Actualmente contempla:

* Consultar un refrigerador junto con los alimentos asociados.
* Agregar un alimento a un refrigerador determinado.

Las rutas utilizadas son:

`GET /refrigeradores/{refrigerador_id}`

`POST /refrigeradores/{refrigerador_id}/alimentos`

---

## `api/v1/dependencies.py`

Aquí se encuentran las dependencias utilizadas para comprobar la autenticación de los usuarios.

### `get_current_user`

Se encarga de obtener el token enviado por el cliente, decodificarlo y comprobar que el usuario asociado exista en la base de datos.

### `get_current_activate_user`

Además de comprobar la autenticación, verifica que el usuario tenga habilitado el campo:

`is_active = True`

---

# Configuración y seguridad — `core`

La carpeta `core` concentra elementos que son utilizados de manera general por la aplicación.

## `config.py`

Administra las variables de configuración mediante `pydantic-settings`.

Los valores se obtienen desde el archivo `.env`.

Entre las configuraciones utilizadas se encuentran:

* `DATABASE_URL`
* `SECRET_KEY`
* `ALGORITHM`
* `ACCESS_TOKEN_EXPIRE_MINUTES`

---

## `security.py`

Contiene las funciones relacionadas con la protección de las credenciales y la autenticación.

Entre ellas se encuentran:

* `get_password_hash`: genera el hash de una contraseña mediante Argon2.
* `verify_password`: comprueba una contraseña contra su hash.
* `create_access_token`: crea y firma los tokens JWT utilizados para la autenticación.

---

## `cors.py`

Contiene la función:

`setup_cors(app)`

Esta función incorpora `CORSMiddleware` a la aplicación FastAPI para permitir la comunicación entre diferentes orígenes.

---

# Acceso a la base de datos — `db`

La carpeta `db` reúne la lógica necesaria para establecer la conexión y trabajar con las sesiones de la base de datos.

## `database.py`

Este archivo contiene los elementos principales para la persistencia de información.

### `DATABASE_URL`

Define la dirección de conexión a la base de datos. Si no se proporciona una configuración externa, se utiliza SQLite mediante:

`sqlite:///./mikedb.db`

### `create_engine`

Se utiliza para crear el motor de conexión con la base de datos.

### `create_db_and_tables()`

Inicializa las tablas correspondientes a los modelos definidos mediante SQLModel.

### `get_session()`

Genera las sesiones que posteriormente pueden ser utilizadas por los endpoints mediante `Depends(get_session)`.

---

# Modelos — `models`

Los modelos representan las entidades que se almacenan en la base de datos.

## `user_model.py`

Define el modelo `Usuario`.

Sus principales campos son:

* `id`
* `username`
* `email`
* `hashed_password`
* `is_active`
* `created_at`

La contraseña no se almacena directamente, sino mediante su correspondiente hash.

---

## `Refrigerador_model.py`

Contiene el modelo `Refrigerador`.

Incluye los siguientes datos:

* `id`
* `nombre`
* `ubicacion`
* `usuario_id`

El campo `usuario_id` funciona como una relación opcional con `Usuario`.

Además, el refrigerador mantiene una relación de uno a muchos con los alimentos.

La relación utiliza:

`cascade="all, delete-orphan"`

---

## `Alimento_model.py`

Representa los alimentos registrados dentro de los refrigeradores.

Sus campos son:

* `id`
* `nombre`
* `tipo`
* `cantidad`
* `fecha_caducidad`
* `refrigerador_id`

`refrigerador_id` establece la relación entre cada alimento y el refrigerador al que pertenece.

---

# Esquemas de datos — `schemas`

Los esquemas se utilizan para definir qué información recibe y devuelve la API, además de realizar la validación correspondiente.

## `user_schema.py`

Define los esquemas:

* `UserCreate`
* `UserUpdate`
* `UserResponse`

`UserResponse` permite devolver los datos del usuario sin exponer la contraseña.

---

## `token_schema.py`

Contiene las estructuras relacionadas con la autenticación:

* `Token`
* `TokenData`

Estos esquemas permiten manejar la información asociada con los tokens.

---

## `Alimento.py`

Contiene `AlimentoOut`, utilizado para estructurar la información de los alimentos que devuelve la API.

---

## `Refrigerador.py`

Define `RefrigeradorOut`.

Este esquema permite devolver la información de un refrigerador junto con los elementos `AlimentoOut` asociados.

---

# Variables de configuración

El proyecto utiliza un archivo `.env` ubicado en la carpeta principal para almacenar los valores de configuración.

La estructura utilizada es:

```env
DATABASE_URL=postgresql://mike3:super_secret_password4@localhost:5435/mikedb3

SECRET_KEY=tu_clave_secreta_aqui_super_segura

ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30
```

De esta manera, la información de conexión, la clave utilizada para los tokens y el tiempo de expiración pueden mantenerse como variables de configuración en lugar de colocarse directamente dentro de la lógica de la aplicación.
