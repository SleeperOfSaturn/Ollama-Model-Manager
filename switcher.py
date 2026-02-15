import gi
import requests
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
class MainWindow(Gtk.Window):
	def __init__(self):
		super().__init__(title="Ollama Switcher")
		self.set_default_size(400,600)
		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
		self.add(box)
		self.button = Gtk.Button(label="Load Models")
		self.combo = Gtk.ComboBoxText()
		self.combo.connect("changed", self.on_model_changed)
		self.button.connect("clicked", self.refresh_combo)
		box.pack_start(self.combo, False, False, 0)
		box.pack_start(self.button, False, False, 0)
	def on_model_changed(self, combo):
		selected = combo.get_active_text()
		print("Selected model:", selected)
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
win = MainWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
