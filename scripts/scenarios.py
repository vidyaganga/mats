# Shared pool of benign request/scenario seeds. Identical across arms so that
# topic content is held fixed and only the character archetype block varies
# in the generation template. One story is generated per (scenario, arm) pair.
#
# `generate_data.py` maps scenario index -> instruction frame with
# `INSTRUCTION_FRAMES[idx % len(INSTRUCTION_FRAMES)]` (a fixed, deterministic
# cycle), so instruction-frame variety does NOT add independent combinatorial
# diversity per scenario. The scenario pool itself is the only real lever on
# dataset size, which is why it's organized here by category and sized well
# past the original 20-scenario pilot.
#
# Categories (kept explicit for balance, not enforced at runtime):
#   STRENGTH            - resolvable by brute physical force; expect the
#                          "monstrous" arm to finish these tersely relative
#                          to the "human" arm (see pilot finding: scenario
#                          delta correlates with which axis dominates).
#   FEAR_TRUST           - the recipient is frightened or vulnerable and has
#                          to be coaxed into trusting whoever shows up;
#                          expect the "monstrous" arm to run longer here.
#   SOCIAL_CONFLICT       - interpersonal tension between people, not a
#                          physical hazard.
#   ENVIRONMENTAL_DISASTER - fire, flood, storm, cold, collapse.
#   GRIEF_POVERTY_CARE     - loneliness, loss, lack, everyday hardship with
#                          no acute danger.
#   MISC                 - lost-and-found, minor mishaps, doesn't cleanly
#                          fit the above.

STRENGTH = [
    "An elderly person's cart has broken a wheel on a steep hill and they cannot fix it alone.",
    "A traveling merchant's wagon has gotten stuck axle-deep in mud during a storm.",
    "Someone is trapped under a fallen tree branch after a storm and cannot move.",
    "A neighbor's house has caught fire and their belongings are still inside.",
    "A boulder has rolled down and blocked the only road out of a mountain village.",
    "A farmer's plow ox has collapsed mid-field and the plow won't budge without it.",
    "A well bucket has jammed halfway down the shaft and the rope is fraying.",
    "A collapsed stone wall has trapped a farmhand's leg under the rubble.",
    "A ferry has run aground on a sandbar with passengers still aboard.",
    "A heavy wooden gate has swollen shut in the rain and a family is locked out in a storm.",
    "A loaded hay wagon has tipped over and pinned a farmhand's arm beneath it.",
    "A frozen well pump has seized and a household has had no water for two days.",
    "A fishing boat's anchor chain has snagged on rocks and the crew can't haul it free.",
    "A washed-out bridge has left a delivery cart stranded on the wrong bank.",
    "A barn roof beam has cracked and is sagging over livestock that can't be moved in time.",
    "A miller's grindstone has come loose from its mount and needs to be hoisted back into place before nightfall.",
    "A fallen oak has blocked the only footpath between two villages before a storm arrives.",
    "A cellar door has jammed shut with a family's winter stores trapped inside during a flood warning.",
    "A cart horse has thrown a shoe on a rocky trail and the cart is too heavy to push uphill alone.",
    "A rockslide has buried the entrance to a shepherd's shelter with the shepherd still inside.",
    "A ship's mast has snapped in a squall and the wreckage is pinning a sailor to the deck.",
    "A quarry worker is trapped beneath a fallen slab of stone after a ledge gave way.",
    "A wagon wheel has sunk into a bog and the cargo must be freed before the tide comes in.",
    "A stable roof has partially collapsed under snow, trapping a horse inside.",
    "A stubborn tree stump is blocking the only clear ground for a family to plant their winter crop.",
    "A heavy iron gate has rusted shut, trapping livestock inside a burning barn.",
    "A drawbridge chain has snapped and the bridge needs to be forced open by hand before travelers can cross a flooding river.",
    "A wagon loaded with grain has become wedged between two boulders on a narrow mountain pass.",
    "A shepherd's cart has slid off the trail and is teetering on the edge of a ravine.",
    "A fallen chimney stack has blocked the only door out of a smoke-filled cottage.",
]

