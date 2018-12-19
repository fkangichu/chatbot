# -*- coding: utf-8 -*-
import logging
import dateutil.parser

from rasa_core_sdk import Action
from rasa_core_sdk.forms import FormAction
from rasa_core_sdk.events import SlotSet, UserUtteranceReverted

logger = logging.getLogger(__name__)

class ActionStoreVisitorName(Action):
    """Stores the visitor's name in a slot"""

    def name(self):
        return "action_store_visitor_name"

    def run(self, dispatcher, tracker, domain):

        visitor = next(tracker.get_latest_entity_values('visitor'), None)

        # if no name was extracted, use the whole user utterance
        # in future this will be stored in a `name_unconfirmed` slot and the
        # user will be asked to confirm their name
        if not visitor:
            visitor = tracker.latest_message.get('text')

        return [SlotSet('visitor_name', visitor)]

class ActionStoreEmployeeName(Action):
    """Stores the employee's name in a slot"""

    def name(self):
        return "action_store_employee_name"

    def run(self, dispatcher, tracker, domain):

        employee = next(tracker.get_latest_entity_values('employee'), None)

        # if no name was extracted, use the whole user utterance
        # in future this will be stored in a `name_unconfirmed` slot and the
        # user will be asked to confirm their name
        if not employee:
            employee = tracker.latest_message.get('text')

        return [SlotSet('employee_name', employee)]


class ActionStoreCompany(Action):
    """Stores the company name in a slot"""

    def name(self):
        return "action_store_company"

    def run(self, dispatcher, tracker, domain):
        company = next(tracker.get_latest_entity_values('company'), None)

        # if no company entity was extracted, use the whole user utterance
        # in future this will be stored in a `company_unconfirmed` slot and
        # the user will be asked to confirm their company name
        if not company:
            company = tracker.latest_message.get('text')

        return [SlotSet('company_name', company)]


class ActionStoreEmail(Action):
    """Stores the email in a slot"""

    def name(self):
        return "action_store_email"

    def run(self, dispatcher, tracker, domain):
        email = next(tracker.get_latest_entity_values('email'), None)

        # if no email entity was recognised, prompt the user to enter a valid
        # email and go back a turn in the conversation to ensure future
        # predictions aren't affected
        if not email:
            dispatcher.utter_message("Please input a valid email.")
            return [UserUtteranceReverted()]

        return [SlotSet('email', email)]

class MessageForm(FormAction):
    """Accept free text input from the user"""

    def name(self):
        return "message_form"

    @staticmethod
    def required_slots(tracker):
        return ["message"]

    def slot_mappings(self):
        return {"message": self.from_text()}

    def submit(self, dispatcher, tracker, domain):
        dispatcher.utter_template('utter_message_sent', tracker)
        return []

# class ActionStoreDatabase(Action):
#     """Saves the information collected into a database"""

#     def name(self):
#         return "action_store_sales_info"

#     def run(self, dispatcher, tracker, domain):
#         import datetime
#         budget = tracker.get_slot('budget')
#         company = tracker.get_slot('company_name')
#         email = tracker.get_slot('email')
#         jobfunction = tracker.get_slot('job_function')
#         name = tracker.get_slot('person_name')
#         use_case = tracker.get_slot('use_case')
#         date = datetime.datetime.now().strftime("%d/%m/%Y")

#         sales_info = [company, use_case, budget, date, name, jobfunction,
#                       email]

#         gdrive = GDriveService()
#         try:
#             gdrive.store_data(sales_info)
#             return [SlotSet('data_stored', True)]
#         except Exception as e:
#             logger.error("Failed to write data to gdocs. Error: {}"
#                          "".format(e.message), exc_info=True)
#             return [SlotSet('data_stored', False)]