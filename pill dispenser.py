import RPi.GPIO as GPIO
import datetime
import time

# GPIO pins
SERVO_PIN = 17
RELAY_PIN = 18  # GPIO pin connected to the relay module

# Disable warnings
GPIO.setwarnings(False)

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(RELAY_PIN, GPIO.OUT)

# Initialize Servo motor
servo = GPIO.PWM(SERVO_PIN, 50)  # 50 Hz frequency
servo.start(0)

# Function to dispense pill and return to initial position
def dispense_pill():
    servo.ChangeDutyCycle(7.5)  # Rotate servo to 90 degrees
    time.sleep(1)
    servo.ChangeDutyCycle(0)  # Stop servo
    time.sleep(1)  # Wait for stability
    servo.ChangeDutyCycle(2.5)  # Rotate servo back to initial position
    time.sleep(1)
    servo.ChangeDutyCycle(0)  # Stop servo

# Function to turn on relay
def turn_on_relay():
    GPIO.output(RELAY_PIN, GPIO.HIGH)  # Activate relay

# Function to turn off relay
def turn_off_relay():
    GPIO.output(RELAY_PIN, GPIO.LOW)  # Deactivate relay

# Function to get pill timing from website
def get_pill_timing():
    # Replace this with your code to fetch pill timing from website
    # For demonstration, returning hardcoded values
    return {
        "morning": "08:00:00",
        "afternoon": "12:00:00",
        "night": "20:00:00"
    }

# Main function
def main():
    pill_timing = get_pill_timing()

    while True:
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        print("Current Time:", current_time)

        # Check if it's time to dispense pills
        if current_time in pill_timing.values():
            dispense_pill()
            turn_on_relay()  # Activate relay
            time.sleep(5)  # Adjust time to allow the servo to dispense pills
            turn_off_relay()  # Deactivate relay

        time.sleep(1)  # Adjust time interval as needed

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        servo.stop()
        GPIO.cleanup()
