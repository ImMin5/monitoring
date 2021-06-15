import logging

from spaceone.core.service import *
from spaceone.monitoring.model.alert_model import Alert
from spaceone.monitoring.model.project_alert_config_model import ProjectAlertConfig
from spaceone.monitoring.model.escalation_policy_model import EscalationPolicy
from spaceone.monitoring.manager.project_alert_config_manager import ProjectAlertConfigManager
from spaceone.monitoring.manager.escalation_policy_manager import EscalationPolicyManager
from spaceone.monitoring.manager.alert_manager import AlertManager

_LOGGER = logging.getLogger(__name__)


@authentication_handler(exclude=['update_state'])
@authorization_handler(exclude=['update_state'])
@mutation_handler
@event_handler
class AlertService(BaseService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.alert_mgr: AlertManager = self.locator.get_manager('AlertManager')

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['title', 'project_id', 'domain_id'])
    def create(self, params):
        """Create alert

        Args:
            params (dict): {
                'title': 'str',
                'description': 'str',
                'assignee': 'str',
                'urgency': 'str',
                'project_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            alert_vo (object)
        """

        project_id = params['project_id']
        domain_id = params['domain_id']

        project_alert_config_mgr: ProjectAlertConfigManager = self.locator.get_manager('ProjectAlertConfigManager')

        project_alert_config_vo: ProjectAlertConfig = project_alert_config_mgr.get_project_alert_config(project_id,
                                                                                                        domain_id)
        escalation_policy_vo: EscalationPolicy = project_alert_config_vo.escalation_policy

        params['escalation_policy_id'] = escalation_policy_vo.escalation_policy_id
        params['escalation_ttl'] = escalation_policy_vo.repeat_count

        # Check Assignee

        return self.alert_mgr.create_alert(params)

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['alert_id', 'domain_id'])
    def update(self, params):
        """Update alert

        Args:
            params (dict): {
                'alert_id': 'str',
                'title': 'str',
                'state': 'str',
                'status_message': 'str',
                'description': 'str',
                'assignee': 'str',
                'urgency': 'str',
                'project_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            alert_vo (object)
        """
        
        alert_id = params['alert_id']
        domain_id = params['domain_id']
        project_id = params.get('project_id')

        if project_id:
            project_alert_config_mgr: ProjectAlertConfigManager = self.locator.get_manager('ProjectAlertConfigManager')

            project_alert_config_vo: ProjectAlertConfig = project_alert_config_mgr.get_project_alert_config(project_id,
                                                                                                            domain_id)
            escalation_policy_vo: EscalationPolicy = project_alert_config_vo.escalation_policy

            params['escalation_policy_id'] = escalation_policy_vo.escalation_policy_id
            params['escalation_ttl'] = escalation_policy_vo.repeat_count
            params['escalation_step'] = 1

        alert_vo = self.alert_mgr.get_alert(alert_id, domain_id)

        # Check Assignee

        return self.alert_mgr.update_alert_by_vo(params, alert_vo)

    @transaction
    @check_required(['alert_id', 'access_key', 'state'])
    def update_state(self, params):
        """Update alert state

        Args:
            params (dict): {
                'alert_id': 'str',
                'access_key': 'str',
                'state': 'str'
            }

        Returns:
            alert_vo (object)
        """

        # Check Access Key

        # Check State

        alert_id = params['alert_id']
        alert_vo = self.alert_mgr.get_alert_by_id(alert_id)

        return self.alert_mgr.update_alert_by_vo({'state': params['state']}, alert_vo)

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['alerts', 'merge_to', 'domain_id'])
    def merge(self, params):
        """Merge alerts

        Args:
            params (dict): {
                'alerts': 'list',
                'merge_to': 'str',
                'domain_id': 'str'
            }

        Returns:
            alert_vo (object)
        """

        return self.alert_mgr.merge_alerts(params)

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['alert_id', 'end_time', 'domain_id'])
    @change_timestamp_value(['end_time'], timestamp_format='iso8601')
    def snooze(self, params):
        """Snooze alert

        Args:
            params (dict): {
                'alert_id': 'str',
                'end_time': 'str',
                'domain_id': 'str'
            }

        Returns:
            alert_vo (object)
        """

        alert_id = params['alert_id']
        domain_id = params['domain_id']

        alert_vo = self.alert_mgr.get_alert(alert_id, domain_id)

        # Check end_times

        params['is_snoozed'] = True
        params['snoozed_end_time'] = params['end_time']

        return self.alert_mgr.update_alert_by_vo(params, alert_vo)

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['alert_id', 'resource_type', 'resource_id', 'domain_id'])
    def add_responder(self, params):
        """Add alert responder

        Args:
            params (dict): {
                'alert_id': 'str',
                'resource_type': 'str',
                'resource_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            alert_vo (object)
        """

        # Check resource_type and resource_id

        return self.alert_mgr.add_responder(params)

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['alert_id', 'resource_type', 'resource_id', 'domain_id'])
    def remove_responder(self, params):
        """Remove alert responder

        Args:
            params (dict): {
                'alert_id': 'str',
                'resource_type': 'str',
                'resource_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            alert_vo (object)
        """

        return self.alert_mgr.remove_responder(params)

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['alert_id', 'project_id', 'domain_id'])
    def add_project_dependency(self, params):
        """Add dependent project

        Args:
            params (dict): {
                'alert_id': 'str',
                'project_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            alert_vo (object)
        """

        # Check project_id

        return self.alert_mgr.add_project_dependency(params)

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['alert_id', 'project_id', 'domain_id'])
    def remove_project_dependency(self, params):
        """Remove dependent project

        Args:
            params (dict): {
                'alert_id': 'str',
                'project_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            alert_vo (object)
        """

        return self.alert_mgr.remove_project_dependency(params)

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['alert_id', 'domain_id'])
    def delete(self, params):
        """Delete alert

        Args:
            params (dict): {
                'alert_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            None
        """

        self.alert_mgr.delete_alert(params['alert_id'], params['domain_id'])

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['alert_id', 'domain_id'])
    def get(self, params):
        """ Get alert

        Args:
            params (dict): {
                'alert_id': 'str',
                'domain_id': 'str',
                'only': 'list
            }

        Returns:
            alert_vo (object)
        """

        return self.alert_mgr.get_alert(params['alert_id'], params['domain_id'], params.get('only'))

    @transaction(append_meta={
        'authorization.scope': 'PROJECT',
        'mutation.append_parameter': {'user_projects': 'authorization.projects'}
    })
    @check_required(['domain_id'])
    @append_query_filter(['alert_number', 'alert_id', 'title', 'state', 'assignee', 'urgency', 'severity', 'is_snoozed',
                          'resource_id', 'webhook_id', 'escalation_policy_id', 'project_id', 'domain_id',
                          'user_projects'])
    @append_keyword_filter(['alert_number', 'alert_id', 'title'])
    def list(self, params):
        """ List alerts

        Args:
            params (dict): {
                'alert_number': 'str',
                'alert_id': 'str',
                'title': 'str',
                'state': 'str',
                'assignee': 'str',
                'urgency': 'str',
                'severity': 'str',
                'is_snoozed': 'bool',
                'resource_id': 'str',
                'webhook_id': 'bool',
                'escalation_policy_id': 'str',
                'project_id': 'str',
                'domain_id': 'str',
                'query': 'dict (spaceone.api.core.v1.Query)',
                'user_projects': 'list', // from meta
            }

        Returns:
            alert_vos (object)
            total_count
        """

        query = params.get('query', {})
        return self.alert_mgr.list_alerts(query)

    @transaction(append_meta={
        'authorization.scope': 'PROJECT',
        'mutation.append_parameter': {'user_projects': 'authorization.projects'}
    })
    @check_required(['query', 'domain_id'])
    @append_query_filter(['domain_id', 'user_projects'])
    @append_keyword_filter(['alert_number', 'alert_id', 'title'])
    def stat(self, params):
        """
        Args:
            params (dict): {
                'domain_id': 'str',
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)',
                'user_projects': 'list', // from meta
            }

        Returns:
            values (list) : 'list of statistics data'

        """

        query = params.get('query', {})
        return self.alert_mgr.stat_alerts(query)
