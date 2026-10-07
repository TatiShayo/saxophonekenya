from selenium import webdriver
from selenium.webdriver.edge.options import Options
import time

options = Options()
options.add_argument('--headless')
options.add_argument('--window-size=1440,1080')

driver = webdriver.Edge(options=options)
driver.get('http://localhost:8080')
time.sleep(2)

# Scroll to videos
driver.execute_script("document.getElementById('videos').scrollIntoView();")
time.sleep(1)
driver.save_screenshot('shot_videos.png')

# Scroll to weddings
driver.execute_script("document.getElementById('weddings').scrollIntoView();")
time.sleep(1)
driver.save_screenshot('shot_weddings.png')

# Scroll to pinterest
driver.execute_script("document.getElementById('pinterest').scrollIntoView();")
time.sleep(1)
driver.save_screenshot('shot_pinterest.png')

driver.quit()
print('Screenshots captured successfully!')
