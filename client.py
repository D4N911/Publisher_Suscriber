#!/usr/bin/env python3
"""
Cliente Subscriber - Modelo Publisher-Subscriber
Se suscribe a colas y procesa mensajes recibidos.
"""

import argparse
import random
import time
import threading
from queue import Queue, Empty
from typing import List, Set, Dict
import socket
import pickle
import struct

# Colas disponibles
COLA_PRINCIPAL = "principal"
COLA_SECUNDARIA = "secundaria"
COLA_TERCIARIA = "terciaria"

# Configuración de red (para comunicación con el servidor)
SERVER_HOST = "localhost"
SERVER_PORT = 8888


class SubscriberClient:
    """
    Cliente que actúa como Subscriber en el modelo Publisher-Subscriber.
    Se suscribe a una o dos colas y procesa los mensajes recibidos.
    """
    
    def __init__(self, cliente_id: str, colas_locales: Dict[str, Queue], server_host: str = SERVER_HOST, server_port: int = SERVER_PORT):
        """
        Inicializa el cliente Subscriber.
        
        Args:
            cliente_id: Identificador único del cliente
            colas_locales: Diccionario con las colas locales (compartidas con el servidor)
            server_host: Dirección del servidor
            server_port: Puerto del servidor
        """
        self.cliente_id = cliente_id
        self.colas_locales = colas_locales
        self.server_host = server_host
        self.server_port = server_port
        self.running = True
        
        # Decidir si se suscribe a 1 o 2 colas (50% probabilidad cada una)
        if random.random() < 0.5:
            # Suscripción a una cola
            cola_elegida = random.choice([COLA_PRINCIPAL, COLA_SECUNDARIA, COLA_TERCIARIA])
            self.colas_suscritas = {cola_elegida}
        else:
            # Suscripción a dos colas
            colas_disponibles = [COLA_PRINCIPAL, COLA_SECUNDARIA, COLA_TERCIARIA]
            self.colas_suscritas = set(random.sample(colas_disponibles, 2))
        
        print(f"Cliente {cliente_id} iniciado. Suscrito a: {', '.join(sorted(self.colas_suscritas))}")
    
    def procesar_numeros(self, numeros: List[int]) -> int:
        """
        Procesa un conjunto de números y retorna el resultado.
        En este caso, suma los números y eleva al cuadrado.
        
        Args:
            numeros: Lista de números a procesar
            
        Returns:
            Resultado del procesamiento
        """
        suma = sum(numeros)
        resultado = suma ** 2
        return resultado
    
    def seleccionar_cola_aleatoria(self) -> str:
        """
        Selecciona aleatoriamente una de las colas a las que está suscrito.
        
        Returns:
            Nombre de la cola seleccionada
        """
        return random.choice(list(self.colas_suscritas))
    
    def obtener_mensaje(self) -> Dict:
        """
        Obtiene un mensaje de cualquiera de las colas a las que está suscrito.
        Si está suscrito a dos colas, selecciona aleatoriamente de cuál obtener.
        
        Returns:
            Mensaje obtenido o None si no hay mensajes disponibles
        """
        if len(self.colas_suscritas) == 1:
            # Solo una cola, obtener de ella
            cola = list(self.colas_suscritas)[0]
            try:
                return self.colas_locales[cola].get(timeout=0.1)
            except Empty:
                return None
        else:
            # Dos colas, seleccionar aleatoriamente
            cola = self.seleccionar_cola_aleatoria()
            try:
                return self.colas_locales[cola].get(timeout=0.1)
            except Empty:
                # Intentar la otra cola
                otra_cola = (self.colas_suscritas - {cola}).pop()
                try:
                    return self.colas_locales[otra_cola].get(timeout=0.1)
                except Empty:
                    return None
    
    def enviar_resultado(self, resultado: int):
        """
        Envía el resultado al servidor.
        
        Args:
            resultado: Resultado a enviar
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.server_host, self.server_port))
            
            # Enviar datos
            datos = {
                'cliente_id': self.cliente_id,
                'resultado': resultado,
                'colas_suscritas': self.colas_suscritas
            }
            
            datos_serializados = pickle.dumps(datos)
            tamaño = len(datos_serializados)
            
            # Enviar tamaño primero
            sock.sendall(struct.pack('!I', tamaño))
            # Enviar datos
            sock.sendall(datos_serializados)
            
            sock.close()
        except Exception as e:
            print(f"Error al enviar resultado: {e}")
    
    def ejecutar(self):
        """
        Ejecuta el ciclo principal del cliente.
        Obtiene mensajes, los procesa y envía los resultados.
        """
        mensajes_procesados = 0
        
        while self.running:
            mensaje = self.obtener_mensaje()
            
            if mensaje is not None:
                numeros = mensaje['numeros']
                resultado = self.procesar_numeros(numeros)
                self.enviar_resultado(resultado)
                mensajes_procesados += 1
                
                if mensajes_procesados % 1000 == 0:
                    print(f"Cliente {self.cliente_id}: {mensajes_procesados:,} mensajes procesados")
            else:
                # No hay mensajes, esperar un poco
                time.sleep(0.01)
        
        print(f"Cliente {self.cliente_id} finalizado. Total procesado: {mensajes_procesados:,} mensajes")


def main():
    """
    Función principal del cliente.
    Nota: En una implementación real, las colas deberían ser compartidas
    entre el servidor y los clientes. Para simplificar, usaremos un enfoque
    donde el cliente se conecta al servidor para recibir mensajes.
    """
    parser = argparse.ArgumentParser(description='Cliente Subscriber')
    parser.add_argument('--id', type=str, required=True, help='ID único del cliente')
    parser.add_argument('--host', type=str, default=SERVER_HOST, help='Dirección del servidor')
    parser.add_argument('--port', type=int, default=SERVER_PORT, help='Puerto del servidor')
    
    args = parser.parse_args()
    
    # Nota: En una implementación real, las colas deberían ser compartidas
    # Por ahora, el cliente se conectará al servidor para recibir mensajes
    # Esta es una simplificación - en producción usaríamos un sistema de mensajería real
    
    print(f"Cliente {args.id} iniciando...")
    print("Nota: Este cliente requiere que el servidor esté ejecutándose")
    print("y compartiendo las colas. Ver implementación completa en server_client_integrated.py")


if __name__ == "__main__":
    main()

