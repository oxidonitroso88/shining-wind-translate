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

Cada carpeta contiene entre 10 y 80+ archivos `.ADX` numerados secuencialmente.

**Observación importante:** La carpeta `S00` solo contiene 4 archivos: `S00_009`, `S00_054`, `S00_055`, `S00_056`. Los IDs S00-001 a S00-008 no existen en voice.cvm — esas voces no fueron grabadas o se almacenan en otro formato.

**Importante:** el texto de los subtítulos correspondientes a estas voces NO está en voice.cvm — está en los archivos `PAC_TOWN##_01.RAX` dentro de st.cvm.

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
| `TDMV` | Bloques de diálogo especiales (ver sección TDMV) |
| `DCMV` | Bloques de cutscene/canvas |
| `DPK\x00` | Bases de datos embebidas |
| `LZSS` | Datos comprimidos con algoritmo LZSS |

### Grupos de archivos RAX

| Grupo | Cantidad aprox. | Contenido |
|-------|-----------------|-----------|
| `PAC_TOWN01–40_01.RAX` | 40 | Diálogos del juego ✅ |
| `PAC_MAIN##_##.RAX` | ~88 | Escenas principales de historia |
| `PAC_ROUTE##_##.RAX` | ~15 | Escenas de rutas |
| `PAC_EVMAP##_01.RAX` | ~9 | Escenas de mapa de eventos |
| `PAC_CHAOS##_01.RAX` | 10 | Escenas modo Chaos |
| `PAC_MIND_[NOMBRE]##.RAX` | ~55 | Escenas del mundo interior (Mind World) de cada personaje |
| `PAC_MEV##_##.RAX` | ~120 | Eventos del mapa (Map Events) |
| `PAC_BEV##_##.RAX` | 8 | Battle events |
| `PAC_FREE##_##.RAX` | ~45 | Batallas libres |
| `PAC_SEV##_##.RAX` | ~40 | Special events |
| `PAC_OEV##_##.RAX` | ~10 | Other events |
| `PAC_SUB##_##.RAX` | 2 | Sub-escenas |
| `PAC_PL_TOWN##_01.RAX` | ~40 | Datos de pueblo (sin diálogos) |
| `PAC_PL_ROUTE##_##.RAX` | ~15 | Datos de ruta (sin diálogos) |
| `BFI_PAC_ENM_FREE##.RAX` | ~100 | Enemigos en batallas libres |
| `BFI_PAC_ENM_MAIN##.RAX` | ~80 | Enemigos en historia principal |
| `SSS_PAC_001–144.RAX` | 144 | Datos de batalla/animación — SIN diálogos ❌ |
| `PAC_BATTLE_TUTORIAL.RAX` | 1 | Tutorial de batalla |
| `TITLE.RAX` | 1 | Pantalla de título — contiene texto de intro comprimido LZSS |
| `SYSTEM.RAX` | 1 | Recursos del sistema (fuentes, iconos, DPKs) |
| `STATUS.RAX` | 1 | Pantalla de estado/stats |
| `STAFFROLL.RAX` | 1 | Créditos |
| `WORLDMAP.RAX` | 3 | Mapa del mundo |

---

## 💬 Archivos PAC_ — Diálogos del juego ✅

**Este es el hallazgo principal.** Los diálogos de todas las escenas del juego están embebidos dentro de los archivos `PAC_TOWN##_01.RAX`, `PAC_MAIN##_##.RAX`, `PAC_ROUTE##_##.RAX`, `PAC_EVMAP##_01.RAX`, y `PAC_MIND_##.RAX`.

### Formato del script embebido — Formato estándar
```
[ID_AUDIO][TEXTO\n]
```
Ejemplo real extraído:
```
M00-002ここは、どこだ……？
```

Donde `M00-002` es el nombre del archivo de audio en `voice.cvm/M00/M00-002.ADX`.

### Formato de los archivos TXT extraídos
```
[ID_AUDIO]
JP: [texto]
[nombre_speaker]
ES: [traducción]
----------------------------------------
```

**Importante:** El speaker siempre aparece en la línea entre `JP:` y `ES:`, nunca dentro del texto. El nombre al final del bloque JP es el personaje que habla esa línea.

### Totales extraídos

| Tipo | Entradas |
|------|----------|
| Diálogos PAC_TOWN | ~10,000+ |
| Diálogos PAC_MAIN | ~3,500+ |
| Diálogos PAC_ROUTE | ~1,500+ |
| Diálogos PAC_EVMAP | ~800+ |
| Diálogos PAC_MIND | ~700+ |
| **Total aproximado** | **~16,631 líneas** |

