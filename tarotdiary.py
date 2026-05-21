# Readme:
# This application use json to store the diary data. 
# I created 30 day's diary entries in advance to test the analysis function.


# import packages
import json # for reading and writing the diary data
import random # for drawing a random tarot card
from datetime import date, datetime, timedelta # for working with dates and time ranges

# 1. Basic file settings
DATA_FILE = "tarot_diary.json" # the JSON file where all diary entries are saved
CANCEL_WORD = "cancel"
BACK_WORD = "back"


# This exception helps me stop a nested input step and return to the menu safely.
class CancelInput(Exception):
    pass


# This function is used instead of input(), so every input step can use cancel.
def read_input(prompt):
    value = input(prompt).strip()
    if value.lower() == CANCEL_WORD:
        raise CancelInput
    return value


# This function prints a simple message when the user cancels an action.
def print_cancelled():
    print("\nCancelled. Returning to the main menu.")


# 2. This class stores the information for one tarot card.
class TarotCard:
    def __init__(self, name, theme, keywords, prompt):
        self.name = name # card name
        self.theme = theme # life theme, such as Learning or Health
        self.keywords = keywords # short keywords for the card
        self.prompt = prompt # reflection question for this card


# 3. Card Database
# I use four cards, and each card connects to one life theme.
tarot_cards = [
    TarotCard(
        "The Fool", "Exploration", "new start, curiosity, brave",
        "The Fool is about the courage to try something for the first time. Today, how much effort did you put into stepping out of your routine to try a new activity or path, and what was the most surprising or fun result you got from it?"
    ),
    TarotCard(
        "The Magician", "Learning", "knowledge, mastery, mental tools",
        "The Magician represents the power of your mind and the mastery of skills. Today, how much mental focus did you actually dedicate to studying or practicing something new, and what specific 'aha!' moment or progress did you feel as a result?"
    ),
    TarotCard(
        "The Moon", "Health", "energy, recovery, physical balance",
        "The Moon represents your internal state and the quiet signals your body sends you. Today, how much intentional effort did you put into physical exercise or a healthy habit, and how did your body respond in terms of energy levels or physical comfort?"
    ),
    TarotCard(
        "The Lovers", "Social", "connection, trust, alignment",
        "The Lovers represents the energy we share with others and the choices we make for harmony. What intentional effort did you make to connect with someone or stay true to a personal value today, and what kind of positive response or warmth did you receive in return?"
    )
]

# 4. Advice Database
# Each card has different advice for different action and feedback patterns.
ADVICE = {
    "The Fool": {
        "flow": "Your exploration is active and enjoyable. Keep following curiosity while noticing which new experiences give you energy.",
        "stagnant": "The desire for something new is there, but you have not stepped outside your routine yet. Choose one small activity you have never tried.",
        "friction": "You are pushing yourself into new things, but the fun is missing. Make the experiment smaller and less pressured.",
        "leverage": "A small new step is giving you a surprisingly strong return. Follow that spark and let curiosity lead the next move.",
        "gift": "Exploration is giving more joy than effort today. Enjoy the surprise, but remember what made it feel safe.",
        "drain": "Trying something new is costing more energy than it returns. Pick a smaller adventure next time.",
        "balanced": "Your curiosity and effort are balanced. Keep taking steady steps outside your routine."
    },
    "The Magician": {
        "flow": "Your learning rhythm is strong. Focus and progress are supporting each other, so keep using the same study method.",
        "stagnant": "The learning tools are available, but your attention has not fully arrived. Start with one clear practice target.",
        "friction": "You are studying hard, but the progress does not feel rewarding. Change the method, shorten the session, or ask for help.",
        "leverage": "A small amount of focused learning is giving you a big result. Identify the technique that made the concept click.",
        "gift": "Your study method is efficient. A little focus is creating real understanding, so save this method for later.",
        "drain": "You are spending mental energy without enough progress. Sharpen the tool: review basics or change your practice style.",
        "balanced": "Your effort and learning result match each other. This is a stable study day."
    },
    "The Moon": {
        "flow": "Your body is responding well to your healthy choices. Keep listening to these quiet signals and protect the routine.",
        "stagnant": "Your health energy feels low and action is also low. Begin with one gentle habit, such as stretching, water, or sleep.",
        "friction": "You are forcing effort, but your body is not feeling better. Reduce intensity and focus on recovery instead.",
        "leverage": "A small healthy action is giving a strong physical return. Repeat the habit that made your body feel lighter.",
        "gift": "Your body responded well to a small habit. Keep that habit simple and repeatable.",
        "drain": "Your body may be asking for rest. Do not treat health like a task to force; choose recovery.",
        "balanced": "Your physical effort and body feedback are balanced. Keep observing what improves comfort and energy."
    },
    "The Lovers": {
        "flow": "Your social effort is creating real warmth. Keep choosing connection that feels honest and mutual.",
        "stagnant": "Connection feels distant and action is low. Send one message, make one plan, or choose one honest conversation.",
        "friction": "You are giving energy socially but not receiving much warmth back. Check whether the connection is balanced.",
        "leverage": "A small social action is bringing a strong positive response. Notice who makes connection feel natural.",
        "gift": "A small social effort brought strong warmth. Accept the support and keep the connection sincere.",
        "drain": "You may be giving more social energy than you receive. Set a boundary or choose a more mutual connection.",
        "balanced": "The give-and-take feels equal. Keep investing in relationships that match your values."
    }
}


