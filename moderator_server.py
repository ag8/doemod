import random
import select
import socket
import subprocess
import threading
import time

import requests


class ModeratorServer:
    def __init__(self, host="0.0.0.0", port=12348):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host, port))
        self.server_socket.listen()
        self.player_names = {}
        self.buzz_event = threading.Event()
        self.buzz_pause = False
        self.current_buzzer = None
        self.scores = {}
        self.buzzed_this_question = []
        print(f"Server started on {host}:{port}. Waiting for players...")

    def get_question(self):
        # URL of the SciBowlDB API for random questions
        url = "https://scibowldb.com/api/questions/random"

        # Make a GET request to the API
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            question_data = response.json()
            return question_data
        else:
            # Handle errors (e.g., network issues, server errors)
            return f"Error: Unable to fetch data (Status code: {response.status_code})"

    def question(self, current_question):
        question_text = f"Your tossup is in {current_question.get('question', '').get('category', '')}; {current_question.get('question', '').get('tossup_format', '')}. "
        question_text += f"{current_question.get('question', '').get('tossup_question', '')}"

        if current_question.get('question', '').get('tossup_format', '') == "Multiple Choice":
            question_text = question_text.replace("\nW)", ". [[slnc 500]] W [[slnc 250]]").replace("\nX)", ". [[slnc 500]] X [[slnc 250]]").replace("\nY)", ". [[slnc 500]] Y [[slnc 250]]").replace("\nZ)", ". [[slnc 500]] Z [[slnc 250]]")

        saying_process = subprocess.Popen(['say', question_text])

        while True:
            if self.buzz_pause:
                # Check that this person hasn't already buzzed
                if self.current_buzzer in self.buzzed_this_question:
                    saying_process.kill()
                    bruh_process = subprocess.Popen(["say", "Bruh, you've already buzzed on this question? The fuck? Re-reading for the other players."])

                    self.buzz_pause = False
                    self.current_buzzer = None

                    while bruh_process.poll() is None:
                        pass

                    self.question(current_question)


                self.buzzed_this_question.append(self.current_buzzer)

                correct_buzz = False

                # Check if the process was still running
                still_running = saying_process.poll() is None

                # Kill the process
                saying_process.kill()

                recognition = ""

                if still_running:
                    recognition = "Interrupt!"

                recognition += " " + self.current_buzzer + "."

                # Recognize the player
                subprocess.Popen(['say', recognition])

                time.sleep(5)  # this is when we'll be getting the voice input
                voice_input = "feldspar"

                # Get the correct answer
                correct_answer = current_question.get('question', '').get('tossup_answer', '')

                if voice_input == correct_answer or random.random() < 0.3:
                    info_subprocess = subprocess.Popen(['say', "That is correct!"])
                    self.scores[self.current_buzzer] += 4
                    correct_buzz = True
                else:
                    info_subprocess = subprocess.Popen(['say', "Incorrect; I'll re-read for the other players."])

                    if still_running:  # interrupt; lose points
                        self.scores[self.current_buzzer] -= 4

                self.buzz_pause = False
                self.current_buzzer = None

                while info_subprocess.poll() is None:  # wait for the info to finish being said
                    pass

                time.sleep(0.5)

                print(self.scores)

                if correct_buzz:
                    self.question_function()
                else:  # incorrect buzz; re-read if there's been less than 2 buzzes
                    if len(self.buzzed_this_question) >= 2:
                        self.question_function()
                    else:
                        self.question(current_question)

    def question_function(self):
        self.buzzed_this_question = []

        current_question = self.get_question()

        self.question(current_question)

    def client_thread(self, conn, addr):
        conn.send("Enter your name: ".encode())
        name = conn.recv(1024).decode().strip()
        self.player_names[conn] = name
        print(f"{name} from {addr} has joined the game.")

        while True:
            try:
                ready_to_read, _, _ = select.select([conn], [], [], 0.1)
                if ready_to_read:
                    _ = conn.recv(1024)  # Client buzzed
                    print(f"{self.player_names[conn]} buzzed!")
                    self.buzz_pause = True
                    self.current_buzzer = self.player_names[conn]
            except Exception as e:
                print(f"Error with client {addr}: {e}")
                break

    def run(self):
        threading.Thread(target=self.accept_clients).start()

        command = input("Type 'start' to begin counting: ").strip().lower()
        if command == 'start':
            print("Starting...")

            # Initialize all scores to zero
            for player_name in self.player_names.values():
                self.scores[player_name] = 0

            threading.Thread(target=self.question_function).start()

    def accept_clients(self):
        try:
            while True:
                conn, addr = self.server_socket.accept()
                threading.Thread(target=self.client_thread, args=(conn, addr)).start()
        except Exception as e:
            print(f"Error accepting clients: {e}")

if __name__ == "__main__":
    server = ModeratorServer()
    server.run()
