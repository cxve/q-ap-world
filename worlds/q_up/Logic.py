from BaseClasses import CollectionState, MultiWorld
from worlds.AutoWorld import LogicMixin

class QUPstate(LogicMixin):
    qup_skill_num: dict[int, int]  # per player

    def init_mixin(self, multiworld: MultiWorld) -> None:
        # Initialize per player with the corresponding "nothing" value, such as 0 or an empty set.
        # You can also use something like Collections.defaultdict
        self.qup_skill_num = { player: 0 for player in multiworld.get_game_players("Q-UP") }
        self.qup_triggerable_skill_num  = { player: 0 for player in multiworld.get_game_players("Q-UP") }
        self.qup_trigger_skill_num  = { player: 0 for player in multiworld.get_game_players("Q-UP") }

        self.qup_dist_q_flat_num = { player: 0 for player in multiworld.get_game_players("Q-UP") }
        self.qup_dist_q_mult_num = { player: 0 for player in multiworld.get_game_players("Q-UP") }
        self.qup_dist_trigger_num = { player: 0 for player in multiworld.get_game_players("Q-UP") }
        self.qup_dist_gold_num = { player: 0 for player in multiworld.get_game_players("Q-UP") }
        self.qup_dist_xp_num = { player: 0 for player in multiworld.get_game_players("Q-UP") }
        self.qup_dist_other_num = { player: 0 for player in multiworld.get_game_players("Q-UP") }

    def copy_mixin(self, new_state) -> CollectionState:
        # Be careful to make a "deep enough" copy here!
        new_state.qup_skill_num = { player: num for player, num in self.qup_skill_num.items() }
        new_state.qup_triggerable_skill_num  = { player: num for player, num in self.qup_triggerable_skill_num.items()}
        new_state.qup_trigger_skill_num = { player: num for player, num in self.qup_trigger_skill_num.items() }

        new_state.qup_dist_q_flat_num = { player: num for player, num in self.qup_dist_q_flat_num.items() }
        new_state.qup_dist_q_mult_num = { player: num for player, num in self.qup_dist_q_mult_num.items() }
        new_state.qup_dist_trigger_num = { player: num for player, num in self.qup_dist_trigger_num.items() }
        new_state.qup_dist_gold_num = { player: num for player, num in self.qup_dist_gold_num.items() }
        new_state.qup_dist_xp_num = { player: num for player, num in self.qup_dist_xp_num.items() }
        new_state.qup_dist_other_num = { player: num for player, num in self.qup_dist_other_num.items() }
        return new_state