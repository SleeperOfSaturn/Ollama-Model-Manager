from io import text_encoding
import json
import gi
import requests

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Ollama Model Manager")
        self.set_default_size(400, 600)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(box)
        row = Gtk.Box(spacing = 20)
        box.pack_start(row, False, True, 0)
        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("Enter the EXACT model name")
        row.pack_start(self.entry, False, True, 0)
        self.pull = Gtk.Button(label="⌲")
        row.pack_start(self.pull, False, False, 0)
        self.pull.connect("clicked", self.pull_model)
        self.combo = Gtk.ComboBoxText()
        self.combo.connect("changed", self.on_model_changed)
        box.pack_start(self.combo, False, False, 0)

        self.button = Gtk.Button(label="Load Models")
        self.button.connect("clicked", self.refresh_combo)
        box.pack_start(self.button, False, False, 0)

        self.delete_button = Gtk.Button(label="Delete Selected")
        self.delete_button.connect("clicked", self.on_delete_clicked)
        box.pack_start(self.delete_button, False, False, 0)

        self.update_delete_state()
    def pull_model(self, widget):
        model = self.entry.get_text()
        if model == "":
            self.pull.set_sensitive(False)
            return
        else:
            self.pull.set_sensitive(True)
            print("Pulling", model)
            print("blehhhh")
    def on_model_changed(self, combo):
        selected = combo.get_active_text()
        print("Selected model:", selected)
        self.update_delete_state()

    def refresh_combo(self, widget):
        try:
            response = requests.get("http://localhost:11434/api/tags")
            data = response.json()
            models = data["models"]

            self.combo.remove_all()

            for model in models:
                self.combo.append_text(model["name"])

            if models:
                self.combo.set_active(0)

        except Exception as e:
            print("Error:", e)

        self.update_delete_state()

    def update_delete_state(self):
        selected = self.combo.get_active_text()
        if selected is None:
            self.delete_button.set_sensitive(False)
        else:
            self.delete_button.set_sensitive(True)

    def on_delete_clicked(self, button):
        selected = self.combo.get_active_text()
        if selected is None:
            return
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"Delete model '{selected}'?"
        )

        dialog.format_secondary_text("This action cannot be undone.")
        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.YES:
            self.perform_delete(selected)

    def perform_delete(self, selected):
        try:
            response = requests.delete("http://localhost:11434/api/delete", json={"name": selected})
            if response.status_code == 200:
                print("Deleted", selected)
                self.refresh_combo(None)
            else:
                print("Deletion Failed", response.text)
        except Exception as e:
            print("Error during deletion:", e)

win = MainWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
