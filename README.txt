Branch Functions and Features:

- Busload Function
	Python Library Requirements:
	- python-can 4.3.1

	Function Definition:
	- Given a defined Bus object and an evaluation time in seconds,
		the function calculates the average CAN busload.
		Function counts number of messages to calculate 
		bits on CANbus.

- 250K Baudrate Detection
	Python Library Requirements:
	- PCAN-Basic API (included in repository)

	Function Definition:
	- Function uses the PCAN Basic API and enables the CAN
		controller to use Listen-Only mode and listen for messages
		@ 250K baud. If a message is detected, function returns True.

Author: Shrikrishna Shivakumar