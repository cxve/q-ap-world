from dataclasses import field

from BaseClasses import Item, ItemClassification
from typing import TypedDict, List

from worlds.q_up import hypernode_names
from worlds.q_up.Data import skill_names, upgradable_skill_names, signature_skill_names, features

# apparently, can be any number greater than 0
base_id = 1_000_000


class QUPitem(Item):
    name: str = "Q-UP"

class ItemDict(TypedDict):
    name: str
    count: int
    classification: ItemClassification

generic_items: List[ItemDict] = [
    {
        "name": "Upgrade Point",
        "count": 35,
        "classification": ItemClassification.progression
    },
    {
        "name": "Crystals",
        "count": 1,
        "classification": ItemClassification.progression
    }
]

filler_items: List[ItemDict] = [
    {
        "name": "Gold",
        "count": 1,
        "classification": ItemClassification.filler
    },
    {
        "name": "Corruption Shards",
        "count": 1,
        "classification": ItemClassification.filler
    },
    {
        "name": "Crystals",
        "count": 1,
        "classification": ItemClassification.progression
    }
]

build = lambda x: [{"name": name, "count": 1, "classification":
    ItemClassification.progression | ItemClassification.useful, "champ": i} for i, champ in enumerate(x) for name in
                   x[champ]]

# list of all skills
skills: List[ItemDict] = build(skill_names)

# list of all upgradable skills
upgradable_skills: List[ItemDict] = build(upgradable_skill_names)

# list of all hypernode_names
hypernodes: List[ItemDict] = [{"name": name, "count": 1, "classification": ItemClassification.progression |
                                ItemClassification.useful} for name in hypernode_names]

# list of all signature skills
signature_skills: List[ItemDict] = build(signature_skill_names)

# this list is to
categorized_signature_skills = [[{"name": name, "count": 1, "classification": ItemClassification.progression} for
                                 name in signature_skill_names[cat]] for cat in signature_skill_names]

feature_items: List[ItemDict] = [
    {"name": "GAME_STORE", "count": 1, "classification": ItemClassification.filler},
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
    {"name": "NEW_BUSINESS_MODEL", "count": 1, "classification": ItemClassification.filler},
    {"name": "PROGRESSIVE_STATS", "count": 3, "classification": ItemClassification.filler},
    {"name": "LOADOUTS", "count": 1, "classification": ItemClassification.filler},
    {"name": "PROGRESSIVE_SHOP_REROLL", "count": 2, "classification": ItemClassification.useful}]

all_items = skills + hypernodes + filler_items + generic_items + feature_items

item_name_groups = ({
    "Skills": skill_names,
    "Shop Upgrades": features
})
