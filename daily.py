import os
import subprocess
import datetime
import requests
from ollama import Client

# Configuration
PROMPTS_FILE = "questions.txt"
ANSWERS_FILE = "answers.txt"

def get_prompt_for_date(date):
    """Generate a prompt asking about something important that happened on the given date in history."""
    return f"What is something important that happened on {date.strftime('%B %d')} in history?"


def get_answer_from_ollama(prompt):
    """Send the prompt to Ollama and get an answer."""
    try:
        client = Client()
        raw_response = client.generate(model="llama3.2", prompt=prompt)
        print(raw_response.response)
        return raw_response.response
    except requests.RequestException as e:
        print(f"Error getting answer from Ollama: {e}")
        return "Sorry, I couldn't answer that."  # Fallback answer


def append_to_file(file_path, content):
    """Append content to a file."""
    with open(file_path, "a") as file:
        file.write(content + "\n")


def git_commit_and_push(commit_message):
    """Add, commit, and push changes to the Git repository."""
    try:
        subprocess.run(["git", "add", "."], capture_output=True, text=True, check=True)
        subprocess.run(["git", "commit", "-m", commit_message], capture_output=True, text=True, check=True)
        subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Git operation failed: {e}")


def main():
    # Get the current date
    today = datetime.datetime.now()

    # Generate a prompt for today's date in history
    prompt = get_prompt_for_date(today)

    # Get the answer from Ollama
    answer = get_answer_from_ollama(prompt)

    # Prepare the content to append
    question_content = f"[{today.strftime('%Y-%m-%d')}]: {prompt}"
    answer_content = f"[{today.strftime('%Y-%m-%d')}]: {answer}"

    # Append the content to the respective files
    questions_file_path = os.path.join(os.getcwd(), PROMPTS_FILE)
    answers_file_path = os.path.join(os.getcwd(), ANSWERS_FILE)
    append_to_file(questions_file_path, question_content)
    append_to_file(answers_file_path, answer_content)

    # Commit and push changes to the Git repository
    commit_message = f"Add prompt and answer for {today.strftime('%Y-%m-%d')}"
    git_commit_and_push(commit_message)


if __name__ == "__main__":
    main()
