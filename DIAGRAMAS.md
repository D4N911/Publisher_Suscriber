# Diagramas de Arquitectura

## Diagrama 1: Arquitectura Producer-Consumer

```
┌─────────────────────────────────────────────────────────────┐
│                    PRODUCER-CONSUMER                        │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐
│  Productor   │
│              │
│ - Genera     │
│   datos      │
└──────┬───────┘
       │
       │ put(item)
       │
       ▼
┌─────────────────┐
│   Cola Única    │
│   Compartida    │
│                 │
│ [item1][item2]  │
│ [item3][item4]  │
└──────┬──────────┘
       │
       │ get()
       │
       ▼
┌──────────────┐
│  Consumidor  │
│              │
│ - Procesa    │
│   datos      │
└──────────────┘

Características:
- Un productor, una cola, un consumidor (o múltiples consumidores compitiendo)
- Relación 1:1 o N:1 (un mensaje → un consumidor)
- Acoplamiento: Productor conoce la cola
- Sincronización: Locks/semáforos para acceso a cola
```

## Diagrama 2: Arquitectura Publisher-Subscriber

```
┌─────────────────────────────────────────────────────────────┐
│                  PUBLISHER-SUBSCRIBER                       │
└─────────────────────────────────────────────────────────────┘

                    ┌──────────────────┐
                    │    Publisher     │
                    │    (Servidor)    │
                    │                  │
                    │ - Genera números │
                    │ - Selecciona cola│
                    │   (criterio)     │
                    └────────┬─────────┘
                             │
                             │ publicar()
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Cola Principal│    │Cola Secundaria│    │Cola Terciaria│
│              │    │              │    │              │
│ [msg1][msg2] │    │ [msg3][msg4] │    │ [msg5][msg6] │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       │                   │                   │
       │ subscribe()       │ subscribe()       │ subscribe()
       │                   │                   │
   ┌───┴───┐          ┌───┴───┐          ┌───┴───┐
   │       │          │       │          │       │
   ▼       ▼          ▼       ▼          ▼       ▼
┌─────┐ ┌─────┐   ┌─────┐ ┌─────┐   ┌─────┐ ┌─────┐
│Sub 1│ │Sub 2│   │Sub 3│ │Sub 4│   │Sub 5│ │Sub 6│
└──┬──┘ └──┬──┘   └──┬──┘ └──┬──┘   └──┬──┘ └──┬──┘
   │       │          │       │          │       │
   │       │          │       │          │       │
   └───┬───┘          └───┬───┘          └───┬───┘
       │                  │                  │
       │    resultado()   │    resultado()   │
       └──────────────────┼──────────────────┘
                          │
                          ▼
                    ┌─────────────┐
                    │  Publisher  │
                    │  (Registro) │
                    └─────────────┘

Características:
- Un publicador, múltiples colas, múltiples suscriptores
- Relación 1:N (un mensaje → múltiples suscriptores posibles)
- Desacoplamiento: Publisher no conoce suscriptores
- Suscripción dinámica: Suscriptores eligen colas
```

## Diagrama 3: Flujo de Datos Publisher-Subscriber (Este Proyecto)

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUJO DE DATOS                           │
└─────────────────────────────────────────────────────────────┘

FASE 1: GENERACIÓN Y PUBLICACIÓN
─────────────────────────────────

Publisher Server
    │
    │ 1. generar_numeros()
    │    → [2, 4, 6]  (ejemplo)
    │
    │ 2. seleccionar_cola(criterio)
    │    → "principal" (ejemplo)
    │
    │ 3. publicar_mensaje()
    │
    ▼
Cola Principal
    │
    │ mensaje: {id: 1, numeros: [2,4,6], cola: "principal"}
    │
    ▼
[Disponible para suscriptores]


FASE 2: SUSCRIPCIÓN Y RECEPCIÓN
────────────────────────────────

Cliente Subscriber
    │
    │ 1. Conectar al servidor
    │ 2. Enviar suscripción: {colas: ["principal", "secundaria"]}
    │
    ▼
Servidor recibe suscripción
    │
    │ 3. Seleccionar aleatoriamente de colas suscritas
    │    → "principal" (aleatorio)
    │
    │ 4. Obtener mensaje de cola "principal"
    │
    │ 5. Enviar mensaje al cliente
    │
    ▼
Cliente recibe mensaje
    │
    │ mensaje: {id: 1, numeros: [2,4,6], cola: "principal"}


FASE 3: PROCESAMIENTO
─────────────────────

Cliente Subscriber
    │
    │ 1. procesar_numeros([2,4,6])
    │    → suma = 2 + 4 + 6 = 12
    │    → resultado = 12² = 144
    │
    │ 2. enviar_resultado(144)
    │
    ▼
Servidor recibe resultado
    │
    │ 3. procesar_resultado(cliente_id, 144, {"principal", "secundaria"})
    │
    │ 4. Registrar:
    │    - resultados.append(144)
    │    - registro_clientes[cliente_id].append(144)
    │    - suscripciones_clientes[cliente_id] = {"principal", "secundaria"}
    │
    │ 5. Verificar si total_resultados >= 1,000,000
    │
    ▼
[Continúa hasta alcanzar objetivo]
```

## Diagrama 4: Criterios de Selección de Cola

```
┌─────────────────────────────────────────────────────────────┐
│           CRITERIOS DE SELECCIÓN DE COLA                    │
└─────────────────────────────────────────────────────────────┘

