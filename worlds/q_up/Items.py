from dataclasses import field

from BaseClasses import Item, ItemClassification
from typing import TypedDict, List

from .Data import hypernode_names, skill_names_flat, tag_to_skill, skill_names, upgradable_skill_names, signature_skill_names

# apparently, can be any number greater than 0
base_id = 1_000_000


class QUPitem(Item):
    name: str = "Q-UP"

class ItemDict(TypedDict):
    name: str
    count: int
    classification: ItemClassification

def get_ids(items: List[ItemDict], offset: int): return {item["name"]: i + offset + base_id for i, item in enumerate(items)}

generic_items: List[ItemDict] = [
    {
        "name": "Upgrade Point",
        "count": 35,
        "classification": ItemClassification.progression_deprioritized
    },
    {
        "name": "Crystals",
        "count": 1,
        "classification": ItemClassification.progression_deprioritized
    },
    {
        "name": "Corruption Shards",
        "count": 1,
        "classification": ItemClassification.progression_deprioritized
    },
    {
        "name": "Gold",
        "count": 0,
        "classification": ItemClassification.filler
    }
]
filler_items = ["Crystals", "Gold", "Corruption Shards", "Crystals"]
generic_item_ids = get_ids(generic_items, 1000 + 200)

def build(x): 
    return [{"name": name, "count": 1, "classification": ItemClassification.progression | ItemClassification.useful, 
            "champ": i} for i, champ in enumerate(x) for name in x[champ]]

# list of all skills
skills: List[ItemDict] = build(skill_names)

# list of all upgradable skills
upgradable_skills: List[ItemDict] = build(upgradable_skill_names)

skill_ids = get_ids(skills, 0)

# list of all signature skills
signature_skills: List[ItemDict] = build(signature_skill_names)

# this list is to
categorized_signature_skills = [[{"name": name, "count": 1, "classification": ItemClassification.progression} for
                                 name in signature_skill_names[cat]] for cat in signature_skill_names]

# list of all hypernode_names
hypernodes: List[ItemDict] = [{"name": name, "count": 1, "classification": ItemClassification.progression |
                                ItemClassification.useful} for name in hypernode_names]

hypernode_ids = get_ids(hypernodes, 1000 + 100)

feature_items: List[ItemDict] = [
    {"name": "GAME_STORE", "count": 0, "classification": ItemClassification.filler},
    {"name": "ITEM_SHOP", "count": 1, "classification": ItemClassification.progression | ItemClassification.useful},
    {"name": "PROGRESSIVE_WALLET_SIZE", "count": 5, "classification": ItemClassification.progression},
    {"name": "PROGRESSIVE_ITEM_RECYCLING_SYSTEM", "count": 2, "classification": ItemClassification.progression},
    {"name": "PROGRESSIVE_CHALLENGES", "count": 2, "classification": ItemClassification.progression},
    {"name": "PROGRESSIVE_ITEM_SLOT", "count": 4, "classification": ItemClassification.progression},
    {"name": "PROGRESSIVE_SHARD_SLOT_CAPACITY", "count": 2, "classification": ItemClassification.progression},
    {"name": "HONOR_DUELS", "count": 1, "classification": ItemClassification.useful},
    {"name": "PROGRESSIVE_SHOP_SLOT", "count": 5, "classification": ItemClassification.filler},
    {"name": "PROGRESSIVE_QBLOCK_BREAKER", "count": 9, "classification": ItemClassification.progression},
    {"name": "TRICKLE_DOWN_", "count": 1, "classification": ItemClassification.filler},
    {"name": "KNOWLEDGE_TRANSFER", "count": 1, "classification": ItemClassification.filler},
    #{"name": "TURBO_SPEED", "count": 1, "classification": ItemClassification.progression}, # unlocked by default
    {"name": "PROGRESSIVE_CHALLENGE_SLOT", "count": 2, "classification": ItemClassification.progression},
    {"name": "SHOP_LOCK", "count": 1, "classification": ItemClassification.useful},
    {"name": "NEW_BUSINESS_MODEL", "count": 0, "classification": ItemClassification.filler},
    {"name": "PROGRESSIVE_STATS", "count": 3, "classification": ItemClassification.filler},
    {"name": "LOADOUTS", "count": 0, "classification": ItemClassification.filler},
    {"name": "PROGRESSIVE_SHOP_REROLL", "count": 2, "classification": ItemClassification.useful}]

feature_ids = get_ids(feature_items, 1000)

all_items = skills + feature_items + hypernodes + generic_items

all_item_ids =  {**skill_ids, **feature_ids, **hypernode_ids, **generic_item_ids}

all_items_with_keys = {item["name"]: item for item in all_items}

item_name_groups: dict[str, set[str]] = {
    "Skill": set(skill_names_flat),
    "Trigger Skill": set(tag_to_skill["trigger"]),
    "Flat Q Skill": set(tag_to_skill["q_flat"]),
    "Q Mult Skill": set(tag_to_skill["q_mult"]),

    "Hypernode": set(hypernode_names),
    "Feature": set([feat["name"] for feat in feature_items])
}
