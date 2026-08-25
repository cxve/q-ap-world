from .Data import corruption_shard_rewards, mail_crystal_rewards, crystal_rewards, shop_costs, shop_data
from math import ceil
from typing import Dict, Callable, TYPE_CHECKING
from BaseClasses import CollectionState
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
        self.location_rules = {}
        for k in shop_data.keys():
            self.location_rules[k] = self.has_shop_req(k)
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

    def has_shop_req(self, location: str) -> Callable[[CollectionState], bool]:
        data = shop_data[location]
        req_rank = data["rank"] if "rank" in data else -1
        efficiency_crystals = self.world.options.itemPoolEfficiencyCrystals.value
        efficiency_corruption_shards = self.world.options.itemPoolEfficiencyCorruptionShards.value
        min_crystals = self.world.options.itemPoolCrystalNum.value
        min_corruption_shards = self.world.options.itemPoolCorruptionShardNum.value

        def crystals(state: CollectionState):
            has_crystals = True
            count_crystals = min(state.count("Crystals", self.player) * efficiency_crystals, min_crystals)
            if count_crystals < min_crystals:
                crystals = sum(crystal_rewards[0:count_crystals])
                crystals += max(0, count_crystals - len(crystal_rewards)) * 100
                crystals += sum(mail_crystal_rewards[0:ceil((count_crystals + 1) / min_crystals * 10)])
                req_crystals = shop_costs[location]
                has_crystals = crystals * 2 > req_crystals
            else: has_crystals = state.has("PROGRESSIVE_ITEM_RECYCLING_SYSTEM", self.player, 2)
            has_rank = req_rank < 0 or self.has_difficulty_req_rank(req_rank)(state)
            return has_crystals and has_rank

        def corruption_shards(state: CollectionState):
            has_shards = True
            count_shards = min(state.count("Corruption Shards", self.player) * efficiency_corruption_shards, min_corruption_shards)
            if count_shards < min_corruption_shards:
                shards = sum(corruption_shard_rewards[0:count_shards])
                shards += max(0, count_shards - len(corruption_shard_rewards)) * 10
                req_shards = shop_costs[location]
                has_shards = shards * 1.5 > req_shards
            else: has_shards = state.has("PROGRESSIVE_CHALLENGES", self.player, 2)
            has_rank = req_rank < 0 or self.has_difficulty_req_rank(req_rank)(state)
            return has_shards and has_rank

        if not "corrupted" in shop_data[location]: return crystals
        else: return corruption_shards


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