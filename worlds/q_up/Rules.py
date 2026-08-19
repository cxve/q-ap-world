from math import ceil
from typing import Dict, Callable, TYPE_CHECKING
from BaseClasses import CollectionState
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
    location_rules: Dict[str, Callable[[CollectionState], bool]]

    def __init__(self, world: QUPworld) -> None:
        self.player = world.player
        self.world = world
        self.location_rules = {
            "GAME_STORE": self.has_crystals,
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
                self.location_rules["Tier " + str(tier + 1) + " Challenge " + str(i + 1)] = (
                    self.has_challenge_req(0 if tier + 1 < 3 else 1 if tier + 1 < 4 else 2))

    def has_challenge_req(self, num_slots: int) -> Callable[[CollectionState], bool]:
        return lambda state: (state.has("PROGRESSIVE_CHALLENGES", self.player)
                              and state.has("PROGRESSIVE_CHALLENGE_SLOT", self.player, num_slots))

    def has_crystals(self, state: CollectionState) -> bool:
        return state.has("Crystals", self.player)

    def has_shop_req(self, location: str = "", prereq_rank: int = -1) -> Callable[[CollectionState], bool]:
        efficiency_crystals = self.world.options.itemPoolEfficiencyCrystals.value
        max_progressive_crystals = self.world.options.itemPoolProgressiveCrystalsNum.value

        def go(loc: str, count: int) -> int:
            if loc not in shopreqs: return count
            return go(shopreqs[loc], count + 1)
        distance = go(location, 0)

        def temp(state: CollectionState):
            reachable = location == "" or state.can_reach_location(location, self.player)
            crystals = (min(state.count("Crystals", self.player) * efficiency_crystals, max_progressive_crystals) >
                        distance * 2)
            rank = prereq_rank < 0 or self.has_difficulty_req_rank(prereq_rank)(state)
            return reachable and crystals and rank
        return temp

    def has_difficulty_req_level(self, level: int) -> Callable[[CollectionState], bool]:
        if level < 4: return lambda state: True
        req_level = self.calc_skill_req_level(level)
        skill_check = lambda state: state.qup_skill_num[self.player] >= req_level
        if level <= 11: return skill_check
        full_skill_check = lambda state: state.has("ITEM_SHOP", self.player) and skill_check(state)
        if 11 < level < 22: return lambda state: (state.has("PROGRESSIVE_CHALLENGES", self.player) or
            full_skill_check(state))
        return full_skill_check

    def has_difficulty_req_rank(self, rank: int) -> Callable[[CollectionState], bool]:
        if rank < 2: return lambda state: True
        req_rank = self.calc_skill_req_rank(rank)
        skill_check = lambda state: state.qup_skill_num[self.player] >= req_rank
        if rank <= 4: return skill_check
        full_skill_check = lambda state: state.has("ITEM_SHOP", self.player) and skill_check(state)
        if rank > 52: return lambda state: (
                state.count("PROGRESSIVE_QBLOCK_BREAKER", self.player) == 9 and full_skill_check(state))
        if rank > 48: return lambda state: (
                state.count("PROGRESSIVE_QBLOCK_BREAKER", self.player) >= 8 and full_skill_check(state))
        if rank > 46: return lambda state: (
                state.count("PROGRESSIVE_QBLOCK_BREAKER", self.player) >= 7 and full_skill_check(state))
        return full_skill_check

    def calc_skill_req_level(self, level: int) -> int:
        return min(round(pow(level, 0.87)*1.16,0), self.world.options.itemPoolTotalSkillNum.value)

    def calc_skill_req_rank(self, rank: int) -> int:
        return min(round(pow(rank,0.865)*1.09,0), self.world.options.itemPoolTotalSkillNum.value)

    def set_all_rules(self) -> None:
        multiworld = self.world.multiworld
        for region in multiworld.get_regions(self.player):
            for loc in region.locations:
                if loc.name in self.location_rules:
                    loc.access_rule = self.location_rules[loc.name]