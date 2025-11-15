#!/usr/bin/env python3
"""
Servidor Publisher - Modelo Publisher-Subscriber
Genera conjuntos de números y los asigna a colas según el criterio configurado.
"""

import argparse
import random
import time
import threading
from queue import Queue
from collections import defaultdict
from typing import List, Tuple, Dict

# Colas para los diferentes tipos de mensajes
COLA_PRINCIPAL = "principal"
COLA_SECUNDARIA = "secundaria"
COLA_TERCIARIA = "terciaria"

# Criterios de selección
CRITERIO_ALEATORIO = "aleatorio"
CRITERIO_PONDERADO = "ponderado"
CRITERIO_CONDICIONAL = "condicional"

# Objetivo de resultados
OBJETIVO_RESULTADOS = 1_000_000


class PublisherServer:
    """
    Servidor que actúa como Publisher en el modelo Publisher-Subscriber.
    Genera conjuntos de números y los distribuye a diferentes colas.
    """
    
    def __init__(self, criterio: str):
        """
        Inicializa el servidor Publisher.
        
        Args:
            criterio: Criterio de selección de cola (aleatorio, ponderado, condicional)
        """
        self.criterio = criterio
        self.colas = {
            COLA_PRINCIPAL: Queue(),
            COLA_SECUNDARIA: Queue(),
            COLA_TERCIARIA: Queue()
        }
        self.resultados = []  # Lista de resultados recibidos
        self.registro_clientes = defaultdict(list)  # Cliente -> [resultados]
        self.suscripciones_clientes = defaultdict(set)  # Cliente -> {colas}
        self.lock = threading.Lock()
        self.total_resultados = 0
        self.running = True
        
        print(f"Servidor Publisher iniciado con criterio: {criterio}")
    
    def seleccionar_cola_aleatorio(self) -> str:
        """
        Selecciona una cola aleatoriamente (33% para cada una).
        
        Returns:
            Nombre de la cola seleccionada
        """
        return random.choice([COLA_PRINCIPAL, COLA_SECUNDARIA, COLA_TERCIARIA])
    
    def seleccionar_cola_ponderado(self) -> str:
        """
        Selecciona una cola de forma ponderada:
        - Principal: 50%
        - Secundaria: 30%
        - Terciaria: 20%
        
        Returns:
            Nombre de la cola seleccionada
        """
        rand = random.random()
        if rand < 0.5:
            return COLA_PRINCIPAL
        elif rand < 0.8:
            return COLA_SECUNDARIA
        else:
            return COLA_TERCIARIA
    
    def seleccionar_cola_condicional(self, numeros: List[int]) -> str:
        """
        Selecciona una cola según las características de los números:
        - Dos números pares → Principal
        - Dos números impares → Secundaria
        - Tres números pares o impares → Terciaria
        
        Args:
            numeros: Lista de números a analizar
            
        Returns:
            Nombre de la cola seleccionada
        """
        pares = sum(1 for n in numeros if n % 2 == 0)
        impares = len(numeros) - pares
        
        if len(numeros) == 2:
            if pares == 2:
                return COLA_PRINCIPAL
            elif impares == 2:
                return COLA_SECUNDARIA
        elif len(numeros) == 3:
            if pares == 3 or impares == 3:
                return COLA_TERCIARIA
        
        # Por defecto, si no cumple ninguna condición, usar ponderado
        return self.seleccionar_cola_ponderado()
    
    def seleccionar_cola(self, numeros: List[int]) -> str:
        """
        Selecciona la cola según el criterio configurado.
        
        Args:
            numeros: Lista de números generados
            
        Returns:
            Nombre de la cola seleccionada
        """
        if self.criterio == CRITERIO_ALEATORIO:
            return self.seleccionar_cola_aleatorio()
        elif self.criterio == CRITERIO_PONDERADO:
            return self.seleccionar_cola_ponderado()
        elif self.criterio == CRITERIO_CONDICIONAL:
            return self.seleccionar_cola_condicional(numeros)
        else:
            raise ValueError(f"Criterio desconocido: {self.criterio}")
    
    def generar_numeros(self) -> List[int]:
        """
        Genera un conjunto aleatorio de números (2 o 3 números).
        
        Returns:
            Lista de números generados
        """
        cantidad = random.choice([2, 3])
        return [random.randint(1, 100) for _ in range(cantidad)]
    
    def publicar_mensaje(self, mensaje: Dict):
        """
        Publica un mensaje en la cola correspondiente.
        
        Args:
            mensaje: Diccionario con los datos del mensaje
        """
        cola = mensaje['cola']
        self.colas[cola].put(mensaje)
    
    def procesar_resultado(self, cliente_id: str, resultado: int, colas_suscritas: set):
        """
        Procesa un resultado recibido de un cliente.
        
        Args:
            cliente_id: Identificador del cliente
            resultado: Resultado calculado por el cliente
            colas_suscritas: Conjunto de colas a las que está suscrito el cliente
        """
        with self.lock:
            self.resultados.append(resultado)
            self.registro_clientes[cliente_id].append(resultado)
            self.suscripciones_clientes[cliente_id].update(colas_suscritas)
            self.total_resultados += 1
            
            if self.total_resultados % 10000 == 0:
                print(f"Resultados recibidos: {self.total_resultados:,}")
            
            if self.total_resultados >= OBJETIVO_RESULTADOS:
                self.running = False
    
    def obtener_cola(self, nombre_cola: str) -> Queue:
        """
        Obtiene la cola por su nombre.
        
        Args:
            nombre_cola: Nombre de la cola
            
        Returns:
            Cola correspondiente
        """
        return self.colas[nombre_cola]
    
    def generar_y_publicar(self):
        """
        Genera números y los publica en las colas correspondientes.
        Se ejecuta en un hilo separado.
        """
        mensaje_id = 0
        while self.running:
            numeros = self.generar_numeros()
            cola = self.seleccionar_cola(numeros)
            
            mensaje = {
                'id': mensaje_id,
                'numeros': numeros,
                'cola': cola,
                'timestamp': time.time()
            }
            
            self.publicar_mensaje(mensaje)
            mensaje_id += 1
            
            # Pequeña pausa para no saturar
            time.sleep(0.001)
    
    def generar_reporte_final(self):
        """
        Genera y muestra el reporte final con:
        - Suma total de resultados
        - Lista de clientes
        - Suscripciones de cada cliente
        """
        suma_total = sum(self.resultados)
        
        print("\n" + "="*80)
        print("REPORTE FINAL DEL SERVIDOR PUBLISHER")
        print("="*80)
        print(f"\nTotal de resultados recibidos: {len(self.resultados):,}")
        print(f"Suma total de resultados: {suma_total:,}")
        print(f"\nNúmero de clientes únicos: {len(self.registro_clientes)}")
        print("\nClientes y sus suscripciones:")
        print("-"*80)
        
        for cliente_id, colas in sorted(self.suscripciones_clientes.items()):
            resultados_cliente = len(self.registro_clientes[cliente_id])
            print(f"Cliente {cliente_id}:")
            print(f"  - Colas suscritas: {', '.join(sorted(colas))}")
            print(f"  - Resultados procesados: {resultados_cliente:,}")
        
        print("="*80)


def main():
    """
    Función principal del servidor.
    """
    parser = argparse.ArgumentParser(description='Servidor Publisher')
    parser.add_argument(
        '--criterio',
        type=str,
        choices=[CRITERIO_ALEATORIO, CRITERIO_PONDERADO, CRITERIO_CONDICIONAL],
        default=CRITERIO_ALEATORIO,
        help='Criterio de selección de cola (aleatorio, ponderado, condicional)'
    )
    
    args = parser.parse_args()
    
    server = PublisherServer(args.criterio)
    
    # Iniciar hilo de generación y publicación
    generador_thread = threading.Thread(target=server.generar_y_publicar, daemon=True)
    generador_thread.start()
    
    print("Servidor iniciado. Esperando clientes...")
    print("Presiona Ctrl+C para detener el servidor")
    
    try:
        # Mantener el servidor corriendo
        while server.running:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDeteniendo servidor...")
        server.running = False
    
    # Esperar a que termine la generación
    generador_thread.join(timeout=2)
    
    # Generar reporte final
    server.generar_reporte_final()


if __name__ == "__main__":
    main()

