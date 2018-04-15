"""
Sims 4 Change Name Console Command
by Scumbumbo @ ModTheSims
Version 5 04/20/15 - Added UI dialog for name input
Version 5a 05/01/15 - Updated for 04/26/15 game patch
Version 7 11/27/17 - Updated UI generation code for 11/15/17 game patch
                    - Special thanks to Deaderpool for some sample code that helped me figure this out
Version 7a 03/19/18 - Increased max length for first and names to 100 characters
"""
import sims4.commands
import sims.sim_info
import services
from sims4.localization import LocalizationHelperTuning
from ui.ui_dialog_generic import UiDialogTextInputOkCancel
from sims4.collections import AttributeDict, FrozenAttributeDict
import mp_essential
from ui.ui_text_input import UiTextInput
from sims4.tuning.tunable import AutoFactoryInit, HasTunableSingletonFactory
from distributor.system import Distributor
def csn_show_usage(output):
    output("usage: rename [OldFirst OldLast]")

class Scum_TextInputLengthName(HasTunableSingletonFactory, AutoFactoryInit):
    __qualname__ = 'Scum_TextInputLengthName'

    def build_msg(self, dialog, msg, *additional_tokens):
        msg.max_length = 100
        msg.min_length = 1
        msg.input_too_short_tooltip = LocalizationHelperTuning.get_raw_text("Names must contain at least one character!")

@sims4.commands.Command('mp_chat', command_type=sims4.commands.CommandType.Live)
def mp_chat(target_id = None, _connection = None):
    client = services.client_manager().get_first_client()
    
    def enter_dialog_callback(dialog):
        if not dialog.accepted:
            return
        dialog_text = dialog.text_input_responses.get("dialog")
        distributor = Distributor.instance().get_distributor_with_active_sim_matching_sim_id(target_id)
        if distributor is not None:
            client = distributor.client
            mp_essential.show_notif(client.active_sim, dialog_text)

    localized_title = lambda **_: LocalizationHelperTuning.get_raw_text("Say Something")
    localized_text = lambda **_: LocalizationHelperTuning.get_raw_text("Say something to anybody who's listening.")
    localized_fname = lambda **_: LocalizationHelperTuning.get_raw_text("Type your message here!")
    localized_lname = lambda **_: LocalizationHelperTuning.get_raw_text("Type your emote here!")
    
    text_input_1 = UiTextInput(sort_order=0)
    text_input_1.default_text = localized_fname
    text_input_1.title = None
    text_input_1.max_length = 100
    text_input_1.initial_value = localized_fname
    text_input_1.length_restriction = Scum_TextInputLengthName()

    inputs = AttributeDict({'dialog': text_input_1})
    dialog = UiDialogTextInputOkCancel.TunableFactory().default(client.active_sim, text=localized_text, title=localized_title, text_inputs=inputs, is_special_dialog=True)
    dialog.add_listener(enter_dialog_callback)
    dialog.show_dialog()
