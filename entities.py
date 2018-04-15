from entity import *

entities = [
    Weapon("Sword").power(10),
    Weapon("Mace").power(15),
    NPC("Frank").level_up(5).dialog("Nice day for fishing, ain't it?"),
    NPC("George").dialog("Hello there.").equip(Weapon("Dagger")),
    NPC("Alice").dialog("Hello there.").equip(Weapon("Dagger")),
    NPC("Bob").dialog("Hello there.").equip(Weapon("Dagger")),
    MOB("Bat").level_up(5),
    Treasure().level(5).add(Weapon("Staff")),
    MOB("Gnoll"),
    MOB("Gnoll"),
    MOB("Gnoll")
]


