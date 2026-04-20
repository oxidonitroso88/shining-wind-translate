# shining-wind-translate
i don't know programming or rom hacking, but I liked the game and characters, and since there is not a single translation out there, i wanted to documentate my findings or tools i found while trying to translate the game.  This most likely will get abandoned, but whatever i find ill post it so someone more capable in the future may try

# PS2 TXR Texture & Text Research

Herramientas, scripts y documentación para analizar y extraer texturas y texto de juegos de PlayStation 2 (`.txr`, `.raw`, etc.).

---

## 📌 Estado del proyecto

🧪 Investigación en progreso
✔ Extracción funcional
✔ Conversión a PNG (parcial)
⚠ Paletas y swizzle aún en análisis
⚠ Reinserción no finalizada

---

## 📂 Estructura del proyecto

```
.
├── scripts/        # Scripts de extracción y conversión
├── docs/           # Documentación del formato
├── examples/       # Ejemplos pequeños (sin assets del juego completo)
└── README.md
```

---

## 🧠 Formato TXR (hallazgos)

### Header

* Tamaño común detectado: `0x170` bytes
* En algunos casos: `0x210`

### Datos de imagen

* Comienzan después del header
* Formatos detectados:

  * **8bpp (grayscale indexado)** → UI, fondos
  * **4bpp (indexado)** → personajes, fuentes

### Paletas (CLUT)

* Archivos separados:

  ```
  *_PAL_*.raw
  ```
* Necesarias para ver colores reales

---

## 📏 Tamaños detectados

| Tipo       | Resolución |
| ---------- | ---------- |
| UI pequeña | 64x48      |
| Texto/UI   | 80xXX      |
| Fondos     | 320x128    |
| Personajes | ~128x128   |
| Shop faces | ~110x110   |

---

## 🔧 Herramientas usadas

* QuickBMS → extracción
* CrystalTile2 → inspección visual
* Python + Pillow → conversión
* Scripts personalizados → automatización

---

## 🚀 Uso básico

### 1. Extraer `.txr`

```bash
quickbms extract_txr.bms archivo.txr output
```

---

### 2. Convertir `.raw` a PNG

```bash
python convert_all.py
```

---

### 3. Detección automática

```bash
python auto_convert.py
```

---

## ⚠ Problemas conocidos

* Muchas texturas están **swizzled (PS2)**
* Algunas usan **4bpp (requiere decodificación especial)**
* Paletas no aplicadas automáticamente aún
* Offsets varían (`0x170`, `0x210`, etc.)

---

## 🧪 Investigación actual

* [ ] Unswizzle PS2 automático
* [ ] Aplicación automática de paletas
* [ ] Soporte completo 4bpp
* [ ] Reinsertar `.txr` modificados
* [ ] Pipeline completo PNG → TXR

---

## 📜 Notas importantes

Este repositorio:

✔ Documenta el formato
✔ Incluye scripts propios
❌ NO incluye assets completos del juego (copyright)

---

## 🤝 Contribuciones

Cualquier aporte es bienvenido:

* descubrimientos de formato
* scripts de conversión
* mejoras en detección

---

## 🧠 Objetivo

Construir una herramienta completa para:

👉 extraer
👉 visualizar
👉 modificar
👉 reinsertar

texturas de juegos de PS2

---

## 📌 Autor

Proyecto personal en progreso.
Si te sirve, usalo y mejoralo 🚀