CRITERIO ALEATORIO
──────────────────
    Números generados
         │
         ▼
    ┌─────────┐
    │ Aleatorio│
    │ 33% cada │
    └────┬────┘
         │
    ┌────┼────┐
    │    │    │
   33%  33%  33%
    │    │    │
    ▼    ▼    ▼
  Principal Secundaria Terciaria


CRITERIO PONDERADO
──────────────────
    Números generados
         │
         ▼
    ┌─────────┐
    │Ponderado│
    └────┬────┘
         │
    ┌────┼────┐
    │    │    │
   50%  30%  20%
    │    │    │
    ▼    ▼    ▼
  Principal Secundaria Terciaria


CRITERIO CONDICIONAL
─────────────────────
    Números generados
         │
         ▼
    ┌──────────────┐
    │  Analizar    │
    │  paridad     │
    └──────┬───────┘
           │
    ┌──────┼──────┐
    │      │      │
   2 pares 2 impares 3 iguales
    │      │      │
    ▼      ▼      ▼
 Principal Secundaria Terciaria
```

## Diagrama 5: Suscripción de Clientes

```
┌─────────────────────────────────────────────────────────────┐
│              SUSCRIPCIÓN DE CLIENTES                         │
└─────────────────────────────────────────────────────────────┘

INICIO DEL CLIENTE
──────────────────
    Cliente inicia
         │
         ▼
    ┌─────────┐
    │ Aleatorio│
    │  50%     │
    └────┬────┘
         │
    ┌────┴────┐
    │         │
  50%       50%
    │         │
    ▼         ▼
1 cola    2 colas
    │         │
    │    ┌────┼────┐
    │    │    │    │
    │  33%   33%  33%
    │    │    │    │
    ▼    ▼    ▼    ▼
  P    S    T   PS  PT  ST
  │    │    │   │   │   │
  │    │    │   │   │   │
  └────┴────┴───┴───┴───┘
       │
       ▼
  Suscrito a cola(s)
       │
       ▼
  Recibe mensajes
  (si 2 colas: selección aleatoria)
```

## Diagrama 6: Comunicación por Sockets

```
┌─────────────────────────────────────────────────────────────┐
│              COMUNICACIÓN POR SOCKETS                       │
└─────────────────────────────────────────────────────────────┘

SERVIDOR (Publisher)
────────────────────
┌─────────────────────────────────────┐
│  Puerto 8888: Servidor de Mensajes  │
│  ────────────────────────────────   │
│  - Escucha conexiones de clientes   │
│  - Recibe suscripciones             │
│  - Envía mensajes a clientes        │
└─────────────────────────────────────┘
         ▲                    │
         │                    │
    connect()            send(message)
         │                    │
         │                    ▼
┌─────────────────────────────────────┐
│  Puerto 8889: Servidor de Resultados│
│  ────────────────────────────────   │
│  - Escucha conexiones de clientes   │
│  - Recibe resultados                │
│  - Registra en base de datos        │
└─────────────────────────────────────┘
         ▲
         │
    send(result)


CLIENTE (Subscriber)
────────────────────
┌─────────────────────────────────────┐
│  Socket 1: Conexión de Mensajes     │
│  ────────────────────────────────   │
│  1. connect(server:8888)            │
│  2. send(suscripción)               │
│  3. recv(mensajes)                  │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  Socket 2: Conexión de Resultados   │
│  ────────────────────────────────   │
│  1. connect(server:8889)            │
│  2. send(resultado)                 │
│  3. close()                         │
└─────────────────────────────────────┘
```

## Diagrama 7: Secuencia de Operaciones

```
┌─────────────────────────────────────────────────────────────┐
│           SECUENCIA DE OPERACIONES                          │
└─────────────────────────────────────────────────────────────┘

Tiempo →
│
│ SERVIDOR                    CLIENTE 1              CLIENTE 2
│     │                          │                      │
│     │─── Iniciar ──────────────│                      │
│     │                          │                      │
│     │                    ┌─────▼─────┐                │
│     │                    │ Suscripción│               │
│     │                    │ 1 o 2 colas│               │
│     │                    └─────┬─────┘                │
│     │                          │                      │
│     │◄──── connect(8888) ──────┤                      │
│     │◄──── send(suscripción) ──┤                      │
│     │                          │                      │
│     │─── Generar números ──────┤                      │
│     │─── Seleccionar cola ─────┤                      │
│     │─── Publicar ─────────────┤                      │
│     │                          │                      │
│     │──── send(mensaje) ───────►│                      │
│     │                          │                      │
│     │                          │─── Procesar ────────►│
│     │                          │─── Calcular ────────►│
│     │                          │                      │
│     │◄──── connect(8889) ──────┤                      │
│     │◄──── send(resultado) ─────┤                      │
│     │                          │                      │
│     │─── Registrar ────────────┤                      │
│     │─── Verificar total ───────┤                      │
│     │                          │                      │
│     │                    [Repetir]                    │
│     │                          │                      │
│     │                    [Hasta 1M resultados]        │
│     │                          │                      │
│     │─── Generar reporte ──────┤                      │
│     │─── Mostrar resultados ────┤                      │
│     │                          │                      │
```

## Notas sobre los Diagramas

- **Producer-Consumer**: Modelo simple, directo, con acoplamiento
- **Publisher-Subscriber**: Modelo flexible, desacoplado, escalable
- **Este proyecto**: Implementa Publisher-Subscriber con:
  - Múltiples colas (3)
  - Criterios configurables de selección
  - Suscripción dinámica (1 o 2 colas)
  - Comunicación por sockets TCP
  - Registro centralizado de resultados

Los diagramas muestran la arquitectura, flujo de datos, y secuencia de operaciones del sistema implementado.

