# Documentación: Modelo Publisher-Subscriber

## Comparativa: Producer-Consumer vs Publisher-Subscriber

### Modelo Producer-Consumer

#### Características:
- **Acoplamiento directo**: El productor conoce directamente al consumidor o a la cola compartida
- **Comunicación punto a punto**: Un mensaje es procesado por un solo consumidor
- **Sincronización explícita**: Requiere mecanismos de sincronización (locks, semáforos) para acceder a colas compartidas
- **Relación 1:1 o N:1**: Un mensaje tiene un único destinatario

#### Arquitectura:
```
Productor → [Cola] → Consumidor
```

#### Ventajas:
- Simplicidad en la implementación
- Control directo sobre el flujo de mensajes
- Bajo overhead de comunicación
- Garantía de procesamiento (el mensaje se procesa una vez)

#### Desventajas:
- Escalabilidad limitada
- Acoplamiento entre productor y consumidor
- Difícil agregar nuevos consumidores dinámicamente
- El productor debe conocer la estructura de consumidores

#### Casos de aplicación:
- Procesamiento de tareas en un sistema de colas de trabajo
- Pipeline de procesamiento de datos secuencial
- Sistemas donde cada tarea debe procesarse exactamente una vez
- Procesamiento de transacciones bancarias
- Sistemas de impresión (una impresora, múltiples trabajos)

---

### Modelo Publisher-Subscriber

#### Características:
- **Desacoplamiento**: El publicador no conoce a los suscriptores
- **Comunicación uno a muchos**: Un mensaje puede ser recibido por múltiples suscriptores
- **Suscripción dinámica**: Los suscriptores pueden suscribirse/desuscribirse en tiempo de ejecución
- **Filtrado por tópicos/colas**: Los suscriptores eligen qué mensajes recibir
- **Relación 1:N**: Un mensaje puede tener múltiples destinatarios

#### Arquitectura:
```
Publisher → [Cola 1] → Subscriber 1
          → [Cola 2] → Subscriber 2
          → [Cola 3] → Subscriber 3
```

#### Ventajas:
- Alta escalabilidad
- Desacoplamiento completo entre publicador y suscriptores
- Flexibilidad para agregar/remover suscriptores sin afectar el publicador
- Soporte para múltiples tipos de mensajes (colas/tópicos)
- Distribución geográfica fácil

#### Desventajas:
- Mayor complejidad de implementación
- Posible overhead de comunicación
- No hay garantía de que todos los suscriptores reciban el mensaje (depende de la implementación)
- Puede requerir infraestructura adicional (message broker)

#### Casos de aplicación:
- Sistemas de notificaciones (email, SMS, push)
- Sistemas de logging distribuido
- Sistemas de eventos en tiempo real
- Chat en tiempo real
- Sistemas de monitoreo y alertas
- Distribución de actualizaciones de software
- Sistemas de IoT (Internet de las Cosas)
- Sistemas de trading financiero (distribución de precios)

---

## Comparación Directa

| Característica | Producer-Consumer | Publisher-Subscriber |
|---------------|-------------------|----------------------|
| **Acoplamiento** | Alto (conocen la cola) | Bajo (desacoplado) |
| **Destinatarios** | Uno por mensaje | Múltiples por mensaje |
| **Suscripción** | Estática | Dinámica |
| **Escalabilidad** | Limitada | Alta |
| **Complejidad** | Baja | Media-Alta |
| **Overhead** | Bajo | Medio |
| **Garantía de entrega** | Alta | Variable |
| **Filtrado de mensajes** | No | Sí (por tópicos/colas) |

---

## Diagramas de Arquitectura

### Diagrama Producer-Consumer

```
┌─────────────┐
│  Productor  │
└──────┬──────┘
       │
       │ put()
       ▼
┌─────────────┐
│    Cola     │
│  Compartida │
└──────┬──────┘
       │
       │ get()
       ▼
┌─────────────┐
│ Consumidor  │
└─────────────┘
```

**Flujo:**
1. El productor genera datos y los coloca en la cola
2. El consumidor obtiene datos de la cola
3. El consumidor procesa los datos
4. La cola actúa como buffer entre productor y consumidor

---

### Diagrama Publisher-Subscriber

