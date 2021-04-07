import concurrent
from concurrent import futures
from lxml import etree
from selenium.common.exceptions import NoSuchElementException
import time
from selenium.webdriver import ActionChains
import driver


def splitList(a_list):
    half = int(len(a_list) / 2)
    return a_list[:half], a_list[half:]


def check_exists_by_class(driver):
    try:
        driver.find_element_by_class_name("article__body").find_elements_by_class_name("article__block")
    except NoSuchElementException:
        return False
    return True


def makeWrite(typeDriver, newRefList, threadNumber):
    newsTemp = []
    tagTemp = []

    counterReady = 0
    for ref in newRefList:
        typeDriver.get(ref)
        # driver.implicitly_wait(1)
        nameNews = typeDriver.find_element_by_class_name("article__title").text
        # print(nameNews)
        if not check_exists_by_class(typeDriver):
            for news in typeDriver.find_element_by_class_name("article__longread").find_elements_by_class_name(
                    "b-longread__row"):
                newsTemp.append(news.text)
        else:
            for bodyText in typeDriver.find_element_by_class_name("article__body").find_elements_by_class_name(
                    "article__block"):
                try:
                    newsTemp.append(bodyText.find_element_by_class_name("article__text").text)
                except NoSuchElementException:
                    continue
        unionText = ''.join(newsTemp)  # для соедин эл-тов списка из temp в newsText, тк a=b=c
        titleXmlData.text = nameNews
        textXmlData.text = etree.CDATA(unionText)
        for tag in typeDriver.find_element_by_class_name("article__tags").find_elements_by_class_name(
                "article__tags-item"):
            tagTemp.append(tag.text)
        stringTag = ','.join(tagTemp)
        tagsXmlData.text = stringTag
        xmlTree = etree.ElementTree(xmlData)
        xmlTree.write(r"" + threadNumber + str(counterReady) + ".xml", encoding="utf-8", xml_declaration=True,
                      pretty_print=True)
        print(counterReady)
        counterReady = counterReady + 1
        newsTemp.clear()
        tagTemp.clear()
    typeDriver.close()


if __name__ == "__main__":
    xmlData = etree.Element("doc")
    # sourceXmlData = etree.SubElement(xmlData, "source")
    # sourceXmlData.text = etree.CDATA(driver.current_url) ; запись источника данных

    categoryXmlData = etree.SubElement(xmlData, "category")
    categoryXmlData.text = "В мире"
    categoryXmlData.attrib['verify'] = "true"
    categoryXmlData.attrib['type'] = "str"
    categoryXmlData.attrib['auto'] = "true"

    titleXmlData = etree.SubElement(xmlData, "title")
    titleXmlData.attrib['verify'] = "true"
    titleXmlData.attrib['type'] = "str"
    titleXmlData.attrib['auto'] = "true"

    textXmlData = etree.SubElement(xmlData, "text")
    textXmlData.attrib['verify'] = "true"
    textXmlData.attrib['type'] = "str"
    textXmlData.attrib['auto'] = "true"

    tagsXmlData = etree.SubElement(xmlData, "tags")
    tagsXmlData.attrib['verify'] = "true"
    tagsXmlData.attrib['type'] = "str"
    tagsXmlData.attrib['auto'] = "true"
    scrollCounter = 0
    newsRef = []

    counter = 0
    driver1 = driver.initDriverChrome()
    driver1.get("https://ria.ru/world/")
    driver1.implicitly_wait(1)

    button = driver1.find_element_by_class_name("list-more")
    driver1.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # прокрутить вниз
    driver1.implicitly_wait(2)
    ActionChains(driver1).move_to_element(button).click().perform()  # элемент +20 находился вне поля зрения

    print("scrollCounter")
    while scrollCounter != 10:  # прогружаю страницу
        scrollCounter = scrollCounter + 1
        driver1.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)
        print(scrollCounter)

    print("counter ref")
    for refs in driver1.find_element_by_class_name("rubric-list").find_elements_by_class_name(
            "list-item"):  # забираю уже в прогруженной странице элементы(тег и название статьи и ссылки на статьи),
        # driver.implicitly_wait(1)
        counter = counter + 1
        print(counter)
        newsRef.append(refs.find_element_by_tag_name("a").get_attribute("href"))
        if counter == 10:
            break

    print("counter Ready")
    firstList, secondList = splitList(newsRef)
    driver2 = driver.initDriverChrome()
    print(len(firstList))
    print(len(secondList))
    with concurrent.futures.ThreadPoolExecutor() as executor:
        thread1 = executor.submit(makeWrite, driver1, firstList, "firstThread")
        thread2 = executor.submit(makeWrite, driver2, secondList, "secondThread")