### Script de extracción
Ver `scripts/extract_pac_town.py`

---

## 🎭 Formato TDMV — Diálogos especiales embebidos

Formato interno del motor para bloques de diálogo embebidos dentro de los RAX. Presente en casi todos los RAX grandes. El extractor estándar NO los captura porque buscaba el patrón `[A-Z]\d\d-\d\d\d` aislado.

### Firma
```
54 44 4D 56 = "TDMV"
```

### Estructura binaria
```
54 44 4D 56 00 01 00 00 XX XX 00 00   → header TDMV (12 bytes)
[speaker en Shift-JIS]\x00            → nombre del hablante + null
[ID en ASCII]\x00                     → ej: "M16-037\x00"
[línea1 en Shift-JIS]\x0A\x00        → texto + newline + null
[línea2 en Shift-JIS]\x0A\x00        → (opcional, segunda línea)
[siguiente speaker]\x00              → cuando cambia el hablante
```

### Ejemplo real (texto de la intro)
```
(TDMV0ラッシィ\x00M16-037\x00ふぅ〜\x0A\x00M16-038\x00ふっふふぅ\x0A\x00久遠の森の詠み手\x00M16-039\x00あら、お客様？\x0A\x00久遠の森にようこそ\x0A\x00
```

### Casos de uso conocidos
- Texto de la pantalla de título/intro (`TITLE.RAX`)
- Mensajes de sistema (guardar, cargar, volver al título)
- Diálogos de batalla con formato diferente

**Pendiente:** Escribir extractor general de bloques TDMV para todos los RAX.

---

## 🎬 Texto de la intro — ラッシィ y 久遠の森の詠み手

### Ubicación
- Archivo fuente: **TITLE.RAX**, offset `0x0132F0`
- Nombre interno del bloque: `event/cs_canvasation.bss`
- El bloque está comprimido con **LZSS**
- En RAM (PCSX2): dirección `0x00AA0AEF`

### Método de extracción
El texto se extrajo volcando `eeMemory.bin` desde un savestate de PCSX2. El archivo `.p2s` es un ZIP con compresión **Zstandard (method=93)**:

```python
import zstandard as zstd, struct, re

with open("savestate.p2s", "rb") as f:
    zip_data = f.read()

headers = [m.start() for m in re.finditer(b'PK\x03\x04', zip_data)]
for h in headers:
    fname_len  = struct.unpack_from("<H", zip_data, h+26)[0]
    extra_len  = struct.unpack_from("<H", zip_data, h+28)[0]
    comp_size  = struct.unpack_from("<I", zip_data, h+18)[0]
    fname      = zip_data[h+30:h+30+fname_len].decode('utf-8', errors='replace')
    data_start = h + 30 + fname_len + extra_len
    if fname == "eeMemory.bin":
        dctx = zstd.ZstdDecompressor()
        ram = dctx.decompress(zip_data[data_start:data_start+comp_size],
                              max_output_size=64*1024*1024)
```

### Contenido completo

| ID | Speaker | Texto |
|----|---------|-------|
| M16-037 | ラッシィ | ふぅ〜 |
| M16-038 | ラッシィ | ふっふふぅ |
| M16-039 | 久遠の森の詠み手 | あら、お客様？ / 久遠の森にようこそ |
| M16-040 | 久遠の森の詠み手 | こんな森の深くまで / 私が語る物語を聞きにきてくれたのね |
| M16-041 | 久遠の森の詠み手 | 私が語るのは / 心の世界を旅する冒険者たちの物語 |
| M16-042 | 久遠の森の詠み手 | この不思議な物語の結末はひとつとはかぎらない / あなたも、私と一緒に彼らを導いてあげて |
| M16-043 | 久遠の森の詠み手 | 彼らの運命は、あなたにゆだねます / さあ、始めましょう |
| M16-044 | ラッシィ | ふぅ〜う |
| M16-045 | 久遠の森の詠み手 | また物語を聞きにきてくれたのね / さあ、物語の行く末は、あなたの手にゆだねます |
| M16-046 | 久遠の森の詠み手 | さぁ、どこから始めましょうか？ |
| M16-047 | 久遠の森の詠み手 | また物語を聞きにきてくれたのね / さあ、物語の行く末は、あなたの手にゆだねます |

Guardado en `dialogos_extraidos/PAC_INTRO_TITLE.txt`

