import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import os
import subprocess
import shutil
from urllib.parse import urlparse, unquote

class Ventana:
    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file("ui/ventana.glade")
        builder.connect_signals(self)

        self.window = builder.get_object("main_window")
        self.list_box = builder.get_object("list_box_pdfs")
        self.scroll_area = builder.get_object("scroll_area")
        self.entry_codigo = builder.get_object("entry_codigo")
        self.entry_titulo = builder.get_object("entry_titulo")

        self.pdfs_arrastrados = []

        self.window.connect("destroy", Gtk.main_quit)

        target = Gtk.TargetEntry.new("text/uri-list", 0, 0)
        self.scroll_area.drag_dest_set(Gtk.DestDefaults.ALL, [target], Gdk.DragAction.COPY)
        self.scroll_area.connect("drag-data-received", self.on_drag_data_received)

        self.window.show_all()

    def on_btn_guardar_clicked(self, button):
        if not self.pdfs_arrastrados:
            self._info("No hay PDFs arrastrados para unir.")
            return

        if shutil.which("pdfunite") is None or shutil.which("pdflatex") is None:
            self._error("Faltan dependencias: instala 'poppler-utils' y 'texlive'.")
            return

        dialog = Gtk.FileChooserDialog(
            title="Selecciona carpeta de destino",
            parent=self.window,
            action=Gtk.FileChooserAction.SELECT_FOLDER
        )
        dialog.set_modal(False)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                           Gtk.STOCK_OK, Gtk.ResponseType.OK)

        dialog.connect("response", self._on_dialog_response)
        dialog.show()

    def _on_dialog_response(self, dialog, response):
        if response == Gtk.ResponseType.OK:
            salida_path = dialog.get_filename()
            dialog.destroy()

            salida_dir = salida_path  # directorio de salida
            plantilla = os.path.join("templates", "Plantilla_Informe.tex")

            codigo = self.entry_codigo.get_text().strip()
            titulo = self.entry_titulo.get_text().strip()

            if not codigo or not titulo:
                self._error("Debes introducir Código y Título antes de guardar.")
                return

            try:
                # Añadimos salida_dir como cuarto parámetro
                cmd = ["bash", os.path.join("scripts", "unir_y_generar.sh"),
                       titulo, codigo, plantilla, salida_dir] + self.pdfs_arrastrados
                print("Ejecutando:", cmd)
                subprocess.run(cmd, check=True)

                # Ya no movemos el PDF, el script lo guarda en salida_dir
                self._info(f"PDF final generado en:\n{salida_dir}")
                self._clear_pdfs()
            except subprocess.CalledProcessError as e:
                self._error(f"Error al generar informe:\n{e}")
        else:
            dialog.destroy()

    def on_btn_limpiar_clicked(self, button):
        self._clear_pdfs()

    def _clear_pdfs(self):
        self.pdfs_arrastrados.clear()
        for row in self.list_box.get_children():
            self.list_box.remove(row)

    def on_drag_data_received(self, widget, drag_context, x, y, data, info, time):
        uris = data.get_uris()
        for uri in uris:
            path = self._ruta_desde_uri(uri)
            if path and path.lower().endswith(".pdf") and os.path.exists(path):
                if path not in self.pdfs_arrastrados:
                    self.pdfs_arrastrados.append(path)
                    self._agregar_fila(path)
        self.list_box.show_all()

    def _agregar_fila(self, path):
        row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        label = Gtk.Label(label=os.path.basename(path), xalign=0)
        label.set_tooltip_text(path)

        btn_del = Gtk.Button(label="Eliminar")
        btn_del.connect("clicked", self._eliminar_fila, row, path)

        hbox.pack_start(label, True, True, 0)
        hbox.pack_start(btn_del, False, False, 0)
        row.add(hbox)
        self.list_box.add(row)

    def _eliminar_fila(self, button, row, path):
        self.list_box.remove(row)
        if path in self.pdfs_arrastrados:
            self.pdfs_arrastrados.remove(path)

    def _ruta_desde_uri(self, uri):
        try:
            parsed = urlparse(uri)
            if parsed.scheme == 'file':
                return unquote(parsed.path)
            return unquote(uri)
        except Exception:
            return None

    def _info(self, texto):
        md = Gtk.MessageDialog(transient_for=self.window, flags=0,
                               message_type=Gtk.MessageType.INFO,
                               buttons=Gtk.ButtonsType.OK, text=texto)
        md.run(); md.destroy()

    def _error(self, texto):
        md = Gtk.MessageDialog(transient_for=self.window, flags=0,
                               message_type=Gtk.MessageType.ERROR,
                               buttons=Gtk.ButtonsType.OK, text=texto)
        md.run(); md.destroy()

    def _confirmar(self, texto):
        md = Gtk.MessageDialog(transient_for=self.window, flags=0,
                               message_type=Gtk.MessageType.QUESTION,
                               buttons=Gtk.ButtonsType.OK_CANCEL, text=texto)
        resp = md.run(); md.destroy()
        return resp == Gtk.ResponseType.OK


