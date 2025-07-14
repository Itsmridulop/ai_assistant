from modules.voice_input import VoiceProcessing
from modules.intent_recognition import IntentRecognizer
from modules.task_executor import TaskExecutor
import os

voice=VoiceProcessing()
input_text = voice.take_speech()
if input_text:
	recognizer = IntentRecognizer()
	result = recognizer.recognize(input_text)
	if result['entity'] == 'exit' and result['entity'] == "None":
		print("Enter file name is in wrong format, Please try again.")
		exit(1)
	executor = TaskExecutor()
	if result['intent'] == "create_file":
		executor.create_file(os.path.join(executor.download_dir, result['entity']))
	elif result['intent'] == "create_folder":
		executor.create_folder(os.path.join(executor.download_dir, result['entity']))
	elif result['intent'] == "open_application":
		if result['entity'] == 'C':
			app_name = 'browser'
		executor.open_application(app_name)
	elif result['intent'] == "web_search":
		executor.web_search(result['entity'])
	elif result['intent'] == "download_file":
		executor.download_file(result['entity'])
	elif result['intent'] == "system_command":
		executor.system_command(result['entity'])
	elif result['intent'] == "exit":
		executor.exit_program()
	else:
		print("I think you enter a wrong command")