### Nota sobre reinserción
El formato TDMV usa strings **null-terminated**. Si la traducción es igual o más corta en bytes que el original, se puede reemplazar directamente en el binario rellenando con `\x00` el espacio sobrante. Si es más larga, se necesita recomprimir el bloque LZSS.

**Pendiente:** El descompresor LZSS actual no descifra correctamente este bloque — investigar variante del algoritmo que usa Media Vision.

---

## 🎭 Elenco de personajes — Nombres confirmados

Los nombres oficiales en inglés se confirmaron desde los archivos AHX de voces de batalla (`SND_BVO_[NOMBRE]##_###.AHX`).

| Japonés | Inglés oficial | Rol |
|---------|---------------|-----|
| キリヤ | KIRIYA | Protagonista |
| シーナ | SEENA | Compañera principal |
| クララクラン | CLALA | Compañera principal |
| ホウメイ | HOUMEI | Compañera principal |
| カリス | CARIS | Compañera principal |
| クレハ | KUREHA | Compañera principal |
| ジンクロウ | JINCROW | Compañero principal |
| ゼクティ | XECTY | Compañera principal |
| ロウエン | ROUEN | Compañero principal |
| ゼロ | XERO | Compañero principal |
| ソウマ | SOUMA | Secundario |
| バソウ | BASOU | Secundario |
| コウリュウ | KOURYU | Secundario |
| ライヒ | RAIHI | Secundario |
| ヒルダレイア | HILDAREIA | Secundario |
| トライハルト | TRAIHARD | Secundario |
| ヒョウウン | HYOUUN | Secundario |
| エンウ | ENWU | Secundario |
| キルレイン | KILLRAIN | Antagonista |
| ジード | ZEED | Antagonista |
| ラッシィ | RASSHI | NPC especial |
| 久遠の森の詠み手 | Narradora del bosque eterno | NPC especial |

**Nota sobre el speaker en los diálogos:** El nombre ロウエン en los archivos extraídos aparece escrito como **ロウエン** (no ローエン como se podría esperar).

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

| Archivo | Ubicación | Entradas | Estado |
|---------|-----------|----------|--------|
| `DBAREAINFO.DPK` | ENEMYINFO/ | 4310 | ✅ Extraído |
| `TXTRESJP.DPK` | raíz ST/ | 307 | ✅ Extraído |
| `SHOPTEXT.DPK` | SHOP/ | 394 | ✅ Extraído |
| `DBENEMYINFO.DPK` | ENEMYINFO/ | 848 | ✅ Extraído |
| `DBENEMYWAZAINFO.DPK` | ENEMYINFO/ | ~100 | ✅ Extraído |
| `DBSTAGEINFO.DPK` | ENEMYINFO/ | ~200 | ✅ Extraído |
| `DBWORLDMAPINFO.DPK` | ENEMYINFO/ | ~50 | ✅ Extraído |
| `DBCLEARCONDITION.DPK` | ENEMYINFO/ | ~80 | ✅ Extraído |
| `DBLANDINFO.DPK` | ENEMYINFO/ | ~40 | ✅ Extraído |
| `DBSOULTREEINFO.DPK` | ENEMYINFO/ | 0 | ⚠️ Formato diferente |
| `BUSTUP/RIGHTNAME.DPK` | BUSTUP/ | 77 | ⚠️ Solo nombres de archivos de texturas, no texto del juego |
| `BUSTUP/BUSTUP.DPK` | BUSTUP/ | — | Sin explorar |
| `SHOP/ITEM_TABLE.DPK` | SHOP/ | — | Sin explorar |
| `SHOP/BARGAIN_TABLE.DPK` | SHOP/ | — | Sin explorar |

### Nota sobre RIGHTNAME.DPK
Contiene 77 entradas con nombres de archivos de texturas de bustos en ASCII (ej: `011R_a`, `011R_b`). Es una tabla de referencia interna del motor para cargar los retratos de personajes. **No es texto traducible.**

### Nota sobre DBSOULTREEINFO.DPK
Tiene una estructura diferente al formato DPK estándar. El extractor genérico devuelve 0 entradas. Pendiente investigar formato específico.

### Encoding
- Texto en **Shift-JIS** (2 bytes por carácter japonés)
- Separador entre strings: byte `0x00`
- Entradas vacías o placeholder usan el string `無効`

### Códigos de control en TXTRESJP.DPK
Los textos de menú/UI contienen caracteres especiales antes del texto visible:
- `♦` — posiblemente indica texto que parpadea
- `°` — cambio de alineación o color
- Letras sueltas pegadas al texto (ej: `wに戻ります`, `Aはじまる絆`) — son códigos de control del motor

