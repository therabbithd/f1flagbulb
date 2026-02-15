# Implementación en React con Pyodide

Este documento detalla la estructura y el código necesario para migrar la lógica de la aplicación Python (`f1flag`) a una aplicación web React ejecutando el código Python directamente en el navegador mediante **Pyodide**.

> [!WARNING]
> **Limitación Crítica de Red (CORS & Sockets)**
> Los navegadores bloquean las conexiones TCP/UDP directas por seguridad.
> 1.  **Kasa Bulb**: La librería `python-kasa` usa sockets UDP/TCP directos que **no funcionarán** dentro de Pyodide en el navegador. Necesitarás un "puente" (WebSocket Proxy) ejecutándose localmente, o una API intermedia.
> 2.  **SignalR/WebSocket**: La conexión a F1 requiere WebSockets. Pyodide puede usar WebSockets, pero la librería Python debe ser compatible con el entorno del navegador (Emscripten).

A continuación se presenta la implementación asumiendo que queremos ejecutar la lógica Python en el navegador.

## 1. Estructura del Proyecto

```text
my-f1-app/
├── public/
│   ├── python/
│   │   ├── config.py
│   │   ├── kasa_manager.py
│   │   ├── f1_monitor.py
│   │   └── main_browser.py  <-- Adaptación para el navegador
├── src/
│   ├── components/
│   │   └── F1Dashboard.jsx
│   ├── hooks/
│   │   └── usePyodide.js
│   ├── App.js
│   └── index.css
├── package.json
└── README.md
```

## 2. Configuración Inicial

Instalar Pyodide en el proyecto React:

```bash
npm install pyodide
```

O usar el CDN en `index.html` (recomendado para cargar los archivos WASM eficientemente):
```html
<script src="https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.js"></script>
```

## 3. Código React

### `src/hooks/usePyodide.js`
Este hook inicializa Pyodide y carga los archivos Python desde la carpeta `public/`.

```javascript
import { useState, useEffect, useRef } from 'react';

export const usePyodide = () => {
  const [pyodide, setPyodide] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    const loadPyodideInstance = async () => {
      try {
        // Inicializar Pyodide (asumiendo script CDN cargado o import dinámico)
        const pyodideInstance = await window.loadPyodide();
        
        // Instalar paquetes necesarios
        await pyodideInstance.loadPackage(['micropip']);
        const micropip = pyodideInstance.pyimport("micropip");
        
        // Instalar dependencias puras de Python si es posible
        // Nota: python-kasa tiene dependencias de red complejas, podría fallar.
        await micropip.install(['asyncio']); 

        // Definir función de log para JS
        pyodideInstance.globals.set("js_log", (msg) => {
          setLogs(prev => [...prev.slice(-49), msg]);
        });

        setPyodide(pyodideInstance);
      } catch (err) {
        console.error("Error cargando Pyodide:", err);
      } finally {
        setIsLoading(false);
      }
    };

    loadPyodideInstance();
  }, []);

  return { pyodide, isLoading, logs };
};
```

### `src/components/F1Dashboard.jsx`
Interfaz de usuario que interactúa con el código Python.

```jsx
import React, { useState, useEffect } from 'react';
import { usePyodide } from '../hooks/usePyodide';

const F1Dashboard = () => {
  const { pyodide, isLoading, logs } = usePyodide();
  const [ip, setIp] = useState("192.168.10.163");
  const [status, setStatus] = useState({ label: "Desconectado", color: "#333" });

  const runPythonLogic = async () => {
    if (!pyodide) return;

    // Leer archivos Python del public folder
    const files = ['config.py', 'kasa_manager.py', 'f1_monitor.py', 'main_browser.py'];
    
    for (const file of files) {
      const response = await fetch(`/python/${file}`);
      const text = await response.text();
      // Escribir archivo en el sistema de archivos virtual de Pyodide
      pyodide.FS.writeFile(file, text);
    }

    // Ejecutar el script principal
    try {
      // Pasar la IP configurada al entorno Python
      pyodide.globals.set("USER_KASA_IP", ip);
      
      // Ejecutar main_browser.py
      await pyodide.runPythonAsync(`
        import main_browser
        import asyncio
        # Iniciar el loop en segundo plano (simulado)
        asyncio.create_task(main_browser.start(USER_KASA_IP))
      `);
    } catch (err) {
      console.error("Error ejecución Python:", err);
    }
  };

  return (
    <div style={{ padding: 20, backgroundColor: '#111', color: 'white', minHeight: '100vh', fontFamily: 'Arial' }}>
      <h1>F1 Flag Monitor (Pyodide)</h1>
      
      <div style={{ border: `4px solid ${status.color}`, padding: 20, borderRadius: 10, margin: '20px 0' }}>
        <h2>ESTADO: {status.label}</h2>
      </div>

      <div style={{ marginBottom: 20 }}>
        <input 
          value={ip} 
          onChange={(e) => setIp(e.target.value)} 
          placeholder="IP Bombilla"
          style={{ padding: 10, marginRight: 10 }}
        />
        <button 
          onClick={runPythonLogic} 
          disabled={isLoading}
          style={{ padding: 10, backgroundColor: '#2196F3', color: 'white', border: 'none' }}
        >
          {isLoading ? "Cargando Pyodide..." : "Iniciar Monitor"}
        </button>
      </div>

      <div style={{ background: '#222', padding: 10, height: 200, overflowY: 'auto', fontFamily: 'monospace' }}>
        {logs.map((log, i) => <div key={i}>{log}</div>)}
      </div>
    </div>
  );
};

export default F1Dashboard;
```