# 5. Display helper functions
# This function prints the command reminder for the current page.
def show_prompt(mode="home"):
    print("\n" + "=" * 62)
    prompts = {
        "home": "Draw a card to write your diary.\nMain commands: draw | history | analysis | help | quit",
        "draw": "Draw finished. Next commands: history | analysis | draw | quit",
        "history": "History finished. Next commands: draw | analysis | quit",
        "analysis": "Analysis page. Choose a question, or go back to change your selections."
    }
    print(prompts.get(mode, ""))
    print("=" * 62)


# This function shows the user how to use the command line program.
def show_help():
    print("\nCommand Guide:")
    print("Start with 'draw' to write today's diary entry.")
    print("During any input step, type 'cancel' to return to the main commands.")
    print("During the analysis wizard, type 'back' to go to the previous selection.")
    print("draw     - Draw a random tarot card and write a new journal entry")
    print("history  - View your journal entry from a specific calendar date")
    print("analysis - Start interactive analysis wizard for trends and suggestions")
    print("help     - Show this help system manual again")
    print("quit     - Close the program")


# 6. Input helper functions
# This function keeps asking until the user enters a score from 1 to 10.
def get_score(label):
    while True:
        value = read_input(f"{label} (1-10, or cancel): ")
        if value.isdigit() and 1 <= int(value) <= 10:
            return int(value)
        print("Invalid input. Please enter a number from 1 to 10.")


# This function keeps asking until the user enters a valid date.
def get_date_input(label):
    while True:
        value = read_input(f"{label} (yyyy-mm-dd, or cancel): ")
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            print("Please use standard date format: yyyy-mm-dd (e.g., 2026-05-21).")


# 7. JSON file handling
# This function reads all saved diary entries from the JSON file.
def load_entries():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


# This function checks whether today already has a journal entry.
def has_entry_for_date(iso_date_str):
    return any(entry["date"] == iso_date_str for entry in load_entries())


