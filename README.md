# Control Modular de PiCar-X

Este es un proyecto en Python para controlar el carrito PiCar-X de forma modular.

## Funciones del Carrito

- **Menú Principal (`main.py`)**: Menú interactivo en consola para elegir qué función usar.
- **Control por Teclado (`features/keyboard_control.py`)**: Maneja el carrito con `W/A/S/D`, mueve la cámara con `I/K/J/L` y toca la bocina con `C`.
- **Monitor de Batería (`features/battery_monitor.py`)**: Muestra el voltaje y porcentaje estimado de la batería en tiempo real.
- **Transmisión de Cámara (`features/camera_server.py`)**: Inicia un servidor web para ver el video de la cámara desde el navegador.
- **Evasión de Obstáculos (`features/obstacle_avoidance.py`)**: Conducción autónoma donde el carrito esquiva paredes usando su sensor de ultrasonido.
- **Rutina de Indicaciones por Voz (`features/voice_prompts.py`)**: Secuencia de movimiento autónomo donde el carrito anuncia cada acción usando TTS en español.
- **Control de Voz Local Offline (`features/vosk_voice_control.py`)**: Manejo por comandos hablados 100% local en español (avanzar, retroceder, girar, bocina) utilizando el modelo Vosk y un micrófono USB.

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

### 3. Precisión del Reconocimiento de Voz Local (Vosk)
- Al utilizar el modelo offline ligero de Vosk en la Raspberry Pi, el motor tiene dificultades para diferenciar palabras con fonemas parecidos o bajo ruido ambiental.
- Para mitigar esto y lograr una precisión del 100%, limitamos los comandos posibles restringiendo la gramática a un vocabulario predefinido.
- Aunque esta solución garantiza que el carrito funcione a la perfección, limita el nivel de personalización de forma escalable, ya que no permite comprender lenguaje natural libre y requiere agregar manualmente cada nueva palabra permitida en el código.

### 4. Lecturas del Sensor de Ultrasonido (Evasión de Obstáculos)
- El sensor ultrasónico tiene limitaciones físicas intrínsecas a su tecnología de eco:
  - **Superficies absorbentes:** Objetos blandos o porosos (como telas, alfombras o peluches) absorben las ondas de sonido en lugar de reflejarlas, haciendo que el sensor no detecte el obstáculo y el carrito choque.
  - **Ángulos de aproximación:** Si el carrito se acerca a una pared o superficie en un ángulo muy inclinado (oblicuo), la onda de sonido rebota hacia otro lado en lugar de regresar al sensor, resultando en lecturas erróneas.
  - **Zonas muertas y objetos delgados:** Objetos muy delgados (como las patas de una silla) o fuera de su cono de detección de 15 grados pueden no ser percibidos por el sensor.

---

## Cómo Ejecutar el Proyecto

Siempre debes iniciar el proyecto usando **`sudo`** para dar permisos de hardware y sonido:

```bash
sudo python3 main.py
```
