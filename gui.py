import tkinter
import routemanager

class Combobox:
  def __init__(self, parent, initial_text, callback):
    self.parent = parent
    self.initial_text = initial_text
    self.variable = tkinter.StringVar(parent)
    self.variable.set(initial_text)
    self.option_menu = tkinter.OptionMenu(parent, self.variable, None)
    self.option_menu.configure(state=tkinter.DISABLED)
    self.callback = callback

  def state(self):
    return self.option_menu.cget('state')

  def _mkcallback(self, item):
    def callback():
      self.variable.set(item["Text"])
      self.callback(item)
      refresh()
    return callback

  def disable_option_menu_eventually(self):
    current_state = self.state()
    if current_state == tkinter.DISABLED:
      pass
    elif current_state == tkinter.NORMAL:
      self.option_menu.configure(state=tkinter.DISABLED)
    else:
      self.option_menu.after(20, lambda: self.disable_option_menu_eventually())

  def set_options(self, options):
    menu = self.option_menu['menu']
    menu.delete(0, 'end')

    if len(options) > 0:
      for o in options:
        text = o["Text"]
        if self.variable.get() == text:
          variable_ok = True
        menu.add_command(label=text, command=self._mkcallback(o))
      self.option_menu.configure(state=tkinter.NORMAL)
    else:
      self.disable_option_menu_eventually()

ROUTE_COMBO = None
SNAP_COMBO = None
LABEL = None
BUTTONS = []
SAVE_NAME_FIELD = None
SAVE_BUTTON = None

def refresh():
  ROUTE_COMBO.set_options(routemanager.get_subdirs(routemanager.ROUTES_PATH))
  if routemanager.CURRENT_SNAPSHOT:
    SNAP_COMBO.set_options(routemanager.get_subdirs(routemanager.CURRENT_SNAPSHOT))
    if routemanager.CURRENT_SNAPSHOT == routemanager.CURRENT_ROUTE:
      SNAP_COMBO.variable.set(SNAP_COMBO.initial_text)
    else:
      SNAP_COMBO.variable.set(routemanager.CURRENT_SNAPSHOT.name)
    LABEL.config(text=routemanager.current_position_text())
  else:
    LABEL.config(text="No snapshot selected.")
  for item, button in BUTTONS:
    if "Predicate" in item and not item["Predicate"]():
      button.config(state=tkinter.DISABLED)
    else:
      button.config(state=tkinter.NORMAL)

def callback_for(item):
  def callback():
    item["Function"]()
    refresh()
  return callback

def save_child_snapshot():
  filename = SAVE_NAME_FIELD.get()
  if filename:
    SAVE_NAME_FIELD.set("")
    routemanager.save_child_snapshot_as(filename)
    refresh()

GUI_ROUTE_MENU = routemanager.ROUTE_MENU + [
  { "Text": "Save new snapshot.",
    "Predicate": lambda: routemanager.CURRENT_ROUTE,
    "Function": save_child_snapshot }
]

if __name__ == "__main__":
  window = tkinter.Tk()
  window.title("Hades Route Manager")
  window.attributes("-topmost", True)

  ROUTE_COMBO = Combobox(window, "Select a route",
    lambda item: routemanager.set_current_route(item["Path"]))
  ROUTE_COMBO.option_menu.pack(fill=tkinter.X)

  SNAP_COMBO = Combobox(window, "Select a snapshot",
    routemanager.set_child_snapshot)
  SNAP_COMBO.option_menu.pack(fill=tkinter.X)

  LABEL = tkinter.Label(window)
  LABEL.pack(fill=tkinter.X)

  for item in GUI_ROUTE_MENU:
    button = tkinter.Button(window, text=item["Text"], command=callback_for(item))
    button.pack(fill=tkinter.X)
    BUTTONS.append((item, button))

  SAVE_NAME_FIELD = tkinter.StringVar()
  save_entry = tkinter.Entry(window, textvariable=SAVE_NAME_FIELD)
  save_entry.pack(fill=tkinter.X)

  refresh()

  window.mainloop()