Al traducir, conservar estos caracteres tal cual y traducir solo el texto japonés que los sigue.

---

## 🎤 Archivos AHX — Voces de batalla

Los archivos `.AHX` en la carpeta `AHX/` son exclusivamente **voces de batalla** (prefijo `BVO` = Battle VOice). No contienen texto traducible pero confirman los nombres oficiales en inglés de los personajes.

Formato de nombre: `SND_BVO_[NOMBRE]##_###.AHX`

Personajes con voces de batalla: KIRIYA (11 variantes), SEENA, HOUMEI, CARIS, KUREHA (2 variantes), JINCROW, ROUEN, XECTY (2 variantes), XERO, CLALA, SOUMA, BASOU, KOURYU, RAIHI, HYOUUN (2 variantes), HILDAREIA, TRAIHARD, KILLRAIN, ZEED.

**Archivo especial:** `SND_ENV_026M.AHX` — sonido de ambiente, no es voz de personaje.

---

## 🗂 Archivos descartados para traducción

| Archivo | Razón |
|---------|-------|
| `OVL00-OVL10.BIN` | Código MIPS puro, sin texto legible |
| `SSS_PAC_001–144.RAX` | Datos de batalla/animación, sin diálogos |
| `BUSTUP/RIGHTNAME.DPK` | Solo nombres internos de archivos de texturas |
| `SYSTEM.RAX` | Contenedor de recursos del sistema, sin texto japonés traducible |

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
| WinHex / WindHex | Análisis hexadecimal |
| CrystalTile2 | Visualización de texturas y texto Shift-JIS |
| Python 3 + struct | Scripts de extracción y análisis |
| PCSX2 (debugger) | Análisis de memoria en tiempo de ejecución |
| zstandard (Python) | Descompresión de savestates PCSX2 (.p2s) |

---

## 📊 Resumen total de texto extraído

| Tipo | Entradas |
|------|----------|
| Diálogos PAC_ (todos los grupos) | ~16,631 |
| Misiones/zonas (DBAREAINFO) | 4,310 |
| Menú/UI (TXTRESJP) | 307 |
| Enemigos (DBENEMYINFO) | 848 |
| Tienda (SHOPTEXT) | 394 |
| Intro/título (PAC_INTRO_TITLE) | 11 |
| Otros DPK menores | ~500 |
| **TOTAL APROXIMADO** | **~23,000 entradas** |

---

## ✅ TODO

- [x] Explorar `voice.cvm`
- [x] Encontrar ubicación de los diálogos de escenas
- [x] Extraer diálogos de `PAC_TOWN##_01.RAX` y otros PAC_
- [x] Extraer DPKs principales (DBAREAINFO, TXTRESJP, SHOPTEXT, DBENEMYINFO)
- [x] Confirmar nombres oficiales de personajes desde AHX
- [x] Extraer texto de la intro (TITLE.RAX / TDMV) via savestate PCSX2
- [x] Descartar archivos sin texto traducible (OVL, SSS_PAC, RIGHTNAME)
- [ ] Escribir extractor general de bloques TDMV para todos los RAX
- [ ] Investigar variante LZSS de Media Vision para descomprimir TITLE.RAX
- [ ] Script de reinserción de texto en archivos RAX
- [ ] Explorar DBSOULTREEINFO.DPK (formato diferente al estándar)
- [ ] Traducir TXTRESJP.DPK (307 entradas de menú/UI)
- [ ] Analizar STATUS.RAX (posibles nombres de stats/parámetros)
- [ ] Investigar PAC_MEV, PAC_SEV, PAC_OEV para diálogos adicionales

---

## 📌 Notas

- El ejecutable `SLPM_666.71` es un ELF estándar de PS2. Solo contiene 5 strings en japonés, todos mensajes de debug del engine.
- Los archivos PAC_ contienen múltiples scripts embebidos — un mismo RAX puede tener diálogos de varias escenas distintas.
- El patrón de IDs de audio (`M00-002`, `E01-015`, etc.) conecta directamente cada línea de texto con su archivo de voz en `voice.cvm`.
- Se encontró ruta del código fuente original del desarrollador embebida: `C:/home/sw/data/pack/script/`
- El texto de la intro (`久遠の森の詠み手`) está comprimido dentro de TITLE.RAX — no es texto plano buscable en disco.
- Los savestates de PCSX2 v2.x usan compresión Zstandard (method=93), no zlib estándar. Requiere la librería `zstandard` de Python.
- El formato TDMV usa strings null-terminated — la reinserción directa es posible si la traducción no supera el tamaño original en bytes.
