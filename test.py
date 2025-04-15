"""Implement tests"""
from contextlib import contextmanager
from time import sleep
from threading import Thread
from unittest import TestCase
from fastapi.testclient import TestClient
import uvicorn
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait


from main import app

class Server(uvicorn.Server):
    """Wrapper class for uvicorn server"""

    def install_signal_handlers(self):
        """No signal handlers"""

    @contextmanager
    def run_in_thread(self):
        """Starts server in another thread"""
        thread = Thread(target=self.run)
        thread.start()
        try:
            while not self.started:
                sleep(1e-3)
            yield
        finally:
            self.should_exit = True
            thread.join()

config = uvicorn.Config("main:app", host="127.0.0.1", log_level="critical")

class TestAPI(TestCase):
    """Scenario: Client developer develops tool to write
    a custom application to visualize our data using our API"""

    def setUp(self):
        self.client = TestClient(app)

    def test_word_cloud_format(self):
        """Verify word cloud API"""
        response = self.client.get("/api/v1/word_frequencies")
        assert response.status_code == 200
        response = response.json()
        assert len(response) > 0
        for obj in response:
            assert isinstance(obj["text"], str)
            assert isinstance(obj["value"], int)

    def test_message_length_frequency_format(self):
        """Verify message length API"""
        response = self.client.get("/api/v1/message_lengths_frequency/30")
        assert response.status_code == 200
        response = response.json()
        assert len(response) > 0
        for obj in response:
            assert isinstance(obj["length"], int)
            assert isinstance(obj["frequency"], int)

class UICase(TestCase):
    """Wrapper test case class for UI testing"""
    def setUp(self):
        options = Options()
        self.browser = webdriver.Firefox(options=options)
        self.server = Server(config=config)
        self.ctx = self.server.run_in_thread()
        self.ctx.__enter__()
        laddr = next(iter(next(iter(self.server.servers)).sockets)).getsockname()
        self.url = f"http://{laddr[0]}:{laddr[1]}/"

    def tearDown(self):
        self.ctx.__exit__(None, None, None)
        self.browser.quit()

class MessageCheckerTest(UICase):
    """Scenario: User visits site and want to check if message is defamation or not."""

    def test_message_defamation(self):
        """Verify message works for message that contains defamation"""
        self.browser.get(self.url)
        input_field = self.browser.find_element(By.ID, 'inputField')
        input_field.send_keys("You fucked your own mother you racist shit.")
        submit_button = self.browser.find_element(By.ID, 'submit')
        submit_button.click()
        output_label = self.browser.find_element(By.ID, "result")

        wait = WebDriverWait(self.browser, timeout=10)
        wait.until(lambda _ : submit_button.get_attribute("disabled") is not None or len(output_label.text) > 3)
        wait.until(lambda _ : submit_button.get_attribute("disabled") is None)
        assert "contains defamation" in output_label.text

    def test_message_not_defamation(self):
        """Verify message works for message that contains defamation"""
        self.browser.get(self.url)
        input_field = self.browser.find_element(By.ID, 'inputField')
        input_field.send_keys("You are a really nice person.")
        submit_button = self.browser.find_element(By.ID, 'submit')
        submit_button.click()
        output_label = self.browser.find_element(By.ID, "result")

        wait = WebDriverWait(self.browser, timeout=10)
        wait.until(lambda _ : submit_button.get_attribute("disabled") is not None or len(output_label.text) > 3)
        wait.until(lambda _ : submit_button.get_attribute("disabled") is None)
        assert "does not contain defamation" in output_label.text

    def test_message_almost_too_long(self):
        """Verify accept not too long message"""
        self.browser.get(self.url)
        input_field = self.browser.find_element(By.ID, 'inputField')
        input_field.send_keys("A" * 4096)
        submit_button = self.browser.find_element(By.ID, 'submit')
        submit_button.click()
        output_label = self.browser.find_element(By.ID, "result")
        wait = WebDriverWait(self.browser, timeout=10)
        wait.until(lambda _ : submit_button.get_attribute("disabled") is not None or len(output_label.text) > 3)
        wait.until(lambda _ : submit_button.get_attribute("disabled") is None)
        assert "does not contain defamation" in output_label.text

    def test_message_too_long(self):
        """Verify reject too long message"""
        self.browser.get(self.url)
        input_field = self.browser.find_element(By.ID, 'inputField')
        input_field.send_keys("A" * 4097)
        submit_button = self.browser.find_element(By.ID, 'submit')
        submit_button.click()
        output_label = self.browser.find_element(By.ID, "result")
        wait = WebDriverWait(self.browser, timeout=10)
        wait.until(lambda _ : submit_button.get_attribute("disabled") is not None or len(output_label.text) > 3)
        wait.until(lambda _ : submit_button.get_attribute("disabled") is None)
        assert "long" in output_label.text
