import requests
from bs4 import BeautifulSoup
import time
import random
def askibaraj_scrape():
    while True:
        url= "https://www.aski.gov.tr/tr/baraj.aspx"
        headers ={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"}
        sayfa = requests.get(url, headers=headers)
        icerik= BeautifulSoup(sayfa.content, "html.parser")
        tarih = icerik.find ("span", {"id": "lblTarih2"}).text
        print("Tarih:", tarih)
        doluluk = icerik.find ("span", {"id": "LblYuzde2"}).text
        print("Toplam Doluluk Yüzdesi:", doluluk)
        aktifKullanilabilir = icerik.find ("span", {"id": "AktifYuzde2"}).text
        print("Aktif Kullanılabilirlik Yüzdesi:", aktifKullanilabilir)
        time.sleep(10)
askibaraj_scrape()