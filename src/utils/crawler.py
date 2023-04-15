import os
import logging
import pickle
from typing import Callable, List
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
import time
import random as rd
from bs4 import BeautifulSoup
import utils.models as models

class Crawler:
    def __init__(self, headless=True):
        self.logged_in = False
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler('crawler.log')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        sh = logging.StreamHandler()
        sh.setLevel(logging.DEBUG)
        sh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(fh)
        self.logger.addHandler(sh)
        
        self.username = os.environ.get('INSTAGRAM_USERNAME')
        
        if os.path.exists('cookies.pkl'):
            if (time.time() - os.path.getmtime('cookies.pkl')) > 2592000:
                os.remove('cookies.pkl')
        opts = webdriver.ChromeOptions()
        if headless:
            opts.add_argument('--headless')
        opts.add_argument('--disable-dev-shm-usage')
        opts.add_argument('--no-sandbox')
        opts.binary_location = os.environ.get('GOOGLE_CHROME_BIN')
        s = Service(executable_path= os.environ.get('CHROMEDRIVER_PATH'))
        self.browser = webdriver.Chrome(executable_path= os.environ.get('CHROMEDRIVER_PATH'), chrome_options= opts)
        if not os.path.exists('cookies.pkl'):
            self.insta_login(self.username, os.environ.get('INSTAGRAM_PASSWORD'))
            self.try_accept_cookies()
            self.try_deny_notifications()
            pickle.dump(self.browser.get_cookies(), open("cookies.pkl", "wb"))
            self.logged_in = True
        else:
            self.browser.get('https://www.instagram.com/direct/inbox/')
            cookies = pickle.load(open("cookies.pkl", "rb"))
            for cookie in cookies:
                self.browser.add_cookie(cookie)
            self.browser.refresh()
            self.try_accept_cookies()
            self.try_deny_notifications()
            self.logged_in = True
            
    def try_deny_notifications(self, timeout_s=5)-> None:
        try:
            deny_notifications = WebDriverWait(self.browser, timeout_s).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div/div[3]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/button[2]'))
            )
        except TimeoutException as e:
            pass
        except Exception as e:
            self.logger.error(f'{e.__class__} : {e.args[0]}')
        else:
            deny_notifications.click()
            
    def try_accept_cookies(self, timeout_s=10) -> None:
        try:
            accept_cookies = WebDriverWait(self.browser, timeout_s).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div/div/button[2]'))
            )
        except TimeoutException as e:
            pass
        except Exception as e:
            self.logger.error(f'{e.__class__} : {e.args[0]}')
        else:
            accept_cookies.click()
        
    def insta_login(self, username:str, password:str) -> None:
        try:
            self.browser.get('https://www.instagram.com/direct/inbox/')
            time.sleep(rd.randrange(2,4))
            input_username = self.browser.find_element(By.NAME, 'username')
            input_password = self.browser.find_element(By.NAME, 'password')
            input_username.send_keys(username)
            time.sleep(rd.randrange(1,2))
            input_password.send_keys(password)
            time.sleep(rd.randrange(1,2))
            input_password.send_keys(Keys.ENTER)
        except Exception as err:
            self.logger.error(f'{err.__class__} : {err.args[0]}')
            self.browser.quit()
        print('Login successful')
    
    def send_message(self, username, message) -> models.Error | models.Message:
        try:
            self.browser.get(f'https://www.instagram.com/{username}/')
            time.sleep(rd.randrange(3,4))
            try:
                self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/header/section/div[1]/div[1]/div/div[2]').click()
            except:
                self.logger.error('Unable to click message button')
                return models.Error('Unable to click message button')
            
            time.sleep(rd.randrange(3,4))
            try:
                self.send_to_message_textarea(message)
            except:
                self.logger.error('Unable to send message')
                return models.Error('Unable to send message')
            
            print(f'Message successfully sent to {username}')
            time.sleep(1)
            return models.Message(self.username, username, message)
        except Exception as e:
            self.logger.error(f'{e.__class__} : {e.args[0]}')
            return models.Error(e.args[0])
        
    def send_to_message_textarea(self, message:str) -> None:
        """
        Throws exception if unable to find textarea
        
        """
        text_area = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div/div[2]/div/section/div/div/div/div/div[2]/div[2]/div/div[2]/div/div/div[2]/textarea'))
        )
        text_area.send_keys(message)
        time.sleep(rd.randrange(2,4))
        text_area.send_keys(Keys.ENTER)
        
    def wait_for_message(self, check_delay_s:int=20) -> None:
        """Waits for message to be received. If not on inbox page, goes to inbox page.

        Args:
            check_delay_s (int, optional): Delay between checks. Defaults to 20.
        """
        if self.browser.current_url != 'https://www.instagram.com/direct/inbox/':
            self.browser.get('https://www.instagram.com/direct/inbox/')
            time.sleep(rd.randrange(3,4))
        while True:
            try: 
                self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div/div[1]/div/div/div/div/div[2]/div[5]/div/a/div/div[1]/div/div[2]')
                break
            except:
                time.sleep(check_delay_s)

    def send_mass_message(self, usernames : List[str], message:str, delay_s:int=6) -> List[models.Message|models.Error]:
        messages = []
        for user in usernames:
            try:
                self.send_message(user, message)
                messages.append(models.Message(self.username, user, message))
            except Exception as e:
                self.logger.error(f'{e.__class__} : {e.args[0]}')
                messages.append(models.Error(e.args[0]))
            time.sleep(delay_s)
    
    def get_any_recent_messages(self, max:int=10, reply_fn:Callable[[List[models.Message]], str]=None) -> List[List[models.Message]] | models.Error:
        try:
            if self.browser.current_url != 'https://www.instagram.com/direct/inbox/':
                self.browser.get('https://www.instagram.com/direct/inbox/')
            time.sleep(rd.randrange(3,4))
            WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div/div[2]/div/section/div/div/div/div/div[1]/div[1]/div/div[2]/div/button/div'))
            )
            user_elems = self.browser.find_elements(By.XPATH, '/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div/div[2]/div/section/div/div/div/div/div[1]/div[2]/div/div/div/div/div')
            unread_profile_img_elems: List[WebElement] = [elem.find_element(By.TAG_NAME, 'img') for elem in user_elems if elem.find_elements(By.XPATH, './a/div[1]/div/div/div[3]')]
            unread_usernames: List[str] = [elem.get_attribute("alt").split("'")[0] for elem in unread_profile_img_elems]
            
            all_messages: List[List[models.Message]] = []
            for (elem, username) in zip(unread_profile_img_elems, unread_usernames):
                elem.click()
                time.sleep(rd.randrange(2,4))
                self.logger.info(f'Getting messages from {username}')
                try:
                    thread_messages: List[models.Message] = self.get_thread_messages(username)
                    if reply_fn:
                        reply:str = reply_fn(thread_messages)
                        self.send_to_message_textarea(reply)
                        self.logger.info(f'Replied to {username} with {reply}')
                        thread_messages.append(models.Message(self.username, username, reply))
                    all_messages.append(thread_messages)
                except Exception as e:
                    pass
                time.sleep(rd.randrange(2,4))
            return all_messages
        except Exception as e:
            self.logger.error(f'{e.__class__} : {e.args[0]}')
            return models.Error(e.args[0])
        
    def get_thread_messages(self, username:str) -> List[models.Message]:
        """Throws exception if unable to find messages"""
        x_left = self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div/div[2]/div/section/div/div/div/div/div[2]/div[2]/div/div[1]/div/div/div/div[2]').rect['x']
        texts:List[str] = [(elem.rect['x'], elem.text) for elem in self.browser.find_elements(By.XPATH, '/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div/div[2]/div/section/div/div/div/div/div[2]/div[2]/div/div[1]/div/div/div/div[2]/div/div')]
        return [models.Message(username, self.username, text) if x == x_left else models.Message(self.username, username, text) for (x, text) in texts]

    def get_followers(self, username):
        """
        Deprecated Not Working Right Now
        """
        self.browser.get('https://www.instagram.com/{}/'.format(username))
        time.sleep(3)
        print(self.browser.title)
        
        try:
            abo = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/section/main/div/header/section/ul/li[2]'))
            )
        except Exception as e:
            return {'status' : True, 'data' : [], 'message' : 'Unable to click abonnés list'}
        else:
            abo.click()
        #self.browser.find_element(By.XPATH, '/html/body/div[1]/section/main/div/header/section/ul/li[2]').click()

        div = WebDriverWait(self.browser, 15).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[6]/div/div/div/div[2]/ul/div/li[1]'))
        )

        for j in range(10):
            self.browser.execute_script(
                f'''
                let ul = document.querySelector('div.isgrP');
                
                ul.scroll({j}*ul.scrollHeight, {j}*ul.scrollHeight + ul.scrollHeight);
                '''
            )
            print('Scroll', j)
            
            time.sleep(2)
        
        soup = BeautifulSoup(self.browser.page_source, 'html.parser')
        follow = soup.find_all('li')[3:]
        data : list[str] = [fol.find('a').get_text() for fol in follow if fol and fol.find('a')]
        
        
        data = [fol.removesuffix("S'abonner").split(maxsplit= 1)[0] for fol in data if fol]
        self.browser.find_element(By.XPATH, '/html/body/div[6]/div/div/div/div[1]/div/div[2]/button').click()

        self.browser.find_element(By.XPATH, '/html/body/div[1]/section/nav/div[2]/div/div/div[3]/div/div[2]/a').click()
        try:
            WebDriverWait(self.browser, 15).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/section/div/div[2]/div/div/div[2]/div/div[3]/div/button'))
            )
        except TimeoutException:
            print('Timeout')

        print(len(data), 'followers found')


        return {'status' : True, 'data' : data, 'message' : r.get('message')}
    
    def __del__(self):
        if self.logged_in:
            pickle.dump(self.browser.get_cookies(), open("cookies.pkl", "wb"))
        self.browser.close()