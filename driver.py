from selenium import webdriver


def initDriverChrome():
    chromedriver = r".\chromedriver.exe"
    options = webdriver.ChromeOptions()
    options.add_argument('headless')  # для открытия headless-браузера
    driver = webdriver.Chrome(executable_path=chromedriver, options=options)
    return driver
