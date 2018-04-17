from entity import *
from quest import Quest

entities = [
    Weapon("Sword").power(10),
    Weapon("Mace").power(15),
    NPC("Frank").level_up(5).dialog("Nice day for fishing, ain't it?"),
    NPC("George").dialog("Hello there.").wielding(Weapon("Dagger")),
    NPC("Alice").dialog("Hello there.").wielding(Weapon("Dagger")),
    NPC("Bob").dialog("Hello there.").wielding(Weapon("Dagger")),
    NPC("Hermit").quest(
        "Please kill the Gnolls!",
        Quest("Gnolls", 5).require_kill("Gnoll"),
        "Thank you for killing the Gnolls!"
    ),
    MOB("Bat").level_up(5),
    Treasure().level(5).add(Weapon("Staff")),
    MOB("Gnoll"),
    MOB("Gnoll"),
    MOB("Gnoll"),
    MOB("Overlord").level_up(20)
]