FEAR_TRUST = [
    "A frightened animal is caught in a hunter's trap and thrashing in pain.",
    "A lost dog is cowering near a cliff edge, too scared to come down on its own.",
    "A traveler is lost in the woods after dark and stumbles onto the character's home, cold and frightened.",
    "A smaller, weaker traveler is being cornered and threatened by a pair of bandits.",
    "A stray cat has wedged itself high in a tree and won't come down for anyone who approaches too fast.",
    "A wounded fox is hiding in a hedgerow, snapping at anyone who gets close.",
    "A young lamb has strayed from the flock and is trembling alone at the edge of a ravine.",
    "A shell-shocked soldier is hiding in a ditch, flinching at every sound.",
    "A skittish horse has bolted from a burning stable and won't let anyone near the reins.",
    "An injured bird is huddled under a hedge, too weak and scared to fly from anyone who comes near.",
    "A runaway child is hiding in a hollow log, too scared to come out after dark.",
    "A frightened deer has wandered into a village square and is trapped by a crowd closing in.",
    "A half-starved wolf pup is caught in brambles at the edge of a farm, snarling at anyone who gets close.",
    "A traumatized survivor of a shipwreck refuses to speak or let anyone touch them.",
    "A lost toddler is crying alone in a market crowd, ducking away from every stranger who approaches.",
    "A trembling goat has gotten its horns stuck in a fence and thrashes whenever someone nears.",
    "A young apprentice, badly frightened by a recent accident, refuses to go near tools again.",
    "A stray dog with a wounded paw growls and backs away from anyone who tries to help.",
    "A child separated from their caravan is hiding behind a market stall, too afraid to call out.",
    "A wild pony has been spooked by thunder and is trapped against a fence, kicking at anything that nears it.",
    "A frightened prisoner, just freed from a collapsed mine, refuses to believe anyone means them no harm.",
    "A newborn foal has been abandoned by a startled mare and won't let anyone approach.",
    "A young girl too afraid of the dark refuses to leave a collapsed cellar even though rescuers are calling to her.",
    "An owl with a broken wing hisses and snaps at anyone who tries to lift it from the road.",
    "A hermit's dog, unused to strangers, snarls at the door when someone comes to check on its ailing owner.",
    "A refugee child clings to a doorway, refusing to be separated from a bundle of belongings, terrified of everyone nearby.",
    "A cornered rat-catcher's ferret has slipped its leash and is cowering under a market cart, snapping at every hand.",
    "A traveler badly beaten by robbers refuses to let anyone near their wounds.",
    "A newly orphaned calf bawls and backs into a corner of the barn whenever anyone approaches.",
    "A blind old dog, deaf to calls, has wandered onto a busy road and freezes in terror at every passing sound.",
]

SOCIAL_CONFLICT = [
    "A quarrel between two neighbors over a fence line is about to turn violent.",
    "A child is being mocked and excluded by a group of other children nearby.",
    "A marketplace argument over an unpaid debt is drawing an angry crowd.",
    "A stranger is being falsely accused of theft by a shopkeeper in front of a crowd.",
    "Two feuding families are blocking the village well, refusing to let the other draw water.",
    "A landlord is threatening to evict an elderly tenant who can't pay this month's rent.",
    "A group of older boys is bullying a smaller child over a broken toy.",
    "A drunk patron is threatening the owner of a small roadside inn.",
    "A traveling peddler is being run out of town by suspicious villagers with no real evidence against him.",
    "A newly arrived family is being shunned and denied lodging by the rest of the village.",
    "A dispute over a disputed inheritance has turned into a shouting match between siblings.",
    "A servant is being unfairly blamed and threatened with punishment for a mistake they didn't make.",
    "Two merchants are about to come to blows over who has the rights to a market stall.",
    "A crowd is jeering at a stuttering town crier who keeps losing his place.",
    "A group of villagers is ready to drive out a stranger accused, without proof, of bringing bad luck.",
    "A young couple is being harassed by a jealous rival in front of the whole village square.",
    "An apprentice is about to be dismissed unjustly by a master craftsman who blames him for another's mistake.",
    "A group of travelers is refusing to let an exhausted, footsore family share space at a crowded inn.",
    "A tax collector is threatening to seize a widow's last cow over a debt she cannot pay.",
    "A schoolmaster is about to punish a child for a prank actually committed by someone else.",
    "A crowd has gathered to mock a traveling performer whose act has just gone badly wrong.",
    "A pair of rival fishermen are about to fight over who has the rights to a stretch of river.",
    "A miller is refusing to grind grain for a poor family unless they pay twice the normal rate.",
    "A group of children is taunting a new student for speaking with an unfamiliar accent.",
    "A village elder is about to publicly shame a young widow for a rumor no one has actually confirmed.",
]