# 8. Draw and save a new entry
# This function handles the whole draw-card and write-diary process.
def draw_entry():
    try:
        today_iso = str(date.today()) # I use YYYY-MM-DD because it is easy to compare dates.
        if has_entry_for_date(today_iso):
            print("\nYou have already written your journal entry for today.")
            print("Please utilize 'history' or 'analysis' command options instead.")
            return

        # Randomly choose one card from the card list.
        card = random.choice(tarot_cards)
        print(f"\nYou drew:\n{card.name} ({card.theme})\nKeywords: {card.keywords}\n\nPrompt:\n{card.prompt}")
        print(f"\nDate: {today_iso}")

        # The user gives two scores: action and feedback.
        action_score = get_score("Action: How much effort did you put in")
        feedback_score = get_score("Feedback: How good did you feel about it")

        # The user writes the diary reflection after drawing the card.
        print("\nWrite your reflection.")
        reflection = read_input("Reflection, or cancel: ")
        while not reflection:
            print("Reflection cannot be empty.")
            reflection = read_input("Reflection, or cancel: ")

        # I save one entry as a dictionary because JSON works well with dictionaries.
        entry_data = {
            "date": today_iso,
            "card": card.name,
            "theme": card.theme,
            "action_score": action_score,
            "feedback_score": feedback_score,
            "reflection": reflection
        }

        # Load the old entries, add the new one, and write the whole list back.
        entries = load_entries()
        entries.append(entry_data)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False, indent=4)

        print("\nEntry saved successfully.")
    except CancelInput:
        print_cancelled()


# 9. View one previous entry
# This function lets the user search for one diary entry by date.
def show_history():
    try:
        entries = load_entries()
        if not entries:
            print("\nNo entries recorded in your journal yet.")
            return

        print("\nEnter the date of the diary entry you want to view.")
        target_date = get_date_input("Date")
        target_iso = str(target_date)

        for entry in entries:
            if entry["date"] == target_iso:
                print("\n" + "-" * 40)
                print(f"Date: {entry['date']}")
                print(f"Card: {entry['card']} ({entry['theme']})")
                print(f"Action Score: {entry['action_score']}/10")
                print(f"Feedback Score: {entry['feedback_score']}/10")
                print(f"Reflection:\n{entry['reflection']}")
                print("-" * 40)
                return

        print("\nNo entry found for that date.")
    except CancelInput:
        print_cancelled()


# 10. Analysis logic
# This function decides the action and feedback situation.
def get_quadrant_title(action, feedback):
    high_a = action >= 6
    high_f = feedback >= 6
    if high_a and high_f: return "flow"
    if not high_a and not high_f: return "stagnant"
    if high_a and not high_f: return "friction"
    return "leverage"


# This function checks whether feedback is much higher, much lower, or close to action.
def get_difference_title(difference):
    if difference > 3: return "gift"
    if difference < -3: return "drain"
    return "balanced"


# This function chooses only the entries that match the selected date range and theme.
def get_filtered_entries(entries, start_date, end_date, theme):
    filtered = []
    for entry in entries:
        try:
            entry_date = date.fromisoformat(entry["date"])
            if start_date <= entry_date <= end_date and entry["theme"] == theme:
                filtered.append(entry)
        except ValueError:
            pass

    filtered.sort(key=lambda item: item["date"])
    return filtered


def print_analysis_answer(question_choice, theme, start_date, end_date, filtered):
    # This function prints only one answer based on the question selected by the user.
    latest = filtered[-1]
    latest_card = latest["card"]
    latest_difference = latest["feedback_score"] - latest["action_score"]

    print("\n" + "=" * 62)

    if question_choice == 1:
        # Question 1 uses the four action/feedback situations.
        q_key = get_quadrant_title(latest["action_score"], latest["feedback_score"])
        advice = ADVICE.get(latest_card, {}).get(q_key, "Continue observing your effort and feedback.")

        print("Question 1: Should I put more effort into this topic?")
        print("\nAdvice:")
        print(advice)

    elif question_choice == 2:
        # Question 2 uses the difference between feedback and action.
        d_key = get_difference_title(latest_difference)
        advice = ADVICE.get(latest_card, {}).get(d_key, "Maintain your balance.")

        print("Question 2: How am I performing on this topic?")
        print("\nAdvice:")
        print(advice)

    elif question_choice == 3:
        # Question 3 looks at the overall difference trend in the filtered entries.
        total_difference = sum(entry["feedback_score"] - entry["action_score"] for entry in filtered)

        print("Question 3: How is my trend on this topic?")
        print("\nAdvice:")
        if total_difference >= 0:
            print("Overall, your effort is working. The feedback is equal to or better than the action you put in, so keep building this habit.")
        else:
            print("Do not lose heart. Your action is higher than your feedback right now, so try reducing pressure or changing your method.")

    print("=" * 62)


