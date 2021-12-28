import time
import pickle
from getpass import getpass
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

LOGIN_FILE = "login.pkl"

try:
    with open(LOGIN_FILE, "rb") as file:
        user, password = pickle.load(file)
    response = input(f"Use saved user {user}? [Y/n]: ")
    if response.lower() in ["n", "no"]:
        raise FileNotFoundError()
except FileNotFoundError:
    user = input("Username: ")
    password = getpass("Password: ")
    save = input("Remember this login? [y/N]: ")

    if save.lower() in ["yes", "y"]:
        with open(LOGIN_FILE, "wb") as file:
            pickle.dump((user, password), file)
        print("Saved login info!")

BASE_URL = "https://www.wizard101.com/quiz/trivia/game/"

service = Service(r"C:\Program Files\ChromeDriver\chromedriver.exe")
options = webdriver.ChromeOptions()
# options.add_argument('headless')
driver = webdriver.Chrome(service=service, options=options)
driver.maximize_window()
driver.get("https://www.wizard101.com/game")
# time.sleep(1)
user_box = driver.find_element(By.ID, "loginUserName")
user_box.clear()
user_box.send_keys(user)
password_box = driver.find_element(By.ID, "loginPassword")
password_box.clear()
password_box.send_keys(password)
submit_button = driver.find_element(By.CSS_SELECTOR, "input[type=submit]")
# time.sleep(2)
submit_button.click()
assert "You might have misspelled something" not in driver.page_source
# time.sleep(5)
# driver.close()
