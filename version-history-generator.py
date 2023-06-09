#!/opt/homebrew/bin/python3

import io
import os
import sys
import time
import hashlib
import logging

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from dotenv import load_dotenv


# Define a custom logging formatter
class VhgFormatter(logging.Formatter):
    def format(self, record):
        record.msg = '[vhg] ' + record.msg
        return super().format(record)

# Define a custom formatter
basic_formatter = '%(asctime)s - %(levelname)s - %(message)s'

# Create a logger instance for your application
logger = logging.getLogger(__name__)

# Create a handler for the logger
handler = logging.StreamHandler()

# Set the formatter to VhgFormatter
handler.setFormatter(VhgFormatter(basic_formatter))

# Assign handler to the logger
logger.addHandler(handler)

# Set the level for the logger
logger.setLevel(logging.DEBUG)

# Load environment variables from .env file
load_dotenv()

gh_username = os.getenv("GITHUB_USERNAME")
gh_password = os.getenv("GITHUB_PASSWORD")

logger.info("🛫 Navigating to github login")
# create a new Chrome browser instance
driver = webdriver.Chrome()

# navigate to the Github login page
driver.get("https://github.com/login")

logger.info("🎫 Entering login credentials")
# find the username input field by class name and enter your username
username = driver.find_element(By.CLASS_NAME, "js-login-field")
username.send_keys(gh_username)

# find the password input field by class name and enter your password
password = driver.find_element(By.CLASS_NAME, "js-password-field")
password.send_keys(gh_password)

# find the login button by class name and click it
login_button = driver.find_element(By.CLASS_NAME, "js-sign-in-button")
login_button.click()

logger.info("🎫 Signing in...")
# wait for the page to load
time.sleep(3)

# Navigate to the project page and open view
view_url = os.getenv("GITHUB_VIEW_URL") 
driver.get(str(view_url))

# wait for the page to load
time.sleep(3)

# Find table view
try: 
    table_view = driver.find_element(By.CSS_SELECTOR, ".Box-sc-g0xbh4-0.jRShZC")
except NoSuchElementException:
    logger.error("Table View: Couldn't find the table element. This may be due to the update of the class names on Github. Please check the class names.")
    sys.exit(1)
        

logger.info("🔍 Starting to read elements.")
issues_dict = {}

# Define issue status literals
issue_open = 1
issue_closed = 0
issue_closed_anp = -1
issue_unknown = 9

# Scroll until the end of the page
i = 0
while i == 0:
    logger.info("📝 Reading elements...")
    # Find all issues in the view
    issue_rows = driver.find_elements(By.CSS_SELECTOR, ".sc-bYMpWt.irTAmX.hoverable")
    if len(issue_rows) == 0:
        logger.warning("Issue Rows: Couldn't find any issue rows. This may be due to the update of the class names on Github. Please check the class names.")
    
    # Define issue status literals
    issue_open_class= "gHFXvr"
    issue_closed_class= "jLdgiv"
    issue_closed_anp_class= "bzUJFx" 

    for row in issue_rows:
        # Get link and the title of the issue
        try: 
            link = row.find_element(By.CSS_SELECTOR, ".Link__StyledLink-sc-14289xe-0.kZAxfs")
            link_url = link.get_attribute("href")
            link_text = link.text
            link_hash = hashlib.sha256(link_url.encode('utf-8')).hexdigest()
        except NoSuchElementException:
            logger.error("Link: Couldn't find the link element of the issue. This may be due to the update of the class names on Github. Please check the class names.")
            sys.exit(1)
        # Get the status of the issue
        try: 
            status = row.find_element(By.CSS_SELECTOR, ".Box-sc-g0xbh4-0.bnmKvJ")
            status_text = status.text
        except NoSuchElementException:
            logger.error("Status: Couldn't find the status element of the issue. This may be due to the update of the class names on Github. Please check the class names.")
            sys.exit(1)

        # Get the status of the issue 
        # try:
            # state_image = row.find_element(By.CSS_SELECTOR, ".Octicon-sc-9kayk9-0.fxtjEX")
            # state_class = state_image.get_attribute("class")
            # state = issue_unknown 
            # if issue_open_class in state_class:
                # state = issue_open 
            # elif issue_closed_class in state_class:
                # state = issue_closed
            # elif issue_closed_anp_class in state_class:
                # state = issue_closed_anp
                
            # if state == issue_unknown:
                # logger.error("The state class of the issue is unknown. This may be due to the update of the class names on Github. Please check the class names.")
                # sys.exit(1)
        # except NoSuchElementException:
            # logger.error("State: Couldn't find the state element of the issue. This may be due to the update of the class names on Github. Please check the class names.")
            # sys.exit(1)

        state = issue_closed

        # Get the label of the issue 
        try:
            labels = row.find_element(By.CSS_SELECTOR, ".Box-sc-g0xbh4-0.faEySC")
            label_text = labels.text
            label_texts = label_text.split("\n")
        except NoSuchElementException:
            logger.error("Labels: Couldn't find the label element of the issue. This may be due to the update of the class names on Github. Please check the class names.")
            sys.exit(1)

        issues_dict[link_hash] = { "url": link_url, "title": link_text, "labels": label_texts, "state": state, "status": status_text } 

    # Wait for the page to load
    time.sleep(2)

    # Scroll down to the bottom of the table
    driver.execute_script("arguments[0].scrollBy(0, window.innerHeight / 1.5);", table_view)
    logger.info("⚙️  Scrolling through elements...")

    # Wait for the page to load
    time.sleep(2)

    # Get the current scroll position of the element
    scroll_position = driver.execute_script("return arguments[0].scrollTop;", table_view)

    # Get the maximum scroll position of the element
    max_scroll_position = driver.execute_script("return arguments[0].scrollHeight - arguments[0].clientHeight;",table_view)

    # Check if the scroll has reached the end
    if scroll_position == max_scroll_position:
        i = 1
        logger.info("🙌 Reading completed. ")
        break;


