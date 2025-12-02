
#!/bin/bash
# Uso: unir_y_generar.sh "TITULO" "CODIGO" plantilla.tex salida_dir pdf1.pdf [pdf2.pdf ...]
# Genera un PDF final compilando una plantilla LaTeX que inserta la unión de los PDFs.
# Compila directamente en 'salida_dir' y borra los archivos auxiliares de LaTeX si todo va bien.

set -euo pipefail

# Comprobar parámetros mínimos
if [ "$#" -lt 5 ]; then
    echo "Uso: $0 \"TITULO\" \"CODIGO\" plantilla.tex salida_dir pdf1.pdf [pdf2.pdf ...]" >&2
    exit 1
fi

# Parámetros
TITULO="$1"
CODIGO="$2"
PLANTILLA="$3"
SALIDA_DIR="$4"
shift 4
PDFS=("$@")

# Comprobar dependencias
command -v pdfunite >/dev/null 2>&1 || { echo "Error: falta 'pdfunite' (instala poppler-utils)." >&2; exit 1; }
command -v pdflatex >/dev/null 2>&1 || { echo "Error: falta 'pdflatex' (instala texlive)." >&2; exit 1; }

# Comprobar que la plantilla existe
if [ ! -f "$PLANTILLA" ]; then
    echo "Error: No se encuentra la plantilla '$PLANTILLA'" >&2
    exit 1
fi

# Comprobar que hay PDFs
if [ "${#PDFS[@]}" -eq 0 ]; then
    echo "Error: Debes indicar al menos un PDF" >&2
    exit 1
fi

# Crear directorio de salida si no existe
if [ ! -d "$SALIDA_DIR" ]; then
    echo "Creando directorio de salida: $SALIDA_DIR"
    mkdir -p "$SALIDA_DIR"
fi

# Generar nombre seguro
# Nota: eliminamos tildes comunes y comas para nombres de archivo; puedes ampliar según tus necesidades.
SAFE_NAME=$(echo "$CODIGO-$TITULO" | tr ' ' '_' | tr -d 'áéíóúÁÉÍÓÚñÑ,')
TEXFILE="${SAFE_NAME}.tex"                        # Se genera en el directorio actual
FINALPDF="${SAFE_NAME}.pdf"                       # Nombre del PDF
FINALPDF_PATH="${SALIDA_DIR}/${FINALPDF}"         # PDF en el directorio de salida
MERGEDPDF="${SAFE_NAME}_merged.pdf"               # PDF unido temporal (en directorio actual)

# Unir PDFs con pdfunite
echo "Uniendo PDFs en $MERGEDPDF..."
pdfunite "${PDFS[@]}" "$MERGEDPDF"

# Sustituir marcadores en la plantilla
echo "Generando archivo LaTeX $TEXFILE..."
# Escapar '&' para sed (evita que se interprete como backreference en el reemplazo)
esc() { printf '%s' "$1" | sed 's/[&]/\\&/g'; }
SED_TITULO=$(esc "$TITULO")
SED_CODIGO=$(esc "$CODIGO")
SED_MERGED=$(esc "$MERGEDPDF")

# Usamos '|' como delimitador para evitar conflicto con '/'
sed "s|@@TITULO@@|${SED_TITULO}|g; s|@@PDF@@|${SED_MERGED}|g; s|@@CODIGO@@|${SED_CODIGO}|g" "$PLANTILLA" > "$TEXFILE"

# Compilar LaTeX directamente en el directorio de salida (dos pasadas)
echo "Compilando PDF final en: $SALIDA_DIR"
pdflatex -output-directory "$SALIDA_DIR" -interaction=nonstopmode "$TEXFILE" || { echo "Error en primera compilación"; exit 1; }
pdflatex -output-directory "$SALIDA_DIR" -interaction=nonstopmode "$TEXFILE" || { echo "Error en primera compilación"; exit 1; }

# Verificar que el PDF final existe
if [ ! -f "$FINALPDF_PATH" ]; then
    echo "Error: No se generó el PDF final en '$FINALPDF_PATH'." >&2
    # No limpiamos para permitir depuración
    exit 1
fi

# Limpieza de archivos auxiliares
echo "Limpiando archivos auxiliares..."
# Auxiliares generados en SALIDA_DIR
rm -f \
  "${SALIDA_DIR}/${SAFE_NAME}.aux" \
  "${SALIDA_DIR}/${SAFE_NAME}.log" \
  "${SALIDA_DIR}/${SAFE_NAME}.toc" \
  "${SALIDA_DIR}/${SAFE_NAME}.out" \
  "${SALIDA_DIR}/${SAFE_NAME}.lof" \
  "${SALIDA_DIR}/${SAFE_NAME}.lot" \
  "${SALIDA_DIR}/${SAFE_NAME}.fls" \
  "${SALIDA_DIR}/${SAFE_NAME}.fdb_latexmk" \
  "${SALIDA_DIR}/${SAFE_NAME}.synctex.gz"

