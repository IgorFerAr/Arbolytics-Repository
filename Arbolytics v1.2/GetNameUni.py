from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import time
from bs4 import BeautifulSoup

def get_nome(ID_MUNICIP,ID_UNIDADE):
  #--1 Setup
  url = "https://cnes.datasus.gov.br/pages/estabelecimentos/ficha/index.jsp?coUnidade=" + str(ID_MUNICIP) + str(ID_UNIDADE)
  options = Options()
  #options.add_argument ("--headless")
  browser = webdriver.Chrome()
  browser.implicitly_wait(2)
  #--| Parse or automatio
  browser.get(url)
  #wait = WebDriverWait (browser, 10)
  #tag = browser.find_elements_by_css_selector('body>li:nth-child(2)')
  #result = browser.find_elements (By.XPATH,'/html/body/div[2]/main/div/div[3]/div[1]/div/section/div[3]/div/div[2]/div[1]/div/form/div[1]/div[1]/div/input')
  
  try:
      element = WebDriverWait(browser, 10).until(
          EC.visibility_of_element_located((By.XPATH, '/html/body/div[2]/main/div/div[3]/div[1]/div/section/div[3]/div/div[2]/div[1]/div/form/div[3]/div[1]/div/input'))
      )
      # Realize alguma ação no elemento (por exemplo, interagir com o input)
      logradouro = browser.find_elements (By.XPATH,'/html/body/div[2]/main/div/div[3]/div[1]/div/section/div[3]/div/div[2]/div[1]/div/form/div[3]/div[1]/div/input')
      numero = browser.find_elements (By.XPATH,'/html/body/div[2]/main/div/div[3]/div[1]/div/section/div[3]/div/div[2]/div[1]/div/form/div[3]/div[2]/div/input')
      bairro = browser.find_elements (By.XPATH,'/html/body/div[2]/main/div/div[3]/div[1]/div/section/div[3]/div/div[2]/div[1]/div/form/div[4]/div[1]/div/input')

  except Exception as e:
      print("Elemento não encontrado ou não visível. Ocorreu um erro:", str(e))

  if len(logradouro):
    for x in logradouro:
      aux1 = x.get_attribute('value')
    for y in numero:
      aux2 = y.get_attribute('value')  
    for z in bairro:
      aux3 = z.get_attribute('value')  

    aux = aux1 + ', ' + aux2 + ', ' + aux3
    return(aux)
  else:
    print('Unidade nao encontrada:' + str(ID_MUNICIP) + ' ' + str(ID_UNIDADE) + ' link: https://cnes.datasus.gov.br/pages/estabelecimentos/ficha/index.jsp?coUnidade=' + str(ID_MUNICIP) + str(ID_UNIDADE))

  
  



