#!/bin/bash
# Uso: unir_pdfs.sh salida.pdf archivo1.pdf archivo2.pdf ...
set -euo pipefail

salida="$1"
shift

if [ "$#" -lt 1 ]; then
  echo "Error: Debes indicar al menos un PDF para unir."
  exit 1
fi

pdfunite "$@" "$salida"
echo "PDF generado en: $salida"
