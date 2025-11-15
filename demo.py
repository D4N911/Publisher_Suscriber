#!/usr/bin/env python3
"""
Script de demostración simplificado para probar el sistema
con un número reducido de resultados (para pruebas rápidas).
"""

import subprocess
import sys
import time
import argparse

# Modificar el objetivo de resultados para pruebas
OBJETIVO_PRUEBA = 1000  # En lugar de 1,000,000


def modificar_objetivo_en_servidor():
    """Modifica temporalmente el objetivo en server_integrated.py para pruebas."""
    # Esta función sería útil si quisiéramos hacer pruebas rápidas
    # Por ahora, solo es informativa
    pass


def main():
    parser = argparse.ArgumentParser(description='Demo del sistema Publisher-Subscriber')
    parser.add_argument('--criterio', type=str, default='aleatorio', 
                       choices=['aleatorio', 'ponderado', 'condicional'],
                       help='Criterio de selección de cola')
    parser.add_argument('--num-clientes', type=int, default=3, 
                       help='Número de clientes a ejecutar')
    
    args = parser.parse_args()
    
    print("="*80)
    print("DEMO: Sistema Publisher-Subscriber")
    print("="*80)
    print(f"\nCriterio: {args.criterio}")
    print(f"Número de clientes: {args.num_clientes}")
    print("\nNOTA: Para una demostración completa, el sistema necesita")
    print("alcanzar 1,000,000 de resultados. Esto puede tomar tiempo.")
    print("\nPara pruebas rápidas, puedes modificar OBJETIVO_RESULTADOS")
    print("en server_integrated.py temporalmente.")
    print("\nIniciando servidor y clientes...")
    print("="*80)
    
    # Iniciar servidor
    print("\n[1/2] Iniciando servidor...")
    server_process = subprocess.Popen(
        [sys.executable, 'server_integrated.py', '--criterio', args.criterio],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(2)  # Dar tiempo al servidor para iniciar
    
    # Iniciar clientes
    print(f"[2/2] Iniciando {args.num_clientes} clientes...")
    client_processes = []
    
    for i in range(args.num_clientes):
        cliente_id = f"cliente_{i+1}"
        proceso = subprocess.Popen(
            [sys.executable, 'client_integrated.py', '--id', cliente_id],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        client_processes.append(proceso)
        print(f"  - {cliente_id} iniciado")
        time.sleep(0.5)
    
    print("\n" + "="*80)
    print("Sistema en ejecución. El servidor mostrará el progreso.")
    print("Presiona Ctrl+C para detener todo.")
    print("="*80 + "\n")
    
    try:
        # Esperar a que termine el servidor (cuando alcance el objetivo)
        server_process.wait()
        
        print("\n" + "="*80)
        print("Servidor finalizado. Deteniendo clientes...")
        print("="*80)
        
        # Detener clientes
        for proceso in client_processes:
            proceso.terminate()
        
        for proceso in client_processes:
            proceso.wait()
        
        print("Todos los procesos detenidos.")
        
    except KeyboardInterrupt:
        print("\n\nDeteniendo todos los procesos...")
        server_process.terminate()
        for proceso in client_processes:
            proceso.terminate()
        
        server_process.wait()
        for proceso in client_processes:
            proceso.wait()
        
        print("Procesos detenidos.")


if __name__ == "__main__":
    main()

