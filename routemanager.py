import re
from pathlib import Path

CURRENT_ROUTE = None
CURRENT_SNAPSHOT = None
EXIT = False

ROUTES_PATH = Path("./Routes")
HADES_SAVES_PATH = Path.home() / "Library/Application Support/Supergiant Games/Hades"

def sorted_by(field, items):
  return sorted(items, key = lambda item: item[field])

def get_subdirs(path):
  return sorted_by("Text", [
    {"Text": d.name, "Path": d}
    for d in path.iterdir()
    if d.is_dir()])

def get_saves():
  return sorted_by("Text", [
    {"Text": f.name, "Path": f}
    for f in HADES_SAVES_PATH.iterdir()
    if re.search(r'^Profile\d\.sav$', f.name)])

def current_save_name():
  for f in CURRENT_ROUTE.iterdir():
    if re.search(r'^Profile\d\.sav$', f.name):
      return f.name

def current_depth():
  return len(CURRENT_SNAPSHOT.relative_to(CURRENT_ROUTE).parts) + 1

def current_temp_name():
  return current_save_name().replace(".sav", "_Temp.sav")

def current_v_name():
  return current_save_name().replace(".sav", ".v.sav")

def copy_file(fromPath, toPath):
  toPath.write_bytes(fromPath.read_bytes())

def prompt_choice(items, prompt=None, alternative=None):
  if prompt:
    print(prompt)
  max = len(items) + 1
  if alternative:
    items = items.copy()
    items.append(alternative)
    max += 1
  for count, item in enumerate(items):
    itemText = None
    try:
      itemText = item["Text"]
    except TypeError:
      itemText = item
    print(f"{count+1}. {itemText}")

  try:
    choice = input("> ")
    i = int(choice)
    if 1 <= i and i < max:
      return items[i-1]
  except ValueError:
    pass

def prompt_filename(prompt):
  filename = ""
  while not re.search(r'[\w\d\-\. ]+', filename):
    filename = input(f"{prompt}\n > ")
  return filename

def create_new_route():
  chosen = prompt_choice(
    get_saves(),
    "Choose the initial save for the route:")
  if not chosen:
    return None
  filename = prompt_filename("Enter a name for the route:")
  new_route = ROUTES_PATH / filename
  new_route.mkdir(exist_ok=True)

  copy_file(chosen["Path"], new_route / chosen["Path"].name)

  return new_route

def load_current_snapshot():
  copy_file(
    CURRENT_SNAPSHOT / current_temp_name(),
    HADES_SAVES_PATH / current_temp_name())

  copy_file(
    CURRENT_SNAPSHOT / current_v_name(),
    HADES_SAVES_PATH / current_v_name())

def save_child_snapshot():
  filename = prompt_filename("Enter a name for the snapshot.")
  new_snapshot = CURRENT_SNAPSHOT / filename
  new_snapshot.mkdir(exist_ok=True)

  copy_file(
    HADES_SAVES_PATH / current_temp_name(),
    new_snapshot / current_temp_name())

  copy_file(
    HADES_SAVES_PATH / current_v_name(),
    new_snapshot / current_v_name())

def choose_child_snapshot():
  global CURRENT_SNAPSHOT
  child = prompt_choice(
    get_subdirs(CURRENT_SNAPSHOT),
    "Choose a child snapshot:",
    {"Text": "None of the above.", "Path": None})

  if not child or not child["Path"]:
    return
  print("ok", child["Path"])

  CURRENT_SNAPSHOT = child["Path"]

def has_parent():
  return not CURRENT_SNAPSHOT.samefile(CURRENT_ROUTE)

def return_to_parent():
  global CURRENT_SNAPSHOT
  CURRENT_SNAPSHOT = CURRENT_SNAPSHOT.parent

def switch_routes():
  global CURRENT_ROUTE
  CURRENT_ROUTE = None

def exit_route_manager():
  global EXIT
  EXIT = True

ROUTE_MENU = [
  { "Text": "Load this snapshot.",
    "Predicate": has_parent,
    "Function": load_current_snapshot },
  { "Text": "Save a new child.",
    "Function": save_child_snapshot },
  { "Text": "Select a child snapshot.",
    "Function": choose_child_snapshot},
  { "Text": "Return to parent.",
    "Predicate": has_parent,
    "Function": return_to_parent },
  { "Text": "Switch routes.",
    "Function": switch_routes },
  { "Text": "Exit.",
    "Function": exit_route_manager }
]

if __name__ == "__main__":
  print("Hades Route Manager starting...")
  while not EXIT:
    if CURRENT_ROUTE:
       print(f"Depth {current_depth()} {CURRENT_SNAPSHOT.name}")
       menu = [ menu_item
         for menu_item in ROUTE_MENU
         if (not "Predicate" in menu_item)
         or (menu_item["Predicate"]())]
       chosen = prompt_choice(menu, "Choose an action:")
       if chosen:
         chosen["Function"]()    
    else:
      chosen = prompt_choice(
        get_subdirs(ROUTES_PATH),
        "Choose a route:",
        {"Text": "Create new.", "Path": None})
      if not chosen:
        continue
      if chosen["Path"]:
        CURRENT_ROUTE = chosen["Path"]
      else:
        CURRENT_ROUTE = create_new_route()
      CURRENT_SNAPSHOT = CURRENT_ROUTE
         