```
                    ┌──────────────┐
                    │  Publisher   │
                    │   (Server)   │
                    └──────┬───────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │  Cola 1  │    │  Cola 2  │    │  Cola 3  │
    │Principal │    │Secundaria│    │ Terciaria│
    └────┬─────┘    └────┬─────┘    └────┬─────┘
         │               │               │
    ┌────┴────┐     ┌────┴────┐     ┌────┴────┐
    │         │     │         │     │         │
    ▼         ▼     ▼         ▼     ▼         ▼
┌──────┐  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
│Sub 1 │  │Sub 2 │ │Sub 3 │ │Sub 4 │ │Sub 5 │
└──────┘  └──────┘ └──────┘ └──────┘ └──────┘
```

**Flujo:**
1. El Publisher genera mensajes y los asigna a colas según criterios
2. Los Subscribers se suscriben a una o más colas
3. El Publisher distribuye mensajes a las colas correspondientes
4. Los Subscribers reciben mensajes de sus colas suscritas
5. Los Subscribers procesan y envían resultados al Publisher
6. El Publisher mantiene registro de resultados y suscripciones

---

## Casos de Aplicación Detallados

### Producer-Consumer

#### 1. Sistema de Procesamiento de Imágenes
- **Productor**: Cámara web capturando frames
- **Cola**: Buffer de frames
- **Consumidor**: Procesador de imágenes que aplica filtros
- **Razón**: Cada frame debe procesarse una vez, en orden

#### 2. Sistema de Impresión
- **Productor**: Aplicaciones enviando trabajos de impresión
- **Cola**: Cola de trabajos de impresión
- **Consumidor**: Servicio de impresión
- **Razón**: Un trabajo de impresión no debe imprimirse múltiples veces

#### 3. Procesamiento de Transacciones
- **Productor**: Terminales de punto de venta
- **Cola**: Cola de transacciones
- **Consumidor**: Procesador de pagos
- **Razón**: Cada transacción debe procesarse exactamente una vez

---

### Publisher-Subscriber

#### 1. Sistema de Notificaciones
- **Publisher**: Sistema de eventos (nuevo pedido, pago recibido)
- **Colas/Tópicos**: email, SMS, push, webhook
- **Subscribers**: Servicios de email, SMS, push notifications, webhooks
- **Razón**: Un evento debe notificarse por múltiples canales simultáneamente

#### 2. Sistema de Trading
- **Publisher**: Exchange de criptomonedas
- **Colas**: Precios BTC, ETH, etc.
- **Subscribers**: Traders, sistemas de análisis, dashboards
- **Razón**: Múltiples sistemas necesitan los mismos datos de precios en tiempo real

#### 3. Sistema de Monitoreo IoT
- **Publisher**: Gateway de sensores
- **Colas**: Temperatura, humedad, movimiento
- **Subscribers**: Sistema de alertas, base de datos, dashboard, análisis
- **Razón**: Los datos de sensores deben llegar a múltiples sistemas de procesamiento

#### 4. Sistema de Logging Distribuido
- **Publisher**: Aplicaciones generando logs
- **Colas**: logs.error, logs.warning, logs.info
- **Subscribers**: Almacenamiento, análisis, alertas, visualización
- **Razón**: Los logs deben ser procesados por múltiples sistemas (almacenamiento, análisis, alertas)

---

## Implementación en este Proyecto

### Características del Sistema Implementado:

1. **Publisher (Servidor)**:
   - Genera conjuntos de números aleatorios
   - Asigna mensajes a colas según criterios configurables:
     - **Aleatorio**: 33% para cada cola
     - **Ponderado**: 50% principal, 30% secundaria, 20% terciaria
     - **Condicional**: Basado en paridad de números
   - Mantiene registro de resultados y suscripciones

2. **Subscriber (Cliente)**:
   - Se suscribe a 1 o 2 colas (50% probabilidad cada opción)
   - Cuando está suscrito a 2 colas, selecciona aleatoriamente de cuál obtener mensajes
   - Procesa números (suma y eleva al cuadrado)
   - Envía resultados al servidor

3. **Criterio de Paro**:
   - El sistema se detiene cuando se alcanzan 1,000,000 de resultados
   - Genera reporte con:
     - Suma total de resultados
     - Lista de clientes
     - Suscripciones de cada cliente


