import time
import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

@pytest.fixture(scope='session')
def login_chrome_driver(request):
    options = webdriver.ChromeOptions()
    options.add_argument('executable_path=tests\\chromedriver.exe')
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    driver.implicitly_wait(10)

    # Open PetFriends base page:
    driver.get('https://petfriends.skillfactory.ru/')

    # click on the new user button
    btn_newuser = driver.find_element('xpath', '//button[@onclick="document.location=\'/new_user\';"]')

    btn_newuser.click()

    # click existing user button
    btn_exist_acc = driver.find_element('xpath', '//a[@href="/login"]')
    btn_exist_acc.click()

    # add email
    field_email = driver.find_element('id', 'email')
    field_email.clear()
    field_email.send_keys("enot@gmail.com")

    # add password
    field_pass = driver.find_element('id', 'pass')
    field_pass.clear()
    field_pass.send_keys("12345")

    # click submit button
    btn_submit = driver.find_element('xpath', '//button[@type="submit"]')
    btn_submit.click()

    if driver.current_url == 'https://petfriends.skillfactory.ru/all_pets':
        link_my_pets = driver.find_element('xpath', '//a[@href="/my_pets"]')
        link_my_pets.click()
    else:
        raise Exception('login error')

    yield driver
    driver.quit()


def test_login_and_open_my_pets(login_chrome_driver):
    assert login_chrome_driver.current_url == 'https://petfriends.skillfactory.ru/my_pets'

def test_all_pets_counted(login_chrome_driver):
    wait = WebDriverWait(login_chrome_driver, 10)
    # Сколько строк в таблице с животными
    rows = wait.until(EC.presence_of_all_elements_located(('xpath', '//div[@id="all_my_pets"]//th[@scope="row"]')))
    # print(len(rows))

    # Число из статистики
    count = wait.until(EC.visibility_of_element_located(('class name', 'task3'))).text
    count = count.split('\n')[1]
    count = count.split(' ')[-1]
    count = int(count)
    #print(count)
    assert len(rows) == count

def test_more_pets_with_photo(login_chrome_driver):
    # Животные с фото
    with_image = login_chrome_driver.find_elements('xpath',
                                        '//div[@id="all_my_pets"]//img[contains(@src, "data")]')
    # Животные без фото
    without_image = login_chrome_driver.find_elements('xpath',
                                           '//div[@id="all_my_pets"]//img[not(contains(@src, "data"))]')
    assert len(with_image) >= len(without_image)

def test_all_pets_have_name(login_chrome_driver):
    # Поиск всех значений поля ИМЯ
    names = login_chrome_driver.find_elements('xpath','//div[@id="all_my_pets"]//tr/td[1]')

    # Проверка, что у всех заполнено имя
    for name in names:
        try:
            assert name.text != ""
        except:
            raise Exception('Есть питомцы без имени')

def test_all_names_are_different(login_chrome_driver):
    # Поиск всех значений поля ИМЯ
    names = WebDriverWait(login_chrome_driver, 10).until(
        EC.presence_of_all_elements_located(('xpath', '//div[@id="all_my_pets"]//tr/td[1]')))
    # Проверка, что у всех питомцев разные имена
    pet_names_set = set()
    for name in names:
        try:
            assert name.text not in pet_names_set
            pet_names_set.add(name.text)
        except:
            raise Exception('Есть питомцы с одинаковыми именами')

def test_all_pets_have_breed(login_chrome_driver):
    # Поиск всех значений поля ПОРОДА
    breeds = login_chrome_driver.find_elements('xpath', '//div[@id="all_my_pets"]//tr/td[2]')
    # Проверка, что у всех заполнена порода
    for breed in breeds:
        try:
            assert breed.text != ""
        except:
            raise Exception('Есть питомцы без породы')

def test_all_pets_have_age(login_chrome_driver):
    # Поиск всех значений поля ВОЗРАСТ
    ages = login_chrome_driver.find_elements('xpath', '//div[@id="all_my_pets"]//tr/td[3]')
    # Проверка, что у всех заполнен возраст
    for age in ages:
        try:
            assert age.text != ""
        except:
            raise Exception('Есть питомцы без возраста')

def test_no_same_pets(login_chrome_driver):

    # Проверка, что нет повторяющихся питомцев
    names = login_chrome_driver.find_elements('xpath', '//div[@id="all_my_pets"]//tr/td[1]')
    breeds = login_chrome_driver.find_elements('xpath', '//div[@id="all_my_pets"]//tr/td[2]')
    ages = login_chrome_driver.find_elements('xpath', '//div[@id="all_my_pets"]//tr/td[3]')

    # Список уникальных животных
    unique_pets = set()

    for name, breed, age in zip(names, breeds, ages):
        pet = (name.text, breed.text, age.text)
        if pet in unique_pets:
            raise Exception('Есть полностью одинаковые питомцы')
        else:
            unique_pets.add(pet)
