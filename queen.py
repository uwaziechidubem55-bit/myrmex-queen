"""ANCHA — the Queen. Memory (vault) + Mind (strategy) + Laws (governance)."""
import json
from colony.db import DB
from treaty import make

RULES = [   # The Mind's decision table: finding contains X -> next mission Y
    ("port", "order:map_deeper"),
    ("echoes", "order:ink:inject_probe"),
    ("Tomcat", "order:floodgate:tomcat_manager"),
    ("auth_gaps", "order:floodgate:auth_bypass"),
    ("forgeable", "order:keyhole:token_forge"),
    ("caches", "order:keyhole:cred_harvest"),
    ("writable_path", "order:rust:escalate"),
    ("in transit", "order:flea:traffic_watch"),
]

class Queen:
    def __init__(self):
        self.db = DB()

    def mission(self, target, tool, domain="network"):
        return make("mission", "ancha", "king", domain, {"target": target, "tool": tool})

    # Role 1: Memory
    def store(self, msg):
        self.db.store_finding(msg)

    # Role 2: Mind
    def decide(self, msg):
        s = json.dumps(msg.get("body", {}))
        return [m for pat, m in RULES if pat in s]

    # Role 3: Laws
    def law(self, name, rule, active=1):
        self.db.add_law(name, rule, active)
        return f"law recorded: {name}"

    def laws(self):
        return self.db.list_laws()
