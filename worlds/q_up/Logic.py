from BaseClasses import CollectionState, MultiWorld
from worlds.AutoWorld import LogicMixin

class QUPstate(LogicMixin):
    qup_skill_num: dict[int, int]  # per player

    def init_mixin(self, multiworld: MultiWorld) -> None:
        # Initialize per player with the corresponding "nothing" value, such as 0 or an empty set.
        # You can also use something like Collections.defaultdict
        self.qup_skill_num = {
            player: 0 for player in multiworld.get_game_players("Q-UP")
        }

    def copy_mixin(self, new_state: CollectionState) -> CollectionState:
        # Be careful to make a "deep enough" copy here!
        new_state.qup_skill_num = {
            player: skill_num for player, skill_num in self.qup_skill_num.items()
        }
        return new_state