# Sistema Distribuido de Caja de Ahorro con Django y MariaDB

## Descripción

Sistema web de administración para una Caja de Ahorro desarrollado con **Django**, **MariaDB** y **Apache**, diseñado para demostrar la implementación de conceptos de **Bases de Datos Distribuidas** y **Programación Distribuida**.

El proyecto implementa un sistema CRUD para la gestión de clientes, cuentas y usuarios, incorporando mecanismos de auditoría, replicación Master-Slave, control de acceso basado en roles, almacenamiento de fechas en UTC y registro de actividades para garantizar la trazabilidad de las operaciones.

---

## Objetivos del Proyecto

Este proyecto fue desarrollado como parte de la asignatura **Sistemas Informáticos Distribuidos** de la carrera de Ingeniería en Redes y Telecomunicaciones.

Los principales objetivos fueron:

* Implementar una arquitectura distribuida basada en múltiples servidores.
* Separar operaciones de lectura y escritura mediante replicación de bases de datos.
* Incorporar mecanismos de auditoría y trazabilidad.
* Aplicar principios de seguridad en la gestión de usuarios.
* Utilizar procedimientos almacenados, funciones, triggers y vistas.
* Implementar respaldos automáticos y monitoreo de replicación.

---

## Arquitectura del Sistema

```text
                    ┌─────────────────┐
                    │     Usuario     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Apache + Django │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼

     ┌─────────────────┐         ┌─────────────────┐
     │ MariaDB Master  │         │ MariaDB Slave   │
     │ Escritura       │         │ Lectura         │
     └────────┬────────┘         └─────────────────┘
              │
              ▼

      Replicación Binaria
```

### Distribución de responsabilidades

| Servidor        | Función                      |
| --------------- | ---------------------------- |
| Apache + Django | Aplicación web               |
| MariaDB Master  | Inserciones y modificaciones |
| MariaDB Slave   | Consultas y lectura de datos |

---

## Funcionalidades Implementadas

### Gestión de Usuarios

* Inicio de sesión seguro.
* Control de acceso basado en roles.
* Registro de nuevos usuarios.
* Activación y desactivación de cuentas.
* Registro de intentos de inicio de sesión.
* Historial de accesos.

### Gestión de Clientes

* Alta de clientes.
* Consulta de clientes.
* Modificación de clientes.
* Eliminación lógica.
* Búsquedas mediante filtros.

### Gestión de Cuentas

* Alta de cuentas.
* Consulta de cuentas.
* Modificación de cuentas.
* Eliminación lógica.
* Asociación con clientes existentes.

### Auditoría

* Registro de inserciones.
* Registro de modificaciones.
* Registro de eliminaciones lógicas.
* Registro de usuario autenticado.
* Registro de dirección IP.
* Registro de zona horaria.
* Almacenamiento de valores anteriores y nuevos en formato JSON.

### Replicación

* Arquitectura Master-Slave.
* Lecturas realizadas desde la réplica.
* Escrituras realizadas sobre el servidor principal.
* Monitoreo del estado de replicación.
* Visualización del retraso (lag) de sincronización.

---

## Tecnologías Utilizadas

### Backend

* Python
* Django
* MariaDB
* MySQL Connector

### Frontend

* HTML5
* CSS3
* JavaScript

### Infraestructura

* Apache
* CentOS
* VMware
* Replicación MariaDB Master-Slave

### Base de Datos

* Procedimientos almacenados
* Funciones
* Triggers
* Vistas
* Logs de auditoría
* Binary Log
* General Log
* Slow Query Log
* Error Log

---

## Seguridad

El sistema incorpora varias medidas de seguridad:

### Control de Roles

| Rol     | Permisos                           |
| ------- | ---------------------------------- |
| Master  | Acceso completo                    |
| Sistema | Inserción, consulta y modificación |
| Lector  | Solo consultas                     |

### Protección de Datos

* Contraseñas almacenadas con SHA-256.
* Correos electrónicos cifrados mediante AES.
* Teléfonos cifrados mediante AES.
* Eliminación lógica de registros.
* Validación de permisos en cada vista.
* Validaciones tanto en frontend como backend.

### Auditoría

Cada operación relevante registra:

* Usuario autenticado.
* Dirección IP.
* Zona horaria.
* Fecha y hora en UTC.
* Tipo de operación.
* Valores modificados.

---

## Manejo de Fechas y Horarios

Todas las fechas almacenadas en la base de datos utilizan el estándar UTC.

Además, el sistema:

* Detecta automáticamente la zona horaria del navegador.
* Guarda la zona geográfica del usuario.
* Convierte las fechas al horario local durante la visualización.

Ejemplo:

```text
Base de datos:
2025-08-15 21:00:00 UTC

Usuario:
America/Mazatlan

Visualización:
2025-08-15 15:00:00
```

---

## Replicación y Consistencia

El proyecto implementa una estrategia de lectura y escritura distribuida:

### Escrituras

Todas las operaciones de inserción y modificación son enviadas al servidor Master.

### Lecturas

Las consultas son enviadas al servidor Slave para reducir la carga sobre el servidor principal.

### Monitoreo

El sistema verifica periódicamente:

* Estado de replicación.
* Estado de los hilos SQL e IO.
* Retraso respecto al servidor Master.

---

## Auditoría mediante JSON

Las tablas de logs almacenan:

```json
{
  "valores_anteriores": {
    "Nombre": "John",
    "Telefono": "1234567890"
  },
  "valores_nuevos": {
    "Nombre": "John Doe",
    "Telefono": "0987654321"
  }
}
```

Esto permite reconstruir completamente cada modificación realizada dentro del sistema.

---

## Características Técnicas Destacadas

* Arquitectura distribuida.
* Replicación Master-Slave.
* Procedimientos almacenados para operaciones CRUD.
* Triggers de auditoría.
* Logs estructurados en JSON.
* Uso de UTC en toda la base de datos.
* Control de acceso basado en roles.
* Eliminación lógica de registros.
* Monitoreo de replicación.
* Respaldos automatizados mediante CRON.
* Validaciones en frontend y backend.

---

## Estructura General del Proyecto

```text
django-crud/
│
├── djangocrud/
│
├── tasks/
│   ├── templates/
│   ├── static/
│   ├── views/
│   ├── decorators/
│   └── utils/
│
├── docs/
│
└── manage.py
```

---

## Conceptos Aplicados

* Sistemas Distribuidos
* Bases de Datos Distribuidas
* Replicación de Bases de Datos
* Arquitectura Cliente-Servidor
* Auditoría de Sistemas
* Seguridad en Aplicaciones Web
* Control de Acceso Basado en Roles (RBAC)
* Programación Web con Django
* Administración de MariaDB
* Automatización de Respaldos

---

## Autor

Kevin Gael Cisneros Herrera

Ingeniería en Redes y Telecomunicaciones

Universidad Politécnica de Durango

---

## Licencia

Proyecto desarrollado con fines académicos y de aprendizaje.
