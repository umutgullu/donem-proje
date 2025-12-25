from flask import Flask, render_template, session, request, redirect, url_for
import random
from veri import askibaraj_scrape

app = Flask(__name__)
app.secret_key = 'ultragizlisifre'

TARGET_DAY = 30

# BARAJ VERİSİNİ ÇEKME
try:
    baraj_data = askibaraj_scrape()
    subaslangic = float(baraj_data['aktifKullanilabilir'].replace('%', '').replace(",", "."))
    STARTING_WATER = subaslangic
    print(f"✓ Baraj verisi: {STARTING_WATER}%")
except Exception as e:
    print(f"Hata: {e}")
    STARTING_WATER = 75.0

EVENTS = [
    {
        "id": 1,
        "text": "Komşun kapıyı yumrukluyor. Çocuğu baygın, bir bardak su için yalvarıyor.",
        "options": [
            {"txt": "Ver (-0.20 Su)", "val": "give"},
            {"txt": "Kapıyı açma (Su gitmez)", "val": "ignore"}
        ]
    },
    {
        "id": 2,
        "text": "Sokakta patlak bir ana boru var. Tazyikli su boşa akıyor ama etraf çok kaygan.",
        "options": [
            {"txt": "Yaklaş ve doldurmayı dene (+0.5 Şanslı / -0.3 Şanssız)", "val": "fill"},
            {"txt": "Uzak dur", "val": "ignore"}
        ]
    },
    {
        "id": 3,
        "text": "Eski bir süpermarket deposu buldun. İçerisi karanlık.",
        "options": [
            {"txt": "İçeri gir ve ara (+0.3 / -0.2)", "val": "scavenge"},
            {"txt": "Güvenli değil, dön", "val": "ignore"}
        ]
    },
    {
        "id": 4,
        "text": "Seyyar satıcı: 'Akıllı saatini ver, yarım şişe ılık su al'.",
        "options": [
            {"txt": "Takas et (+0.15 Su)", "val": "trade"},
            {"txt": "Reddet", "val": "ignore"}
        ]
    },
    {
        "id": 5,
        "text": "Aşırı sıcak hava dalgası! Buharlaşma çok yüksek.",
        "options": [
            {"txt": "Ekstra su iç (-0.15)", "val": "drink"},
            {"txt": "Dayanmaya çalış (Riskli)", "val": "endure"}
        ]
    },
    {
        "id": 6,
        "text": "Parktaki fıskiyeler arızalanmış, damlatıyor.",
        "options": [
            {"txt": "Sabırla bekle ve biriktir (+0.2)", "val": "wait"},
            {"txt": "Vakit kaybı", "val": "ignore"}
        ]
    },
    {
        "id": 7,
        "text": "Yaşlı bir adam sana yardım istiyor: 'Torunuma götürmem lazım'.",
        "options": [
            {"txt": "Yardım et (-0.25 Su)", "val": "give"},
            {"txt": "Kusura bakma dede", "val": "ignore"}
        ]
    },
    {
        "id": 8,
        "text": "Terk edilmiş bir evin bodrumunda eski su bidonları gördün.",
        "options": [
            {"txt": "Kontrol et (+0.4 / -0.1)", "val": "scavenge"},
            {"txt": "Riskli görünüyor", "val": "ignore"}
        ]
    },
    {
        "id": 9,
        "text": "Meteoroloji: 'Yarın gece %30 yağmur ihtimali var'.",
        "options": [
            {"txt": "Kapları dışarı koy ve bekle (+0.6 / 0)", "val": "wait"},
            {"txt": "Boş iş, vakit kaybet", "val": "ignore"}
        ]
    },
    {
        "id": 10,
        "text": "Silahlı bir grup yol kesiyor: 'Suyunu ver yoksa...'",
        "options": [
            {"txt": "Teslim ol (-0.40 Su)", "val": "give"},
            {"txt": "Kaç ve saklan (Riskli / -0.2)", "val": "endure"}
        ]
    },
    {
        "id": 11,
        "text": "Hastanede gönüllü çalışanlar: 'Yardım edersen günlük rasyondan veriyoruz'.",
        "options": [
            {"txt": "Kabul et ve çalış (+0.25 Su)", "val": "trade7"},
            {"txt": "Enerjini koru", "val": "ignore"}
        ]
    },
    {
        "id": 12,
        "text": "Klimalı bir ofise girebilirsin ama güvenlik senin suyunu kontrol ediyor.",
        "options": [
            {"txt": "Gir ve serinle (-0.05 Su vergisi)", "val": "drink"},
            {"txt": "Dışarıda kal", "val": "ignore"}
        ]
    },
    {
        "id": 13,
        "text": "Bodrum katta eski bir kuyu var. İpi çürümüş.",
        "options": [
            {"txt": "İnmeyi dene (+0.7 / -0.4)", "val": "fill"},
            {"txt": "Çok tehlikeli", "val": "ignore"}
        ]
    },
    {
        "id": 14,
        "text": "İnternet kafelerde 'Su Avı' oyunu var: Kazanırsan gerçek su alıyorsun.",
        "options": [
            {"txt": "Oyna (+0.3 / -0.1)", "val": "trade6"},
            {"txt": "Kumara girmem", "val": "ignore"}
        ]
    },
    {
        "id": 15,
        "text": "Bir kedi sürekli miyavlıyor. Susuz görünüyor.",
        "options": [
            {"txt": "Biraz ver (-0.10 Su)", "val": "give"},
            {"txt": "Hayvanlar adapte olur", "val": "ignore"}
        ]
    },
    {
        "id": 16,
        "text": "Yer altı çarşısında 'Kaçak Su Ticareti' duyumları var.",
        "options": [
            {"txt": "Araştır (+0.35 / -0.3)", "val": "scavenge"},
            {"txt": "Polise yakalanmak istemem", "val": "ignore"}
        ]
    },
    {
        "id": 17,
        "text": "Eski arkadaşın aradı: 'Buluşalım, belki bir şeyler halledebiliriz'.",
        "options": [
            {"txt": "Git (+0.2 / 0)", "val": "trade5"},
            {"txt": "Fazla yorgun hissediyorum", "val": "ignore"}
        ]
    },
    {
        "id": 18,
        "text": "Belediye seyyar tankerleri su dağıtıyor. 3 saatlik kuyruk var.",
        "options": [
            {"txt": "Bekle (+0.45 Su)", "val": "wait"},
            {"txt": "Enerjimi harcamam", "val": "ignore"}
        ]
    },
    {
        "id": 19,
        "text": "Gece yarısı siren sesleri! 'Acil su kesintisi 48 saat sürecek'.",
        "options": [
            {"txt": "Panikle fazla iç (-0.20)", "val": "drink"},
            {"txt": "Sakin kal, planına devam et", "val": "ignore"}
        ]
    },
    {
        "id": 20,
        "text": "Zengin bir adam: 'Benim yerime sıraya gir, iki kat veririm'.",
        "options": [
            {"txt": "Kabul et (+0.35 Su)", "val": "trade4"},
            {"txt": "Onuruma dokunur", "val": "ignore"}
        ]
    },
    {
        "id": 21,
        "text": "Çocuklar mahalleye su kaçağı bulmuş. Herkes koşuyor.",
        "options": [
            {"txt": "Sen de koş (+0.4 / -0.15)", "val": "fill"},
            {"txt": "Kavgaya girmek istemem", "val": "ignore"}
        ]
    },
    {
        "id": 22,
        "text": "Sırtındaki çantayı çalmaya çalışan biri var!",
        "options": [
            {"txt": "Direnmeden ver (-0.5 Su)", "val": "give"},
            {"txt": "Direne direne kaç (-0.2 / -0.4)", "val": "endure"}
        ]
    },
    {
        "id": 23,
        "text": "Eski bir cami avlusunda musluk açık unutulmuş.",
        "options": [
            {"txt": "Sessizce yaklaş ve doldur (+0.3)", "val": "fill"},
            {"txt": "Saygısızlık olur", "val": "ignore"}
        ]
    },
    {
        "id": 24,
        "text": "Doktor: 'Dehidratasyon belirtileri gösteriyorsun, çok iç'.",
        "options": [
            {"txt": "Tavsiyeyi dinle (-0.25 Su)", "val": "drink"},
            {"txt": "İyi hissediyorum, idare ederim", "val": "ignore"}
        ]
    },
    {
        "id": 25,
        "text": "İnşaat alanında işçiler su borusu kırmış. Ortalık çamur deryası.",
        "options": [
            {"txt": "Çamurlu da olsa topla (+0.25 / -0.1)", "val": "scavenge"},
            {"txt": "Hastalık riski çok yüksek", "val": "ignore"}
        ]
    },
    {
        "id": 26,
        "text": "Radyo: 'Hükümet yardım paketi dağıtacak. Kimlik gerekli'.",
        "options": [
            {"txt": "Başvur ve bekle (+0.5 Su)", "val": "wait"},
            {"txt": "Bürokratik işler, vakit kaybı", "val": "ignore"}
        ]
    },
    {
        "id": 27,
        "text": "Sokakta bidon satıyorlar: 'Telefonunu ver, 1 litre su senin'.",
        "options": [
            {"txt": "Değiştir (+0.30 Su)", "val": "trade2"},
            {"txt": "Telefonuma ihtiyacım var", "val": "ignore"}
        ]
    },
    {
        "id": 28,
        "text": "Gölet kenarında insanlar su filtreliyor. Yöntem şüpheli.",
        "options": [
            {"txt": "Denemeye değer (+0.35 / -0.25)", "val": "scavenge"},
            {"txt": "Sağlığımı riske atmam", "val": "ignore"}
        ]
    },
    {
        "id": 29,
        "text": "Apartman yöneticisi: 'Ortak su deposu var, katkı yapacak mısın?'",
        "options": [
            {"txt": "Katkı yap (-0.15 Su) [Sonra +0.2 şans]", "val": "trade3"},
            {"txt": "Kendi başıma hallederim", "val": "ignore"}
        ]
    },
    {
        "id": 30,
        "text": "Eski bir otobüs durağında karton üstü 'Yardım' yazısı var.",
        "options": [
            {"txt": "Yaklaş ve bak (+0.15 / 0)", "val": "scavenge"},
            {"txt": "Tuzak olabilir", "val": "ignore"}
        ]
    }
]

