import services
import zone
from event_testing.test_events import TestEvent
from server_commands.persistence_commands import save_game


def on_build_buy_exit(self):
    self._update_navmesh_id_if_neccessary()
    self.is_in_build_buy = False
    self._add_expenditures_and_do_post_bb_fixup()

    services.active_lot().flag_as_premade(False)
    services.get_event_manager().process_events_for_household(TestEvent.OnExitBuildBuy, None)

    self._should_perform_deferred_front_door_check = True

    laundry_service = services.get_laundry_service()

    if laundry_service is not None:
        laundry_service.on_build_buy_exit()

    save_game()


zone.Zone.on_build_buy_exit = on_build_buy_exit
