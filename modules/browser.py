import os
import re
import time
import json
import base64
import shutil
from PIL import Image
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from openai import OpenAI

def get_webdriver_service() -> Service:
    service = Service(
        executable_path=shutil.which('chromedriver')
    )
    return service

def open_browser():
    if "driver" not in st.session_state:
        print("Navigating to Google...")
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        if shutil.which('chromedriver'):
            st.write(shutil.which('chromedriver'))
            chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(service=get_webdriver_service(), options=chrome_options)
        # driver = webdriver.Chrome(options=chrome_options)

        # Get screen size
        screen_width = driver.execute_script("return screen.width;")
        screen_height = driver.execute_script("return screen.height;")

        # Calculate window size
        window_width = screen_width // 2
        window_height = screen_height

        # Set maximize window
        # driver.maximize_window()
        # Set browser window position to the left half of the screen
        driver.set_window_position(0, 0)
        driver.set_window_size(window_width, window_height)

        driver.get("https://www.google.com/")
        st.session_state['driver'] = driver
        print("Browser is running in the background...")

def close_browser():
    if "driver" in st.session_state:
        driver = st.session_state['driver']
        driver.quit()
        del st.session_state['driver']

def unmark_page():
    if "driver" in st.session_state:
        driver = st.session_state['driver']
        driver.execute_script("""
        var labels = document.querySelectorAll('.highlight-label');
        if (labels.length > 0) {
            labels.forEach(function(label) {
                label.remove();
            });
        }
        """)

def mark_page():
    if "driver" in st.session_state:
        driver = st.session_state['driver']
        serialized_data = driver.execute_script("""
        var labels = document.querySelectorAll('.highlight-label');
        
        if (labels.length > 0) {
            return;
        }
        var allElements = document.querySelectorAll('*');
        var index = 0;
        var itemsToHighlight = [];
        for(var element of allElements) {
            var tagName = element.tagName;
            
            var shouldHighlight = (element.tagName === "INPUT" || element.tagName === "TEXTAREA" || element.tagName === "SELECT") ||
            (element.tagName === "BUTTON" || element.tagName === "A" || (element.onclick != null) || window.getComputedStyle(element).cursor == "pointer") ||
            (element.tagName === "IFRAME" || element.tagName === "VIDEO");
            
            var rect = element.getBoundingClientRect();
            var area = rect.width * rect.height;
    
            if (shouldHighlight && area > 500) {
                itemsToHighlight.push(element);
            }
        }
        
        // Filter nested elements, retaining only the outermost elements
        var outermostItems = itemsToHighlight.filter(function (element) {
          return !itemsToHighlight.some(function (otherElement) {
            return otherElement !== element && otherElement.contains(element);
          });
        });
        
        outermostItems.forEach(function (element, index) {
            // Create a highlighted border element to enclose the target element
            var rect = element.getBoundingClientRect();
            var highlight = document.createElement("div");
            highlight.className = "highlight-label";
            highlight.style.position = "fixed";
            highlight.style.left = rect.left + "px";
            highlight.style.top = rect.top + "px";
            highlight.style.width = rect.width + "px";
            highlight.style.height = rect.height + "px";
            highlight.style.zIndex = 1000;
            highlight.style.border = "2px dashed red";
            highlight.style.pointerEvents = "none";
                            
            // Add a marker number to the top right corner of the highlighted area
            var label = document.createElement("span");
            label.style.position = "absolute";
            label.style.right = "2px";
            label.style.top = "0px";
            label.textContent = index;
            label.style.color = "red";
            label.style.background = "white"
            label.style.fontWeight = "bold";
             
            // Insert the marker into the highlight element
            highlight.appendChild(label);
            
            document.body.appendChild(highlight);
        }); 
        
        // Add listeners to handle viewport scaling
        window.addEventListener('resize', function() {
            console.log('Window was resized.');
            
            var labels = document.querySelectorAll('.highlight-label');
            
            if (labels.length > 0) {
                labels.forEach(function(label) {
                    label.remove();
                });
                outermostItems.forEach(function (element, index) {
                    // Create a highlighted border element to enclose the target element
                    var rect = element.getBoundingClientRect();
                    var highlight = document.createElement("div");
                    highlight.className = "highlight-label";
                    highlight.style.position = "fixed";
                    highlight.style.left = rect.left + "px";
                    highlight.style.top = rect.top + "px";
                    highlight.style.width = rect.width + "px";
                    highlight.style.height = rect.height + "px";
                    highlight.style.zIndex = 1000;
                    highlight.style.border = "2px dashed red";
                    highlight.style.pointerEvents = "none";
                                    
                    // Add a marker number to the top right corner of the highlighted area
                    var label = document.createElement("span");
                    label.style.position = "absolute";
                    label.style.right = "2px";
                    label.style.top = "0px";
                    label.textContent = index;
                    label.style.color = "red";
                    label.style.background = "white"
                    label.style.fontWeight = "bold";
                     
                    // Insert the marker into the highlight element
                    highlight.appendChild(label);
                    
                    document.body.appendChild(highlight);
                });
            } 
        });
        
        var dataForPython = outermostItems.map(function (item) {
            var rect = item.getBoundingClientRect();
            return {
                x: (rect.left + rect.right) / 2, 
                y: (rect.top + rect.bottom) / 2,
                bboxs: [[rect.left, rect.top, rect.width, rect.height]]
            };
        });
        return JSON.stringify(dataForPython);
        """)
        if serialized_data:
            data = json.loads(serialized_data)
            st.session_state.element_positions = data

