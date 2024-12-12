import os
import time
import json
import google.generativeai as genai

genai.configure(api_key='HAPPY_LITTLE_API_KEY')

class PyGemQuiz:
    def __init__(self, topic):
        self.number_of_questions = 0
        self.topic = topic
        
        # Create the model
        generation_config = {
            "temperature": 0,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain"
            }

        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config=generation_config,
            system_instruction="You are a quiz maker for Python programming\n\nQuiz Generation:\n\n    Topic Selection:\n        Allow the user to specify a specific Python topic (e.g., data types, control flow, functions, modules, object-oriented programming, etc.) or let the AI randomly select a topic.\n    Question Generation:\n        Generate a variety of question types:\n            Multiple-choice questions: Present four or more answer options, with only one correct answer.\n            True/false questions: Require the user to determine the accuracy of a given statement.\n            Short answer questions: Ask the user to provide a concise text-based answer.\n            Code-based questions: Present a code snippet with a specific task and ask the user to complete it or identify errors.\n    Difficulty Level:\n        Allow the user to choose the difficulty level (easy, medium, or hard).\n        Adjust the complexity of questions based on the selected difficulty level.\n    Question Pool:\n        Maintain a diverse question pool for each topic and difficulty level.\n        Continuously update the question pool with new and challenging questions.\n\nQuiz Administration:\n\n    Answer Submission:\n        Allow users to submit their answers after each question or at the end of the quiz.\n    Immediate Feedback:\n        Provide immediate feedback for each question, indicating whether the answer is correct or incorrect.\n    Explanation of Incorrect Answers:\n        For incorrect answers, offer detailed explanations to help the user understand the correct solution.\n\nQuiz Evaluation:\n\n    Scoring:\n        Calculate the user's score based on the number of correct answers.\n    Performance Analysis:\n        Identify the topics or question types where the user struggled.\n    Personalized Feedback:\n        Provide tailored feedback based on the user's suggesting areas for improvement.",
            )

        self.chat_session = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [
                        "Here are the user's notes to give an idea of where the programmer is in their journey.",
                    ],
                },
                {
                    "role": "model",
                    "parts": [
                        "It looks like these are notes for a Python programming course, covering a wide range of topics from basic syntax to advanced concepts like metaclasses and network programming. They seem to be personal study notes, possibly in preparation for an exam or to solidify understanding. The notes are quite detailed, including code examples, explanations of concepts, and even some reminders (\"Note:\", \"Don't forget\").\n\nHere's a breakdown of the topics covered and the apparent level of the student:\n\n* **Basics:** Data types, operators, control flow, functions, modules, I/O. The notes cover these comprehensively, suggesting a good grasp of fundamental concepts.\n* **Intermediate:** Object-oriented programming (OOP), exceptions, strings, working with files (CSV, XML, JSON), the `copy` module, `random`, `platform`, `sys`, `math`. The notes show a solid understanding of OOP principles and working with different file formats.\n* **Advanced:** Metaclasses, decorators, closures, network programming (sockets, HTTP, TCP/IP), GUI programming with Tkinter, databases (SQLite), logging, configuration files (ConfigParser). The notes on these topics are less detailed in some areas, indicating that the student is still learning these more advanced concepts. There are also some question marks (???) and \"Not too sure\" comments, highlighting areas where further study is needed.\n\n**Areas for Improvement/Further Study:**\n\n* **GUI Programming (Tkinter):** While the notes cover many Tkinter widgets and concepts, they could benefit from more practical examples and exploring more advanced layouts and event handling.\n* **Network Programming:** The notes are quite theoretical. Hands-on practice with creating client-server applications would be beneficial.\n* **Metaclasses:** The notes touch on metaclasses but could be expanded with more practical examples and use cases.\n* **Testing:** The notes briefly mention testing environments but don't go into detail about testing methodologies or frameworks. This would be a valuable area to explore.\n\n**Quiz Suggestions:**\n\nGiven the student's notes, here are some quiz ideas tailored to their learning:\n\n* **Basic Python Quiz:** Focus on data types, operators, control flow, and basic function definitions.\n* **OOP Quiz:** Test understanding of classes, objects, inheritance, polymorphism, and encapsulation. Include questions about abstract classes and methods.\n* **File Handling Quiz:** Cover reading and writing CSV, JSON, and XML files. Include questions about different file modes and error handling.\n* **Modules and Packages Quiz:** Test knowledge of importing modules, using standard library modules like `sys`, `os`, `math`, and `random`, and creating custom modules and packages.\n* **Advanced Concepts Quiz:** Focus on decorators, closures, metaclasses, and exception handling.\n* **Network Programming Quiz:** Test understanding of sockets, HTTP methods, and client-server interactions.\n* **GUI Programming Quiz:** Ask questions about Tkinter widgets, layouts, event handling, and dialog boxes.\n* **Database and Logging Quiz:** Cover SQLite basics and using the `logging` module.\n\nThe quizzes should include a mix of question types (multiple-choice, true/false, short answer, code-based) and vary in difficulty to assess the student's understanding across different levels. Providing detailed explanations for incorrect answers will be crucial for reinforcing learning.\n",
                    ],
                }
            ]
        )

    @staticmethod
    def upload_to_gemini(path, mime_type=None):
        """Uploads the given file to Gemini.

        See https://ai.google.dev/gemini-api/docs/prompting_with_media
        """
        file = genai.upload_file(path, mime_type=mime_type)
        print(f"Uploaded file '{file.display_name}' as: {file.uri}")
        return file

    @staticmethod
    def wait_for_files_active(files):
        """Waits for the given files to be active.

        Some files uploaded to the Gemini API need to be processed before they can be
        used as prompt inputs. The status can be seen by querying the file's "state"
        field.

        This implementation uses a simple blocking polling loop. Production code
        should probably employ a more sophisticated approach.
        """

        print("Waiting for file processing...")
        for name in (file.name for file in files):
            file = genai.get_file(name)
            while file.state.name == "PROCESSING":
                print(".", end="", flush=True)
                time.sleep(10)
                file = genai.get_file(name)
            if file.state.name != "ACTIVE":
                raise Exception(f"File {file.name} failed to process")

        print("...all files ready")
        print()

    def start_quiz(self):
        testing = True
        while testing:
            self.number_of_questions += 1
            print()
            response = self.chat_session.send_message(f"Generate a multi-choice question on {self.topic}. Don't give the answer.")
            print(response.text)

            ans = input("User answer: ")
            print()
            print("Gemini's response:")
            response = self.chat_session.send_message(f"I selected \"{ans}\". Is it right or wrong? Explain your reason.")
            print(response.text)

            ans = input("Next question? Y/N. Or @gemini to ask a question: ").lower()
            if ans == 'y':
                continue
            elif ans == 'n':
                testing = False
                print("Ending quiz.")
            elif ans == "@gemini":
                self.chat_to_gemini()
            else:
                print("Invalid response")
                testing = False

        response = self.chat_session.send_message(f"The quiz is finished. {self.number_of_questions} question/s have been asked. Give a scoring.")
        print(response.text)
        self.number_of_questions
                
    def chat_to_gemini(self):
        print("Entering chat. next/end/exit to exit")
      
        conversation = True
        while conversation:
            user_text = input("Ask Gemini: ")
            if user_text in ("next", "end", "exit"):
                return
            response = self.chat_session.send_message(user_text)
            print(response.text)
                

if __name__ == '__main__':
    try:
        print("Starting Test...")
        pygemquiz = PyGemQuiz('Advanced OOP')
        pygemquiz.start_quiz()
        
    except Exception as e:
        print(e)
        print("Ending quiz.")
