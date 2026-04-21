# Shining Wind (PS2) — Reverse Engineering Notes

> Investigación personal sobre la estructura de archivos del juego.
> Plataforma: PlayStation 2 | Desarrollador: Media.Vision | Publisher: Sega (2006)

---

## 📀 Estructura del disco

```
CD/
├── SLPM_666.71        → Ejecutable principal (ELF/MIPS)
├── MODULES.LST        → Lista de módulos del sistema
├── MODULES.CIX        → Índice de memoria del sistema PS2
├── modules/           → Drivers del sistema IOP (no contienen datos del juego)
│   ├── CRI_ADXI.IRX   → Driver de audio CRI Middleware
│   ├── PADMAN.IRX     → Driver de control
│   ├── MCMAN.IRX      → Driver de memory card
│   ├── LIBSD.IRX      → Driver de sonido
│   └── ... (10 archivos .IRX en total)
├── st.cvm             → Contenedor principal del juego
└── voice.cvm          → Contenedor de voces (por explorar)
```

---

## 🗂 Formato CVM

Los archivos `.cvm` son contenedores tipo ISO que se pueden montar o extraer con QuickBMS.

- `st.cvm` — contiene todos los recursos del juego
- `voice.cvm` — contiene archivos de voz (por explorar)

---

## 📁 Contenido de st.cvm

### Extensiones encontradas

| Extensión | Cantidad | Contenido |
|-----------|----------|-----------|
| `.rax` | 2069 | Contenedor principal de recursos (ver sección RAX) |
| `.txr` | 724 | Texturas sueltas |
| `.ahx` | 285 | Audio comprimido CRI (efectos/música) |
| `.adx` | 72 | Audio CRI formato alternativo |
| `.bra` | 64 | Archivos de índice/tabla (header INAB/LAPB) |
| `.sfd` | 31 | Videos (cinemáticas) |
| `.dpk` | 14 | Base de datos del juego (contienen texto japonés) |
| `.cix` | 1 | Índice de memoria |
| `.lst` | 1 | Lista de módulos |
| `.cnf` | 1 | Configuración |

---

## 📦 Formato RAX

Los `.rax` son **contenedores** que embeben múltiples sub-archivos internos.

### Magic bytes
```
52 41 58 = "RAX"
```

### Sub-formatos encontrados dentro de RAX

| Magic | Descripción |
|-------|-------------|
| `INAB` | Contenedor externo de Media.Vision |
| `LAPB` | Bloque de datos interno (tablas de animación/script) |
| `TXR\x00` | Texturas embebidas |
| `AHX` | Audio de voz embebido |
| `RAX` | Sub-contenedores anidados |

### Ejemplo de estructura interna (PACK001A.RAX, 2MB)
```
0x0000      → Header RAX
0x0020      → Ruta embebida: "chara/Player/001a.bra"
0x0040      → Sub-archivo INAB (header 12 bytes)
0x004C      → Sub-archivo LAPB (tabla de script/animación, 1036 bytes)
0x197E8     → Inicio de texturas TXR (~300+ texturas)
0x173EC0    → Segundo bloque INAB/LAPB
0x1D2620    → Inicio de archivos AHX (voces embebidas)
             → ahx/snd_bvo_kiriya00_001.ahx
             → ahx/snd_bvo_kiriya00_002.ahx
             → ... (10+ archivos de voz por escena)
0x1F7E20    → Referencias a archivos .lgc (lógica de personaje)
0x1FA820    → common/menu_face_a.txr
0x1FBC60    → pac_eff_p01.rax (efectos embebidos)
```

### Grupos de archivos RAX

| Grupo | Cantidad aprox. | Contenido |
|-------|-----------------|-----------|
| `PACK001A–020B.RAX` | ~53 | Escenas principales de historia |
| `PACK###_EV1.RAX` | ~11 | Variantes de evento por escena |
| `BFI_PAC_ENM_FREE##.RAX` | ~100 | Enemigos en batallas libres |
| `BFI_PAC_ENM_MAIN##.RAX` | ~80 | Enemigos en historia principal |
| `OI_PAC_NORMAL_01–10.RAX` | 10 | Escenas normales |
| `OI_PAC_MIRROR_01–10.RAX` | 10 | Escenas del espejo |
| `OI_PAC_SOULBLADE_01–10.RAX` | 10 | Escenas Soul Blade |
| `PAC_CHAOS01–10.RAX` | 10 | Escenas modo Chaos |
| `PAC_BEV02_##.RAX` | 8 | Battle events |
| `PAC_DBENC_ENE_###.RAX` | muchos | Encuentros con enemigos |
| `SSS_PAC_001–144.RAX` | 144 | Sin explorar en detalle |
| `BUSTUP/###_X.RAX` | ~300 | Retratos de personajes (texturas) |
| `CHARACTERSELECT.RAX` | 2 | Pantalla de selección |
| `MENUWINDOW.RAX` | 1 | Ventana de menú |
| `WORLDMAP.RAX` | 3 | Mapa del mundo |
| `STAFFROLL.RAX` | 1 | Créditos |
| `TITLE.RAX` | 1 | Pantalla de título |