def screenshot():
    if "driver" in st.session_state:
        mark_page()
        if not os.path.exists('tmp'):
            os.makedirs('tmp')
        file_path = 'tmp/screenshot.png'
        driver = st.session_state['driver']
        driver.get_screenshot_as_file(file_path)
        st.chat_message("assistant").image(file_path)
        unmark_page()

def extract_json_from_markdown(md_string):
    # This captures content between ```json and ```
    regex = r'```json\s*([\s\S]+?)\s*```'

    match = re.search(regex, md_string)
    if not match:
        print("No JSON block found")
        return None

    json_string = match.group(1).strip()
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as err:
        print('Failed to parse JSON:', err)
        return None

def click_action(element_index):
    if "element_positions" in st.session_state and len(st.session_state.element_positions) > element_index and "driver" in st.session_state:
        x = st.session_state.element_positions[element_index]['x']
        y = st.session_state.element_positions[element_index]['y']
        ActionChains(st.session_state["driver"]).move_by_offset(x, y).click().perform()
        ActionChains(st.session_state["driver"]).move_by_offset(-x, -y).perform()
        st.chat_message("assistant").write(f'clicking element {element_index}')
        st.session_state.messages.append({"role": "assistant", "content": f'click element {element_index}'})

def type_action(element_index, text):
    if "element_positions" in st.session_state and len(
            st.session_state.element_positions) > element_index and "driver" in st.session_state:
        x = st.session_state.element_positions[element_index]['x']
        y = st.session_state.element_positions[element_index]['y']
        # Move cursor to the input box
        ActionChains(st.session_state["driver"]).move_by_offset(x, y).click().perform()
        # Wait a short while to ensure the input box is focused
        time.sleep(0.5)
        # Input text and press Enter
        ActionChains(st.session_state["driver"]) \
            .send_keys(text) \
            .send_keys(Keys.RETURN) \
            .perform()
        # Reset the mouse position at the end
        ActionChains(st.session_state["driver"]).move_by_offset(-x, -y).perform()
        st.chat_message("assistant").write(f'typing {text} into element {element_index}')
        st.session_state.messages.append({"role": "assistant", "content": f'typing {text} into element {element_index}'})


def scroll_action(direction, scroll_percentage):
    # Set the percentage of the scroll
    # scroll_percentage = 0.5

    if "driver" in st.session_state:
        driver = st.session_state.driver
        # Get the viewport height of the window
        viewport_height = driver.execute_script("return window.innerHeight")
        # Calculate the amount to scroll
        scroll_amount = viewport_height * scroll_percentage
        if "up" == direction:
            # Scroll the page up
            driver.execute_script(f"window.scrollBy(0, {-scroll_amount});")
        else:
            # Scroll the page down
            driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        st.chat_message("assistant").write(f'scrolling screen {direction}')
        st.session_state.messages.append({"role": "assistant", "content": f'scrolling screen {direction}'})

def toActionForResult():
    if "action" in st.session_state:
        action = st.session_state.action
        data = extract_json_from_markdown(action)
        msg = action if data is None else data['briefExplanation']
        print(msg)
        if "history_actions" not in st.session_state:
            st.session_state["history_actions"] = []
        st.session_state["history_actions"].append(msg)
        result = False
        if data is not None:
            next_action = data.get("nextAction")
            action = next_action.get("action")
            if action == "click":
                element_index = next_action.get("element")
                click_action(element_index)
            elif action == "type":
                element_index = next_action.get("element")
                text = next_action.get("text")
                type_action(element_index, text)
            elif action == "scroll":
                direction = next_action.get("direction")
                scroll_percentage = next_action.get("scroll_percentage")
                scroll_action(direction, scroll_percentage)
            elif action == "done":
                st.chat_message("assistant").write(f"Task execution completed.\n{msg}")
                st.session_state.messages.append({"role": "assistant", "content": f"Task execution completed.\n{msg}"})
                result = True
            else:
                unknown = f"unknown action {next_action}"
                print(unknown)
                st.chat_message("assistant").write(unknown)
                st.session_state.messages.append({"role": "assistant", "content": unknown})
                result = True
        return result
    else:
        st.chat_message("assistant").write("Please observe first")
        st.session_state.messages.append({"role": "assistant", "content": "Please observe first"})

