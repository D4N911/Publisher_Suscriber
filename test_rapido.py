#!/usr/bin/env python3
"""
Script de prueba rápida con objetivo reducido (1000 resultados en lugar de 1M).
Útil para verificar que el sistema funciona correctamente.
"""

import subprocess
import sys
import time
import argparse
import re

OBJETIVO_PRUEBA = 1000  # Resultados para prueba rápida
OBJETIVO_ORIGINAL = 1_000_000


def modificar_objetivo_en_archivo(archivo, nuevo_objetivo):
    """Modifica temporalmente el objetivo en el archivo del servidor."""
    try:
        with open(archivo, 'r') as f:
            contenido = f.read()
        
        # Buscar y reemplazar OBJETIVO_RESULTADOS
        contenido_modificado = re.sub(
            r'OBJETIVO_RESULTADOS\s*=\s*\d+',
            f'OBJETIVO_RESULTADOS = {nuevo_objetivo}',
            contenido
        )
        
        # Guardar backup
        with open(archivo + '.backup', 'w') as f:
            f.write(contenido)
        
        # Guardar modificado
        with open(archivo, 'w') as f:
            f.write(contenido_modificado)
        
        return True
    except Exception as e:
        print(f"Error modificando archivo: {e}")
        return False


def restaurar_archivo(archivo):
    """Restaura el archivo desde el backup."""
    try:
        with open(archivo + '.backup', 'r') as f:
            contenido = f.read()
        
        with open(archivo, 'w') as f:
            f.write(contenido)
        
        import os
        os.remove(archivo + '.backup')
        return True
    except Exception as e:
        print(f"Error restaurando archivo: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Prueba rápida del sistema')
    parser.add_argument('--criterio', type=str, default='aleatorio',
                       choices=['aleatorio', 'ponderado', 'condicional'],
                       help='Criterio de selección de cola')
    parser.add_argument('--num-clientes', type=int, default=3,
                       help='Número de clientes a ejecutar')
    parser.add_argument('--objetivo', type=int, default=OBJETIVO_PRUEBA,
                       help='Número de resultados objetivo para la prueba')
    
    args = parser.parse_args()
    
    print("="*80)
    print("PRUEBA RÁPIDA DEL SISTEMA PUBLISHER-SUBSCRIBER")
    print("="*80)
    print(f"\nObjetivo de resultados: {args.objetivo:,}")
    print(f"Criterio: {args.criterio}")
    print(f"Número de clientes: {args.num_clientes}")
    print("\nModificando servidor para prueba rápida...")
    
    # Modificar el objetivo en el servidor
    if not modificar_objetivo_en_archivo('server_integrated.py', args.objetivo):
        print("Error: No se pudo modificar el archivo del servidor")
        return
    
    print("✓ Servidor modificado para prueba rápida")
    print("\nIniciando servidor y clientes...")
    print("="*80)
    
    # Iniciar servidor
    print("\n[1/2] Iniciando servidor...")
    server_process = subprocess.Popen(
        [sys.executable, 'server_integrated.py', '--criterio', args.criterio],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    time.sleep(2)
    
    # Iniciar clientes
    print(f"[2/2] Iniciando {args.num_clientes} clientes...")
    client_processes = []
    
    for i in range(args.num_clientes):
        cliente_id = f"cliente_{i+1}"
        proceso = subprocess.Popen(
            [sys.executable, 'client_integrated.py', '--id', cliente_id],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        client_processes.append(proceso)
        print(f"  ✓ {cliente_id} iniciado")
        time.sleep(0.3)
    
    print("\n" + "="*80)
    print("Sistema en ejecución. Esperando resultados...")
    print("Presiona Ctrl+C para detener.")
    print("="*80 + "\n")
    
    try:
        # Monitorear salida del servidor
        while server_process.poll() is None:
            line = server_process.stdout.readline()
            if line:
                print(line.strip())
            time.sleep(0.1)
        
        # Leer salida restante
        stdout, stderr = server_process.communicate()
        if stdout:
            print(stdout)
        if stderr:
            print("Errores:", stderr, file=sys.stderr)
        
        print("\n" + "="*80)
        print("Servidor finalizado. Deteniendo clientes...")
        print("="*80)
        
        # Detener clientes
        for proceso in client_processes:
            proceso.terminate()
        
        for proceso in client_processes:
            proceso.wait()
        
        print("✓ Todos los procesos detenidos")
        
    except KeyboardInterrupt:
        print("\n\nDeteniendo todos los procesos...")
        server_process.terminate()
        for proceso in client_processes:
            proceso.terminate()
        
        server_process.wait()
        for proceso in client_processes:
            proceso.wait()
        
        print("✓ Procesos detenidos")
    
    finally:
        # Restaurar archivo original
        print("\nRestaurando configuración original del servidor...")
        if restaurar_archivo('server_integrated.py'):
            print("✓ Configuración restaurada")
        else:
            print("⚠ No se pudo restaurar. Revisa server_integrated.py.backup")


if __name__ == "__main__":
    main()

