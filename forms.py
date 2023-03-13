import json
import re

default_keyboard = None
end_handlers = {}
custom_actions = {}
send_message = None
forms = {}
user_data = {}
is_in_form = {}
current_form = {}
current_field = {}




#читаем конфиг файл
print("Начинаю читать конфиг")
file = open("config.json", mode="r", encoding="utf-8")
config = json.load(file)
file.close()

for form in config["forms"]:
	forms[form["name"]] = form.copy()
print("Закончил читать конфиг")

def get_user_data():
	if not user_id in user_data:
		user_data[user_id] = {}
	return user_data[user_id]

def is_user_in_form(user_id):
	if not user_id in is_in_form:
		is_in_form[user_id] = False
	return is_in_form[user_id]

def set_current_field(user_id, field_name):
	current_field[user_id] = field_name

def get_previous_field(user_id):
	if not user_id in is_in_form:
		return None


	fields = forms[ current_form[user_id] ]["fields"]
	field_to_find = current_field[user_id]

	for field in fields:
		if fields[field]["next_field"] == field_to_find:
			field_to_find = field
	for field in fields:
		if fields[field]["next_field"] == field_to_find:
			return field

	return forms[ current_form[user_id] ]["first_field"]





def start_form(user_id, form_name):
	user_data[user_id] = {}
	user_data[user_id][form_name] = {}

	field = forms[form_name]["first_field"]

	is_in_form[user_id] = True
	current_form[user_id] = form_name
	current_field[user_id] = field

	if "custom_action" in forms[form_name]["fields"][field]:
		custom_action = forms[form_name]["fields"][field]["custom_action"]
		custom_actions[custom_action](user_id)
		return
	answer = forms[form_name]["fields"][field]["message"]
	send_message(user_id, answer, default_keyboard)


def cancel_form(user_id):
	is_in_form[user_id] = False
	

def handle_previous_field(message):
	prev_field = get_previous_field(message.user_id)
	print(f"Предыдущее поле: {prev_field}")
	if prev_field is None:
		is_in_form[user_id] = False
		current_form[user_id] = None
		current_field[user_id] = None
		return

	form_name = current_form[message.user_id]
	message.text = user_data[message.user_id][form_name][prev_field]
	
	handle_form_field(message, form_name, prev_field)
	return

def handle_form_field(message, form_name, form_field):
	print(f"Текущее поле: {form_field}")
	if message.text.lower() == "отмена":
		cancel_form(message.user_id)
		return
	if message.text.lower() == "назад":
		handle_previous_field(message)
		return

	field_type = forms[form_name]["fields"][form_field]["field_data"]["type"]
	if field_type == "string":
		user_data[message.user_id][form_name][form_field] = message.text
		pattern = forms[form_name]["fields"][form_field]["field_data"]["validation"]
		if re.match(pattern, message.text):
			pass
		else:
			answer = forms[form_name]["fields"][form_field]["validation_error"]
			send_message(message.user_id, answer, default_keyboard)
			return
	else:
		user_data[message.user_id][form_name][form_field] = message.text
	

	if forms[form_name]["fields"][form_field]["next_field"] == "":
		function_name = forms[form_name]["end_handler"]
		end_handlers[function_name](message)
		is_in_form[message.user_id] = False
		return

	new_field = forms[form_name]["fields"][form_field]["next_field"]
	current_form[message.user_id] = form_name
	current_field[message.user_id] = new_field
	if "custom_action" in forms[form_name]["fields"][new_field]:
		custom_action = forms[form_name]["fields"][new_field]["custom_action"]
		custom_actions[custom_action](message.user_id)
		return
	answer = forms[form_name]["fields"][new_field]["message"]
	send_message(message.user_id, answer, default_keyboard)
	


def update(message):
	handle_form_field(
		message, 
		current_form[message.user_id],
		current_field[message.user_id]
		)
	