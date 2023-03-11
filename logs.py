from uuid import uuid4
import json

session_id = str(uuid4())
logs_file_name = "logs.json"

def open_or_create_logs():
  open(logs_file_name, "a+")


def logs_create_session():
  data = {}
  sessions = []
  new_session = {
      "session_id": session_id,
      "messages": []
  }

  open_or_create_logs()

  with open(logs_file_name, "r", encoding="utf-8") as json_file:
      try:
          data = json.load(json_file)
          sessions = data["sessions"]
      except:
          data = { "sessions": [] }

      for session in sessions:
          if session["session_id"] == session_id:
              return      
          
      sessions.append(new_session)
      data["sessions"] = sessions

  with open(logs_file_name, "w", encoding="utf-8") as json_file:
      json.dump(data, json_file, ensure_ascii=False, indent=4)

def logs_write_message(message):
  current_session = None
  with open(logs_file_name, "r", encoding="utf-8") as json_file:
    try:
      data = json.load(json_file)
      sessions = data["sessions"]
    except:
      print("Could not read file sessions")
      return

    for session in sessions:
      if session["session_id"] == session_id:
          current_session = session

    if not current_session:
      print("Could not find current session in logs")
      return
  
    messages = current_session["messages"]
    messages.append(message)
    current_session["messages"] = messages

    for session in sessions:
      if session["session_id"] == session_id:
          session = current_session

    data["sessions"] = sessions

  with open(logs_file_name, "w", encoding="utf-8") as json_file:
    json.dump(data, json_file, ensure_ascii=False, indent=4)