def observe() :
    if "task" in st.session_state:
        screenshot()
        action = gpt_4v_process()
        st.session_state.action = action
        st.chat_message("assistant").write(action)
        st.session_state.messages.append({"role": "assistant", "content": action})
        return action
    else:
        st.chat_message("assistant").write("Please start a task")
        st.session_state.messages.append({"role": "assistant", "content": "Please start a task"})



def send():
    if "history_actions" in st.session_state:
        st.session_state["history_actions"].clear()
    if "driver" in st.session_state:
        st.session_state.driver.get("https://www.google.com/")
    else:
        open_browser()
    count = 0
    finish = False
    while (count < 5 and not finish) :
        observe()
        finish = toActionForResult()
        count = count+1
    if not finish:
        print("Reached the limit of rounds:5")
        st.chat_message("assistant").write("Reached the limit of rounds:5")
        st.session_state.messages.append({"role": "assistant", "content": "Reached the limit of rounds:5"})
        pass

system_prompt = """
# instructions
the content for 'task', 'history_actions' and image will be entered by user. 
the content for  'response_format', 'nextAction_selectable_lists' and 'response_examples' are given below.
Observe the image, based on the 'task' and the 'history_actions', think about what to do next, complete the task in as few rounds as possible. 
The image encloses the selectable elements and their numbers in red boxes.
Select one type of action from 'nextAction_selectable_lists' for output in the 'response_format' and in a json markdown code block, please refer to 'response_examples'.
If the current image already has results, please provide the obtained information from the image to the user.
-----------------------------------------------------------------------
## response_format
{
  briefExplanation: string,
  nextAction: ClickAction | TypeAction | ScrollAction | Done
}

## nextAction_selectable_lists
- ClickAction = { action: "click", element: number }
- TypeAction = { action: "type", element: number, text: string }
- ScrollAction = { action: "scroll", direction: "up" | "down", scroll_percentage: number }
- Done = { action: "done" }

## response_examples
example1:
```json
{
  "briefExplanation": "Today's doodle looks interesting, I'll click it."
  "nextAction": { "action": "click", "element": 9 }
}
```
example2:
```json
{
  "briefExplanation": "I'll type 'funny cat videos' into the search bar."
  "nextAction": { "action": "type", "element": 4, "text": "funny cat videos" }
}
```
example3:
```json
{
  "briefExplanation": "I'll scroll down the page to view additional job information."
  "nextAction": { "action": "scroll", "direction": "down", "scroll_percentage": 0.5 }
}
---------------------------------------------------------------------------
"""

system_prompt1 = """
# instructions
the content for 'task', 'history_actions' and image will be entered by user. 
the content for  'response_format', 'nextAction_selectable_lists' and 'response_examples' are given below.
Observe the image, based on the 'task' and the 'history_actions', think about what to do next. 
The image encloses the selectable elements and their numbers in red boxes.
Select one type of action from 'nextAction_selectable_lists' for output in the 'response_format' and in a json markdown code block.
Keep the response for 'briefExplanation' as concise and easy to understand as possible. The language of the response should be consistent with that of the 'task'.
Do your best to complete the task this time; if it's really not possible, then proceed to the next round of tasks.
-----------------------------------------------------------------------
## response_format
{
  briefExplanation: string,
  nextAction: ClickAction | TypeAction | ScrollAction | RequestInfoFromUser | RememberInfoFromSite | Done
}

## nextAction_selectable_lists
- ClickAction = { action: "click", element: number }
- TypeAction = { action: "type", element: number, text: string }
- ScrollAction = { action: "scroll", direction: "up" | "down" }
- RequestInfoFromUser = { action: "request-info", prompt: string }
- RememberInfoFromSite = { action: "remember-info", info: string }
- Done = { action: "done" }

## response_examples
{
  "briefExplanation": "I'll type 'funny cat videos' into the search bar"
  "nextAction": { "action": "type", "element": 4, "text": "funny cat videos" }
}
{
  "briefExplanation": "Today's doodle looks interesting, I'll click it"
  "nextAction": { "action": "click", "element": 9 }
}
---------------------------------------------------------------------------
"""

def format_prompt(task, history_actions):
    prompt = {"task":task,"history_actions":history_actions}
    return prompt


# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def gpt_4v_process():
    if "task" in st.session_state:
        client = OpenAI()
        # Path to your image
        image_path = "tmp/screenshot.png"

        # Getting the base64 string
        base64_image = encode_image(image_path)

        if "history_actions" not in st.session_state:
            st.session_state["history_actions"] = []

        prompt = format_prompt(st.session_state["task"], st.session_state["history_actions"])

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": json.dumps(prompt)},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    },
                ],
            }]

        # st.chat_message("assistant").write(prompt)
        # st.session_state.messages.append({"role": "assistant", "content": prompt})
        request_parameters = {
            "model": "gpt-4-vision-preview",
            "messages": messages,
            "max_tokens": 300
        }

        completion = client.chat.completions.create(**request_parameters)
        return completion.choices[0].message.content
    else:
        st.chat_message("assistant").write("Please start a task")
        st.session_state.messages.append({"role": "assistant", "content": "Please start a task"})