# import gi
# gi.require_version('Gtk', '3.0')
# from gi.repository import Gtk, Gdk
# import os
# import subprocess
# import shutil
# from urllib.parse import urlparse, unquote

# class Ventana:
#     def __init__(self):
#         builder = Gtk.Builder()
#         builder.add_from_file("ui/ventana.glade")
#         builder.connect_signals(self)

#         self.window = builder.get_object("main_window")
#         self.list_box = builder.get_object("list_box_pdfs")
#         self.scroll_area = builder.get_object("scroll_area")

#         self.pdfs_arrastrados = []

#         # Cerrar correctamente al pulsar la X
#         self.window.connect("destroy", Gtk.main_quit)

#         # Configurar DnD externo (arrastrar PDFs desde explorador)
#         target = Gtk.TargetEntry.new("text/uri-list", 0, 0)
#         self.scroll_area.drag_dest_set(Gtk.DestDefaults.ALL, [target], Gdk.DragAction.COPY)
#         self.scroll_area.connect("drag-data-received", self.on_drag_data_received)

#         self.window.show_all()

#     # ----------------- Botón Guardar -----------------
#     def on_btn_guardar_clicked(self, button):
#         if not self.pdfs_arrastrados:
#             self._info("No hay PDFs arrastrados para unir.")
#             return

#         if shutil.which("pdfunite") is None:
#             self._error("No se encontró 'pdfunite'. Instala 'poppler-utils'.")
#             return

#         dialog = Gtk.FileChooserDialog(
#             title="Guardar PDF unido",
#             parent=self.window,
#             action=Gtk.FileChooserAction.SAVE
#         )
#         dialog.set_modal(False)  # No bloquear la ventana principal
#         dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
#                            Gtk.STOCK_SAVE, Gtk.ResponseType.OK)

#         filtro_pdf = Gtk.FileFilter()
#         filtro_pdf.set_name("Documentos PDF")
#         filtro_pdf.add_pattern("*.pdf")
#         dialog.add_filter(filtro_pdf)
#         dialog.set_current_name("resultado.pdf")

#         # Conectar señal response en lugar de usar run()
#         dialog.connect("response", self._on_dialog_response)
#         dialog.show()

#     def _on_dialog_response(self, dialog, response):
#         if response == Gtk.ResponseType.OK:
#             salida_path = dialog.get_filename()
#             if not salida_path.lower().endswith(".pdf"):
#                 salida_path += ".pdf"

#             if os.path.exists(salida_path):
#                 if not self._confirmar(f"El archivo ya existe:\n{salida_path}\n¿Sobrescribir?"):
#                     dialog.destroy()
#                     return

#             try:
#                 cmd = ["bash", os.path.join("scripts", "unir_pdfs.sh"), salida_path] + self.pdfs_arrastrados
#                 subprocess.run(cmd, check=True)
#                 self._info(f"PDF generado:\n{salida_path}")
#                 self._clear_pdfs()
#             except subprocess.CalledProcessError as e:
#                 self._error(f"Error al unir PDFs:\n{e}")
#         dialog.destroy()

