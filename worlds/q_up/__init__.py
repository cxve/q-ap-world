from math import floor, ceil
from typing import Any, Dict

from BaseClasses import Item, Tutorial, Region, ItemClassification, CollectionState
from Options import OptionError
from worlds.AutoWorld import World, WebWorld
from .Data import skill_names, skill_names_flat, signature_skill_names, signature_skill_names_flat, champ, \
    upgradable_skill_names_flat, features, skill_cat_to_idx, tagged_skills, special_require_any, tag_to_skill, \
    special_require_specific, hypernode_names
from .Items import base_id, QUPitem, all_item_ids, all_items_with_keys, generic_items, ItemDict, feature_items, item_name_groups, filler_items
from .Locations import all_locations, QUPlocation, rank_location_ids, rank_locations, level_location_ids, \
    level_locations, feature_location_ids, build_challenge_location_ids, all_location_ids
from .Options import QUPoptions, option_groups
from .Rules import QUPrules
from .Logic import QUPstate

class QUPweb(WebWorld):
    theme = "partyTime"

    option_groups = option_groups

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
    options: QUPoptions
    all_items = all_items_with_keys
    item_name_to_id = all_item_ids
    all_locations = all_locations
    location_name_to_id = all_location_ids
    origin_region_name = "Game"
    progressive_crystal_number = 0
    item_name_groups = item_name_groups
    items_added = 1 # one location always has the victory condition as item!

    def collect(self, state: CollectionState, item: Item) -> bool:
        change = super().collect(state, item)
        if change and item.name in skill_names_flat: state.qup_skill_num[self.player] += 1
        return change

    def remove(self, state: CollectionState, item: Item) -> bool:
        change = super().remove(state, item)
        if change and item.name in skill_names_flat: state.qup_skill_num[self.player] -= 1
        return change

    def generate_early(self):
        # make sure player YAML does not require more items than it has locations
        num_challenges = self.options.sanityNumChallenges.value
        sum_locations = len(self.all_locations) + num_challenges

        efficiency_upgrade_points = self.options.itemPoolEfficiencyUpgradePoints.value
        efficiency_crystals = self.options.itemPoolEfficiencyCrystals.value

        num_upgrade_points = ceil(self.options.itemPoolSkillUpgradeNum.value / efficiency_upgrade_points)
        num_crystals = ceil(self.options.itemPoolCrystalNum.value / efficiency_crystals)
        num_hypernodes = self.options.itemPoolHypernodeNum.value
        num_total_skills = self.options.itemPoolTotalSkillNum.value
        num_feature_items = sum([feat["count"] if feat["classification"] != ItemClassification.filler else 0\
                                 for feat in feature_items])
        num_buffer = 4 # this is specifically to avoid fill errors and timeouts caused by restrictive starts

        sum_items = num_hypernodes + num_total_skills + num_feature_items + num_buffer
        sum_items_suggestion = num_upgrade_points + num_crystals
        if sum_items + sum_items_suggestion > sum_locations:
            while efficiency_upgrade_points < 4 or efficiency_crystals < 4:
                if efficiency_upgrade_points <= efficiency_crystals: efficiency_upgrade_points += 1
                else: efficiency_crystals += 1
                num_upgrade_points = ceil(self.options.itemPoolSkillUpgradeNum.value / efficiency_upgrade_points)
                num_crystals = ceil(self.options.itemPoolCrystalNum.value / efficiency_crystals)
                sum_items_suggestion = num_upgrade_points + num_crystals
                if sum_items + sum_items_suggestion < sum_locations:
                    raise OptionError(f"Your YAML generates too many progression items!\n"
                                      f"Here is a suggested fix: In your YAML file, please set Upgrade Point "
                                      f"Efficiency to at least {efficiency_upgrade_points} and Crystal Efficiency to "
                                      f"at least {efficiency_crystals}!")

    def get_filler_item_name(self) -> str:
        return self.random.choice(filler_items)

    def create_item(self, name: str) -> Item:
        item_id = self.item_name_to_id[name]
        item_data = self.all_items[name]
        return QUPitem(name, item_data["classification"], item_id, self.player)

    def create_items(self) -> None:
        num_upgrade_points = self.options.itemPoolSkillUpgradeNum.value
        num_crystals = self.options.itemPoolCrystalNum.value
        num_fixed_skills = self.options.itemPoolFixedSkillNum.value
        num_total_skills = self.options.itemPoolTotalSkillNum.value
        num_fixed_skills = num_fixed_skills if num_fixed_skills < num_total_skills else num_total_skills
        num_hypernodes = self.options.itemPoolHypernodeNum.value

        num_challenges = self.options.sanityNumChallenges.value

        efficiency_upgrade_points = self.options.itemPoolEfficiencyUpgradePoints.value
        efficiency_crystals = self.options.itemPoolEfficiencyCrystals.value

        champ_id = self.options.champ.value
        champ_key = champ[champ_id]

        my_flex_skills = set(skill_names_flat) - set(signature_skill_names_flat)
        my_flex_skills = list(my_flex_skills) + list(signature_skill_names[champ_key])
        my_flex_skills = set(my_flex_skills) - set(upgradable_skill_names_flat)
        my_flex_skills = list(my_flex_skills)
        my_flex_skills.sort()

        pool_fixed = set(upgradable_skill_names_flat) - set(signature_skill_names_flat)
        pool_fixed = list(pool_fixed) + list(set(upgradable_skill_names_flat) & set(signature_skill_names[champ_key]))
        pool_fixed.sort()

        dist_mode = self.options.skillDistMode.value
        dist_gates = self.options.skillDistGates.value

        # list of all valid skills for this champ
        my_skills = set(skill_names_flat) - set(signature_skill_names_flat)
        my_skills = list(my_skills) + list(signature_skill_names[champ_key])
        my_skills.sort()

        def skill_add(skills, tags, skill):
            # if skill is invalid for this champ, skip
            if skill not in my_skills: return

            # if skill is already selected, skip
            if skill in skills: return

            _skills = skills.copy()
            _tags = tags.copy()

            # if this skill tag category is full, skip
            if dist_gates >= 0:
                skill_tags = tagged_skills[skill]
                if len(skill_tags) > 0 and skill_tags[0] in skill_cat_to_idx:
                    tag = skill_cat_to_idx[skill_tags[0]]
                else:
                    tag = 5
                if _tags[tag] >= num_skill_cat[tag]: return
                _tags[tag] += 1

            # assume this skill is going to be added
            _skills.append(skill)

            # check tag dependencies
            if skill in special_require_any and len(set(skills) & set(tag_to_skill[special_require_any[skill]])) < 1:
                skill_add_from_pool(_skills, _tags, tag_to_skill[special_require_any[skill]], 1)
                # was not able to add this skill, skip!
                if len(_skills) is len(skills): return

            num_skill_current = len(_skills)
            # check specific dependencies
            if skill in special_require_specific and special_require_specific[skill] not in _skills:
                skill_add(_skills, _tags, special_require_specific[skill])
                # was not able to add this skill, skip!
                if len(_skills) is num_skill_current: return

            # all checks passed, add skill!
            for i in range(len(tags)): tags[i] = _tags[i]
            skills.extend(set(skills) ^ set(_skills))

        def skill_add_from_pool(skills, tags, _pool, num):
            pool = _pool.copy()
            self.random.shuffle(pool)
            num_start = len(skills)
            for i in range(len(pool)):
                skill_add(skills, tags, pool[i])
                if len(skills) - num_start >= num: break
            skills.sort()

        if dist_gates >= 0:
            dist = [
                self.options.skillDistQFlat.value,
                self.options.skillDistQMult.value,
                self.options.skillDistTrigger.value,
                self.options.skillDistGold.value,
                self.options.skillDistXP.value,
                self.options.skillDistOther.value,
            ]
            dist_signature = self.options.skillDistSignature.value

            # apply approx mode
            if dist_mode == 1:
                if dist_signature > 6: dist_signature += self.random.choice([-3, 0, 3])
                for i in range(len(dist)):
                    x = dist[i]
                    if x > 1:
                        x += self.random.choice([-1, 0, 1])
                        dist[i] = x

            num_signature = ceil(dist_signature / 100 * num_total_skills)

            # normalize weights
            dist_normal = [d / sum(dist) for d in dist]

            # convert normalized weights to skill amounts
            dist_skill_total = 0
            dist_skill_exact = []

            # first: remove rare skill categories from distribution
            for i in range(len(dist_normal)):
                d = dist_normal[i]
                num = d * num_total_skills
                if 0 < num < 1:
                    num = 1
                    dist_skill_total += num
                    dist_normal[i] = 0
                dist_skill_exact.append(num)

            # then: recalculate remaining skill amount and distribution
            dist_normal = [d / sum(dist_normal) for d in dist_normal]
            for i in range(len(dist_skill_exact)):
                num = dist_skill_exact[i]
                d = dist_normal[i]
                if num > 1: dist_skill_exact[i] = d * (num_total_skills - dist_skill_total)

            # then split remainder
            num_skill_cat = [floor(d) for d in dist_skill_exact]
            remainder = num_total_skills - sum(num_skill_cat)
            fractions = [(d % 1, i) for i, d in enumerate(dist_skill_exact)]
            fractions.sort(reverse=True)
            for i in range(remainder): num_skill_cat[fractions[i][1]] += 1

            # create skill pools
            pool_signature = signature_skill_names[champ_key].copy()

            other_skills = my_flex_skills.copy()
            pool_tags = []
            for key in skill_cat_to_idx:
                _skills = []
                for skill in tag_to_skill[key]:
                    if skill in my_flex_skills:
                        _skills.append(skill)
                        if skill in other_skills: other_skills.remove(skill)
                pool_tags.append(_skills)
            pool_tags.append(other_skills)

            # fill the skill slots
            skills = []
            tags = [0, 0, 0, 0, 0, 0]

            skill_add_from_pool(skills, tags, pool_fixed, num_fixed_skills)
            skill_add_from_pool(skills, tags, pool_signature, num_signature)
            for i in range(6):
                skill_add_from_pool(skills, tags, pool_tags[i], num_skill_cat[i] - tags[i])

            pool_unused = list(set(my_flex_skills) ^ set(skills))
            pool_unused.sort()
            skill_add_from_pool(skills, tags, pool_unused, num_total_skills - len(skills))
        else:
            skills = []
            skill_add_from_pool(skills, [], pool_fixed, num_fixed_skills)
            skill_add_from_pool(skills, [], my_flex_skills, num_total_skills - len(skills))

        def create_items(pool):
            for i in range(len(pool)):
                new_item = self.create_item(pool[i])
                self.multiworld.itempool.append(new_item)
                self.items_added += 1

        create_items(skills)
        _hypernodes = hypernode_names.copy()
        self.random.shuffle(_hypernodes)
        create_items(_hypernodes[:num_hypernodes])

        _generic_items = generic_items.copy()
        _generic_items[0]["count"] = ceil(num_upgrade_points / efficiency_upgrade_points)
        _generic_items[1]["count"] = ceil(num_crystals / efficiency_crystals)

        # add generic items to the pool
        for item in _generic_items:
            for _ in range(item["count"]):
                new_item = self.create_item(item["name"])
                self.multiworld.itempool.append(new_item)
                self.items_added += 1

        # just add shop items to the pool
        for item in [item for item in feature_items if item["classification"] != ItemClassification.filler]:
            for _ in range(item["count"]):
                new_item = self.create_item(item["name"])
                self.multiworld.itempool.append(new_item)
                self.items_added += 1

        feature_filler = [item for item in feature_items if item["classification"] == ItemClassification.filler]
        self.random.shuffle(feature_filler)
        for item in feature_filler:
            for _ in range(item["count"]):
                if self.items_added >= len(self.all_locations) + num_challenges: break
                new_item = self.create_item(item["name"])
                self.multiworld.itempool.append(new_item)
                self.items_added += 1

        filler_count = len(self.all_locations) + num_challenges - self.items_added
        filler_count = filler_count if filler_count > 0 else 0
        for i in range(filler_count):
            index = i % len(filler_items)
            new_item = self.create_item(filler_items[index])
            self.multiworld.itempool.append(new_item)

    def create_regions(self) -> None:
        goal_rank = self.options.goal.value
        self.multiworld.regions.append(Region("Game", self.player, self.multiworld))
        region = self.get_region("Game")
        _rank_location_ids = rank_location_ids.copy()
        _rank_location_ids[rank_locations[goal_rank - 1]] = None
        region.add_locations({ location: _rank_location_ids[location] for location in rank_locations })
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

    def create_event(self, event: str) -> QUPitem:
        # while we are at it, we can also add a helper to create events
        return QUPitem(event, ItemClassification.progression, None, self.player)

    def set_rules(self) -> None:
        QUPrules(self).set_all_rules()
        goal_rank = self.options.goal.value
        goal_rank_name = rank_locations[goal_rank - 1]
        self.multiworld.get_location(goal_rank_name, self.player).place_locked_item(self.create_event("Victory"))
        self.multiworld.completion_condition[self.player] = lambda state: state.has("Victory", self.player)

    def fill_slot_data(self) -> Dict[str, Any]:
        return self.options.as_dict("champ", "goal",
                                    "itemPoolEfficiencyCrystals",
                                    "itemPoolEfficiencyUpgradePoints",
                                    "sanityNumChallenges",
                                    "sanityNumChallengesTier4",
                                    "itemPoolCrystalNum",
                                    "itemPoolCorruptionShardNum",
                                    "itemPoolTotalSkillNum") | { "version": self.world_version.as_simple_string() }