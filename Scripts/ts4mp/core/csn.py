# handle chat dialog
# originally by Scumbumbo
import sims4.commands
from distributor.system import Distributor
from sims4.collections import AttributeDict
from sims4.localization import LocalizationHelperTuning
from sims4.tuning.tunable import AutoFactoryInit, HasTunableSingletonFactory
from ui.ui_dialog_generic import UiDialogTextInputOkCancel
from ui.ui_dialog_notification import UiDialogNotification
from ui.ui_text_input import UiTextInput

# TODO: Complete overhaul and streamlined L18N support
from ts4mp.debug.log import ts4mp_log


def show_notif(sim, text):
    title = "{} said".format(Distributor.instance().get_distributor_with_active_sim_matching_sim_id(sim.id).client._account.persona_name)
    notification = UiDialogNotification.TunableFactory().default(sim, text=lambda **_: LocalizationHelperTuning.get_raw_text(text), title=lambda **_: LocalizationHelperTuning.get_raw_text(title))
    notification.show_dialog(icon_override=(None, sim))


class Scum_TextInputLengthName(HasTunableSingletonFactory, AutoFactoryInit):
    __qualname__ = 'Scum_TextInputLengthName'

    def build_msg(self, dialog, msg, *additional_tokens):
        msg.max_length = 100
        msg.min_length = 1
        msg.input_too_short_tooltip = LocalizationHelperTuning.get_raw_text("Names must contain at least one character!")


@sims4.commands.Command('mp_chat', command_type=sims4.commands.CommandType.Live)
def mp_chat(target_id=None, _connection=None):
    try:
        target_id = int(target_id)

        ts4mp_log("chat", target_id)
        distributor = Distributor.instance().get_distributor_with_active_sim_matching_sim_id(target_id)

        client = distributor.client
        ts4mp_log("chat", client)

        def enter_dialog_callback(dialog):
            if not dialog.accepted:
                return
            dialog_text = dialog.text_input_responses.get("dialog")
            ts4mp_log("chat", 'Showing message')

            distributor = Distributor.instance().get_distributor_with_active_sim_matching_sim_id(target_id)
            if distributor is not None:
                client = distributor.client
                ts4mp_log("chat", 'Showing message')

                show_notif(client.active_sim, dialog_text)

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
        ts4mp_log("chat", "Dialog id: {}".format(dialog.dialog_id))
        dialog.add_listener(enter_dialog_callback)
        dialog.show_dialog()
    except Exception as e:
        ts4mp_log('chat', e)
