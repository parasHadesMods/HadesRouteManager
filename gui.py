import tkinter
import routemanager

class ButtonItem:
  def __init__(self, parent, item):
    self.button = tkinter.Button(parent, text=item["Text"],
      command=ButtonItem._mkcallback(item))
    if "Predicate" in item:
      self.predicate = item["Predicate"]
    else:
      self.predicate = lambda: True

  @staticmethod
  def _mkcallback(item):
    def callback():
      item["Function"]()
      refresh()
    return callback

  def refresh(self):
    if self.predicate():
      self.button.config(state=tkinter.NORMAL)
    else:
      self.button.config(state=tkinter.DISABLED)

class ComboItem:
  def __init__(self, parent, item):
    self.parent = parent
    self.item = item
    self.prompt = item["Prompt"]
    self.get_current = item["GetCurrent"]
    self.on_select = item["OnSelect"]
    self.get_options = item["GetOptions"]
    self.variable = tkinter.StringVar(parent)
    self.option_menu = tkinter.OptionMenu(parent, self.variable, None)
    self.option_menu.configure(state=tkinter.DISABLED)

  def state(self):
    return self.option_menu.cget('state')

  def _mkcallback(self, item):
    def callback():
      self.on_select(item)
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
    options = self.get_options()
    menu = self.option_menu['menu']
    menu.delete(0, 'end')

    if len(options) > 0:
      for o in options:
        text = o["Text"]
        menu.add_command(label=text, command=self._mkcallback(o))
      self.option_menu.configure(state=tkinter.NORMAL)
    else:
      self.disable_option_menu_eventually()

    path = self.get_current()
    if path:
      self.variable.set(path.name)
    else:
      self.variable.set(self.prompt)

CURRENT_PROFILE = None
SAVE_NAME_FIELD = None
ELEMENTS = []

def refresh():
  for elem in ELEMENTS:
    if "Refresh" in elem:
      elem["Refresh"]()

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

def type_button(item):
  item["Type"] = "Button"
  return item

ELEMENTS = [
  { "Type": "Combo",
    "Prompt": "Select a route",
    "GetCurrent": lambda: routemanager.CURRENT_ROUTE,
    "OnSelect": lambda item: routemanager.set_current_route(item["Path"]),
    "GetOptions": lambda: routemanager.get_subdirs(routemanager.ROUTES_PATH) },
  { "Type": "Combo",
    "Prompt": "Select a snapshot",
    "GetCurrent": lambda: routemanager.CURRENT_SNAPSHOT,
    "OnSelect": routemanager.set_child_snapshot,
    "GetOptions": lambda: routemanager.get_subdirs(routemanager.CURRENT_SNAPSHOT) },
  { "Type": "Label",
    "GetCurrent": lambda: routemanager.current_save_name() if routemanager.CURRENT_ROUTE else ""},
  { "Type": "Button",
    "Text": "Load this snapshot",
    "Predicate": routemanager.has_parent,
    "Function": routemanager.load_current_snapshot },
  { "Type": "Button",
    "Text": "Return to parent",
    "Predicate": routemanager.has_parent,
    "Function": routemanager.return_to_parent },
  { 
    "Type": "Button",
    "Text": "Save new snapshot",
    "Predicate": lambda: routemanager.CURRENT_ROUTE,
    "Function": save_child_snapshot },
  { "Type": "Button",
    "Text": "Create new route",
    "Predicate": lambda: CURRENT_PROFILE,
    "Function": create_new_route },
  { "Type": "Combo",
    "Prompt": "Select slot for new route",
    "GetCurrent": lambda: CURRENT_PROFILE["Path"] if CURRENT_PROFILE else None,
    "OnSelect": set_current_profile,
    "GetOptions": lambda: routemanager.get_saves() },
  {  "Type": "Entry" } ,
]

if __name__ == "__main__":
  window = tkinter.Tk()
  window.title("Hades Route Manager")
  window.attributes("-topmost", True)

  SAVE_NAME_FIELD = tkinter.StringVar()

  for item in ELEMENTS:
    if item["Type"] == "Combo":
      element = ComboItem(window, item)
      element.option_menu.pack(fill=tkinter.X)
      item["Refresh"] = element.refresh
    if item["Type"] == "Button":
      element = ButtonItem(window, item)
      element.button.pack(fill=tkinter.X)
      item["Refresh"] = element.refresh
    if item["Type"] == "Entry":
      entry = tkinter.Entry(window, textvariable=SAVE_NAME_FIELD)
      entry.pack(fill=tkinter.X)
    if item["Type"] == "Label":
      label = tkinter.Label(window)
      label.pack(fill=tkinter.X)
      item["Refresh"] = lambda label=label,item=item: label.configure(text=item["GetCurrent"]())

  refresh()

  window.mainloop()

