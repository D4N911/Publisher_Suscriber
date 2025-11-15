# Sistema Publisher-Subscriber

Implementación de un modelo de comunicación Publisher-Subscriber donde un servidor genera conjuntos de números y los distribuye a diferentes colas, mientras que múltiples clientes se suscriben a estas colas y procesan los mensajes.

## Características

### Servidor (Publisher)
- Genera conjuntos aleatorios de números (2 o 3 números)
- Asigna mensajes a una de tres colas (principal, secundaria, terciaria) según criterios configurables:
  - **Aleatorio**: 33% de probabilidad para cada cola
  - **Ponderado**: 50% principal, 30% secundaria, 20% terciaria
  - **Condicional**: Basado en paridad de números
    - Dos números pares → Cola principal
    - Dos números impares → Cola secundaria
    - Tres números pares o impares → Cola terciaria
- Mantiene registro de resultados y suscripciones de clientes
- Se detiene al alcanzar 1,000,000 de resultados

### Cliente (Subscriber)
- Se suscribe a 1 o 2 colas (50% probabilidad cada opción)
- Cuando está suscrito a 2 colas, selecciona aleatoriamente de cuál obtener mensajes
- Procesa números (suma y eleva al cuadrado)
- Envía resultados al servidor

## Requisitos

- Python 3.7 o superior
- No se requieren dependencias externas (solo librerías estándar)

## Instalación

1. Clonar o descargar el repositorio
2. Asegurarse de tener Python 3.7+ instalado

```bash
python3 --version
```

## Uso

### 1. Iniciar el Servidor

El servidor debe iniciarse primero. Puedes elegir el criterio de selección de cola:

```bash
# Criterio aleatorio (por defecto)
python3 server_integrated.py --criterio aleatorio

# Criterio ponderado
python3 server_integrated.py --criterio ponderado

# Criterio condicional
python3 server_integrated.py --criterio condicional
```

Opciones adicionales:
- `--host`: Dirección del servidor (por defecto: localhost)
- `--port`: Puerto del servidor (por defecto: 8888)

Ejemplo:
```bash
python3 server_integrated.py --criterio ponderado --host localhost --port 8888
```

### 2. Iniciar Clientes

En terminales separadas o usando el script de ejecución múltiple:

#### Opción A: Script de inicio rápido (recomendado)

```bash
# Inicia servidor y clientes automáticamente
./inicio_rapido.sh [criterio] [num_clientes]

# Ejemplo:
./inicio_rapido.sh ponderado 5
```

#### Opción B: Ejecutar clientes individualmente

```bash
# Terminal 1
python3 client_integrated.py --id cliente_1

# Terminal 2
python3 client_integrated.py --id cliente_2

# Terminal 3
python3 client_integrated.py --id cliente_3
```

#### Opción C: Ejecutar múltiples clientes automáticamente

```bash
python3 run_clients.py --num-clientes 5
```

Opciones del script:
- `--num-clientes`: Número de clientes a ejecutar (por defecto: 5)
- `--host`: Dirección del servidor (por defecto: localhost)
- `--port`: Puerto del servidor (por defecto: 8888)

### 3. Monitoreo

El servidor mostrará:
- Progreso cada 10,000 resultados recibidos
- Mensaje cuando se alcance el objetivo de 1,000,000 resultados
- Reporte final con:
  - Suma total de resultados
  - Lista de clientes
  - Suscripciones de cada cliente

Los clientes mostrarán:
- Suscripciones al iniciar
- Progreso cada 1,000 mensajes procesados

## Ejemplo de Ejecución Completa

### Opción 1: Script de inicio rápido (más fácil)

```bash
./inicio_rapido.sh ponderado 5
```

### Opción 2: Manual (dos terminales)

```bash
# Terminal 1: Iniciar servidor
python3 server_integrated.py --criterio ponderado

# Terminal 2: Iniciar múltiples clientes
python3 run_clients.py --num-clientes 5
```

### Opción 3: Prueba rápida (1000 resultados)

```bash
python3 test_rapido.py --criterio aleatorio --num-clientes 3
```

## Estructura del Proyecto

