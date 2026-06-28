"""
User state management

Future me isko Redis/Database me shift karenge.
Abhi memory me store kar rahe hain.
"""

# Example:
# {
#   "918275435461": "MAIN_MENU"
# }

user_states = {}


def get_state(user_number):

    # User ki current state return karta hai.
    state = user_states.get(user_number, "START")

    print(f"GET_STATE -> {user_number} = {state}")

    return state


def set_state(user_number, state):

    # User ki new state save karta hai.
    user_states[user_number] = state

    print(f"SET_STATE -> {user_number} = {state}")
