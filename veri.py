import requests
from bs4 import BeautifulSoup
import time
from flask import Flask, render_template

def askibaraj_scrape():

    try:
        url= "https://www.aski.gov.tr/tr/baraj.aspx"
        headers ={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"}
        sayfa = requests.get(url, headers=headers)

        icerik= BeautifulSoup(sayfa.content, "html.parser")
        tarih = icerik.find ("span", {"id": "lblTarih2"}).text
        doluluk = icerik.find ("span", {"id": "LblYuzde2"}).text
        aktifKullanilabilir = icerik.find ("span", {"id": "AktifYuzde2"}).text

        return {
            'tarih': tarih,
            'doluluk': doluluk,
            'aktifKullanilabilir': aktifKullanilabilir
        }
    except Exception as e:
        return None

app = Flask(__name__, template_folder='./templates')

@app.route('/')
def ana_sayfa():
    try:
        veri = askibaraj_scrape()

        
        if veri is None:
            return "VERİ ÇEKİLEMEDİ - SCRAPING HATASI"
        
        return render_template('index.html', data=veri)
    except Exception as e:
        return f"Scraping Hatası: {e}"

if __name__ == '__main__':
    app.run(debug=True)