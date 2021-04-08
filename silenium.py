from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import QWidget, QProgressBar, QPushButton, QTextEdit
from lxml import etree
from selenium.common.exceptions import NoSuchElementException
import time
from selenium.webdriver import ActionChains
import driver
from PyQt5 import QtCore


class Ui_MainWindow(object):
    def __init__(self, MainWindow):
        self.centralwidget = QWidget(MainWindow)
        self.progressBar = QProgressBar(self.centralwidget)
        self.pushButton = QPushButton(self.centralwidget)
        self.textEdit = QTextEdit(self.centralwidget)
        self.store = 0

    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(776, 538)
        MainWindow.setMinimumSize(QSize(776, 538))
        MainWindow.setMaximumSize(QSize(776, 538))
        icon = QIcon()
        icon.addFile(u"cat.jpg", QSize(), QIcon.Normal, QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setWindowOpacity(50.000000000000000)
        MainWindow.setToolButtonStyle(Qt.ToolButtonIconOnly)
        MainWindow.setAnimated(True)
        MainWindow.setDocumentMode(False)
        self.centralwidget.setObjectName(u"centralwidget")
        font = QFont()
        font.setFamily(u"Eras Bold ITC")
        font.setPointSize(10)
        self.centralwidget.setFont(font)
        self.centralwidget.setCursor(QCursor(Qt.ArrowCursor))
        self.centralwidget.setAutoFillBackground(False)
        self.centralwidget.setStyleSheet(
            u"background-color:qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0.79096 rgba(0, 112, 118, "
            u"187), stop:1 rgba(255, 255, 255, 255))")
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setGeometry(QRect(20, 490, 441, 23))
        self.progressBar.setMaximum(10)  # максимум
        self.progressBar.setValue(0)
        self.progressBar.setOrientation(Qt.Horizontal)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(20, 460, 141, 21))
        font1 = QFont()
        font1.setFamily(u"Tahoma")
        font1.setBold(True)
        font1.setWeight(75)
        self.pushButton.setFont(font1)
        self.pushButton.setStyleSheet(u"\n"
                                      "QPushButton{\n"
                                      "background-color:white;\n"
                                      "}\n"
                                      "\n"
                                      "QPushButton:hover {\n"
                                      "background-color:silver;\n"
                                      "}")
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setGeometry(QRect(10, 20, 521, 311))
        self.textEdit.setStyleSheet(u"background-color:white")
        self.textEdit.setReadOnly(True)
        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        self.pushButton.clicked.connect(self.start)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Silenium", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"\u0421\u0442\u0430\u0440\u0442", None))

    def splitList(self, a_list):
        half = int(len(a_list) / 2)
        return a_list[:half], a_list[half:]

    def on_update(self, data):
        self.store = data + self.store
        self.progressBar.setValue(self.store)

    def start(self):
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
        while scrollCounter != 1:  # прогружаю страницу
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
        firstList, secondList = self.splitList(newsRef)
        driver2 = driver.initDriverChrome()

        # Создаю потоки
        self.task1 = SlowTask(driver1, firstList, "firstThread")
        self.task1.updated.connect(self.on_update)
        self.task1.start()

        self.task2 = SlowTask(driver2, secondList, "secondThread")
        self.task2.updated.connect(self.on_update)
        self.task2.start()


class SlowTask(QtCore.QThread):
    updated = QtCore.pyqtSignal(int)

    def __init__(self, typeDriver, newRefList, threadNumber):
        super(SlowTask, self).__init__()
        self.threadNumber = threadNumber
        self.newRefList = newRefList
        self.typeDriver = typeDriver
        self.percent = 1

    def check_exists_by_class(self, driver):
        try:
            driver.find_element_by_class_name("article__body").find_elements_by_class_name("article__block")
        except NoSuchElementException:
            return False
        return True

    def run(self):
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
        newsTemp = []
        tagTemp = []

        counterReady = 0
        for ref in self.newRefList:
            self.typeDriver.get(ref)
            # driver.implicitly_wait(1)
            nameNews = self.typeDriver.find_element_by_class_name("article__title").text
            # print(nameNews)
            if not self.check_exists_by_class(self.typeDriver):
                for news in self.typeDriver.find_element_by_class_name("article__longread").find_elements_by_class_name(
                        "b-longread__row"):
                    newsTemp.append(news.text)
            else:
                for bodyText in self.typeDriver.find_element_by_class_name("article__body").find_elements_by_class_name(
                        "article__block"):
                    try:
                        newsTemp.append(bodyText.find_element_by_class_name("article__text").text)
                    except NoSuchElementException:
                        continue
            unionText = ''.join(newsTemp)  # для соедин эл-тов списка из temp в newsText, тк a=b=c
            titleXmlData.text = nameNews
            textXmlData.text = etree.CDATA(unionText)
            for tag in self.typeDriver.find_element_by_class_name("article__tags").find_elements_by_class_name(
                    "article__tags-item"):
                tagTemp.append(tag.text)
            stringTag = ','.join(tagTemp)
            tagsXmlData.text = stringTag
            xmlTree = etree.ElementTree(xmlData)
            xmlTree.write(r"" + self.threadNumber + str(counterReady) + ".xml", encoding="utf-8", xml_declaration=True,
                          pretty_print=True)
            print(counterReady)
            counterReady = counterReady + 1
            newsTemp.clear()
            tagTemp.clear()
            self.updated.emit(int(self.percent))
        self.typeDriver.close()
