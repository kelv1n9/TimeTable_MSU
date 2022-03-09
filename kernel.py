from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from config import *
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from bot_logging import logger
import os


class BotParser(Chrome):
    def __init__(self):
        self.driver = None

    def start(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        self.driver = Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

    def login(self):
        self.driver.get(url=url)

        element_present = ec.presence_of_element_located((By.NAME, 'username'))
        WebDriverWait(self.driver, timeout).until(element_present)

        self.driver.find_element(By.NAME, "username").send_keys(login)
        self.driver.find_element(By.NAME, "password").send_keys(password)
        self.driver.find_element(By.NAME, "submit").click()

        element_present = ec.presence_of_element_located((By.ID, 'tdMenu'))
        WebDriverWait(self.driver, timeout).until(element_present)

        self.driver.find_elements(By.ID, "tdMenu")[0].click()

        element_present = ec.presence_of_element_located((By.ID, 'tdeduGraph_common'))
        WebDriverWait(self.driver, timeout).until(element_present)

        self.driver.find_element(By.ID, "tdeduGraph_common").click()

    def go_to_spec(self, specialization_):
        logger.info(specialization_)

        element_present = ec.presence_of_element_located((By.ID, 'repProfId'))
        WebDriverWait(self.driver, timeout).until(element_present)

        Select(self.driver.find_element(By.ID, 'repProfId')).select_by_visible_text(specialization_)

    def go_to_week(self, course_):
        logger.info(course_)
        element_present = ec.presence_of_element_located((By.ID, 'repCourseId'))
        WebDriverWait(self.driver, timeout).until(element_present)

        Select(self.driver.find_element(By.ID, 'repCourseId')).select_by_visible_text(course_)

        element_present = ec.presence_of_element_located((By.ID, 'repWeekId'))
        WebDriverWait(self.driver, timeout).until(element_present)
        self.driver.find_element(By.ID, 'repWeekId').click()

    def go_to_table(self, call_data):
        element_present = ec.presence_of_element_located((By.NAME, 'repWeekId'))
        WebDriverWait(self.driver, timeout).until(element_present)

        Select(self.driver.find_element(By.ID, 'repWeekId')).select_by_visible_text(call_data)

        element_present = ec.presence_of_element_located((By.NAME, 'repGraph'))
        WebDriverWait(self.driver, timeout).until(element_present)

        self.driver.find_element(By.ID, 'repGraph').click()

    def parse_week(self):
        element_present = ec.presence_of_element_located((By.ID, 'repWeekId'))
        WebDriverWait(self.driver, timeout).until(element_present)

        return list(
            BeautifulSoup(self.driver.page_source, 'html5lib').find('select', id="repWeekId").stripped_strings)

    def screenshot(self):
        element_present = ec.presence_of_element_located((By.ID, 'divPrint'))
        WebDriverWait(self.driver, timeout).until(element_present)

        self.driver.set_window_size(1460, 1390)
        image = self.driver.find_element(By.ID, 'divPrint').screenshot_as_png
        return image

    def login_ex(self):
        self.driver.get(url=url)

        element_present = ec.presence_of_element_located((By.NAME, 'username'))
        WebDriverWait(self.driver, timeout).until(element_present)

        self.driver.find_element(By.NAME, "username").send_keys(login)
        self.driver.find_element(By.NAME, "password").send_keys(password)
        self.driver.find_element(By.NAME, "submit").click()

        element_present = ec.presence_of_element_located((By.ID, 'tdMenu'))
        WebDriverWait(self.driver, timeout).until(element_present)

        self.driver.find_elements(By.ID, "tdMenu")[1].click()

        element_present = ec.presence_of_element_located((By.ID, 'tdexamGraph_common'))
        WebDriverWait(self.driver, timeout).until(element_present)

        self.driver.find_element(By.ID, "tdexamGraph_common").click()

    def login_plan(self):
        self.driver.get(url=url)

        element_present = ec.presence_of_element_located((By.NAME, 'username'))
        WebDriverWait(self.driver, timeout).until(element_present)

        self.driver.find_element(By.NAME, "username").send_keys(login)
        self.driver.find_element(By.NAME, "password").send_keys(password)
        self.driver.find_element(By.NAME, "submit").click()

        element_present = ec.presence_of_element_located((By.ID, 'tdMenu'))
        WebDriverWait(self.driver, timeout).until(element_present)

        self.driver.find_elements(By.ID, "tdMenu")[0].click()

        element_present = ec.presence_of_element_located((By.ID, 'tdeduPlan_common'))
        WebDriverWait(self.driver, timeout).until(element_present)

        self.driver.find_element(By.ID, "tdeduPlan_common").click()

    def go_to_year_cur(self, year):
        logger.info(year)

        element_present = ec.presence_of_element_located((By.ID, 'eduplanId'))
        WebDriverWait(self.driver, timeout).until(element_present)

        Select(self.driver.find_element(By.ID, 'eduplanId')).select_by_visible_text(year)

        self.driver.find_element(By.ID, 'btnEduShow').click()

    def parse_year(self):
        element_present = ec.presence_of_element_located((By.ID, 'eduplanId'))
        WebDriverWait(self.driver, timeout).until(element_present)

        return list(
            BeautifulSoup(self.driver.page_source, 'html5lib').find('select', id="eduplanId").stripped_strings)

    def go_to_spec_cur(self, spec):
        logger.info(spec)

        element_present = ec.presence_of_element_located((By.ID, 'profId'))
        WebDriverWait(self.driver, timeout).until(element_present)

        Select(self.driver.find_element(By.ID, 'profId')).select_by_visible_text(spec)

    def go_to_term_cur(self, term):
        element_present = ec.presence_of_element_located((By.NAME, 'graphSemestrId'))
        WebDriverWait(self.driver, timeout).until(element_present)

        Select(self.driver.find_element(By.ID, 'graphSemestrId')).select_by_visible_text(term)

    def exit(self):
        try:
            self.driver.quit()
            self.driver = None
        except Exception:
            logger.error("Browser is already closed.")

