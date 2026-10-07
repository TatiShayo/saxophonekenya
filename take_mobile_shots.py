from selenium import webdriver
from selenium.webdriver.edge.options import Options
import time

options = Options()
options.add_argument('--headless')
options.add_argument('--window-size=390,844')

driver = webdriver.Edge(options=options)
driver.get('http://localhost:8080')
time.sleep(2)

driver.save_screenshot('mobile_hero.png')

driver.execute_script("document.getElementById('videos').scrollIntoView();")
time.sleep(1)
driver.save_screenshot('mobile_videos.png')

driver.execute_script("document.getElementById('weddings').scrollIntoView();")
time.sleep(1)
driver.save_screenshot('mobile_weddings.png')

driver.execute_script("document.getElementById('pinterest').scrollIntoView();")
time.sleep(1)
driver.save_screenshot('mobile_pinterest.png')

driver.quit()
print('Mobile screenshots captured successfully!')
