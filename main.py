import math
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from Levenshtein import distance

QUIZ_NAMES_FILE = "quiz_names.txt"
BASE_URL = "https://www.wizard101.com/quiz/trivia/game/"
LOGIN_TIMEOUT = 15
NUM_QUESTIONS = 12
MAX_QUESTION_DIST = 2

service = Service(r"C:\Program Files\ChromeDriver\chromedriver.exe")
options = webdriver.ChromeOptions()
# options.add_argument('headless') # can't do this anymore since login is needed manually
driver = webdriver.Chrome(service=service, options=options)
# driver.maximize_window()
driver.get("https://www.wizard101.com/game")

driver.execute_script("alert('Please login to your Wizard101 account; "
                      "you have 15 seconds after this alert is closed.')")

while expected_conditions.alert_is_present()(driver):
    time.sleep(0.1)


wait = WebDriverWait(driver, LOGIN_TIMEOUT)
results = wait.until(lambda driver: "Logout" in driver.page_source)

with open(QUIZ_NAMES_FILE, "r") as file:
    quiz_names = file.read().splitlines()

for quiz_name in quiz_names:
    driver.get(BASE_URL + quiz_name)

    with open(f"./answers/{quiz_name}.txt", "r") as file:
        answers = {}
        for line in file.read().splitlines():
            parts = line.split("\t")
            question = parts[0]
            answer = parts[-1]
            answers[question] = answer

    print(answers)

    # TODO: wait for confirm
    for question_num in range(NUM_QUESTIONS):
        print(f"Question number {question_num + 1}!")
        actual_question = wait.until(lambda driver:
                                     driver.find_element(By.CLASS_NAME, "quizQuestion")).text
        answer_elements = wait.until(lambda driver: driver.find_elements(By.CLASS_NAME, "answerText"))
        answer_boxes = wait.until(lambda driver: driver.find_elements(By.CLASS_NAME, "largecheckbox"))

        # language=JavaScript
        driver.execute_script("""
            for (let e of document.getElementsByClassName('answer')) {
                e.style.visibility = 'visible';
            }
            document.getElementById('nextQuestion').style.visibility = 'visible';
        """)

        closest_q = None
        closest_q_dist = math.inf

        for poss_question in answers:
            d = distance(actual_question, poss_question)
            if d < closest_q_dist:
                closest_q = poss_question
                closest_q_dist = d

        if closest_q_dist > MAX_QUESTION_DIST:
            # TODO: add changed boolean, and rewrite to quiz answers file if changed
            print(f"Unrecognized question! (closest was \"{closest_q}\" with dist {closest_q_dist})")
            # TODO: make it so you only have to click, and show alert saying that click is needed
            actual_answer = input("Please copy the correct answer here: ")
            answers[actual_question] = actual_answer
            closest_q = actual_question

        correct_answer = answers[closest_q]

        closest_answer = None
        closest_answer_i = None
        closest_answer_dist = math.inf

        for i, poss_answer in enumerate(answer_elements):
            d = distance(correct_answer, poss_answer.text)
            if d < closest_answer_dist:
                closest_answer = poss_answer.text
                closest_answer_i = i
                closest_answer_dist = d

        answer_boxes[closest_answer_i].click()

        print(f"Actual question: {actual_question}")
        print(f"Closest question found: {closest_q} (dist {closest_q_dist})")
        print(f"Correct answer: {correct_answer}")
        print(f"Closest answer found: {closest_answer} (dist {closest_answer_dist})")

        next_button = wait.until(lambda driver: driver.find_element(By.ID, "nextQuestion"))
        # print(next_button)
        while not expected_conditions.element_to_be_clickable(next_button)(driver):
            # print(next_button)
            time.sleep(0.25)

        next_button.click()