---

## 📝 Formato DPK — Archivos de texto

Los `.dpk` son el lugar donde se encontró **texto japonés real y legible**.

### Header común
```
Offset 0x00: 01 00 00 00   → versión
Offset 0x04: 00 00 00 00   → padding
Offset 0x08: XX XX 00 00   → offset donde empieza el bloque de texto
Offset 0x0C: XX XX 00 00   → cantidad de entradas
Offset 0x10: inicio de tabla de punteros
```

### Archivos DPK encontrados

| Archivo | Contenido | Entradas extraídas |
|---------|-----------|-------------------|
| `DBAREAINFO.DPK` | Descripciones de zonas y misiones | **4310 entradas** ✅ |
| `TXTRESJP.DPK` | Textos de menú e interfaz | **307 entradas** ✅ |
| `SHOPTEXT.DPK` | Textos de tienda | por explorar |
| `DBENEMYINFO.DPK` | Datos/nombres de enemigos | por explorar |
| `DBENEMYWAZAINFO.DPK` | Nombres de habilidades/ataques | por explorar |
| `DBSOULTREEINFO.DPK` | Árbol de almas | por explorar |
| `DBSTAGEINFO.DPK` | Info de escenarios | por explorar |
| `DBWORLDMAPINFO.DPK` | Info del mapa mundial | por explorar |
| `DBCLEARCONDITION.DPK` | Condiciones de victoria | por explorar |
| `DBLANDINFO.DPK` | Info de terrenos | por explorar |
| `BUSTUP/RIGHTNAME.DPK` | Nombres de personajes | por explorar |
| `SHOP/ITEM_TABLE.DPK` | Tabla de ítems | por explorar |
| `SHOP/BARGAIN_TABLE.DPK` | Tabla de ofertas | por explorar |

### Encoding
- Texto en **Shift-JIS** (2 bytes por carácter japonés)
- Separador entre strings: byte `0x00`
- Entradas "vacías" o placeholder usan el string `無効`

### Script de extracción
Ver `scripts/extract_dpk.py`

---

## 🔤 Estado de los textos de diálogo

El juego usa un sistema de diálogo estilo **novela visual** — cuadro de texto con retrato de personaje (bustup) y voice acting simultáneo.

| Tipo de texto | Ubicación encontrada | Estado |
|---------------|---------------------|--------|
| Descripciones de misiones | `DBAREAINFO.DPK` | ✅ Extraído |
| Textos de menú/UI | `TXTRESJP.DPK` | ✅ Extraído |
| Textos de tienda | `SHOPTEXT.DPK` | por explorar |
| Nombres de enemigos | `DBENEMYINFO.DPK` | por explorar |
| **Diálogos de escenas** | **desconocido** | ❓ No encontrado aún |

### Hipótesis sobre los diálogos
Los diálogos de las escenas principales (con bustup) no fueron encontrados en ningún archivo de `st.cvm`. Las posibilidades son:
- Están en `voice.cvm` como archivos de subtítulos junto a los `.ahx`
- Están dentro de los PACK comprimidos con algoritmo propio de Media.Vision
- Están en el ejecutable `SLPM_666.71` en una sección no analizada

---

## 🔧 Formato BRA

Los `.bra` son archivos de índice/tabla con header propio de Media.Vision.

### Magic bytes
```
Offset 0x00: 49 4E 41 42 = "INAB"
Offset 0x0C: 4C 41 50 42 = "LAPB"
```
No contienen texto del juego — son tablas de referencias a otros recursos.

---

## 🛠 Herramientas utilizadas

| Herramienta | Uso |
|-------------|-----|
| QuickBMS | Extracción de archivos .cvm |
| WinHex | Análisis hexadecimal |
| CrystalTile2 | Visualización de texturas y texto Shift-JIS |
| Python 3 + struct | Scripts de extracción y análisis |

---

## ✅ TODO

- [ ] Explorar `voice.cvm`
- [ ] Explorar DPKs restantes (SHOPTEXT, DBENEMYINFO, etc.)
- [ ] Encontrar ubicación de los diálogos de escenas
- [ ] Entender formato INAB/LAPB completamente
- [ ] Script de reinserción de texto traducido
- [ ] Analizar `SSS_PAC_001–144.RAX`

---

## 📌 Notas

- El ejecutable `SLPM_666.71` es un ELF estándar de PS2. Solo contiene 5 strings en japonés, todos mensajes de debug del engine.
- Los archivos `PACK###.RAX` contienen las voces de cada escena embebidas directamente (formato `ahx/snd_bvo_kiriya##_###.ahx`).
- Todos los `.rax` analizados individualmente muestran datos binarios que el encoding Shift-JIS interpreta como kanji falsos — no son texto real.
