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
└── voice.cvm          → Contenedor de voces (solo .ADX)
```

---

## 🗂 Formato CVM

Los archivos `.cvm` son contenedores tipo ISO que se pueden montar o extraer con QuickBMS.

- `st.cvm` — contiene todos los recursos del juego
- `voice.cvm` — contiene únicamente archivos de voz `.ADX` organizados en carpetas

---

## 📁 Contenido de voice.cvm

Solo contiene archivos `.ADX` organizados en carpetas con la siguiente nomenclatura:

| Carpeta | Contenido probable |
|---------|-------------------|
| `E01–E11` | Voces de eventos principales (escenas de historia) |
| `H01–H11` | Voces de escenas de heroínas |
| `M00–M16` | Voces de escenas del arco principal |
| `S00–S14` | Voces de sub-escenas y personajes secundarios |

Cada carpeta contiene entre 10 y 80+ archivos `.ADX` numerados secuencialmente. Por ejemplo `E01` tiene 82 archivos (`E01_000.ADX` a `E01_081.ADX`), uno por cada línea de diálogo hablado de esa escena.

**Importante:** el texto de los subtítulos correspondientes a estas voces NO está en voice.cvm — está en los archivos `PAC_TOWN##_01.RAX` dentro de st.cvm (ver sección más abajo).

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
| `PAC_TOWN01–40_01.RAX` | 40 | **Diálogos del juego** ✅ (ver sección PAC_TOWN) |
| `PACK001A–020B.RAX` | ~53 | Escenas principales de historia (modelos + audio) |
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

## 💬 Archivos PAC_TOWN — Diálogos del juego ✅

**Este es el hallazgo principal.** Los diálogos de todas las escenas del juego están embebidos dentro de los archivos `PAC_TOWN##_01.RAX`.

### Descripción
Hay 40 archivos `PAC_TOWN01_01.RAX` a `PAC_TOWN40_01.RAX`. Cada uno contiene el script completo de una o más escenas, con el texto de cada línea de diálogo vinculado al ID del archivo de audio correspondiente en `voice.cvm`.

### Formato del script embebido
El script está en texto plano Shift-JIS dentro del binario RAX. Los desarrolladores confirmaron esto — se encontró la ruta original del código fuente embebida en el archivo:
```
C:/home/sw/data/pack/script/_pac_mev14_03.txt
```
Esto indica que originalmente eran archivos `.txt` que se empaquetaron dentro de los RAX durante la compilación.

### Estructura de cada entrada
```
[ID_AUDIO][TEXTO\n]
```
Ejemplo real extraído:
```
M00-002ここは、どこだ……？
M00-003いつも見る……夢……？
M00-004……鍵を握る者よ
M00-005俺を、呼んでいる……のか？
```

Donde `M00-002` es el nombre del archivo de audio en `voice.cvm/M00/M00-002.ADX` y el texto que sigue es el subtítulo que aparece en pantalla.

### Líneas extraídas por archivo

| Archivo | Líneas | Archivo | Líneas |
|---------|--------|---------|--------|
| PAC_TOWN01 | 733 | PAC_TOWN21 | 32 |
| PAC_TOWN02 | 250 | PAC_TOWN22 | 64 |
| PAC_TOWN03 | 110 | PAC_TOWN23 | 11 |
| PAC_TOWN04 | 33 | PAC_TOWN24 | 11 |
| PAC_TOWN05 | 32 | PAC_TOWN25 | 84 |
| PAC_TOWN06 | 176 | PAC_TOWN26 | 20 |
| PAC_TOWN07 | 281 | PAC_TOWN27 | 11 |
| PAC_TOWN08 | **1931** | PAC_TOWN28 | 11 |
| PAC_TOWN09 | 65 | PAC_TOWN29 | 16 |
| PAC_TOWN10 | 53 | PAC_TOWN30 | **1861** |
| PAC_TOWN11 | **1905** | PAC_TOWN31 | 11 |
| PAC_TOWN12 | 60 | PAC_TOWN32 | 55 |
| PAC_TOWN13 | 388 | PAC_TOWN33 | 27 |
| PAC_TOWN14 | 33 | PAC_TOWN34 | 11 |
| PAC_TOWN15 | 71 | PAC_TOWN35 | 12 |
| PAC_TOWN16 | 141 | PAC_TOWN36 | 11 |
| PAC_TOWN17 | **2038** | PAC_TOWN37 | 12 |
| PAC_TOWN18 | 22 | PAC_TOWN38 | 36 |
| PAC_TOWN19 | 16 | PAC_TOWN39 | 11 |
| PAC_TOWN20 | 11 | PAC_TOWN40 | **1861** |

### Script de extracción
Ver `scripts/extract_pac_town.py`

---

## 📝 Formato DPK — Archivos de texto

Los `.dpk` contienen **texto japonés real y legible** para menús, UI y datos del juego.

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
- Entradas vacías o placeholder usan el string `無効`

### Script de extracción
Ver `scripts/extract_dpk.py`

---

## 🔤 Estado de los textos

El juego usa un sistema de diálogo estilo **novela visual** — cuadro de texto con retrato de personaje (bustup) y voice acting simultáneo. El audio empieza al mismo tiempo que aparece el texto en pantalla.

| Tipo de texto | Ubicación | Estado |
|---------------|-----------|--------|
| Descripciones de misiones | `DBAREAINFO.DPK` | ✅ Extraído |
| Textos de menú/UI | `TXTRESJP.DPK` | ✅ Extraído |
| **Diálogos de escenas** | **`PAC_TOWN##_01.RAX`** | ✅ **Extraído** |
| Textos de tienda | `SHOPTEXT.DPK` | por explorar |
| Nombres de enemigos | `DBENEMYINFO.DPK` | por explorar |

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

- [x] Explorar `voice.cvm`
- [x] Encontrar ubicación de los diálogos de escenas
- [x] Extraer diálogos de `PAC_TOWN##_01.RAX`
- [ ] Explorar DPKs restantes (SHOPTEXT, DBENEMYINFO, etc.)
- [ ] Entender formato INAB/LAPB completamente
- [ ] Script de reinserción de texto traducido
- [ ] Analizar `SSS_PAC_001–144.RAX`
- [ ] Verificar si hay diálogos en otros grupos RAX (OI_PAC, PAC_CHAOS, etc.)

---

## 📌 Notas

- El ejecutable `SLPM_666.71` es un ELF estándar de PS2. Solo contiene 5 strings en japonés, todos mensajes de debug del engine.
- Los archivos `PACK###.RAX` contienen las voces de cada escena embebidas directamente (formato `ahx/snd_bvo_kiriya##_###.ahx`), pero los subtítulos están en `PAC_TOWN##_01.RAX`.
- Los archivos `PAC_TOWN` contienen múltiples scripts embebidos — un mismo RAX puede tener diálogos de varias escenas distintas.
- El patrón de IDs de audio (`M00-002`, `E01-015`, etc.) conecta directamente cada línea de texto con su archivo de voz en `voice.cvm`.
- Se encontró ruta del código fuente original del desarrollador embebida: `C:/home/sw/data/pack/script/`
