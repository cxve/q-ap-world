from .Data import corruption_shard_rewards, mail_crystal_rewards, crystal_rewards, shop_costs, shop_data
from math import ceil, floor
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
        self.location_rules = {
            "Double Triple Set": self.has_recycling_set_req(), 
            "Six of a Kind Set": self.has_recycling_set_req(), 
            "Two by Four Set": self.has_recycling_set_req(), 
            "Four of a Kind Set": self.has_recycling_set_req(), 
            "Three Pairs Set": self.has_recycling_set_req(), 
            "Three of a Kind Set": self.has_recycling_set_req(), 
            "Two Pairs Set": self.has_recycling_set_req(),
            "Typical Set": self.has_recycling_set_req(), 
            "Timeline Saturated Set": self.has_recycling_set_req(), 
            "PVP Set": self.has_recycling_set_req("HONOR_DUELS"),
        }
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

    def has_recycling_set_req(self, add_req: str | None = None) -> Callable[[CollectionState], bool]:
        has_recycling = lambda state: state.has("PROGRESSIVE_ITEM_RECYCLING_SYSTEM", self.player, 2)
        if add_req == None: return has_recycling
        else: return lambda state: state.has(add_req, self.player) and has_recycling(state)

    def has_challenge_req(self, num_slots: int) -> Callable[[CollectionState], bool]:
        return lambda state: (state.has("PROGRESSIVE_CHALLENGES", self.player)
                              and state.has("PROGRESSIVE_CHALLENGE_SLOT", self.player, num_slots))

    def has_crystals(self, state: CollectionState) -> bool:
        return state.has("Crystals", self.player)

    def count_effective_skills(self, state, max: int) -> int:
        if state.qup_trigger_skill_num[self.player] > 0 or state.qup_skill_num[self.player] >= max: return state.qup_skill_num[self.player]
        else: return state.qup_triggerable_skill_num[self.player]

    def has_shop_req(self, location: str) -> Callable[[CollectionState], bool]:
        data = shop_data[location]
        cost = shop_costs[location]
        num_skills = self.world.options.itemPoolTotalSkillNum.value
        req_rank = data["rank"] if "rank" in data else 0
        if req_rank < 30 and data["cost"] > 300: req_rank = 30
        efficiency_crystals = self.world.options.itemPoolEfficiencyCrystals.value
        efficiency_corruption_shards = self.world.options.itemPoolEfficiencyCorruptionShards.value
        min_crystals = self.world.options.itemPoolCrystalNum.value
        min_corruption_shards = self.world.options.itemPoolCorruptionShardNum.value

        def crystals(state: CollectionState):      
            if req_rank > 0 and not self.has_difficulty_req_rank(req_rank)(state): return False
            count_recycling = state.count("PROGRESSIVE_ITEM_RECYCLING_SYSTEM", self.player)
            count_crystals = state.count("Crystals", self.player) * efficiency_crystals * (count_recycling + 1)
            crystals = sum(crystal_rewards[0:count_crystals])
            crystals += max(0, count_crystals - len(crystal_rewards)) * 100
            crystals += sum(mail_crystal_rewards[0:floor(count_crystals / 2) + 1])
            has_crystals = crystals >= cost or (count_crystals >= min_crystals and count_recycling == 2)
            return has_crystals

        def corruption_shards(state: CollectionState):
            if req_rank > 0 and not self.has_difficulty_req_rank(req_rank)(state): return False
            count_challenges = state.count("PROGRESSIVE_CHALLENGES", self.player)
            count_shards = state.count("Corruption Shards", self.player) * efficiency_corruption_shards * (count_challenges + 1)
            shards = sum(corruption_shard_rewards[0:count_shards])
            shards += max(0, count_shards - len(corruption_shard_rewards)) * 10
            has_shards = shards >= cost or (count_shards >= min_corruption_shards and count_challenges == 2)
            return has_shards

        if "corrupted" in data: return corruption_shards
        else: return crystals

    def skill_dist_check(self, num_current, num_max):
        num_gates = self.world.options.skillDistGates.value
        if num_gates < 2 or num_current >= num_max: return lambda state: True
        step = floor(num_current / num_max * num_gates)
        num_skill_cat = [floor(val / num_gates * step) for val in self.world.num_skill_cat]
        def check(state):
            return state.qup_dist_q_flat_num[self.player] >= num_skill_cat[0] and \
                state.qup_dist_q_mult_num[self.player] >= num_skill_cat[1] and \
                state.qup_dist_trigger_num[self.player] >= num_skill_cat[2] and \
                state.qup_dist_gold_num[self.player] >= num_skill_cat[3] and \
                state.qup_dist_xp_num[self.player] >= num_skill_cat[4] and \
                state.qup_dist_other_num[self.player] >= num_skill_cat[5]
        return check

    def has_difficulty_req_level(self, level: int) -> Callable[[CollectionState], bool]:
        if level < 6: return lambda state: True
        req_level = self.calc_skill_req_level(level)
        skill_dist_check = self.skill_dist_check(level, 50)
        num_skills = self.world.options.itemPoolTotalSkillNum.value
        skill_check = lambda state: self.count_effective_skills(state, num_skills) >= req_level and skill_dist_check(state)
        if level <= 11: return lambda state: state.has("PROGRESSIVE_CHALLENGES", self.player) or skill_check(state)
        skill_check_2 = lambda state: state.has("ITEM_SHOP", self.player) and skill_check(state)
        skill_check_3 = lambda state: state.has("PROGRESSIVE_CHALLENGES", self.player) and skill_check_2(state)
        if 11 < level < 15: return lambda state: state.has("PROGRESSIVE_CHALLENGES", self.player) or skill_check_2(state)
        if 15 <= level < 22: return lambda state: state.has("PROGRESSIVE_CHALLENGES", self.player)
        return skill_check_3

    def has_difficulty_req_rank(self, rank: int) -> Callable[[CollectionState], bool]:
        if rank < 3: return lambda state: True
        req_rank = self.calc_skill_req_rank(rank)
        skill_dist_check = self.skill_dist_check(rank, 55)
        num_skills = self.world.options.itemPoolTotalSkillNum.value
        skill_check = lambda state: self.count_effective_skills(state, num_skills) >= req_rank and skill_dist_check(state)
        if rank <= 4: return skill_check
        skill_check_2 = lambda state: state.has("ITEM_SHOP", self.player) and skill_check(state)
        if rank <= 15: return skill_check_2
        skill_check_3 = lambda state: state.has("PROGRESSIVE_CHALLENGES", self.player) and skill_check_2(state)
        if rank > 51: return lambda state: (
                state.count("PROGRESSIVE_QBLOCK_BREAKER", self.player) >= 9 and skill_check_3(state))
        if rank > 44: return lambda state: (
                state.count("PROGRESSIVE_QBLOCK_BREAKER", self.player) >= 8 and skill_check_3(state))
        if rank > 42: return lambda state: (
                state.count("PROGRESSIVE_QBLOCK_BREAKER", self.player) >= 7 and skill_check_3(state))
        if rank > 40: return lambda state: (
                state.count("PROGRESSIVE_QBLOCK_BREAKER", self.player) >= 6 and skill_check_3(state))
        if rank > 39: return lambda state: (
                state.count("PROGRESSIVE_QBLOCK_BREAKER", self.player) >= 5 and skill_check_3(state))
        if rank > 38: return lambda state: (
                state.count("PROGRESSIVE_QBLOCK_BREAKER", self.player) >= 4 and skill_check_3(state))
        if rank > 37: return lambda state: (
                state.count("PROGRESSIVE_QBLOCK_BREAKER", self.player) >= 3 and skill_check_3(state))
        if rank > 36: return lambda state: (
                state.count("PROGRESSIVE_QBLOCK_BREAKER", self.player) >= 2 and skill_check_3(state))
        if rank > 35: return lambda state: (
                state.count("PROGRESSIVE_QBLOCK_BREAKER", self.player) >= 1 and skill_check_3(state))
        return skill_check_3

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