# 11. Interactive analysis page
# This function lets the user choose time window, theme, and question.
def show_analysis():
    try:
        entries = load_entries()
        if not entries:
            print("\nNo entries recorded in your journal yet. Please write daily logs first.")
            return

        themes = sorted(list(set(card.theme for card in tarot_cards)))
        days_map = {"1": 7, "2": 14, "3": 30}

        while True:
            # Step 1: choose the time range first.
            print("\n" + "-" * 40)
            print("Step 1: Choose the analysis time window.")
            print("1. Past 7 days")
            print("2. Past 14 days")
            print("3. Past 30 days")

            window_choice = read_input("Select (1, 2, 3), or 'back' to return to main menu: ").lower()
            if window_choice == BACK_WORD:
                return
            if window_choice not in days_map:
                print("Invalid input. Please choose 1, 2, or 3.")
                continue

            end_date = date.today()
            start_date = end_date - timedelta(days=days_map[window_choice])

            while True:
                # Step 2: choose which life theme to analyze.
                print("\n" + "-" * 40)
                print("Step 2: Choose a theme.")
                for i, theme in enumerate(themes, start=1):
                    print(f"{i}. {theme}")

                theme_input = read_input(f"Select (1-{len(themes)}) or 'back': ").lower()
                if theme_input == BACK_WORD:
                    break
                if not (theme_input.isdigit() and 1 <= int(theme_input) <= len(themes)):
                    print(f"Invalid input. Please choose a number from 1 to {len(themes)}.")
                    continue

                theme_choice = themes[int(theme_input) - 1]
                filtered = get_filtered_entries(entries, start_date, end_date, theme_choice)

                # If there is no data, the program asks the user to choose again.
                if not filtered:
                    print(f"\nNo diary logs found for '{theme_choice}' in this time window.")
                    print("Choose another theme, or type 'back' to change the time window.")
                    continue

                while True:
                    # Step 3: the user can keep asking different analysis questions.
                    print("\n" + "-" * 40)
                    print("Step 3: Choose one insight question.")
                    print("1. Should I put more effort into this topic?")
                    print("2. How am I performing on this topic?")
                    print("3. How is my trend on this topic?")

                    question_input = read_input("Select (1, 2, 3) or 'back': ").lower()
                    if question_input == BACK_WORD:
                        break
                    if question_input not in ["1", "2", "3"]:
                        print("Invalid input. Please choose 1, 2, or 3.")
                        continue

                    print_analysis_answer(
                        int(question_input),
                        theme_choice,
                        start_date,
                        end_date,
                        filtered
                    )
                    print("\nYou can choose another question, or type 'back' to change theme.")

    except CancelInput:
        print_cancelled()


# 12. Main program loop
# This is where the command line program starts running.
def main():
    print("Welcome to Tarot Reflection Journal!")
    show_help()
    show_prompt("home")

    while True:
        # The user types a command here, such as draw, history, or analysis.
        try:
            command = read_input("Command > ").lower()
        except CancelInput:
            print("\nNothing to cancel. Type 'quit' to exit the program.")
            show_prompt("home")
            continue

        if command == "draw":
            draw_entry()
            show_prompt("draw")
        elif command == "history":
            show_history()
            show_prompt("history")
        elif command == "analysis":
            show_analysis()
            show_prompt("home")
        elif command == "help":
            show_help()
            show_prompt("home")
        elif command == BACK_WORD:
            print("You are already at the main menu. Choose draw, history, analysis, help, or quit.")
            show_prompt("home")
        elif command == "quit":
            print("Goodbye.")
            break
        else:
            print("Unknown command. Type 'help' to see the command list.")
            show_prompt("home")

if __name__ == "__main__":
    main()
