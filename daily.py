import os
import subprocess
import datetime
import requests

# Configuration
OLLAMA_API_URL = "http://localhost:11434"  # Ollama's default local API
PROMPTS_FILE = "questions_and_answers.txt"
REPO_PATH = "/path/to/your/repo"  # Path to your Git repository


def get_random_prompt():
    """Fetch a random prompt from Ollama."""
    try:
        response = requests.post(f"{OLLAMA_API_URL}/api/random_prompt")
        response.raise_for_status()
        return response.json().get("prompt", "What is your favorite book?")
    except requests.RequestException as e:
        print(f"Error fetching prompt from Ollama: {e}")
        return "What is your favorite book?"  # Fallback prompt


def get_answer_from_ollama(prompt):
    """Send the prompt to Ollama and get an answer."""
    try:
        response = requests.post(f"{OLLAMA_API_URL}/api/answer", json={"prompt": prompt})
        response.raise_for_status()
        return response.json().get("answer", "Sorry, I couldn't answer that.")
    except requests.RequestException as e:
        print(f"Error getting answer from Ollama: {e}")
        return "Sorry, I couldn't answer that."  # Fallback answer


def append_to_file(file_path, content):
    """Append content to a file."""
    with open(file_path, "a") as file:
        file.write(content + "\n")


def git_commit_and_push(repo_path, commit_message):
    """Add, commit, and push changes to the Git repository."""
    try:
        subprocess.run(["git", "add", "-A"], cwd=repo_path, check=True)
        subprocess.run(["git", "commit", "-m", commit_message], cwd=repo_path, check=True)
        subprocess.run(["git", "push"], cwd=repo_path, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Git operation failed: {e}")


def main():
    # Get the current date
    today = datetime.datetime.now().strftime("%Y-%m-%d")

    # Get a random prompt and its answer
    prompt = get_random_prompt()
    answer = get_answer_from_ollama(prompt)

    # Prepare the content to append
    content = f"[{today}]\nPrompt: {prompt}\nAnswer: {answer}\n"

    # Append the content to the file
    file_path = os.path.join(REPO_PATH, PROMPTS_FILE)
    append_to_file(file_path, content)

    # Commit and push changes to the Git repository
    commit_message = f"Add prompt and answer for {today}"
    git_commit_and_push(REPO_PATH, commit_message)


if __name__ == "__main__":
    main()
