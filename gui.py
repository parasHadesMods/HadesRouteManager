import tkinter
import routemanager

class PathVar:
  def __init__(self, parent, initial_text, refresh_callback):
    self.parent = parent
    self.variable = tkinter.StringVar(parent)
    self.initial_text = initial_text
    self.refresh_callback = refresh_callback

  def refresh(self):
    value = self.refresh_callback()
    if value:
      self.variable.set(value.name)
    else:
      self.variable.set(self.initial_text)

class ButtonItem:
  def __init__(self, parent, item):
    self.item = item
    self.button = tkinter.Button(parent, text=item["Text"],
      command=ButtonItem._mkcallback(item))

  @staticmethod
  def _mkcallback(item):
    def callback():
      item["Function"]()
      refresh()
    return callback

  def refresh(self):
    if "Predicate" in self.item and not self.item["Predicate"]():
      self.button.config(state=tkinter.DISABLED)
    else:
      self.button.config(state=tkinter.NORMAL)

class Combobox:
  def __init__(self, parent, variable, select_callback, refresh_callback):
    self.parent = parent
    self.option_menu = tkinter.OptionMenu(parent, variable, None)
    self.option_menu.configure(state=tkinter.DISABLED)
    self.select_callback = select_callback
    self.refresh_callback = refresh_callback

  def state(self):
    return self.option_menu.cget('state')

  def _mkcallback(self, item):
    def callback():
      self.select_callback(item)
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

  def refresh(self):
    options = self.refresh_callback()
    menu = self.option_menu['menu']
    menu.delete(0, 'end')

    if len(options) > 0:
      for o in options:
        text = o["Text"]
        menu.add_command(label=text, command=self._mkcallback(o))
      self.option_menu.configure(state=tkinter.NORMAL)
    else:
      self.disable_option_menu_eventually()

CURRENT_PROFILE = None
SAVE_NAME_FIELD = None
REFRESHABLE = []

def register(item):
  REFRESHABLE.append(item)

def refresh():
  for item in REFRESHABLE:
    item.refresh()

def save_child_snapshot():
  filename = SAVE_NAME_FIELD.get()
  if filename:
    SAVE_NAME_FIELD.set("")
    routemanager.save_child_snapshot_as(filename)

def create_new_route():
  filename = SAVE_NAME_FIELD.get()
  profile = CURRENT_PROFILE
  if filename and profile:
    SAVE_NAME_FIELD.set("")
    set_current_profile(None)
    route = routemanager.create_new_route_as(profile, filename)
    routemanager.set_current_route(route)

def set_current_profile(profile):
  global CURRENT_PROFILE
  CURRENT_PROFILE = profile

GUI_ROUTE_MENU = routemanager.ROUTE_MENU + [
  { "Text": "Save new snapshot.",
    "Predicate": lambda: routemanager.CURRENT_ROUTE,
    "Function": save_child_snapshot },
  { "Text": "Create new route.",
    "Function": create_new_route }
]

if __name__ == "__main__":
  window = tkinter.Tk()
  window.title("Hades Route Manager")
  window.attributes("-topmost", True)

  profile_var = PathVar(window, "Select a save slot",
    lambda: CURRENT_PROFILE)
  register(profile_var)

  profile_combo = Combobox(window,
    profile_var.variable,
    set_current_profile,
    lambda: routemanager.get_saves())
  profile_combo.option_menu.pack(fill=tkinter.X)
  register(profile_combo)

  route_var = PathVar(window, "Select a route",
    lambda: routemanager.CURRENT_ROUTE)
  register(route_var)

  route_combo = Combobox(window,
    route_var.variable,
    lambda item: routemanager.set_current_route(item["Path"]),
    lambda: routemanager.get_subdirs(routemanager.ROUTES_PATH))
  route_combo.option_menu.pack(fill=tkinter.X)
  register(route_combo)

  snap_var = PathVar(window, "Select a snapshot",
    lambda: routemanager.CURRENT_SNAPSHOT)
  register(snap_var)

  snap_combo = Combobox(window,
    snap_var.variable,
    routemanager.set_child_snapshot,
    lambda: routemanager.get_subdirs(routemanager.CURRENT_SNAPSHOT))
  snap_combo.option_menu.pack(fill=tkinter.X)
  register(snap_combo)

  for item in GUI_ROUTE_MENU:
    item_button = ButtonItem(window, item)
    item_button.button.pack(fill=tkinter.X)
    register(item_button)

  SAVE_NAME_FIELD = tkinter.StringVar()
  save_entry = tkinter.Entry(window, textvariable=SAVE_NAME_FIELD)
  save_entry.pack(fill=tkinter.X)

  refresh()

  window.mainloop()

