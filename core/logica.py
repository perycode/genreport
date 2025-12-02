import subprocess
import os


class Logica:
    def unir_pdfs(self, archivos, salida):
        # Rutas deben ser STR (no objetos GTK)
        if not all(isinstance(a, str) for a in archivos):
            print("[ERROR] Lista de archivos contiene elementos no-str:", archivos)
            return False

        # Construir ruta absoluta del script
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts", "unir_pdfs.sh"))

        # Verificar existencia
        if not os.path.isfile(script_path):
            print("[ERROR] No se encuentra el script:", script_path)
            return False

        comando = [script_path, salida] + archivos
        print("Ejecutando:", comando)

        try:
            subprocess.run(comando, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print("[ERROR] Falló pdfunite:", e)
            return False
        except Exception as e:
            print("[ERROR] Excepción al ejecutar:", e)
            return False
