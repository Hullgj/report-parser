import fsm

def test_basic_connection():
	state = fsm.START()
	script = ["write", "error", "connect", "accept", "write", "read", "read", "write", "close", "connect"]

	for event in script:
		print(event, ">>>", state)
		state = state(event)

test_basic_connection()