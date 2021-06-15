import logging

from spaceone.core.manager import BaseManager
from spaceone.monitoring.model.event_model import Event

_LOGGER = logging.getLogger(__name__)


class EventManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_model: Event = self.locator.get_model('Event')

    def create_event(self, params):
        def _rollback(event_vo):
            _LOGGER.info(f'[create_event._rollback] '
                         f'Delete event : {event_vo.event_id}')
            event_vo.delete()

        event_vo: Event = self.event_model.create(params)
        self.transaction.add_rollback(_rollback, event_vo)

        return event_vo

    def update_event(self, params):
        event_vo: Event = self.get_event(params['event_id'], params['domain_id'])
        return self.update_event_by_vo(params, event_vo)

    def update_event_by_vo(self, params, event_vo):
        def _rollback(old_data):
            _LOGGER.info(f'[update_event_by_vo._rollback] Revert Data : '
                         f'{old_data["event_id"]}')
            event_vo.update(old_data)

        self.transaction.add_rollback(_rollback, event_vo.to_dict())

        return event_vo.update(params)

    def delete_event(self, event_id, domain_id):
        event_vo: Event = self.get_event(event_id, domain_id)
        event_vo.delete()

    def get_event(self, event_id, domain_id, only=None):
        return self.event_model.get(event_id=event_id, domain_id=domain_id, only=only)

    def get_event_by_key(self, event_key):
        event_vos = self.event_model.filter(event_key=event_key)
        if event_vos.count() > 0:
            return event_vos[0]
        else:
            return None

    def list_events(self, query={}):
        return self.event_model.query(**query)

    def stat_events(self, query):
        return self.event_model.stat(**query)
