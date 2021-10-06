import datetime
import time
import glob
import os


def get_latest_file(path_to_dir):
    list_of_files = glob.glob(path_to_dir)
    return max(list_of_files, key=os.path.getctime)

def wait_element(browser, locator, timeout=10, is_need_screen=True):
    is_success = False
    timer = datetime.datetime.now() + datetime.timedelta(0, timeout)

    while not is_success and timer > datetime.datetime.now():
        if browser.does_page_contain_element(locator):
            try:
                elem = browser.find_element(locator)
                is_success = elem.is_displayed()
            except:
                time.sleep(1)
        if not is_success:
            if browser.does_page_contain_element(
                "//div[@id='select2-drop']/ul[@class='select2-results']/li[@class='select2-no-results']"
            ):
                elem = browser.find_element(
                    "//div[@id='select2-drop']/ul[@class='select2-results']/li[@class='select2-no-results']"
                )
                if elem.is_displayed():
                    break
    if not is_success and is_need_screen:
        browser.capture_page_screenshot(
            os.path.join(
                os.environ.get("ROBOT_ROOT", os.getcwd()),
                "output",
                "Element_not_available_{}.png".format(
                    datetime.datetime.now().strftime("%H_%M_%S")
                ),
            )
        )
        browser.close_all_browsers()
        raise Exception("Element '{}' not available".format(locator), "ERROR")
