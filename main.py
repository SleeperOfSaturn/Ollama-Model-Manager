#!/usr/bin/env python3
import json
import gi
import requests
import threading

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib


class OllamaAPI:
    BASE_URL = "http://localhost:11434"

    def list_models(self):
        r = requests.get(f"{self.BASE_URL}/api/tags")
        r.raise_for_status()
        return r.json()["models"]

    def delete_model(self, name):
        r = requests.delete(
            f"{self.BASE_URL}/api/delete",
            json={"name": name}
        )
        r.raise_for_status()

    def pull_model(self, name):
        return requests.post(
            f"{self.BASE_URL}/api/pull",
            json={"name": name},
            stream=True
        )


class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Ollama Model Manager")
        self.set_default_size(420, 640)

        self.api = OllamaAPI()

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        main_box.set_margin_top(20)
        main_box.set_margin_bottom(20)
        main_box.set_margin_start(20)
        main_box.set_margin_end(20)
        self.add(main_box)

        # --- Download Section ---
        download_label = Gtk.Label()
        download_label.set_markup("<b>Download Model</b>")
        download_label.set_xalign(0)
        main_box.pack_start(download_label, False, False, 0)

        pull_row = Gtk.Box(spacing=8)
        main_box.pack_start(pull_row, False, False, 0)

        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("e.g. phi3:mini")
        pull_row.pack_start(self.entry, True, True, 0)

        self.pull = Gtk.Button(label="Pull")
        self.pull.connect("clicked", self.pull_model)
        pull_row.pack_start(self.pull, False, False, 0)

        self.status_label = Gtk.Label(label="Idle")
        self.status_label.set_xalign(0.5)
        main_box.pack_start(self.status_label, False, False, 0)

        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        self.progress_bar.set_fraction(0.0)
        main_box.pack_start(self.progress_bar, False, False, 0)

        # --- Section Divider ---
        divider = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        main_box.pack_start(divider, False, False, 10)

        # --- Installed Models Section ---
        installed_label = Gtk.Label()
        installed_label.set_markup("<b>Installed Models</b>")
        installed_label.set_xalign(0)
        main_box.pack_start(installed_label, False, False, 0)

        self.combo = Gtk.ComboBoxText()
        self.combo.connect("changed", self.on_model_changed)
        main_box.pack_start(self.combo, False, False, 0)

        self.load_button = Gtk.Button(label="Load Installed Models")
        self.load_button.connect("clicked", self.refresh_combo)
        main_box.pack_start(self.load_button, False, False, 0)

        self.delete_button = Gtk.Button(label="Delete Selected")
        self.delete_button.connect("clicked", self.on_delete_clicked)
        main_box.pack_start(self.delete_button, False, False, 0)

        self.update_delete_state()

    def pull_model(self, widget):
        model = self.entry.get_text().strip()
        if not model:
            return

        self.progress_bar.set_fraction(0.0)
        self.progress_bar.set_text("Starting...")
        self.status_label.set_text("Pulling model...")
        self.pull.set_sensitive(False)
        self.entry.set_sensitive(False)

        thread = threading.Thread(
            target=self.perform_pull,
            args=(model,),
            daemon=True
        )
        thread.start()

    def update_status(self, text):
        self.status_label.set_text(text)
        return False

    def update_progress(self, fraction, status):
        self.progress_bar.set_fraction(fraction)
        self.progress_bar.set_text(f"{int(fraction * 100)}%")
        self.status_label.set_text(status)
        return False

    def pull_finished(self):
        self.progress_bar.set_fraction(1.0)
        self.progress_bar.set_text("Done")
        self.status_label.set_text("Pull complete")
        self.pull.set_sensitive(True)
        self.entry.set_sensitive(True)
        self.refresh_combo(None)
        return False

    def pull_error(self, message):
        self.status_label.set_text("Error: " + message)
        self.pull.set_sensitive(True)
        self.entry.set_sensitive(True)
        return False

    def perform_pull(self, model):
        try:
            response = self.api.pull_model(model)

            for line in response.iter_lines():
                if not line:
                    continue

                data = json.loads(line.decode())
                status = data.get("status", "")

                if "completed" in data and "total" in data and data["total"] > 0:
                    fraction = data["completed"] / data["total"]
                    GLib.idle_add(self.update_progress, fraction, status)
                else:
                    GLib.idle_add(self.update_status, status)

            GLib.idle_add(self.pull_finished)

        except Exception as e:
            GLib.idle_add(self.pull_error, str(e))

    def on_model_changed(self, combo):
        self.update_delete_state()

    def refresh_combo(self, widget):
        try:
            models = self.api.list_models()
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
        self.delete_button.set_sensitive(selected is not None)

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
            self.api.delete_model(selected)
            self.refresh_combo(None)
        except Exception as e:
            print("Error during deletion:", e)


win = MainWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()

