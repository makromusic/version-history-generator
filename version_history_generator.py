from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import io
import hashlib
import dotenv
import os
from datetime import datetime

version = input("What's version? (v1.0.0): ") or "v1.0.0"
buildnm = input("What's build number? (b1.0): ") or "b1.0"

# Load environment variables from .env file
dotenv.load_dotenv()

gh_username = os.getenv("GITHUB_USERNAME")
gh_password = os.getenv("GITHUB_PASSWORD")

print("🛫 Navigating to github login")
# create a new Chrome browser instance
driver = webdriver.Chrome()

# navigate to the Github login page
driver.get("https://github.com/login")

print("🎫 Entering login credentials")
# find the username input field by class name and enter your username
username = driver.find_element(By.CLASS_NAME, "js-login-field")
username.send_keys(gh_username)

# find the password input field by class name and enter your password
password = driver.find_element(By.CLASS_NAME, "js-password-field")
password.send_keys(gh_password)

# find the login button by class name and click it
login_button = driver.find_element(By.CLASS_NAME, "js-sign-in-button")
login_button.click()

print("🎫 Signing in...")
# wait for the page to load
time.sleep(3)

# Navigate to the project page and open view
view_url = os.getenv("GITHUB_VIEW_URL") 
driver.get(view_url)

# wait for the page to load
time.sleep(3)

# Find table view
table_view = driver.find_element(By.CSS_SELECTOR, ".Box-sc-g0xbh4-0.dCHmvW")


print("🔍 Starting to read elements.")
issues_dict = {}

# Scroll until the end of the page
i = 0
while i == 0:
    # Get the current scroll position of the element
    scroll_position = driver.execute_script("return arguments[0].scrollTop;", table_view)

    # Get the maximum scroll position of the element
    max_scroll_position = driver.execute_script("return arguments[0].scrollHeight - arguments[0].clientHeight;",table_view)

    # Check if the scroll has reached the end
    if scroll_position == max_scroll_position:
        i = 1
        print("🙌 Reading completed. ")
        break;

    print("📝 Reading elements...")
    # Find all issues in the view
    issue_rows = driver.find_elements(By.CSS_SELECTOR, ".sc-fnGiBr.cPxcLo.hoverable")
    
    for row in issue_rows:
        issue = row.find_element(By.CSS_SELECTOR, ".Link__StyledLink-sc-14289xe-0.kZAxfs")
        label = row.find_element(By.CSS_SELECTOR, ".Box-sc-g0xbh4-0.faEySC")
        link_url = issue.get_attribute("href")
        link_text = issue.text
        link_hash = hashlib.sha256(link_url.encode('utf-8')).hexdigest()
        label_text = label.text
        issues_dict[link_hash] = { "url": link_url, "title": link_text, "label": label_text } 

    # Wait for the page to load
    time.sleep(2)


    # Scroll down to the bottom of the table
    driver.execute_script("arguments[0].scrollBy(0, window.innerHeight / 1.5);", table_view)
    print("⚙️  Scrolling through elements...")

    # Wait for the page to load
    time.sleep(2)


# close the browser
driver.quit()

print("✏️  Creating markdown file...")
now = datetime.now()
formatted_date = now.strftime("%d.%m.%Y")

# Define each issue category
new_feature_list = []
bug_list = []
refactor_list = []
enhancement_list = []
documentation_list = []
other_list =[]

for value in issues_dict.values():
    label = value["label"]
    if label == "new-feature":
        new_feature_list.append(value)
    elif label == "bug":
        bug_list.append(value)
    elif label == "refactor":
        refactor_list.append(value)
    elif label == "enhancement":
        enhancement_list.append(value)
    elif label == "documentation":
        documentation_list.append(value)
    else:
        other_list.append(value)
        
def write_issue_list(buffer, issues):
    for issue in issues:
        title = issue["title"]
        url = issue["url"]
        label = issue["label"]
        line = "* **[{}]**: {} [[{}]({})] \n".format(label,title,url,url)
        buffer.write(line)
    buffer.write("\n") 

content_buff = io.StringIO()
# Write h1 header
content_buff.write("# makromusic {}-{} ({})\n\n".format(version, buildnm, formatted_date))

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
name_prefix = os.getenv("MARKDOWN_SAVE_PREFIX")
with open("{}_{}_{}.md".format(name_prefix, version, buildnm), 'w') as f:
    f.write(content_buff.getvalue())

print("✅ All steps completed.")




