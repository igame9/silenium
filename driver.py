from selenium import webdriver


def initDriverChrome():
    chromedriver = r"C:\Users\Andrey\PycharmProjects\silenium\chromedriver.exe"
    options = webdriver.ChromeOptions()
    options.add_argument('headless')  # для открытия headless-браузера
    driver = webdriver.Chrome(executable_path=chromedriver, options=options)
    return driver
