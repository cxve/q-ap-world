from math import ceil
from typing import Dict, Callable, TYPE_CHECKING

import rule_builder.rules
from BaseClasses import CollectionState
from rule_builder.rules import True_, Has, And, HasGroupUnique, CanReachLocation
from .Data import skill_names_flat, shopreqs
from .Locations import rank_locations, level_locations

if TYPE_CHECKING:
    from . import QUPworld
else:
    QUPworld = object

# Based on Inscryption's implementation
class QUPrules:
    player: int
    world: QUPworld
    location_rules: Dict[str, rule_builder.rules.Rule]

    def __init__(self, world: QUPworld) -> None:
        self.player = world.player
        self.world = world
        self.location_rules = {
            "GAME_STORE": Has("Crystals"),
            "ITEM_SHOP": self.has_shop_req("GAME_STORE"),
            "INCREASED_WALLET_SIZE": self.has_shop_req("GAME_STORE"),
            "EVEN_BIGGER_WALLET": self.has_shop_req("INCREASED_WALLET_SIZE"),
            "JUMBO_WALLET": self.has_shop_req("EVEN_BIGGER_WALLET"),
            "FULLBODY_WALLET_SUIT": self.has_shop_req("JUMBO_WALLET"),
            "WORLDS_BIGGEST_WALLET": self.has_shop_req("FULLBODY_WALLET_SUIT"),
            "CHALLENGES": self.has_shop_req("GAME_STORE", 10),
            "ADDITIONAL_ITEM_SLOT_1": self.has_shop_req("ITEM_SHOP", 5),
            "ADDITIONAL_ITEM_SLOT_2": self.has_shop_req("ADDITIONAL_ITEM_SLOT_1"),
            "ADDITIONAL_ITEM_SLOT_3": self.has_shop_req("ADDITIONAL_ITEM_SLOT_2"),
            "ADDITIONAL_ITEM_SLOT_4": self.has_shop_req("ADDITIONAL_ITEM_SLOT_3"),
            "INCREASED_SHARD_SLOT_CAPACITY": self.has_shop_req("ITEM_SHOP", 10),
            "MAXIMUM_SHARD_SLOT_CAPACITY": self.has_shop_req("INCREASED_SHARD_SLOT_CAPACITY"),
            "HONOR_DUELS": self.has_shop_req(prereq_rank=25),
            "ADDITIONAL_SHOP_SLOT_1": self.has_shop_req("ITEM_SHOP", 5),
            "ADDITIONAL_SHOP_SLOT_2": self.has_shop_req("ADDITIONAL_SHOP_SLOT_1"),
            "ADDITIONAL_SHOP_SLOT_3": self.has_shop_req("ADDITIONAL_SHOP_SLOT_2"),
            "ADDITIONAL_SHOP_SLOT_4": self.has_shop_req("ADDITIONAL_SHOP_SLOT_3"),
            "ADDITIONAL_SHOP_SLOT_5": self.has_shop_req("ADDITIONAL_SHOP_SLOT_4"),
            "QBLOCK_BREAKER_1": self.has_shop_req(prereq_rank=35),
            "QBLOCK_BREAKER_2": self.has_shop_req("QBLOCK_BREAKER_1"),
            "QBLOCK_BREAKER_3": self.has_shop_req("QBLOCK_BREAKER_2"),
            "QBLOCK_BREAKER_4": self.has_shop_req("QBLOCK_BREAKER_3"),
            "QBLOCK_BREAKER_5": self.has_shop_req("QBLOCK_BREAKER_4"),
            "QBLOCK_BREAKER_6": self.has_shop_req("QBLOCK_BREAKER_5"),
            "QBLOCK_BREAKER_7": self.has_shop_req("QBLOCK_BREAKER_6"),
            "QBLOCK_BREAKER_8": self.has_shop_req("QBLOCK_BREAKER_7"),
            "QBLOCK_BREAKER_9": self.has_shop_req("QBLOCK_BREAKER_8"),
            "TRICKLE_DOWN_": self.has_shop_req("WORLDS_BIGGEST_WALLET"),
            "KNOWLEDGE_TRANSFER": self.has_shop_req(prereq_rank=40),
            "SHOP_REROLL": self.has_shop_req("ADDITIONAL_SHOP_SLOT_3"),
            "TURBO_SPEED": self.has_shop_req(prereq_rank=20),
            "EXTREMELY_COOL_SHOPS_SOMETIMES": self.has_shop_req("SHOP_REROLL", 35),
            "MORE_BETTERED_CHALLENGES": self.has_shop_req("EXTREMELY_COOL_SHOPS_SOMETIMES"),
            "ITEM_RECYCLING_SYSTEM": self.has_shop_req("ITEM_SHOP"),
            "ENHANCED_ITEM_RECYCLING__SORTING": self.has_shop_req("ITEM_RECYCLING_SYSTEM"),
            "SHOP_LOCK": self.has_shop_req("ADDITIONAL_SHOP_SLOT_1"),
            "ADDITIONAL_CHALLENGE_SLOT_1": self.has_shop_req("CHALLENGES", 25),
            "ADDITIONAL_CHALLENGE_SLOT_2": self.has_shop_req("ADDITIONAL_CHALLENGE_SLOT_1"),
            "NEW_BUSINESS_MODEL": self.has_shop_req(prereq_rank=10),
            "STATS_": self.has_shop_req(prereq_rank=5),
            "STATS_CHARTS": self.has_shop_req("STATS_", 9),
            "LOADOUTS": self.has_shop_req(prereq_rank=20)
        }
        for i in range(len(rank_locations)):
            self.location_rules[rank_locations[i]] = self.has_difficulty_req_rank(i + 1)
        for i in range(len(level_locations)):
            self.location_rules[level_locations[i]] = self.has_difficulty_req_level(i + 2)
        for tier in range(4):
            for i in range(10):
                name = "Tier " + str(tier + 1) + " Challenge " + str(i + 1)
                self.location_rules[name] = self.has_challenge_req(0 if tier + 1 < 3 else 1 if tier + 1 < 4 else 2)

    @staticmethod
    def has_challenge_req(num_slots: int) -> rule_builder.rules.Rule:
        return Has("PROGRESSIVE_CHALLENGES") & Has("PROGRESSIVE_CHALLENGE_SLOT", num_slots)

    def has_shop_req(self, location: str = "", prereq_rank: int = -1) -> rule_builder.rules.Rule:
        efficiency_crystals = self.world.options.itemPoolEfficiencyCrystals.value
        max_progressive_crystals = self.world.options.itemPoolProgressiveCrystalsNum.value

        def go(loc: str, count: int) -> int:
            if loc not in shopreqs: return count
            return go(shopreqs[loc], count + 1)
        distance = go(location, 0)

        reachable = True_() if location == "" else CanReachLocation(location)
        crystals = Has("Crystals", min(max_progressive_crystals, ceil(distance * 2 / efficiency_crystals)))
        rank = True_() if prereq_rank < 0 else self.has_difficulty_req_rank(prereq_rank)
        return reachable & crystals & rank

    def has_difficulty_req_level(self, level: int) -> rule_builder.rules.Rule:
        if level < 4: return True_()
        if level <= 11: return HasGroupUnique("Skill", self.calc_skill_req_level(level))
        rule = Has("ITEM_SHOP") & HasGroupUnique("Skill", self.calc_skill_req_level(level))
        if 11 < level < 22: return Has("PROGRESSIVE_CHALLENGES") | rule
        return rule

    def has_difficulty_req_rank(self, rank: int) -> rule_builder.rules.Rule:
        if rank < 2: return True_()
        if rank <= 4: return HasGroupUnique("Skill", self.calc_skill_req_rank(rank))
        rule = Has("ITEM_SHOP") & HasGroupUnique("Skill", self.calc_skill_req_rank(rank))
        if rank > 52: return Has("PROGRESSIVE_QBLOCK_BREAKER", 9) & rule
        if rank > 48: return Has("PROGRESSIVE_QBLOCK_BREAKER", 8) & rule
        if rank > 46: return Has("PROGRESSIVE_QBLOCK_BREAKER", 7) & rule
        return rule

    def calc_skill_req_level(self, level: int) -> int:
        return int(min(round(pow(level, 0.87)*1.16,0), self.world.options.itemPoolTotalSkillNum.value))

    def calc_skill_req_rank(self, rank: int) -> int:
        return int(min(round(pow(rank,0.865)*1.09,0), self.world.options.itemPoolTotalSkillNum.value))

    def set_all_rules(self) -> None:
        multiworld = self.world.multiworld
        for region in multiworld.get_regions(self.player):
            for loc in region.locations:
                if loc.name in self.location_rules:
                    self.world.set_rule(loc, self.location_rules[loc.name])