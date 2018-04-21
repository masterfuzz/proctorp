import event
import colors
import entity

def u(uuid):
    return entity.all_entities[uuid]

pc = u(entity.player_uuid)


@event.on("combat.attack")
def clog_attack(kwg):
    sub = u(kwg['sub'])
    obj = u(kwg['obj'])
    hprint("{} attacks {}!\n".format(sub, obj))

@event.on("combat.damage")
def clog_damage(kwg):
    sub = u(kwg['sub'])
    hprint("{}: Ouch! (-{} HP)\n".format(sub.name, kwg['amount']))

@event.when("entity.xp.gain", {'sub': pc.uuid})
def clog_xp_gain(k):
    pcprint("You gained {} XP!\n".format(k['amount']))

@event.on("quest.completed")
def clog_quest_complete(k):
    quest = u(k['obj'])
    pc.gain_xp(quest.xp)
    pcprint("You completed the quest '{}'!\n+{} XP\n".format(quest.name,
                                                           quest.xp))

@event.on("quest.accepted")
def clog_quest_accept(k):
    quest = u(k['obj'])
    pcprint("You accepted the quest '{}'!\n".format(quest.name))

def hprint(msg):
    colors.cprint(msg, color=colors.FAIL)

def pcprint(msg):
    colors.cprint(msg, color=colors.OKBLUE)
