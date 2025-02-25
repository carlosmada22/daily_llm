import os
import subprocess
import datetime
import requests
import sys
from ollama import Client

# Configuration
PROMPTS_FILE = "questions.txt"
ANSWERS_FILE = "answers.txt"

def get_prompt_for_date(date, previous_answers, variation=0):
    """Generate a prompt asking about something important that happened on the given date in history."""
    base_prompt = f"What is something important that happened on {date.strftime('%B %d')} in history?"
    if variation == 1:
        return f"Give me information about ANOTHER important thing that happened on {date.strftime('%B %d')} in history (different from these: {previous_answers})."
    elif variation == 2:
        return f"Give me information about a THIRD important thing that happened on {date.strftime('%B %d')} in history (different from these: {previous_answers})."
    return base_prompt

def get_previous_answers(date):
    """Retrieve previous answers for the given date from the answers file."""
    answers_file_path = os.path.join(os.getcwd(), ANSWERS_FILE)
    previous_answers = []
    if os.path.exists(answers_file_path):
        with open(answers_file_path, "r") as file:
            first_line = file.readline().strip()
            if first_line:
                previous_answers.append(first_line)  # Add the first line to the previous answers
            for line in file:
                if line.startswith(f"[{date.strftime('%Y-%m-%d')}]:"):
                    previous_answers.append(line.split("]: ")[1].strip())
    return previous_answers


def get_answer_from_ollama(prompt):
    """Send the prompt to Ollama and get an answer."""
    try:
        client = Client()
        raw_response = client.generate(model="deepseek-r1:7b", prompt=prompt)
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

def chain_question_from_answer(answer):
    """Generate a follow-up question based on the given answer."""
    return f"Can you provide more details about: {answer.split('.')[0]}?"


def main():
    variation = 0
    if len(sys.argv) > 1:
        if sys.argv[1] == "-1":
            variation = 1
        elif sys.argv[1] == "-2":
            variation = 2

    # Get the current date
    today = datetime.datetime.now()

    # Retrieve previous answers for today's date
    previous_answers = get_previous_answers(today)
    previous_answers_text = " | ".join(previous_answers) if previous_answers else "None"

    # Generate a prompt for today's date in history
    prompt = get_prompt_for_date(today, previous_answers_text, variation)

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

    # Generate a follow-up question based on the answer
    follow_up_prompt = chain_question_from_answer(answer)
    follow_up_answer = get_answer_from_ollama(follow_up_prompt)

    # Append follow-up content
    follow_up_question_content = f"[{today.strftime('%Y-%m-%d')}]: {follow_up_prompt}"
    follow_up_answer_content = f"[{today.strftime('%Y-%m-%d')}]: {follow_up_answer}"
    append_to_file(questions_file_path, follow_up_question_content)
    append_to_file(answers_file_path, follow_up_answer_content)

    # Commit and push changes to the Git repository
    commit_message = f"Add prompt and answer for {today.strftime('%Y-%m-%d')}"
    git_commit_and_push(commit_message)


if __name__ == "__main__":
    main()
