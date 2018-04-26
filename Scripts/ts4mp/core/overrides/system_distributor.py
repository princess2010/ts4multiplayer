import weakref
from contextlib import contextmanager

import distributor.system
import gsi_handlers
import services
from distributor import logger
from distributor.system import Journal, _distributor_log_enabled
from gsi_handlers.distributor_handlers import archive_operation
from protocolbuffers import Distributor_pb2
from protocolbuffers.Consts_pb2 import MSG_OBJECTS_VIEW_UPDATE
from server.client import Client
from sims4.callback_utils import consume_exceptions

from ts4mp.debug.log import ts4mp_log
from ts4mp.core.pending_client_commands import get_command_function_from_pb, try_get_client_id_of_pending_command, remove_earliest_command_client


class SystemDistributor:
    def __init__(self):
        self.journal = Journal()
        self._pending_creates = weakref.WeakSet()
        self.events = list()

        self.client_distributors = list()

    def __repr__(self):
        return '<Distributor events={}>'.format(len(self.events))

    @property
    def client(self):
        first_client_distributor = next(iter(self.client_distributors), None)
        if first_client_distributor is not None:
           return first_client_distributor.client
        else:
            return None

    @contextmanager
    def dependent_block(self):
        if not self.journal.deferring:
            with consume_exceptions('Distributor', 'Exception raised during a dependent block:'):
                self.journal.start_deferring()
                try:
                    yield None
                finally:
                    self.journal.stop_deferring()
        else:
            yield None

    @classmethod
    def instance(cls):
        return distributor.system._distributor_instance

    def add_object(self, obj):
        logger.info('Adding {0}', obj)

        obj.visible_to_client = True

        if not obj.visible_to_client:
            return

        if not services.client_manager():
            return

        op = obj.get_create_op()

        if op is None:
            obj.visible_to_client = False
            return

        self.journal.add(obj, op, ignore_deferral=True)
        self._pending_creates.add(obj)

        if hasattr(obj, 'on_add_to_client'):
            obj.on_add_to_client()

    def remove_object(self, obj, **kwargs):
        logger.info('Removing {0}', obj)

        was_visible = obj.visible_to_client

        if was_visible and hasattr(obj, 'on_remove_from_client'):
            obj.on_remove_from_client()

        if was_visible:
            delete_op = obj.get_delete_op(**kwargs)

            if delete_op is not None:
                self.add_op(obj, delete_op)

            obj.visible_to_client = False

    def add_client(self, client):
        for client_distributor in self.client_distributors:
            if client_distributor.client.id == client.id:
                raise ValueError('Client is already registered')

        self.process()
        logger.info('Adding {0}', client)

        client_distributor = distributor.system.Distributor()
        client_distributor.add_client(client)
        client_distributor._add_ops_for_client_connect(client)

        self.client_distributors.append(client_distributor)

    def remove_client(self, client):
        self.remove_client_from_id(client.id)

    def remove_client_from_id(self, client_id):
        logger.info('Removing {0}', client_id)
        self.process()

        for client_distributor in self.client_distributors:
            if client_distributor.client.id == client_id:
                client_distributor.remove_client(None)
                self.client_distributors.remove(client_distributor)

    def add_op(self, obj, op):
        if isinstance(obj, Client):
            # ts4mp_log_debug("logs", "The owner of this operation is a client.")
            client_distributor = self.get_client(obj.id)

            if client_distributor is not None:
                client_distributor.add_op(obj, op)

            return

        self.journal.add(obj, op)

    def add_op_with_no_owner(self, op):
        self.journal.add(None, op)

    def send_op_with_no_owner_immediate(self, op):
        global _send_index

        journal_seed = self.journal._build_journal_seed(op, obj=None)
        journal_entry = self.journal._build_journal_entry(journal_seed)
        (obj_id, operation, manager_id, obj_name) = journal_entry

        view_update = Distributor_pb2.ViewUpdate()
        entry = view_update.entries.add()
        entry.primary_channel.id.manager_id = manager_id
        entry.primary_channel.id.object_id = obj_id
        entry.operation_list.operations.append(operation)

        if gsi_handlers.distributor_handlers.archiver.enabled or gsi_handlers.distributor_handlers.sim_archiver.enabled:
            _send_index += 1

            if _send_index >= 4294967295:
                _send_index = 0

            archive_operation(obj_id, obj_name, manager_id, operation, _send_index, self.client)

        for client_distributor in self.client_distributors:
            client_distributor.client.send_message(MSG_OBJECTS_VIEW_UPDATE, view_update)

        if _distributor_log_enabled:
            logger.error('------- SENT IMMEDIATE --------')

    def add_event(self, msg_id, msg, immediate=False):
        if self.client is None:
            logger.error('Could not add event {0} because there are no attached clients', msg_id)
            return

        ts4mp_log("client_specific", "Trying to add an event to a client.")
        function_name = get_command_function_from_pb(msg_id)
        ts4mp_log("client_specific", "Function is {}".format(function_name))

        if function_name is not None:
            client_id = try_get_client_id_of_pending_command(function_name)
            ts4mp_log("client_specific", "Client is {}".format(client_id))

            if client_id is not None:
                remove_earliest_command_client(function_name)
                target_client = self.get_client(client_id)

                if target_client is not None:
                    target_client.add_event(msg_id, msg, immediate)
                    ts4mp_log("client_specific", "Adding event to client")
                    return

        ts4mp_log("client_specific", "No suitable client found, so I'm just going to send it to everybody")
        self.events.append((msg_id, msg))

        if immediate:
            self.process_events()

    def add_event_for_client(self, client, msg_id, msg, immediate):
        client.add_event(msg_id, msg, immediate)
        ts4mp_log("events", "Sending msg with id {} to client {}".format(msg_id, client.client.id))

    def process(self):
        for client_distributor in self.client_distributors:
            client_distributor.process()

        self.process_events()
        self._send_view_updates()

    def process_events(self):
        for (msg_id, msg) in self.events:
            for client_distributor in self.client_distributors:
                client_distributor.client.send_message(msg_id, msg)

        del self.events[:]

    def _send_view_updates(self):
        journal = self.journal

        if journal.entries:
            ops = list(journal.entries)
            journal.clear()

            try:
                for client_distributor in self.client_distributors:
                    client_distributor._send_view_updates_for_client(client_distributor.client, ops)
            except:
                logger.exception('Error sending view updates to client!')

        self._pending_creates.clear()

    def get_client(self, client_id):
        for client_distributor in self.client_distributors:
            if client_distributor.client.id == client_id:
                return client_distributor

    def get_distributor_with_active_sim_matching_sim_id(self, sim_id):
        for client_distributor in self.client_distributors:
            if client_distributor.client.active_sim is not None:
                ts4mp_log("chat", "Active client sim id: {}".format(client_distributor.client.active_sim.id))

                if client_distributor.client.active_sim.id == sim_id:
                    return client_distributor

        return None
