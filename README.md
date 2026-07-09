# Control Modular de PiCar-X

Este es un proyecto en Python para controlar el carrito PiCar-X de forma modular.

## Funciones del Carrito

- **Menú Principal (`main.py`)**: Menú interactivo en consola para elegir qué función usar.
- **Control por Teclado (`features/keyboard_control.py`)**: Maneja el carrito con `W/A/S/D`, mueve la cámara con `I/K/J/L` y toca la bocina con `C`.
- **Monitor de Batería (`features/battery_monitor.py`)**: Muestra el voltaje y porcentaje estimado de la batería en tiempo real.
- **Transmisión de Cámara (`features/camera_server.py`)**: Inicia un servidor web para ver el video de la cámara desde el navegador.
- **Evasión de Obstáculos (`features/obstacle_avoidance.py`)**: Conducción autónoma donde el carrito esquiva paredes usando su sensor de ultrasonido.

---

## Limitaciones del Carrito Actual

### 1. Desgaste de Motores Traseros (Tracción)
- El **motor derecho** está muy gastado y gira más lento que el izquierdo.
- Para que el carro vaya recto, en `core/motor_drive.py` aplicamos un balance de `-0.90` (esto reduce la velocidad del motor izquierdo al 10% para emparejarla con el motor lento).
- *Calibración:* Este valor específico de `-0.90` se obtuvo de forma experimental utilizando la herramienta interactiva de calibración en `tools/motor_calibration.py`.

### 2. Inversión de Cables de Motores (Motor 1 y Motor 2)
- Físicamente, el sentido de giro o el cableado de los motores estaban invertidos (haciendo que el carrito fuera en sentido contrario).
- Se creó el script de diagnóstico `tools/motor_test.py` para probar y aislar de forma individual cada motor (Motor 1 Izquierdo, Motor 2 Derecho).
- Gracias al diagnóstico del script, se pudieron reorganizar correctamente los cables físicos para que el movimiento real coincida con el lógico.

---

## Cómo Ejecutar el Proyecto

Siempre debes iniciar el proyecto usando **`sudo`** para dar permisos de hardware y sonido:

```bash
sudo python3 main.py
```
