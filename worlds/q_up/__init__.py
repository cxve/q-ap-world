import math
from math import ceil
from typing import Any, Dict

from BaseClasses import Item, Tutorial, Region, ItemClassification
from Options import OptionGroup
from worlds.AutoWorld import World, WebWorld
from .Data import skill_names, skill_names_flat, signature_skill_names, signature_skill_names_flat, champ, \
    upgradable_skill_names_flat, features
from .Items import base_id, QUPitem, filler_items, all_items, signature_skills, upgradable_skills, generic_items, \
    ItemDict, categorized_signature_skills, feature_items, skills, item_name_groups
from .Locations import all_locations, QUPlocation, rank_location_ids, rank_locations, level_location_ids, \
    level_locations, feature_location_ids, build_challenge_location_ids, all_location_ids
from .Options import QUPoptions
from .Rules import QUPrules


class QUPweb(WebWorld):
    theme = "partyTime"

    option_groups = [
        OptionGroup("Item Pool", [
            Options.ItemPoolTotalSkillNum,
            Options.ItemPoolFixedSkillNum,
            Options.ItemPoolSkillUpgradeNum,
            Options.ItemPoolProgressiveCrystalsNum,
            Options.ItemPoolEfficiencyUpgradePoints,
            Options.ItemPoolEfficiencyCrystals
        ]),
        OptionGroup("Sanity", [
           Options.SanityNumChallenges,
            Options.SanityNumChallengesTier4,
        ])
    ]

    guide_en = Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up the Q-UP Archipelago Multiworld",
        "English",
        "setup_en.md",
        "setup/en",
        ["cxve"]
    )

    tutorials = [guide_en]

    bug_report_page = "https://github.com/cxve/Q-AP-world"


class QUPworld(World):
    """
    Sick of long queues, unfair matchups, and arbitrary reflex tests? Try Q-UP, the coin flipping eSport. It's one part
    clicker, one part multiplayer strategy game, one part demented capitalism simulator, and 100% completely random.
    """
    game = "Q-UP"
    web = QUPweb()
    options_dataclass = QUPoptions
    options = QUPoptions
    all_items = all_items
    item_name_to_id = {item["name"]: i + base_id for i, item in enumerate(all_items)}
    all_locations = all_locations
    location_name_to_id = all_location_ids
    origin_region_name = "Game"
    progressive_crystal_number = 0
    item_name_groups = item_name_groups
    items_added = 0

    def get_filler_item_name(self) -> str:
        return self.random.choice(filler_items)["name"]

    def create_item(self, name: str) -> Item:
        item_id = self.item_name_to_id[name]
        item_data = self.all_items[item_id - base_id]
        return QUPitem(name, item_data["classification"], item_id, self.player)

    def create_items(self) -> None:
        num_upgrade_points = self.options.itemPoolSkillUpgradeNum.value
        num_crystals = self.options.itemPoolProgressiveCrystalsNum.value

        num_challenges = self.options.sanityNumChallenges.value

        efficiency_upgrade_points = self.options.itemPoolEfficiencyUpgradePoints.value
        efficiency_crystals = self.options.itemPoolEfficiencyCrystals.value

        champ_id = self.options.champ.value
        champ_key = champ[champ_id]

        my_flex_skills = set(skill_names_flat) - set(signature_skill_names_flat)
        my_flex_skills = list(my_flex_skills) + list(signature_skill_names[champ_key])
        my_flex_skills = set(my_flex_skills) - set(upgradable_skill_names_flat)
        my_flex_skills = list(my_flex_skills)

        my_fixed_signature_skills = list(set(upgradable_skill_names_flat) & set(signature_skill_names[champ_key]))
        my_fixed_skills = set(upgradable_skill_names_flat) - set(signature_skill_names_flat)
        my_fixed_skills = list(my_fixed_skills) + list(my_fixed_signature_skills)

        num_fixed_skills = self.options.itemPoolFixedSkillNum.value
        num_total_skills = self.options.itemPoolTotalSkillNum.value
        num_fixed_skills = num_fixed_skills if num_fixed_skills < num_total_skills else num_total_skills

        def create_items(pool, num):
            self.random.shuffle(pool)
            for i in range(num):
                new_item = self.create_item(pool[i])
                self.multiworld.itempool.append(new_item)
                self.items_added += 1

        create_items(list(set(my_fixed_skills)), num_fixed_skills)
        create_items(list(set(my_flex_skills)), num_total_skills - num_fixed_skills)

        # just add shop items to the pool
        for item in feature_items:
            for _ in range(item["count"]):
                new_item = self.create_item(item["name"])
                self.multiworld.itempool.append(new_item)
                self.items_added += 1

        _generic_items = generic_items.copy()
        _generic_items[0]["count"] = ceil(num_upgrade_points / efficiency_upgrade_points)
        _generic_items[1]["count"] = ceil(num_crystals / efficiency_crystals)

        # add generic items to the pool
        for item in _generic_items:
            for _ in range(item["count"]):
                new_item = self.create_item(item["name"])
                self.multiworld.itempool.append(new_item)
                self.items_added += 1

        filler_count = len(self.all_locations) + num_challenges - self.items_added
        filler_count = filler_count if filler_count > 0 else 0
        for i in range(filler_count):
            index = i % len(filler_items)
            filler_item = filler_items[index]
            new_item = self.create_item(filler_item["name"])
            self.multiworld.itempool.append(new_item)

    def create_regions(self) -> None:
        self.multiworld.regions.append(Region("Game", self.player, self.multiworld))
        region = self.get_region("Game")
        region.add_locations({ location: rank_location_ids[location] for location in rank_locations })
        region.add_locations({ location: level_location_ids[location] for location in level_locations })
        region.add_locations({ location: feature_location_ids[location] for location in features })
        challenges = [0, 0, 0, 0]
        for i in range(self.options.sanityNumChallenges.value):
            if challenges[3] < self.options.sanityNumChallengesTier4.value and challenges[2] > challenges[3] + 1:
                challenges[3] += 1
            elif challenges[1] > challenges[2] + 1: challenges[2] += 1
            elif challenges[0] > challenges[1] + 1: challenges[1] += 1
            else: challenges[0] += 1
        for i in range(len(challenges)):
            if challenges[i] < 1: continue
            region.add_locations(build_challenge_location_ids(i + 1, challenges[i]))
        region.locations.append(QUPlocation(self.player,"Novice",None, region))

    def create_event(self, event: str) -> QUPitem:
        # while we are at it, we can also add a helper to create events
        return QUPitem(event, ItemClassification.progression, None, self.player)

    def set_rules(self) -> None:
        Rules.QUPrules(self).set_all_rules()
        self.multiworld.get_location("Novice", self.player).place_locked_item(self.create_event("Victory"))
        self.multiworld.completion_condition[self.player] = lambda state: state.has("Victory", self.player)

    def fill_slot_data(self) -> Dict[str, Any]:
        return self.options.as_dict("champ",
                                    "itemPoolEfficiencyCrystals",
                                    "itemPoolEfficiencyUpgradePoints",
                                    "sanityNumChallenges",
                                    "sanityNumChallengesTier4")

