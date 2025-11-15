#!/usr/bin/env python3
"""
Script para ejecutar múltiples clientes en paralelo.
"""

import subprocess
import sys
import argparse
import time

def main():
    parser = argparse.ArgumentParser(description='Ejecutar múltiples clientes')
    parser.add_argument('--num-clientes', type=int, default=5, help='Número de clientes a ejecutar')
    parser.add_argument('--host', type=str, default='localhost', help='Dirección del servidor')
    parser.add_argument('--port', type=int, default=8888, help='Puerto del servidor')
    
    args = parser.parse_args()
    
    procesos = []
    
    print(f"Iniciando {args.num_clientes} clientes...")
    
    try:
        for i in range(args.num_clientes):
            cliente_id = f"cliente_{i+1}"
            proceso = subprocess.Popen(
                [sys.executable, 'client_integrated.py', '--id', cliente_id, '--host', args.host, '--port', str(args.port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            procesos.append(proceso)
            print(f"Cliente {cliente_id} iniciado (PID: {proceso.pid})")
            time.sleep(0.1)  # Pequeña pausa entre inicios
        
        print(f"\n{args.num_clientes} clientes ejecutándose. Presiona Ctrl+C para detenerlos.")
        
        # Esperar a que terminen todos los procesos
        for proceso in procesos:
            proceso.wait()
            
    except KeyboardInterrupt:
        print("\nDeteniendo clientes...")
        for proceso in procesos:
            proceso.terminate()
        for proceso in procesos:
            proceso.wait()
        print("Clientes detenidos.")

if __name__ == "__main__":
    main()

