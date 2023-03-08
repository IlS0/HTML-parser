import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By


def get_pages_number(url):
    '''
    Функция получает значение количества страниц товаров и возвращает его.
    '''
    pages_tag = bs(requests.get(url).text, "html.parser").find(
        'div', {"class": 'col-sm-6 text-right'})
    pages_number = pages_tag.text.split()[-2]
    return int(pages_number)+1
    # или брать ссылку на последнюю страницу из спика, а из нее последнюю цифру. сложнее?


def check_http_returncode(url):
    '''
    Функция проверяет код возврата http запроса. 
    '''
    if (requests.get(url).status_code != 200):
        print("Ответ по данному url не был положительным. Попробуйте другой url.")
        return False
    return True


def get_names(soup, res_dict):
    """
    Функция находит наименования товаров и записывает их в словарь.
    """
    product_names = soup.find_all('span', itemprop="name")
    for name in product_names:
        res_dict['Название'].append(name.text)


def get_prices(soup, res_dict):
    """
    Функция находит цены товаров и записывает их в словарь.
    """
    prices = soup.find_all('meta', itemprop='price')
    for price in prices:
        res_dict['Цена'].append(price['content'])


def get_descriptions(soup, res_dict):
    """
    Функция находит описания товаров и записывает их в словарь.
    """
    descriptions = soup.find_all('div', {"class": 'description'})
    for descr in descriptions:
        text = descr.get_text(' ')
        res_dict['Описание'].append(text.replace('\n', '')[:-2])


def login(cabinet_url):
    """
    Функция вводит значения в строки для логина и пароля личного кабинета.
    Сохраняет скриншот результата попытки входа.
    """
    #<input type="text" name="email" value="" placeholder="E-Mail адрес" id="input-email" class="form-control"> - поле логина
    #<input type="password" name="password" value="" placeholder="Пароль" id="input-password" class="form-control"> - поле пароля
    #<input style="margin-top: 15px; display: inline-block;" type="submit" value="Вход" class="btn btn-primary pull-right"> - кнопка ввода
    options = webdriver.ChromeOptions() 
    options.add_experimental_option('excludeSwitches', ['enable-logging']) #чтоб хром не писал ворнинги на какие-то usb

    try:
        driver = webdriver.Chrome(options=options,executable_path="Computer-networks\\Lab1\\chromedriver\\chromedriver.exe")
        driver.get(cabinet_url)

        login_field = driver.find_element(By.NAME,"email")
        password_field = driver.find_element(By.NAME,"password")
        login_field.send_keys("some text")
        password_field.send_keys("and some")
        buttons = driver.find_elements(By.CLASS_NAME,"btn.btn-primary.pull-right") #кнопки "регистрация" и "ввод"
        buttons[1].click()

        driver.save_screenshot("login result.png")
    except Exception as ex:
        print(ex)
    finally:
        driver.quit()


if __name__ == "__main__":
    # получать на инпуте?
    url = "https://elikon.ru/tele-video-audio/televizory-i-aksessuary/televizory"
    if not check_http_returncode(url):
        exit()

    pages_number = get_pages_number(url)
    res_dict = {'Название': [], 'Цена': [], 'Описание': []}

    for i in range(1, pages_number):
        tmp_url = url+"?page={}".format(i)
        # есть смысл проверять каждую ссылку?
        # if not check_http_returncode(tmp_url): exit()
        soup = bs(requests.get(tmp_url).text, "html.parser")
        get_names(soup, res_dict)
        get_prices(soup, res_dict)
        get_descriptions(soup, res_dict)

    csv_table = pd.DataFrame(res_dict)
    csv_table.to_csv('result.csv')

    # проверка результата 
    #csv = pd.read_csv("result.csv", index_col=0)
    #print(csv)

    cabinet_url ="https://elikon.ru/my_account"
    login(cabinet_url)

    
    