## 4. Adaptación del Código Python (`public/python/`)

Debido a que el navegador maneja el Loop de eventos, no podemos usar `app.mainloop()` ni hilos bloqueantes. Debemos usar `asyncio` integrado con el navegador.

### `public/python/main_browser.py`
Versión adaptada de `main.py` para correr en Pyodide.

```python
import asyncio
import js # Módulo puente para interactuar con JS
from config import COLORS
# Nota: KasaManager necesitará ser mockeado o proxied si python-kasa falla en WASM
# from kasa_manager import KasaManager 

class BrowserLogger:
    def __call__(self, msg):
        js.js_log(f"[Py] {msg}")

logger = BrowserLogger()

async def start(ip):
    logger(f"Iniciando con IP: {ip}")
    
    # Simulación de conexión (ya que UDP/TCP directo no funciona)
    logger("Conectando a bombilla (Simulado en navegador)...")
    await asyncio.sleep(1)
    logger("Bombilla conectada (Simulación)")

    # Bucle principal simulado
    while True:
        # Aquí iría la lógica real de F1Monitor si Websockets funcionan en Pyodide
        # O pooling a una API
        await asyncio.sleep(5) 
        logger("Monitoreando estado F1...")

# Exponer funciones al scope global si es necesario
```

## 5. Implementación del Proxy (Bridge) para Hardware

Para que `python-kasa` funcione desde la aplicación React (ya que los navegadores bloquean conexiones directas a los dispositivos), utilizaremos el servidor Flask (`web_app.py`) que creamos anteriormente como **Bridge (Puente)**.

### Paso 1: Configurar el Servidor Proxy (Backend)

Asegúrate de que `web_app.py` esté ejecutándose. Este archivo actúa como el "Proxy" que recibe peticiones HTTP del frontend y ejecuta los comandos reales de `python-kasa` en el servidor.

**Comando:**
```bash
python web_app.py
# El servidor iniciará en http://localhost:5000
```

### Paso 2: Configurar el Proxy en React

Para evitar problemas de CORS y conectar React con Flask transparentemente, configuramos un proxy en el entorno de desarrollo.

**Opción A: Si usas Vite (Recomendado)**
Edita `vite.config.js`:
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Redirige cualquier petición que empiece con /api al backend Flask
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
      }
    }
  }
})
```

**Opción B: Si usas Create React App (CRA)**
Instala `http-proxy-middleware`:
```bash
npm install http-proxy-middleware --save
```
Crea `src/setupProxy.js`:
```javascript
const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://localhost:5000',
      changeOrigin: true,
    })
  );
};
```

### Paso 3: Integración en el Componente

Ahora, desde tu componente React (`F1Dashboard.jsx`), puedes llamar a las funciones de Kasa usando endpoints estándar, sin preocuparte por Pyodide para esta parte específica.

```javascript
// Ejemplo de función para el componente
const updateBulbIP = async (newIp) => {
  // Esta petición va a React -> Proxy -> Flask (web_app.py) -> Kasa Bulb
  const res = await fetch('/api/config/ip', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ ip: newIp })
  });
  const data = await res.json();
  console.log(data);
};
```

> [!TIP]
> **Arquitectura Híbrida**: Usa **Pyodide** para lógica de cálculo pura (ej. procesar datos de telemetría complejos en el cliente) y el **Proxy Flask** para interactuar con el hardware (bombillas, sockets reales).