```
Publisher-Suscriber/
├── server_integrated.py      # Servidor Publisher (principal)
├── client_integrated.py       # Cliente Subscriber (principal)
├── run_clients.py            # Script para ejecutar múltiples clientes
├── test_rapido.py            # Script de prueba rápida (1000 resultados)
├── demo.py                   # Script de demostración
├── inicio_rapido.sh          # Script bash de inicio rápido
├── server.py                 # Versión alternativa del servidor
├── client.py                 # Versión alternativa del cliente
├── requirements.txt          # Dependencias (vacío, solo stdlib)
├── README.md                 # Este archivo
├── DOCUMENTACION.md          # Documentación técnica detallada
├── DIAGRAMAS.md              # Diagramas de arquitectura
├── ENTREGABLES.md            # Lista de entregables
└── .gitignore                # Archivos a ignorar en git
```

## Criterios de Selección de Cola

### Aleatorio
Cada mensaje tiene un 33% de probabilidad de ir a cualquier cola.

### Ponderado
- Cola Principal: 50%
- Cola Secundaria: 30%
- Cola Terciaria: 20%

### Condicional
Basado en las características de los números:
- **2 números pares** → Cola Principal
- **2 números impares** → Cola Secundaria
- **3 números (todos pares o todos impares)** → Cola Terciaria
- Si no cumple ninguna condición, usa el criterio ponderado

## Comunicación

El sistema usa sockets TCP para la comunicación:
- **Puerto 8888**: Servidor de mensajes (Publisher → Subscribers)
- **Puerto 8889**: Servidor de resultados (Subscribers → Publisher)

## Reporte Final

Al alcanzar 1,000,000 de resultados, el servidor genera un reporte que incluye:

1. **Total de resultados recibidos**
2. **Suma total de resultados**
3. **Número de clientes únicos**
4. **Para cada cliente**:
   - Colas a las que está suscrito
   - Número de resultados procesados

Ejemplo de salida:
```
================================================================================
REPORTE FINAL DEL SERVIDOR PUBLISHER
================================================================================

Total de resultados recibidos: 1,000,000
Suma total de resultados: 1,234,567,890

Número de clientes únicos: 5

Clientes y sus suscripciones:
--------------------------------------------------------------------------------
Cliente cliente_1:
  - Colas suscritas: principal, secundaria
  - Resultados procesados: 200,000
Cliente cliente_2:
  - Colas suscritas: principal
  - Resultados procesados: 150,000
...
================================================================================
```

## ⏱️ Tiempo Estimado de Ejecución

Para alcanzar **1,000,000 de resultados**:

- **Con 5 clientes (por defecto)**: ~5-15 minutos
- **Con 10 clientes**: ~3-8 minutos
- **Con 20 clientes**: ~2-5 minutos

*El tiempo varía según el hardware y carga del sistema.*

**Para pruebas rápidas**, usa el script de prueba:
```bash
python3 test_rapido.py --criterio aleatorio --num-clientes 5 --objetivo 1000
```

Ver `TIEMPO_ESTIMADO.md` para más detalles.

## Notas Técnicas

- El servidor genera mensajes continuamente hasta alcanzar el objetivo
- Los clientes procesan mensajes de forma asíncrona
- La suscripción de cada cliente se determina al inicio (50% 1 cola, 50% 2 colas)
- Cuando un cliente está suscrito a 2 colas, selecciona aleatoriamente de cuál obtener mensajes
- El procesamiento de números consiste en sumar y elevar al cuadrado
- El servidor muestra progreso cada 10,000 resultados recibidos

## Solución de Problemas

### Error: "Connection refused"
- Asegúrate de que el servidor esté ejecutándose antes de iniciar los clientes
- Verifica que el puerto no esté en uso por otro proceso

### El servidor no alcanza 1,000,000 de resultados
- Asegúrate de tener suficientes clientes ejecutándose
- Verifica que los clientes estén conectados correctamente
- Revisa los logs de error en los clientes

### Los clientes no reciben mensajes
- Verifica que el servidor esté generando mensajes
- Comprueba que las colas a las que están suscritos los clientes reciban mensajes
- Revisa la configuración de red (host, puerto)

## Documentación Adicional

Para más detalles sobre:
- Comparativa Producer-Consumer vs Publisher-Subscriber
- Diagramas de arquitectura
- Casos de aplicación

Ver `DOCUMENTACION.md`

## Licencia

Este proyecto es de código abierto y está disponible para uso educativo.