# close the browser
driver.quit()

logger.info("✏️  Creating markdown file...")

# Define each issue category
new_feature_list = []
bug_list = []
refactor_list = []
enhancement_list = []
documentation_list = []
other_list =[]

for value in issues_dict.values():
    labels = value["labels"]
    if "new-feature" in labels:
        new_feature_list.append(value)
    elif "bug" in labels:
        bug_list.append(value)
    elif "refactor" in labels:
        refactor_list.append(value)
    elif "enhancement" in labels:
        enhancement_list.append(value)
    elif "documentation" in labels:
        documentation_list.append(value)
    else:
        other_list.append(value)

# Read markdown format string ("state,status,labels,title,link")
md_format_str = os.getenv("MARKDOWN_FORMAT")
if md_format_str == None:
    md_format_str="state,status,labels,title,link"
md_format_list = str(md_format_str).split(",")

def write_issue_list(buffer, issues):
    for issue in issues:
        # Convert values
        state = int(issue["state"])
        if state == 0:
            state = "🦄"
        if state == 1:
            state = "🐢"
        if state == -1:
            state = "🐨"

        title = str(issue["title"])
        url = str(issue["url"])
        status = str(issue["status"])
        issue_id = url.split("/")[-1]
        labels = "|".join(list(issue["labels"]))

        # Generate issue line 
        line_buff = io.StringIO()

        line_buff.write("* ")

        if "state" in md_format_list:
            line_buff.write("[{}]".format(state))
            if "status" in md_format_list or "labels" in md_format_list:
                line_buff.write(" ")
        if "status" in md_format_list:
            line_buff.write("[{}]".format(status))
            if "labels" in md_format_list:
                line_buff.write(" ")
        if "labels" in md_format_list:
            line_buff.write("[{}]".format(labels))

        line_buff.write(": ")

        if "title" in md_format_list:
            line_buff.write(title)
            line_buff.write(" ")
        
        if "link" in md_format_list:
            line_buff.write("[[#{}]({})]".format( issue_id, url))
        line_buff.write("\n")

        # Write issue line
        buffer.write(line_buff.getvalue())
    buffer.write("\n") 

content_buff = io.StringIO()
# Write h1 header
markdown_title = os.getenv("MARKDOWN_TITLE")
content_buff.write("# {}\n\n".format(markdown_title))

# Write each issue category
if len(new_feature_list) > 0:
    content_buff.write("## 📱 Yeni Özellikler\n")
    write_issue_list(content_buff, new_feature_list)
if len(bug_list) > 0:
    content_buff.write("## 🐛 Giderilen Hatalar\n")
    write_issue_list(content_buff, bug_list)
if len(enhancement_list) > 0:
    content_buff.write("## 🌿 Uygulama İyileştirme\n")
    write_issue_list(content_buff, enhancement_list)
if len(refactor_list) > 0:
    content_buff.write("## ⚙️  Kod İyileştirme (refactoring)\n")
    write_issue_list(content_buff, refactor_list)
if len(documentation_list) > 0:
    content_buff.write("## 📑 Dökümanlama\n")
    write_issue_list(content_buff, documentation_list)
if len(other_list) > 0:
    content_buff.write("## 📦 Diğer\n")
    write_issue_list(content_buff, other_list)

# Create markdown file
markdown_filename= os.getenv("MARKDOWN_FILENAME")
with open("{}.md".format(markdown_filename), 'w') as f:
    f.write(content_buff.getvalue())

logger.info("✅ All steps completed.")




