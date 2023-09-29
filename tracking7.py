import os
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

current_directory = os.getcwd()
print(current_directory)

class GitHandler(FileSystemEventHandler):
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.last_event_time = time.time()  # Initialize last_event_time
        self.modified_detected = False

    def on_any_event(self, event):
        # Exclude changes within the .git directory
        if self.is_in_git_directory(event.src_path):
            return

        if event.event_type in ['created', 'modified', 'deleted']:
            print(f"Change detected: {event.src_path}, Event Type: {event.event_type}")
            self.commit_and_push()
            self.last_event_time = time.time()  # Update last_event_time on event
            self.modified_detected = True

    def is_in_git_directory(self, path):
        return any(part == '.git' for part in os.path.normpath(path).split(os.path.sep))

    def commit_and_push(self):
        print("Committing and pushing changes...")
        subprocess.run(["git", "add", "."], cwd=self.repo_path)
        subprocess.run(["git", "commit", "-m", "Auto-commit"], cwd=self.repo_path)
        subprocess.run(["git", "push"], cwd=self.repo_path)
        # print(cwd=self.repo_path)
if __name__ == "__main__":
    path_to_watch = current_directory
    event_handler = GitHandler(repo_path=current_directory)

    while True:
        observer = Observer()
        observer.schedule(event_handler, path=path_to_watch, recursive=True)
        observer.start()

        try:
            # Run the observer for 5 minutes or until a modification is detected
            time_limit = 1 * 60  # 5 minutes in seconds
            time_elapsed = 0
            while time_elapsed < time_limit and not event_handler.modified_detected:
                time.sleep(1)
                time_elapsed += 1
            observer.stop()
            observer.join()
            # --------------------------------------
            # exec(open('mailing.py').read())
            # --------------------------------------
        except KeyboardInterrupt:
            observer.stop()

        # If a modification was detected, immediately restart the observer
        if event_handler.modified_detected:
            event_handler.modified_detected = False
            continue

        # Wait for 2 minutes before starting the observer again
        print("Waiting for 2 minutes before starting again...")
        time.sleep(1 * 60)  # 2 minutes in seconds
