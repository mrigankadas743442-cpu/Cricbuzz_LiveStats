from models.player import Player
from services import crud_service as svc
from utils.exceptions import AppError

pid = svc.create_player(Player("Test Player", "India", "Batsman"))
print("Created", pid)
svc.update_player(pid, {"playing_role": "All-rounder"})
print(svc.get_player(pid))
for bad in (Player("A", "India"), Player("Test Player", "India")):
    try:
        svc.create_player(bad)
    except AppError as e:
        print("Expected error:", e)
try:
    svc.delete_player(1)  # seed player with scorecards
except AppError as e:
    print("Expected error:", e)
svc.delete_player(pid)
print("Deleted", pid)