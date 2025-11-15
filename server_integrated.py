#!/usr/bin/env python3
"""
Servidor Publisher Integrado - Modelo Publisher-Subscriber
Maneja la generación de mensajes, colas y recepción de resultados.
"""

import argparse
import random
import time
import threading
import socket
import pickle
import struct
from queue import Queue, Empty
from collections import defaultdict
from typing import List, Dict, Set

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

# Configuración de red
SERVER_HOST = "localhost"
SERVER_PORT = 8888


class PublisherServer:
    """
    Servidor que actúa como Publisher en el modelo Publisher-Subscriber.
    """
    
    def __init__(self, criterio: str, host: str = SERVER_HOST, port: int = SERVER_PORT):
        """
        Inicializa el servidor Publisher.
        
        Args:
            criterio: Criterio de selección de cola
            host: Dirección del servidor
            port: Puerto del servidor
        """
        self.criterio = criterio
        self.host = host
        self.port = port
        self.colas = {
            COLA_PRINCIPAL: Queue(),
            COLA_SECUNDARIA: Queue(),
            COLA_TERCIARIA: Queue()
        }
        self.resultados = []
        self.registro_clientes = defaultdict(list)
        self.suscripciones_clientes = defaultdict(set)
        self.lock = threading.Lock()
        self.total_resultados = 0
        self.running = True
        self.socket_server = None
        
        print(f"Servidor Publisher iniciado con criterio: {criterio}")
    
    def seleccionar_cola_aleatorio(self) -> str:
        """Selecciona una cola aleatoriamente (33% para cada una)."""
        return random.choice([COLA_PRINCIPAL, COLA_SECUNDARIA, COLA_TERCIARIA])
    
    def seleccionar_cola_ponderado(self) -> str:
        """Selecciona una cola de forma ponderada: 50% principal, 30% secundaria, 20% terciaria."""
        rand = random.random()
        if rand < 0.5:
            return COLA_PRINCIPAL
        elif rand < 0.8:
            return COLA_SECUNDARIA
        else:
            return COLA_TERCIARIA
    
    def seleccionar_cola_condicional(self, numeros: List[int]) -> str:
        """
        Selecciona una cola según las características de los números.
        - Dos números pares → Principal
        - Dos números impares → Secundaria
        - Tres números pares o impares → Terciaria
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
        
        # Por defecto, usar ponderado
        return self.seleccionar_cola_ponderado()
    
    def seleccionar_cola(self, numeros: List[int]) -> str:
        """Selecciona la cola según el criterio configurado."""
        if self.criterio == CRITERIO_ALEATORIO:
            return self.seleccionar_cola_aleatorio()
        elif self.criterio == CRITERIO_PONDERADO:
            return self.seleccionar_cola_ponderado()
        elif self.criterio == CRITERIO_CONDICIONAL:
            return self.seleccionar_cola_condicional(numeros)
        else:
            raise ValueError(f"Criterio desconocido: {self.criterio}")
    
    def generar_numeros(self) -> List[int]:
        """Genera un conjunto aleatorio de números (2 o 3 números)."""
        cantidad = random.choice([2, 3])
        return [random.randint(1, 100) for _ in range(cantidad)]
    
    def generar_y_publicar(self):
        """Genera números y los publica en las colas correspondientes."""
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
            
            self.colas[cola].put(mensaje)
            mensaje_id += 1
            
            # Pequeña pausa para no saturar
            if mensaje_id % 1000 == 0:
                time.sleep(0.01)
    
    def procesar_resultado(self, cliente_id: str, resultado: int, colas_suscritas: Set[str]):
        """Procesa un resultado recibido de un cliente."""
        with self.lock:
            self.resultados.append(resultado)
            self.registro_clientes[cliente_id].append(resultado)
            self.suscripciones_clientes[cliente_id].update(colas_suscritas)
            self.total_resultados += 1
            
            if self.total_resultados % 10000 == 0:
                print(f"Resultados recibidos: {self.total_resultados:,} / {OBJETIVO_RESULTADOS:,}")
            
            if self.total_resultados >= OBJETIVO_RESULTADOS:
                self.running = False
                print(f"\n¡Objetivo alcanzado! {self.total_resultados:,} resultados recibidos.")
    
    def manejar_cliente_mensajes(self, cliente_socket, cliente_address):
        """
        Maneja las solicitudes de mensajes de un cliente.
        El cliente envía las colas a las que está suscrito y recibe mensajes.
        """
        try:
            # Recibir información de suscripción del cliente
            tamaño_data = cliente_socket.recv(4)
            if len(tamaño_data) < 4:
                return
            
            tamaño = struct.unpack('!I', tamaño_data)[0]
            datos = b''
            while len(datos) < tamaño:
                chunk = cliente_socket.recv(tamaño - len(datos))
                if not chunk:
                    return
                datos += chunk
            
            suscripcion = pickle.loads(datos)
            cliente_id = suscripcion.get('cliente_id', 'unknown')
            colas_suscritas = suscripcion.get('colas', set())
            
            print(f"Cliente {cliente_id} conectado desde {cliente_address}, suscrito a: {', '.join(sorted(colas_suscritas))}")
            
            # Enviar mensajes al cliente mientras esté conectado
            while self.running:
                mensaje_enviado = False
                
                # Si el cliente está suscrito a múltiples colas, seleccionar aleatoriamente
                # Si está suscrito a una sola, usar esa
                colas_lista = list(colas_suscritas)
                if len(colas_lista) > 1:
                    # Selección aleatoria cuando hay múltiples colas
                    random.shuffle(colas_lista)
                
                # Intentar obtener un mensaje de cualquiera de las colas suscritas
                for cola in colas_lista:
                    try:
                        mensaje = self.colas[cola].get(timeout=0.1)
                        
                        # Serializar y enviar mensaje
                        datos_mensaje = pickle.dumps(mensaje)
                        tamaño_mensaje = len(datos_mensaje)
                        
                        cliente_socket.sendall(struct.pack('!I', tamaño_mensaje))
                        cliente_socket.sendall(datos_mensaje)
                        
                        mensaje_enviado = True
                        break
                    except Empty:
                        continue
                
                if not mensaje_enviado:
                    # No hay mensajes, enviar señal de espera
                    time.sleep(0.01)
                
                # Verificar si el cliente sigue conectado
                try:
                    cliente_socket.settimeout(0.1)
                    cliente_socket.recv(1, socket.MSG_PEEK)
                except (socket.timeout, ConnectionResetError, BrokenPipeError):
                    break
                    
        except Exception as e:
            print(f"Error manejando cliente {cliente_address}: {e}")
        finally:
            cliente_socket.close()
    
    def manejar_resultados(self, cliente_socket, cliente_address):
        """
        Maneja la recepción de resultados de los clientes.
        """
        try:
            while self.running:
                # Recibir tamaño
                tamaño_data = cliente_socket.recv(4)
                if len(tamaño_data) < 4:
                    break
                
                tamaño = struct.unpack('!I', tamaño_data)[0]
                
                # Recibir datos
                datos = b''
                while len(datos) < tamaño:
                    chunk = cliente_socket.recv(tamaño - len(datos))
                    if not chunk:
                        return
                    datos += chunk
                
                resultado_data = pickle.loads(datos)
                cliente_id = resultado_data['cliente_id']
                resultado = resultado_data['resultado']
                colas_suscritas = resultado_data['colas_suscritas']
                
                self.procesar_resultado(cliente_id, resultado, colas_suscritas)
                
        except Exception as e:
            print(f"Error recibiendo resultado de {cliente_address}: {e}")
        finally:
            cliente_socket.close()
    
    def servidor_mensajes(self):
        """Servidor que maneja las solicitudes de mensajes de los clientes."""
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self.host, self.port))
            sock.listen(10)
            sock.settimeout(1.0)
            
            print(f"Servidor de mensajes escuchando en {self.host}:{self.port}")
        except OSError as e:
            if e.errno == 48:  # Address already in use
                print(f"ERROR: El puerto {self.port} ya está en uso.")
                print(f"Por favor, detén el proceso anterior o usa otro puerto con --port")
                print(f"Para encontrar el proceso: lsof -i :{self.port}")
                self.running = False
                if sock:
                    sock.close()
                return
            else:
                if sock:
                    sock.close()
                raise
        
        try:
            while self.running:
                try:
                    cliente_socket, cliente_address = sock.accept()
                    thread = threading.Thread(
                        target=self.manejar_cliente_mensajes,
                        args=(cliente_socket, cliente_address),
                        daemon=True
                    )
                    thread.start()
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"Error en servidor de mensajes: {e}")
        finally:
            if sock:
                sock.close()
    
    def servidor_resultados(self):
        """Servidor que maneja la recepción de resultados."""
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self.host, self.port + 1))
            sock.listen(10)
            sock.settimeout(1.0)
            
            print(f"Servidor de resultados escuchando en {self.host}:{self.port + 1}")
        except OSError as e:
            if e.errno == 48:  # Address already in use
                print(f"ERROR: El puerto {self.port + 1} ya está en uso.")
                print(f"Por favor, detén el proceso anterior o usa otro puerto con --port")
                print(f"Para encontrar el proceso: lsof -i :{self.port + 1}")
                self.running = False
                if sock:
                    sock.close()
                return
            else:
                if sock:
                    sock.close()
                raise
        
        try:
            while self.running:
                try:
                    cliente_socket, cliente_address = sock.accept()
                    thread = threading.Thread(
                        target=self.manejar_resultados,
                        args=(cliente_socket, cliente_address),
                        daemon=True
                    )
                    thread.start()
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"Error en servidor de resultados: {e}")
        finally:
            if sock:
                sock.close()
    
    def generar_reporte_final(self):
        """Genera y muestra el reporte final."""
        suma_total = sum(self.resultados)
        
        print("\n" + "="*80)
        print("REPORTE FINAL DEL SERVIDOR PUBLISHER")
        print("="*80)
        print(f"\nTotal de resultados recibidos: {len(self.resultados):,}")
        print(f"Suma total de resultados: {suma_total:,}")
        print(f"\nNúmero de clientes únicos: {len(self.registro_clientes)}")
        print("\nClientes y sus suscripciones:")
        print("-"*80)
        
        for cliente_id in sorted(self.registro_clientes.keys()):
            colas = self.suscripciones_clientes[cliente_id]
            resultados_cliente = len(self.registro_clientes[cliente_id])
            print(f"Cliente {cliente_id}:")
            print(f"  - Colas suscritas: {', '.join(sorted(colas))}")
            print(f"  - Resultados procesados: {resultados_cliente:,}")
        
        print("="*80)
    
    def iniciar(self):
        """Inicia todos los servicios del servidor."""
        # Hilo de generación y publicación
        generador_thread = threading.Thread(target=self.generar_y_publicar, daemon=True)
        generador_thread.start()
        
        # Hilo del servidor de mensajes
        mensajes_thread = threading.Thread(target=self.servidor_mensajes, daemon=True)
        mensajes_thread.start()
        
        # Hilo del servidor de resultados
        resultados_thread = threading.Thread(target=self.servidor_resultados, daemon=True)
        resultados_thread.start()
        
        # Esperar hasta alcanzar el objetivo
        while self.running:
            time.sleep(1)
        
        # Esperar a que terminen los hilos
        generador_thread.join(timeout=2)
        mensajes_thread.join(timeout=2)
        resultados_thread.join(timeout=2)
        
        # Generar reporte final
        time.sleep(2)  # Dar tiempo para que lleguen los últimos resultados
        self.generar_reporte_final()


def main():
    """Función principal del servidor."""
    parser = argparse.ArgumentParser(description='Servidor Publisher')
    parser.add_argument(
        '--criterio',
        type=str,
        choices=[CRITERIO_ALEATORIO, CRITERIO_PONDERADO, CRITERIO_CONDICIONAL],
        default=CRITERIO_ALEATORIO,
        help='Criterio de selección de cola (aleatorio, ponderado, condicional)'
    )
    parser.add_argument('--host', type=str, default=SERVER_HOST, help='Dirección del servidor')
    parser.add_argument('--port', type=int, default=SERVER_PORT, help='Puerto del servidor')
    
    args = parser.parse_args()
    
    server = PublisherServer(args.criterio, args.host, args.port)
    
    print("Servidor iniciado. Presiona Ctrl+C para detener.")
    
    try:
        server.iniciar()
    except KeyboardInterrupt:
        print("\nDeteniendo servidor...")
        server.running = False
        server.generar_reporte_final()


if __name__ == "__main__":
    main()