def get_random_event():
    return random.choice(EVENTS)

@app.route('/')
def index():
    session.clear()
    return render_template('index.html', page='welcome')

@app.route('/intro', methods=['POST'])
def intro():
    return render_template('index.html', page='start')

@app.route('/start', methods=['POST'])
def start_game():
    session['day'] = 1
    session['water'] = round(STARTING_WATER, 2)
    session['game_over'] = False
    
    first_event = get_random_event()
    
    return render_template('index.html',
                         page='game',
                         day=1,
                         water=round(STARTING_WATER, 2),
                         event_text=first_event['text'],
                         options=first_event['options'],
                         msg=None)

@app.route('/action', methods=['POST'])
def action():
    if session.get('game_over'):
        return redirect(url_for('index'))

    choice = request.form.get('choice')
    current_water = session.get('water', 0)
    current_day = session.get('day', 1)
    
    msg = ""
    water_change = 0
    dice = random.randint(1, 100)
    
    # Seçim sonuçları
    if choice == 'ignore':
        msg = "Harekete geçmedin. Durum değişmedi."
        water_change = 0
    elif choice == 'give':
        water_change = -0.20
        msg = "Suyu paylaştın. Vicdanın rahat ama rezerve kan ağlıyor."
    elif choice == 'fill':
        if dice > 40: 
            water_change = 0.50
            msg = "Başardın! Kovanı ağzına kadar doldurdun."
        else:
            water_change = -0.30
            msg = "Hayır! Ayağın kaydı, elindeki suyun bir kısmı döküldü."
    elif choice == 'scavenge':
        if dice > 50:
            water_change = 0.30
            msg = "Tozlu rafların arkasında bir şişe su buldun!"
        else:
            water_change = -0.20
            msg = "Tuzak! Bir fare üzerine atladı, korkuyla su mataranı düşürdün."
    elif choice == 'trade':
        water_change = 0.15
        msg = "Saatini verdin. Artık zamanı bilmiyorsun ama suyun var."
    elif choice =="trade2":
        water_change=1.05
        msg="Takas yaptın ve büyük bir su stoğu elde ettin!"
    elif choice == 'trade3':
        water_change = -0.15
        msg = "Katkıda bulundun. Topluluk seni takdir ediyor."
    elif choice == 'trade4':
        water_change = 0.35
        msg = "Zengin adamın teklifini kabul ettin. Su stokların arttı."
    elif choice == 'trade5':
        water_change = 0.20
        msg = "Arkadaşınla buluştun ve su takası yaptınız."
    elif choice == 'trade6':
        water_change = 0.30 - 0.10
        msg = "Oyunu kazandın! Hem su kazandın hem de biraz kaybettin."
    elif choice == 'trade7':
        water_change = 0.25
        msg = "Hastanede çalıştın ve günlük rasyondan su aldın."
    elif choice == 'drink':
        water_change = -0.15
        msg = "Serinledin. Hayatta kalmak için gerekliydi."
    elif choice == 'endure':
        if dice > 70:
            water_change = 0
            msg = "İnanılmaz bir iradeyle susuzluğa dayandın."
        else:
            water_change = -0.25
            msg = "Dayanamadın. Baygınlık geçirdin ve terleyerek çok su kaybettin."
    elif choice == 'wait':
        if dice > 20:
            water_change = 0.20
            msg = "Sabreden derviş muradına ermiş. Birkaç yudum birikti."
        else:
            water_change = -0.05
            msg = "Beklerken güneş tepene vurdu, daha çok susadın."
    
    # Günlük tüketim
    daily_drain = round(random.uniform(0.08, 0.12), 2)
    total_change = water_change - daily_drain
    new_water = round(current_water + total_change, 2)
    
    full_msg = f"{msg} (Günlük Tüketim: -{daily_drain:.2f})"
    
    # Su bitti mi?
    if new_water <= 0:
        new_water = 0
        session['game_over'] = True
        return render_template('index.html',
                             page='end',
                             title="HAYATİ FONKSİYONLAR DURDU",
                             message=f"SUYUN BİTTİ! {current_day}. GÜNDE HAYAT SON BULDU. SU HAYATTIR! SAHİP ÇIKIN!",

                             win=False)
    
    # Gün ilerlet
    session['water'] = new_water
    session['day'] = current_day + 1
    
    # Kazanma kontrolü
    if session['day'] > TARGET_DAY:
        session['game_over'] = True
        return render_template('index.html',
                             page='end',
                             title="GÖREV BAŞARILI",
                             message=f"30. GÜNÜ TAMAMLADIN! YAĞMURLAR BAŞLADI. KALAN SU: {new_water} LT \n GERÇEKTE SU BİRİKTİRMEK, OYUNDA BİRİKTİRMEKTEN DAHA ZOR!",
                             win=True)
    
    # Yeni olay
    next_event = get_random_event()
    
    return render_template('index.html',
                         page='game',
                         day=session['day'],
                         water=new_water,
                         event_text=next_event['text'],
                         options=next_event['options'],
                         msg=full_msg)

if __name__ == '__main__':
    app.run(debug=True, port=5000)