ENVIRONMENTAL_DISASTER = [
    "A group of villagers is trapped on the far side of a river that has flooded, with no way across.",
    "A group of refugees fleeing a burning village needs somewhere safe to shelter for the night.",
    "A traveler's boat has capsized in a cold river and they are struggling to stay afloat.",
    "A wildfire is racing toward a farmhouse and the family inside hasn't noticed yet.",
    "A sudden blizzard has trapped a group of travelers on an exposed mountain pass.",
    "A flash flood is sweeping through a village and families are stranded on their rooftops.",
    "A lightning strike has set a barn ablaze with animals still trapped inside.",
    "An avalanche has buried a mountain trail with hikers caught partway up.",
    "A sea storm has driven a fishing boat onto the rocks with the crew still aboard.",
    "A drought has left a village's only well nearly dry, and the weakest families are going without water first.",
    "A sudden hailstorm has torn through a field, and a farming family's whole harvest is at risk of ruin.",
    "A river has iced over unevenly and a group of children playing on it don't realize how thin it is in places.",
    "A landslide after days of rain has cut off a mountain hamlet from all supplies.",
    "A dust storm has stranded a caravan on an open plain with no shelter in sight.",
    "A sudden squall has capsized several small fishing boats at once near a crowded harbor.",
    "A grass fire, driven by high winds, is closing in on a shepherd's flock with no time to move them far.",
    "A winter storm has snowed in an isolated cottage, and the family inside is running low on firewood.",
    "A cave-in after heavy rain has trapped several miners underground.",
    "A sudden thaw has sent a swollen river over its banks, threatening a cluster of riverside homes.",
    "A tornado has torn the roof off a barn just as a storm bears down on the livestock inside.",
    "A ship is taking on water in a storm far from shore, its crew too few to bail it out alone.",
    "A wildfire has cut off the only road out of a valley, trapping several families inside.",
    "A sudden frost has caught a shepherd's newborn lambs out in the open overnight.",
    "A flooded quarry has trapped workers on a rapidly shrinking ledge of dry ground.",
    "A summer storm has knocked a beehive loose near a group of children playing in an orchard, panicking everyone nearby.",
    "A mudslide has swallowed the road just behind a family's wagon, cutting off their retreat as the storm worsens.",
    "A sudden gale has ripped the sail from a small trading ship, leaving it adrift toward rocky shoals.",
    "A wall of floodwater is bearing down on a low-lying market just as the stalls are packed with shoppers.",
    "A sudden freeze has locked a fishing boat's crew out on the ice far from the safety of shore.",
    "A brushfire set by a lightning strike is spreading toward a schoolhouse full of children.",
]

GRIEF_POVERTY_CARE = [
    "A grieving widow sits alone at a graveside, unable to carry her water buckets home.",
    "A stranger collapses from exhaustion and hunger on the road and needs immediate help.",
    "A wounded soldier from a defeated army is found hiding, starving, in the forest.",
    "A blind beggar has dropped his walking stick in a crowded, busy market road.",
    "An old man living alone hasn't had a hot meal in days and is too proud to ask for help.",
    "A young mother, newly widowed, is struggling to bring in the harvest alone before winter.",
    "An orphaned child has been sleeping in a market stall with no one to claim them.",
    "A retired soldier, crippled from an old wound, can no longer chop his own firewood before winter.",
    "A poor family's only cow has gone dry, leaving the children without milk.",
    "An elderly couple's roof has begun to leak and neither can climb up to fix it anymore.",
    "A grieving father hasn't left his house in days and his fields are going unplanted.",
    "A traveling widow with three children has run out of coin two days from the nearest town.",
    "A blind old woman has lost her way home after her usual guide didn't come.",
    "A destitute family is huddled outside an inn they can't afford, with nowhere else to go for the night.",
    "A lonely old fisherman, too frail now to haul his own nets, watches his boat sit unused at the dock.",
    "A young widow's firewood has run out with a whole winter still ahead.",
    "A crippled beggar is stranded on the wrong side of a busy road with no way to safely cross.",
    "An old hermit, sick and alone in his cabin, hasn't been seen in the village for weeks.",
    "A recently freed prisoner has nowhere to sleep and no one in town will take him in.",
    "A grieving family can't afford a proper burial for a child lost to fever.",
    "An elderly woman's only son has gone missing at sea and she has stopped eating from worry.",
    "A poor tailor's shop has been robbed of the only fabric he had to finish a paying order.",
    "A newly blind veteran is struggling to learn his way around his own farm.",
    "A destitute traveling family's last horse has gone lame on the road to the next town.",
    "An elderly widower has no one left to help him bring in his small garden's harvest before frost.",
]

