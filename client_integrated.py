#!/usr/bin/env python3
"""
Cliente Subscriber Integrado - Modelo Publisher-Subscriber
Se conecta al servidor, se suscribe a colas y procesa mensajes.
"""

import argparse
import random
import time
import threading
import socket
import pickle
import struct
from typing import List, Set

# Colas disponibles
COLA_PRINCIPAL = "principal"
COLA_SECUNDARIA = "secundaria"
COLA_TERCIARIA = "terciaria"

# Configuración de red
SERVER_HOST = "localhost"
SERVER_PORT = 8888


class SubscriberClient:
    """
    Cliente que actúa como Subscriber en el modelo Publisher-Subscriber.
    """
    
    def __init__(self, cliente_id: str, server_host: str = SERVER_HOST, server_port: int = SERVER_PORT):
        """
        Inicializa el cliente Subscriber.
        
        Args:
            cliente_id: Identificador único del cliente
            server_host: Dirección del servidor
            server_port: Puerto del servidor
        """
        self.cliente_id = cliente_id
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
        Suma los números y eleva al cuadrado.
        
        Args:
            numeros: Lista de números a procesar
            
        Returns:
            Resultado del procesamiento
        """
        suma = sum(numeros)
        resultado = suma ** 2
        return resultado
    
    def enviar_resultado(self, resultado: int):
        """
        Envía el resultado al servidor.
        
        Args:
            resultado: Resultado a enviar
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.server_host, self.server_port + 1))
            
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
            print(f"Cliente {self.cliente_id}: Error al enviar resultado: {e}")
    
    def recibir_mensajes(self):
        """
        Se conecta al servidor y recibe mensajes de las colas suscritas.
        """
        mensajes_procesados = 0
        
        try:
            # Conectar al servidor de mensajes
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.server_host, self.server_port))
            
            # Enviar información de suscripción
            suscripcion = {
                'cliente_id': self.cliente_id,
                'colas': self.colas_suscritas
            }
            
            datos_suscripcion = pickle.dumps(suscripcion)
            tamaño_suscripcion = len(datos_suscripcion)
            
            sock.sendall(struct.pack('!I', tamaño_suscripcion))
            sock.sendall(datos_suscripcion)
            
            # Recibir mensajes
            while self.running:
                try:
                    # Recibir tamaño del mensaje
                    tamaño_data = sock.recv(4)
                    if len(tamaño_data) < 4:
                        break
                    
                    tamaño = struct.unpack('!I', tamaño_data)[0]
                    
                    # Recibir datos del mensaje
                    datos = b''
                    while len(datos) < tamaño:
                        chunk = sock.recv(tamaño - len(datos))
                        if not chunk:
                            break
                        datos += chunk
                    
                    if len(datos) < tamaño:
                        break
                    
                    mensaje = pickle.loads(datos)
                    numeros = mensaje['numeros']
                    
                    # Procesar números
                    resultado = self.procesar_numeros(numeros)
                    
                    # Enviar resultado
                    self.enviar_resultado(resultado)
                    
                    mensajes_procesados += 1
                    
                    if mensajes_procesados % 1000 == 0:
                        print(f"Cliente {self.cliente_id}: {mensajes_procesados:,} mensajes procesados")
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"Cliente {self.cliente_id}: Error recibiendo mensaje: {e}")
                    break
            
            sock.close()
            
        except ConnectionRefusedError:
            print(f"Cliente {self.cliente_id}: No se pudo conectar al servidor. ¿Está ejecutándose?")
        except Exception as e:
            print(f"Cliente {self.cliente_id}: Error: {e}")
        finally:
            print(f"Cliente {self.cliente_id} finalizado. Total procesado: {mensajes_procesados:,} mensajes")
    
    def ejecutar(self):
        """Ejecuta el cliente."""
        self.recibir_mensajes()


def main():
    """Función principal del cliente."""
    parser = argparse.ArgumentParser(description='Cliente Subscriber')
    parser.add_argument('--id', type=str, required=True, help='ID único del cliente')
    parser.add_argument('--host', type=str, default=SERVER_HOST, help='Dirección del servidor')
    parser.add_argument('--port', type=int, default=SERVER_PORT, help='Puerto del servidor')
    
    args = parser.parse_args()
    
    client = SubscriberClient(args.id, args.host, args.port)
    
    try:
        client.ejecutar()
    except KeyboardInterrupt:
        print(f"\nDeteniendo cliente {args.id}...")
        client.running = False


if __name__ == "__main__":
    main()

