import firebase_admin
from firebase_admin import credentials, db
import numpy as np
import random

# Firebase Admin SDK Setup
cred = credentials.Certificate('ztechxroofgarden-firebase-adminsdk-4252t-1e3a99c703.json')  # from file
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://ztechxroofgarden-default-rtdb.firebaseio.com/'  # from Firebase Realtime Database
})

# Firebase Database references
soil_moisture_ref1 = db.reference('sensors/soilMoisture1')
soil_moisture_ref2 = db.reference('sensors/soilMoisture2')
irrigation_ref = db.reference('commands/irrigation')
drainage_ref = db.reference('commands/drainage')

# Q-learning parameters
gamma = 0.95   # Discount factor
alpha = 0.8    # Learning rate
epsilon = 0.1  # Exploration rate
n_actions = 2  # Actions: 0 = Do nothing, 1 = Turn On
n_states = 3   # States: Dry (0), Optimal (1), Wet (2)

# Q-table initialized to zero
Q_table = np.zeros((n_states, n_actions))

# Define states based on moisture levels
def get_state(moisture_level):
    if moisture_level < 30:
        return 0  # Dry
    elif 30 <= moisture_level <= 70:
        return 1  # Optimal
    else:
        return 2  # Wet

# Get action (exploration or exploitation)
def get_action(state):
    if random.uniform(0, 1) < epsilon:
        # Explore: choose a random action
        return random.randint(0, n_actions - 1)
    else:
        # Exploit: choose the action with the highest Q-value
        return np.argmax(Q_table[state])

# Define rewards
def get_reward(state):
    if state == 1:
        return 10  # Optimal moisture, give a positive reward
    else:
        return -10  # Non-optimal, give a negative reward

# Update Q-table using the Q-learning formula
def update_Q_table(state, action, reward, next_state):
    predict = Q_table[state, action]
    target = reward + gamma * np.max(Q_table[next_state])
    Q_table[state, action] += alpha * (target - predict)

# Function to control the actuators (irrigation, drainage)
def control_actuators(irrigation_action, drainage_action):
    if irrigation_action == 1:
        irrigation_ref.set(True)  # Turn irrigation on
    else:
        irrigation_ref.set(False)  # Turn irrigation off

    if drainage_action == 1:
        drainage_ref.set(True)  # Turn drainage on
    else:
        drainage_ref.set(False)  # Turn drainage off

# Main loop to fetch data, run Q-learning, and control the system
def main():
    while True:
        # Fetch moisture levels from Firebase
        moisture_level1 = soil_moisture_ref1.get()
        moisture_level2 = soil_moisture_ref2.get()

        # Get states based on moisture levels
        state1 = get_state(moisture_level1)
        state2 = get_state(moisture_level2)

        # Choose actions based on Q-learning
        irrigation_action = get_action(state1)
        drainage_action = get_action(state2)

        # Control the actuators based on the actions chosen
        control_actuators(irrigation_action, drainage_action)

        # Get rewards for the current states
        reward1 = get_reward(state1)
        reward2 = get_reward(state2)

        # Get next states after taking actions (simulate the transition)
        next_state1 = get_state(moisture_level1)  # Fetch updated state from Firebase (or assume constant for now)
        next_state2 = get_state(moisture_level2)

        # Update Q-table
        update_Q_table(state1, irrigation_action, reward1, next_state1)
        update_Q_table(state2, drainage_action, reward2, next_state2)

        # Optionally: Print the current Q-table for debugging
        print("Q-table for Irrigation/Drainage:", Q_table)

# Run the main loop
if __name__ == "__main__":
    main()