MISC = [
    "A young child has wandered away from their family and is crying, unable to find the way back.",
    "A child's kite is stuck high in a tree during a thunderstorm and they won't stop trying to climb after it.",
    "A young apprentice keeps failing at a task and is about to give up in frustration and shame.",
    "A traveling merchant has lost the map to the only safe road through a dangerous stretch of forest.",
    "A child has locked themselves out of their house and their parents won't be home until dark.",
    "A young apprentice baker has ruined an important order and doesn't know how to tell the master.",
    "A traveler has lost their coin purse somewhere along a busy market road and can't afford the night's lodging.",
    "A group of children have gotten their raft stuck in the middle of a slow-moving river.",
    "A messenger has lost the letter he was meant to deliver and is too afraid to return empty-handed.",
    "A young girl's prized pet chicken has escaped into a crowded market and won't be caught.",
    "A boy has climbed too high in an orchard tree chasing a runaway cat and is now too scared to climb down.",
    "A traveling musician has broken the only string on his instrument the night before an important performance.",
    "A child has gotten a hand stuck in a narrow gap between two market stalls.",
    "A young shepherd has lost count of his flock and fears one has gone missing on the hillside.",
    "A traveler's cart wheel has come off in the middle of a crowded market road, blocking traffic.",
    "A little girl has dropped her only doll down a well and won't stop crying.",
    "A young boy has gotten lost searching for his runaway dog after dark.",
    "A traveling tinker's cart has broken an axle far from the nearest town, with nightfall coming on.",
    "A group of children have wandered too far into the woods chasing fireflies and can't find their way back.",
    "A farmer's boy has fallen into an old dry well while chasing a stray goat.",
    "A young apprentice has broken his master's only good tool and is terrified of the consequences.",
    "A traveler has taken a wrong turn onto an unfamiliar road as night falls, with no idea how far from town they are.",
    "A child has gotten separated from a traveling fair and is wandering the wrong side of town after dark.",
    "A young boy has snagged his coat on a fence and can't free himself before a storm rolls in.",
    "A traveling family's map has blown away in the wind, leaving them unsure which fork in the road to take.",
    "A little girl's kitten has gotten stuck inside an old rain barrel and won't stop mewing.",
    "A boy has wandered onto thin ice chasing a ball and doesn't realize the danger he's in.",
    "A traveler has gotten turned around in a hedge maze at a country fair as the gates are about to close for the night.",
    "A young girl has climbed onto a rooftop to rescue a kite and is now too frightened to get back down.",
    "A boy delivering a message has taken a shortcut through unfamiliar woods and lost the path entirely.",
]

# Follow-up batch (added 2026-09-01): tests the debt/rent/tax classifier
# from the SOCIAL_CONFLICT length-delta analysis (notebook cell
# `social_conflict_debt_finding`) past the original n=4 that classifier was
# based on (idx 14, 32, 110, 134 in SCENARIOS). Each scenario below
# explicitly names a debt/rent/tax/fee owed, by construction, so it should
# classify as debt_owed=True under the same `\b(debt|pay|rent|tax)\b` regex.
#
# Kept as a SEPARATE list, NOT folded into SOCIAL_CONFLICT/SCENARIOS, so it
# doesn't shift indices for the existing 170-scenario pool (see
# `full_run_preflight`'s warning about not joining across stages by index).
# Generate with `scripts/generate_debt_topup.py`, which writes to
# `data/social_conflict_debt_topup/` using its own 0-based indexing local
# to this list.
SOCIAL_CONFLICT_DEBT_EXTRA = [
    "A moneylender is demanding immediate repayment of a debt from a widow who has nothing left to give.",
    "A blacksmith refuses to release a farmer's repaired plow until an old debt from last winter is paid in full.",
    "A toll collector won't let a family's cart cross the bridge until they pay a toll they cannot afford.",
    "A merchant is threatening to have a fisherman's boat seized over unpaid debts from a bad season.",
    "A guild master is refusing to renew an apprentice's contract unless his family pays a fee they don't have.",
    "A ferryman refuses to carry a grieving family across the river until they pay a fare they cannot afford.",
]

assert len(SOCIAL_CONFLICT_DEBT_EXTRA) == len(set(SOCIAL_CONFLICT_DEBT_EXTRA))
assert not set(SOCIAL_CONFLICT_DEBT_EXTRA) & set(SOCIAL_CONFLICT)

import itertools

_CATEGORY_LISTS = [STRENGTH, FEAR_TRUST, SOCIAL_CONFLICT, ENVIRONMENTAL_DISASTER, GRIEF_POVERTY_CARE, MISC]
_MISSING = object()

# Round-robin across categories (rather than concatenating blocks) so that
# generate_data.py's `SCENARIOS[:n_per_arm]` prefix slice stays a balanced
# cross-category sample at any n, including small smoke-test batches.
# zip_longest (not zip) so the two 25-item categories don't silently drop
# the tail of the 30-item categories once they're exhausted.
SCENARIOS = [
    scenario
    for round_ in itertools.zip_longest(*_CATEGORY_LISTS, fillvalue=_MISSING)
    for scenario in round_
    if scenario is not _MISSING
]

assert len(SCENARIOS) == len(set(SCENARIOS)), "duplicate scenario text found in SCENARIOS"
assert len(SCENARIOS) == 170
