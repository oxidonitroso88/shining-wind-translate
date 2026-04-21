import os, re

ruta = "."
os.makedirs("dialogos_extraidos", exist_ok=True)

patron = re.compile(rb'([A-Z]\d\d-\d\d\d)')

for nombre in sorted(os.listdir(ruta)):
    if not nombre.startswith("PAC_TOWN") or not nombre.endswith(".RAX"):
        continue

    with open(os.path.join(ruta, nombre), "rb") as f:
        data = f.read()

    # Encontrar todos los IDs y sus posiciones
    matches = list(patron.finditer(data))
    if not matches:
        print(f"  Sin script: {nombre}")
        continue

    entradas = []
    for idx, m in enumerate(matches):
        aid = m.group(0).decode('ascii')
        
        # El texto empieza justo después del ID
        texto_inicio = m.end()
        
        # El texto termina donde empieza el siguiente ID (o 200 bytes después)
        if idx + 1 < len(matches):
            texto_fin = matches[idx+1].start()
        else:
            texto_fin = texto_inicio + 200
        
        bloque = data[texto_inicio:texto_fin]
        
        # Decodificar
        try:
            txt = bloque.decode('shift-jis', errors='replace')
        except:
            continue
        
        # Limpiar — quedarse solo con texto japonés/ASCII legible
        txt = txt.strip('\x00').strip()
        
        # Filtrar líneas con basura binaria
        lineas_ok = []
        for linea in txt.split('\n'):
            linea = linea.strip('\x00\r').strip()
            # Contar caracteres raros
            raros = sum(1 for c in linea if ord(c) < 0x20 or 0x80 <= ord(c) <= 0x9F)
            if raros > 2:
                break
            if linea:
                lineas_ok.append(linea)
        
        texto_final = '\n'.join(lineas_ok).strip()
        
        # Solo guardar si tiene texto japonés real
        tiene_japones = any('\u3000' <= c <= '\u9fff' or 
                           '\u3040' <= c <= '\u30ff' for c in texto_final)
        if tiene_japones:
            entradas.append((aid, texto_final))

    salida = nombre.replace('.RAX', '.txt')
    with open(f"dialogos_extraidos/{salida}", "w", encoding="utf-8") as out:
        for aid, dialogo in entradas:
            out.write(f"[{aid}]\n")
            out.write(f"JP: {dialogo}\n")
            out.write(f"ES: \n")
            out.write("-"*40 + "\n")

    print(f"✓ {nombre} → {len(entradas)} líneas")

print("\n¡Listo!")