#     # ----------------- Botón Limpiar -----------------
#     def on_btn_limpiar_clicked(self, button):
#         self._clear_pdfs()

#     def _clear_pdfs(self):
#         self.pdfs_arrastrados.clear()
#         for row in self.list_box.get_children():
#             self.list_box.remove(row)

#     # ----------------- Arrastrar PDFs -----------------
#     def on_drag_data_received(self, widget, drag_context, x, y, data, info, time):
#         uris = data.get_uris()
#         for uri in uris:
#             path = self._ruta_desde_uri(uri)
#             if path and path.lower().endswith(".pdf") and os.path.exists(path):
#                 if path not in self.pdfs_arrastrados:
#                     self.pdfs_arrastrados.append(path)
#                     self._agregar_fila(path)
#         self.list_box.show_all()

#     # ----------------- Crear fila con botones -----------------
#     def _agregar_fila(self, path):
#         row = Gtk.ListBoxRow()
#         hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

#         label = Gtk.Label(label=os.path.basename(path), xalign=0)
#         label.set_tooltip_text(path)

#         btn_up = Gtk.Button(label="↑")
#         btn_down = Gtk.Button(label="↓")
#         btn_del = Gtk.Button(label="Eliminar")

#         btn_up.connect("clicked", self._mover_arriba, row)
#         btn_down.connect("clicked", self._mover_abajo, row)
#         btn_del.connect("clicked", self._eliminar_fila, row, path)

#         hbox.pack_start(label, True, True, 0)
#         hbox.pack_start(btn_up, False, False, 0)
#         hbox.pack_start(btn_down, False, False, 0)
#         hbox.pack_start(btn_del, False, False, 0)

#         row.add(hbox)
#         self.list_box.add(row)

#     # ----------------- Acciones de botones -----------------
#     def _mover_arriba(self, button, row):
#         index = row.get_index()
#         if index > 0:
#             self.list_box.remove(row)
#             self.list_box.insert(row, index - 1)
#             self._swap(index, index - 1)

#     def _mover_abajo(self, button, row):
#         index = row.get_index()
#         total = len(self.pdfs_arrastrados)
#         if index < total - 1:
#             self.list_box.remove(row)
#             self.list_box.insert(row, index + 1)
#             self._swap(index, index + 1)

#     def _eliminar_fila(self, button, row, path):
#         self.list_box.remove(row)
#         if path in self.pdfs_arrastrados:
#             self.pdfs_arrastrados.remove(path)

#     def _swap(self, i, j):
#         self.pdfs_arrastrados[i], self.pdfs_arrastrados[j] = self.pdfs_arrastrados[j], self.pdfs_arrastrados[i]

#     # ----------------- Utilidades -----------------
#     def _ruta_desde_uri(self, uri):
#         try:
#             parsed = urlparse(uri)
#             if parsed.scheme == 'file':
#                 return unquote(parsed.path)
#             return unquote(uri)
#         except Exception:
#             return None

#     def _info(self, texto):
#         md = Gtk.MessageDialog(transient_for=self.window, flags=0,
#                                message_type=Gtk.MessageType.INFO,
#                                buttons=Gtk.ButtonsType.OK, text=texto)
#         md.run(); md.destroy()

#     def _error(self, texto):
#         md = Gtk.MessageDialog(transient_for=self.window, flags=0,
#                                message_type=Gtk.MessageType.ERROR,
#                                buttons=Gtk.ButtonsType.OK, text=texto)
#         md.run(); md.destroy()

#     def _confirmar(self, texto):
#         md = Gtk.MessageDialog(transient_for=self.window, flags=0,
#                                message_type=Gtk.MessageType.QUESTION,
#                                buttons=Gtk.ButtonsType.OK_CANCEL, text=texto)
#         resp = md.run(); md.destroy()
#         return resp == Gtk.ResponseType.OK
