from selenium import webdriver
from selenium.webdriver.edge.options import Options
import time

options = Options()
options.add_argument('--headless')
options.add_argument('--window-size=1440,1080')

driver = webdriver.Edge(options=options)
driver.get('http://localhost:8080')
time.sleep(2)

# Hero
driver.save_screenshot('shot_hero_bright.png')

# Bio / Artist section with IMG_2259 background
driver.execute_script("document.getElementById('bio').scrollIntoView();")
time.sleep(1)
driver.save_screenshot('shot_bio_bg.png')

# Videos
driver.execute_script("document.getElementById('videos').scrollIntoView();")
time.sleep(1)
driver.save_screenshot('shot_videos_bg.png')

# Weddings
driver.execute_script("document.getElementById('weddings').scrollIntoView();")
time.sleep(1)
driver.save_screenshot('shot_weddings_bg.png')

# Calendar & Availability
driver.execute_script("document.getElementById('calendar').scrollIntoView();")
time.sleep(1)
driver.save_screenshot('shot_calendar_bg.png')

# Rate Card & Portal
driver.execute_script("document.getElementById('ratecard').scrollIntoView();")
time.sleep(1)
driver.save_screenshot('shot_ratecard_bg.png')

driver.quit()
print('All section screenshots captured successfully!')
