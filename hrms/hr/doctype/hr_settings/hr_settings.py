# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import format_date

# Wether to proceed with frequency change
PROCEED_WITH_FREQUENCY_CHANGE = False


class HRSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		ada: DF.Link | None
		afd: DF.Link | None
		allow_employee_checkin_from_mobile_app: DF.Check
		allow_geolocation_tracking: DF.Check
		allow_multiple_shift_assignments: DF.Check
		ama: DF.Link | None
		auto_leave_encashment: DF.Check
		ceo: DF.Link | None
		check_vacancies: DF.Check
		concept_note: DF.Link | None
		concept_note_rejection: DF.Link | None
		emp_created_by: DF.Literal["Naming Series", "Employee Number", "Full Name"]
		employee_advance_approval_notification_template: DF.Link | None
		employee_advance_status_notification_template: DF.Link | None
		encashment_approval_notification_template: DF.Link | None
		encashment_status_notification_template: DF.Link | None
		enote_approval_notification: DF.Link | None
		enote_copyto_notification: DF.Link | None
		enote_reviewer_notification: DF.Link | None
		enote_status_notification: DF.Link | None
		exit_questionnaire_notification_template: DF.Link | None
		exit_questionnaire_web_form: DF.Link | None
		expense_approver_mandatory_in_expense_claim: DF.Check
		feedback_reminder_notification_template: DF.Link | None
		frequency: DF.Literal["Weekly", "Monthly"]
		hiring_sender: DF.Link | None
		hiring_sender_email: DF.Data | None
		hr_approver: DF.Link | None
		hr_manager: DF.Link | None
		hr_manager_name: DF.Data | None
		iad: DF.Link | None
		icthr: DF.Link | None
		interview_reminder_template: DF.Link | None
		is_basic_salary_for_ltc: DF.Check
		leave_application_approval_notification_template: DF.Link | None
		leave_application_status_notification_template: DF.Link | None
		leave_approval_notification_template: DF.Link | None
		leave_approver_mandatory_in_leave_application: DF.Check
		leave_status_notification_template: DF.Link | None
		ltc_fixed_amount: DF.Currency
		overtime_approval_notification_template: DF.Link | None
		overtime_limit: DF.Int
		overtime_limit_type: DF.Literal["Per Day", "Per Week", "Per Month"]
		overtime_status_notification_template: DF.Link | None
		pc: DF.Link | None
		prevent_self_leave_approval: DF.Check
		prorate_ltc: DF.Check
		remind_before: DF.Time | None
		restrict_backdated_leave_application: DF.Check
		retirement_age: DF.Data | None
		return_day_dsa: DF.Literal["", "100", "70", "50", "20", "0"]
		role_allowed_to_create_backdated_leave_application: DF.Link | None
		send_birthday_reminders: DF.Check
		send_holiday_reminders: DF.Check
		send_interview_feedback_reminder: DF.Check
		send_interview_reminder: DF.Check
		send_leave_notification: DF.Check
		send_work_anniversary_reminders: DF.Check
		sender: DF.Link | None
		sender_email: DF.Data | None
		show_leaves_of_all_department_members_in_calendar: DF.Check
		standard_working_hours: DF.Float
		sws: DF.Link | None
		travel_authorization_approval_notification_template: DF.Link | None
		travel_authorization_status_notification_template: DF.Link | None
		travel_claim_approval_notification_template: DF.Link | None
		travel_claim_status_notification_template: DF.Link | None
		unlink_payment_on_cancellation_of_employee_advance: DF.Check
		user_creation: DF.Link | None
	# end: auto-generated types

	def validate(self):
		self.set_naming_series()

		# Based on proceed flag
		global PROCEED_WITH_FREQUENCY_CHANGE
		if not PROCEED_WITH_FREQUENCY_CHANGE:
			self.validate_frequency_change()
		PROCEED_WITH_FREQUENCY_CHANGE = False

	def set_naming_series(self):
		from erpnext.utilities.naming import set_by_naming_series

		set_by_naming_series(
			"Employee",
			"employee_number",
			self.get("emp_created_by") == "Naming Series",
			hide_name_field=True,
		)

	def validate_frequency_change(self):
		weekly_job_name = frappe.db.get_value(
			"Scheduled Job Type",
			{
				"method": "hrms.controllers.employee_reminders.send_reminders_in_advance_weekly"
			},
			"name",
		)

		monthly_job_name = frappe.db.get_value(
			"Scheduled Job Type",
			{
				"method": "hrms.controllers.employee_reminders.send_reminders_in_advance_monthly"
			},
			"name",
		)

		if not weekly_job_name or not monthly_job_name:
			return

		weekly_job = frappe.get_doc("Scheduled Job Type", weekly_job_name)
		monthly_job = frappe.get_doc("Scheduled Job Type", monthly_job_name)

		next_weekly_trigger = weekly_job.get_next_execution()
		next_monthly_trigger = monthly_job.get_next_execution()

		if self.freq_changed_from_monthly_to_weekly():
			if next_monthly_trigger < next_weekly_trigger:
				self.show_freq_change_warning(
					next_monthly_trigger,
					next_weekly_trigger
				)

		elif self.freq_changed_from_weekly_to_monthly():
			if next_monthly_trigger > next_weekly_trigger:
				self.show_freq_change_warning(
					next_weekly_trigger,
					next_monthly_trigger
				)

	def freq_changed_from_weekly_to_monthly(self):
		return self.has_value_changed("frequency") and self.frequency == "Monthly"

	def freq_changed_from_monthly_to_weekly(self):
		return self.has_value_changed("frequency") and self.frequency == "Weekly"

	def show_freq_change_warning(self, from_date, to_date):
		from_date = frappe.bold(format_date(from_date))
		to_date = frappe.bold(format_date(to_date))

		raise_exception = frappe.ValidationError
		if (
			frappe.flags.in_test
			or frappe.flags.in_patch
			or frappe.flags.in_install
			or frappe.flags.in_migrate
		):
			raise_exception = False

		frappe.msgprint(
			msg=frappe._(
				"Employees will miss holiday reminders from {} until {}. <br> Do you want to proceed with this change?"
			).format(from_date, to_date),
			title="Confirm change in Frequency",
			primary_action={
				"label": frappe._("Yes, Proceed"),
				"client_action": "hrms.proceed_save_with_reminders_frequency_change",
			},
			raise_exception=raise_exception,
		)


@frappe.whitelist()
def set_proceed_with_frequency_change():
	"""Enables proceed with frequency change"""
	global PROCEED_WITH_FREQUENCY_CHANGE
	PROCEED_WITH_FREQUENCY_CHANGE = True