# Temporales generados en el directorio actual
rm -f "$MERGEDPDF" "$TEXFILE"

echo "PDF final generado: $FINALPDF_PATH"

# #!/bin/bash
# # Uso: unir_y_generar.sh "TITULO" "CODIGO" plantilla.tex salida_dir pdf1.pdf [pdf2.pdf ...]
# # Genera un PDF final compilando una plantilla LaTeX que inserta la unión de los PDFs.
# # Guarda el PDF final en 'salida_dir' y borra los archivos auxiliares de LaTeX si todo va bien.

# set -euo pipefail

# # Comprobar parámetros mínimos
# if [ "$#" -lt 5 ]; then
#     echo "Uso: $0 \"TITULO\" \"CODIGO\" plantilla.tex salida_dir pdf1.pdf [pdf2.pdf ...]" >&2
#     exit 1
# fi

# # Parámetros
# TITULO="$1"
# CODIGO="$2"
# PLANTILLA="$3"
# SALIDA_DIR="$4"
# shift 4
# PDFS=("$@")

# # Comprobar que la plantilla existe
# if [ ! -f "$PLANTILLA" ]; then
#     echo "Error: No se encuentra la plantilla '$PLANTILLA'" >&2
#     exit 1
# fi

# # Comprobar que hay PDFs
# if [ "${#PDFS[@]}" -eq 0 ]; then
#     echo "Error: Debes indicar al menos un PDF" >&2
#     exit 1
# fi

# # Crear directorio de salida si no existe
# if [ ! -d "$SALIDA_DIR" ]; then
#     echo "Creando directorio de salida: $SALIDA_DIR"
#     mkdir -p "$SALIDA_DIR"
# fi

# # Generar nombre seguro
# SAFE_NAME=$(echo "$CODIGO-$TITULO" | tr ' ' '_' | tr -d 'áéíóúÁÉÍÓÚñÑ,')
# TEXFILE="${SAFE_NAME}.tex"
# FINALPDF_LOCAL="${SAFE_NAME}.pdf"        # Se compila en el directorio actual
# FINALPDF_DEST="${SALIDA_DIR}/${SAFE_NAME}.pdf"  # Destino final
# MERGEDPDF="${SAFE_NAME}_merged.pdf"

# # (Opcional) Preparar limpieza en caso de error
# # cleanup_on_error() { rm -f "$MERGEDPDF" "$TEXFILE"; }
# # trap cleanup_on_error ERR

# # Unir PDFs con pdfunite
# echo "Uniendo PDFs en $MERGEDPDF..."
# pdfunite "${PDFS[@]}" "$MERGEDPDF"

# # Sustituir marcadores en la plantilla
# echo "Generando archivo LaTeX $TEXFILE..."
# # Ojo con caracteres especiales en sed; si TITULO o CODIGO incluyen '/', podría ser necesario escapar.
# # Para robustez, usamos delimitador distinto y escapamos '&'
# esc() { printf '%s' "$1" | sed 's/[&]/\\&/g'; }
# SED_TITULO=$(esc "$TITULO")
# SED_CODIGO=$(esc "$CODIGO")
# SED_MERGED=$(esc "$MERGEDPDF")

# sed "s|@@TITULO@@|${SED_TITULO}|g; s|@@PDF@@|${SED_MERGED}|g; s|@@CODIGO@@|${SED_CODIGO}|g" "$PLANTILLA" > "$TEXFILE"

# # Compilar LaTeX dos veces
# echo "Compilando PDF final..."
# pdflatex -interaction=nonstopmode "$TEXFILE"|| { echo "Error en primera compilación"; exit 1; }
# echo "Compilando PDF de nuevo para incluir referencias..."
# pdflatex -interaction=nonstopmode "$TEXFILE" || { echo "Error en segunda compilación"; exit 1; }

# # Mover PDF final al directorio de salida
# echo "Moviendo PDF final a: $FINALPDF_DEST"
# mv -f "$FINALPDF_LOCAL" "$FINALPDF_DEST"

# # Borrar archivos auxiliares de LaTeX si todo ha ido bien
# echo "Limpiando archivos auxiliares..."
# rm -f \
#   "${SAFE_NAME}.aux" \
#   "${SAFE_NAME}.log" \
#   "${SAFE_NAME}.toc" \
#   "${SAFE_NAME}.out" \
#   "${SAFE_NAME}.lof" \
#   "${SAFE_NAME}.lot" \
#   "${SAFE_NAME}.fls" \
#   "${SAFE_NAME}.fdb_latexmk" \
#   "${SAFE_NAME}.synctex.gz" \
#   "$MERGEDPDF" \
#   "$TEXFILE"

# echo "PDF final generado: $FINALPDF_DEST"
