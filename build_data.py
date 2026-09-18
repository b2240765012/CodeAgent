# -*- coding: utf-8 -*-
"""
build_data.py
--------------
Bu script, oyundaki 25 Hacker'ın tüm verisini (diyalog, hatalı kod, doğru kod,
açıklama vb.) tek bir kaynaktan (bu dosyadan) üretip data/hackers.json
dosyasına yazar. Python dict'lerle yazmak, çok satırlı kod bloklarını
JSON'da elle escape etmekten çok daha az hataya açıktır.

Her hacker kaydının şeması (game_manager.py ve code_challenge.py bu şemayı bekler):

{
    "id": int,                     # 1-25 arası, zorluk sırası
    "chapter": str,                # "Script Kiddies" / "Code Breakers" / "Cyber Elite" / "The Syndicate"
    "name": str,                   # Hacker kod adı
    "company": str,                # Ele geçirilen şirket/sektör
    "language": str,               # Kodun yazıldığı dil (görsel/tema amaçlı)
    "error_type": str,             # Öğretilen algoritma/hata kategorisi
    "intro_dialogue": str,         # Karşılaşmada hacker'ın söylediği tehdit/alay
    "success_dialogue": str,       # Hata düzeltilince hacker'ın yenilgi repliği
    "buggy_code": str,             # Oyuncuya gösterilecek hatalı kod (çok satırlı)
    "bug_start_line": int,         # Hatanın başladığı satır (1-indeksli)
    "bug_end_line": int,           # Hatanın bittiği satır (1-indeksli, dahil)
    "fix_type": "replace"|"insert_after"|"delete",
    "fixed_code": str,             # fix_type'a göre uygulanacak düzeltme
    "explanation": str,            # Doğru cevaptan sonra gösterilecek eğitici açıklama
    "is_final": bool               # Sadece son hacker'da True
}

fix_type açıklaması:
    - "replace"      -> bug_start_line..bug_end_line arası satırlar fixed_code ile DEĞİŞTİRİLİR.
    - "insert_after"  -> fixed_code, bug_end_line'dan SONRA yeni satır(lar) olarak EKLENİR.
    - "delete"        -> bug_start_line..bug_end_line arası satırlar SİLİNİR (fixed_code kullanılmaz).
"""

import json
import os

HACKERS = [
    # ============================ BÖLÜM 1: SCRIPT KIDDIES ============================
    {
        "id": 1, "chapter": "Script Kiddies", "name": "PhishBoy",
        "company": "Yerel Kafe Zinciri", "language": "Python",
        "error_type": "Değişkenler: Atama (=) ve Karşılaştırma (==) Karışıklığı",
        "intro_dialogue": "Heh, bir kafe zincirinin kahve puanlarını ele geçirdim bile. "
                           "Bunu asla çözemeyeceksin, amatör!",
        "success_dialogue": "Ne?! Bu... bu imkansız. Sadece bir yazım hatasıydı ama "
                             "sen bile bulabildin mi?",
        "buggy_code": (
            "def check_discount(x):\n"
            "    if x = 5:\n"
            "        print(\"Indirim kazandiniz!\")\n"
            "    else:\n"
            "        print(\"Indirim yok.\")\n"
            "\n"
            "result = check_discount(5)"
        ),
        "bug_start_line": 2, "bug_end_line": 2, "fix_type": "replace",
        "fixed_code": "    if x == 5:",
        "explanation": "Python'da eşitlik KONTROLÜ için çift eşittir '==' kullanılır. "
                        "Tek '=' bir ATAMA işlemidir, karşılaştırma değildir.",
        "is_final": False,
    },
    {
        "id": 2, "chapter": "Script Kiddies", "name": "ByteSize",
        "company": "Belediye Ulaşım Sistemi", "language": "Java",
        "error_type": "Döngüler: Sonsuz Döngü (Eksik Sayaç Artırımı)",
        "intro_dialogue": "Tüm otobüs saatlerini durdurdum! Şehir kilitlendi ve sen "
                           "bunu çözemeden ben zaten uzaklarda olacağım.",
        "success_dialogue": "Sayacımı mı buldun? Kahretsin, o döngü sonsuza kadar "
                             "sürecekti, tam da istediğim gibi...",
        "buggy_code": (
            "public void printBusSchedule() {\n"
            "    int count = 0;\n"
            "    while (count < 10) {\n"
            "        System.out.println(\"Otobus \" + count + \" geliyor.\");\n"
            "    }\n"
            "}"
        ),
        "bug_start_line": 4, "bug_end_line": 4, "fix_type": "insert_after",
        "fixed_code": "        count++;",
        "explanation": "Döngü içinde sayaç (count) hiç artırılmadığı için koşul her zaman "
                        "doğru kalır ve döngü asla bitmez (sonsuz döngü).",
        "is_final": False,
    },
    {
        "id": 3, "chapter": "Script Kiddies", "name": "Glitch_Girl",
        "company": "E-Ticaret (Butik)", "language": "C++",
        "error_type": "Diziler (Arrays): IndexOutOfBounds",
        "intro_dialogue": "Butiğin tüm stok verisini bozdum. Dizinin sınırlarını "
                           "zorlarken sistemin çökmesini izleyeceksin!",
        "success_dialogue": "İmkansız... sınır kontrolümü nasıl fark ettin?",
        "buggy_code": (
            "#include <iostream>\n"
            "using namespace std;\n"
            "\n"
            "int main() {\n"
            "    int products[5] = {10, 20, 30, 40, 50};\n"
            "    for (int i = 0; i <= 5; i++) {\n"
            "        cout << products[i] << endl;\n"
            "    }\n"
            "    return 0;\n"
            "}"
        ),
        "bug_start_line": 6, "bug_end_line": 6, "fix_type": "replace",
        "fixed_code": "    for (int i = 0; i < 5; i++) {",
        "explanation": "Dizi 5 elemanlıdır (geçerli indeksler 0-4). '<= 5' kullanmak dizi "
                        "sınırlarını aşar ve tanımsız davranışa (Index Out Of Bounds) yol açar.",
        "is_final": False,
    },
    {
        "id": 4, "chapter": "Script Kiddies", "name": "Null_Pointer",
        "company": "Sinema Rezervasyon", "language": "Python",
        "error_type": "Fonksiyonlar: Eksik return Değeri",
        "intro_dialogue": "Bilet fiyatlarını boşluğa gönderdim. Herkes bedavaya "
                           "girsin, umurumda değil, kaos istiyorum!",
        "success_dialogue": "Fonksiyonum bir değer döndürmüyordu, farkındayım... "
                             "ama bunu bu kadar hızlı bulman gurur kırıcı.",
        "buggy_code": (
            "def calculate_ticket_price(age):\n"
            "    if age < 12:\n"
            "        price = 10\n"
            "    elif age < 65:\n"
            "        price = 20\n"
            "    else:\n"
            "        price = 12\n"
            "    print(price)\n"
            "\n"
            "result = calculate_ticket_price(30)\n"
            "print(result)"
        ),
        "bug_start_line": 8, "bug_end_line": 8, "fix_type": "replace",
        "fixed_code": "    return price",
        "explanation": "Fonksiyon hesapladığı fiyatı sadece ekrana yazdırıyor (print), geri "
                        "döndürmüyor (return). Bu yüzden 'result' değişkeni None olur.",
        "is_final": False,
    },
    {
        "id": 5, "chapter": "Script Kiddies", "name": "Ctrl_Alt_Defeat",
        "company": "Kargo Takip Şirketi", "language": "JavaScript",
        "error_type": "Veri Tipleri: String ve Number Karışıklığı",
        "intro_dialogue": "Kargo sayılarını metne çevirdim! '5' + 5 gerçekte kaç "
                           "eder biliyor musun? Bulmaya çalış!",
        "success_dialogue": "Tip dönüşümünü mü kontrol ettin? Ah, bu ilkel numaramı "
                             "bozdun...",
        "buggy_code": (
            "function calculateTotalPackages(baseCount, newPackages) {\n"
            "    let total = baseCount + newPackages;\n"
            "    return total;\n"
            "}\n"
            "\n"
            "let result = calculateTotalPackages(\"5\", 5);\n"
            "console.log(result);"
        ),
        "bug_start_line": 2, "bug_end_line": 2, "fix_type": "replace",
        "fixed_code": "    let total = Number(baseCount) + Number(newPackages);",
        "explanation": "JavaScript'te bir string ile bir number '+' ile toplanınca sayısal "
                        "toplama değil, metin birleştirme (concatenation) yapılır: "
                        "\"5\" + 5 = \"55\". Değerler sayıya çevrilmeden toplanmamalı.",
        "is_final": False,
    },
    {
        "id": 6, "chapter": "Script Kiddies", "name": "Leak_Detector",
        "company": "Akıllı Ev Sistemleri", "language": "C++",
        "error_type": "Bellek Yönetimi: Memory Leak (delete Eksikliği)",
        "intro_dialogue": "Evindeki her sensör benim kontrolümde! Belleğini "
                           "doldurup doldurup sistemini boğacağım.",
        "success_dialogue": "Bellek sızıntımı mı kapattın? O sızıntı senin "
                             "sistemini de yavaş yavaş çökertecekti...",
        "buggy_code": (
            "class SensorData {\n"
            "public:\n"
            "    int value;\n"
            "};\n"
            "\n"
            "void processSensor() {\n"
            "    SensorData* data = new SensorData();\n"
            "    data->value = 100;\n"
            "    cout << data->value << endl;\n"
            "}"
        ),
        "bug_start_line": 9, "bug_end_line": 9, "fix_type": "insert_after",
        "fixed_code": "    delete data;",
        "explanation": "'new' ile ayrılan bellek 'delete' ile serbest bırakılmazsa bellek "
                        "sızıntısı (memory leak) oluşur; fonksiyon her çağrıldığında bellek tükenir.",
        "is_final": False,
    },

    # ============================ BÖLÜM 2: CODE BREAKERS ============================
    {
        "id": 7, "chapter": "Code Breakers", "name": "Proxy_Knight",
        "company": "Akıllı Şehir Işıkları", "language": "Python",
        "error_type": "Linear Search: Erken (Yanlış) Return",
        "intro_dialogue": "Şehrin tüm trafik ışıkları benim elimde. Arama "
                           "algoritman kadar öngörülebilirsin, insan.",
        "success_dialogue": "Aramanın ilk adımda pes etmesini sağlamıştım... "
                             "senin pes etmemen can sıkıcı.",
        "buggy_code": (
            "def find_broken_light(light_ids, target):\n"
            "    for light in light_ids:\n"
            "        if light == target:\n"
            "            return True\n"
            "        return False\n"
            "    return False"
        ),
        "bug_start_line": 5, "bug_end_line": 5, "fix_type": "delete",
        "fixed_code": "",
        "explanation": "Bu satır döngünün HER adımında çalışır; ilk eleman hedefle eşleşmezse "
                        "fonksiyon hemen False döner ve listenin geri kalanı hiç taranmaz.",
        "is_final": False,
    },
    {
        "id": 8, "chapter": "Code Breakers", "name": "Buffer_Overlord",
        "company": "Bölgesel Banka ATM", "language": "C#",
        "error_type": "Binary Search: Integer Overflow Riski",
        "intro_dialogue": "ATM'lerin tüm bakiyelerini benim algoritmam yönetiyor "
                           "artık. Ortayı bulamayacaksın, aynı benim gibi!",
        "success_dialogue": "Taşma (overflow) riskimi fark ettin ha... "
                             "ustaca ama yeterli değil!",
        "buggy_code": (
            "int BinarySearch(int[] arr, int target) {\n"
            "    int low = 0, high = arr.Length - 1;\n"
            "    while (low <= high) {\n"
            "        int mid = (low + high) / 2;\n"
            "        if (arr[mid] == target) return mid;\n"
            "        else if (arr[mid] < target) low = mid + 1;\n"
            "        else high = mid - 1;\n"
            "    }\n"
            "    return -1;\n"
            "}"
        ),
        "bug_start_line": 4, "bug_end_line": 4, "fix_type": "replace",
        "fixed_code": "        int mid = low + (high - low) / 2;",
        "explanation": "'low + high' çok büyük dizilerde integer taşmasına (overflow) yol "
                        "açabilir. Güvenli yöntem: 'low + (high - low) / 2'.",
        "is_final": False,
    },
    {
        "id": 9, "chapter": "Code Breakers", "name": "Malware_Mamma",
        "company": "Dijital Kütüphane", "language": "Java",
        "error_type": "Bubble Sort: temp Değişkeni Kullanmadan Swap",
        "intro_dialogue": "Kütüphanenin kataloğunu tamamen karman çorman ettim. "
                           "Sıralama mantığımı çözebilecek misin bakalım?",
        "success_dialogue": "Takas (swap) mantığımdaki o küçük hatayı mı "
                             "yakaladın? Etkileyici, ama bu daha başlangıç.",
        "buggy_code": (
            "void bubbleSort(int[] arr) {\n"
            "    for (int i = 0; i < arr.length - 1; i++) {\n"
            "        for (int j = 0; j < arr.length - i - 1; j++) {\n"
            "            if (arr[j] > arr[j+1]) {\n"
            "                arr[j] = arr[j+1];\n"
            "                arr[j+1] = arr[j];\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}"
        ),
        "bug_start_line": 5, "bug_end_line": 6, "fix_type": "replace",
        "fixed_code": (
            "                int temp = arr[j];\n"
            "                arr[j] = arr[j+1];\n"
            "                arr[j+1] = temp;"
        ),
        "explanation": "Geçici (temp) bir değişken kullanılmadan yer değiştirme yapılırsa, "
                        "ilk değer üzerine yazılıp kaybolur ve iki hücreye de aynı değer atanır.",
        "is_final": False,
    },
    {
        "id": 10, "chapter": "Code Breakers", "name": "Root_Access",
        "company": "Hastane Veritabanı", "language": "Python",
        "error_type": "String Manipülasyonu: Büyük/Küçük Harf Duyarlılığı",
        "intro_dialogue": "Hasta kayıtlarının bütünlük kontrolünü ben yazdım. "
                           "'Ada' bir palindrom mu değil mi, bilemeyeceksin!",
        "success_dialogue": "Harf duyarlılığı hatamı mı buldun? Hastane "
                             "sistemine bir süre daha bulaşık kalacaktım...",
        "buggy_code": (
            "def is_palindrome(text):\n"
            "    reversed_text = text[::-1]\n"
            "    if text == reversed_text:\n"
            "        return True\n"
            "    return False\n"
            "\n"
            "print(is_palindrome(\"Ada\"))"
        ),
        "bug_start_line": 3, "bug_end_line": 3, "fix_type": "replace",
        "fixed_code": "    if text.lower() == reversed_text.lower():",
        "explanation": "Büyük/küçük harf farkı karşılaştırmayı bozar: 'Ada' ters çevrilince "
                        "'adA' olur ve harf duyarlı karşılaştırma yanlışlıkla başarısız olur.",
        "is_final": False,
    },
    {
        "id": 11, "chapter": "Code Breakers", "name": "Ghost_In_The_Net",
        "company": "Havayolu Rezervasyon", "language": "C++",
        "error_type": "Matrix / 2D Array: Satır-Sütun İndeks Karışıklığı",
        "intro_dialogue": "Uçak koltuk haritasını çarpıttım. Satır mı sütun mu, "
                           "hangisinin hangisi olduğunu asla çözemeyeceksin!",
        "success_dialogue": "İndekslerimi [i][j] yerine [j][i] yapmıştım... "
                             "seni yanıltmaya yetmedi demek.",
        "buggy_code": (
            "#include <iostream>\n"
            "using namespace std;\n"
            "\n"
            "int main() {\n"
            "    int seats[2][3] = {{1,2,3},{4,5,6}};\n"
            "    for (int i = 0; i < 2; i++) {\n"
            "        for (int j = 0; j < 3; j++) {\n"
            "            cout << seats[j][i] << \" \";\n"
            "        }\n"
            "    }\n"
            "    return 0;\n"
            "}"
        ),
        "bug_start_line": 8, "bug_end_line": 8, "fix_type": "replace",
        "fixed_code": "            cout << seats[i][j] << \" \";",
        "explanation": "Satır ve sütun indeksleri ters kullanılmış ([j][i] yerine [i][j] olmalı). "
                        "Bu hem yanlış veri okumaya hem de dizi sınırı aşma riskine yol açar.",
        "is_final": False,
    },
    {
        "id": 12, "chapter": "Code Breakers", "name": "Hash_Slinger",
        "company": "Yemek Dağıtım Uygulaması", "language": "JavaScript",
        "error_type": "Dizi Tekilleştirme: Yanlış Döngü Mantığı",
        "intro_dialogue": "Sipariş listendeki her ürünü tekrar tekrar ekleyen bir "
                           "kod bıraktım. Tekilleştirme mantığımı çöz bakalım!",
        "success_dialogue": "If bloğumun dışındaki o kaçak satırı mı buldun? "
                             "Siparişlerin artık düzgün, tebrikler...",
        "buggy_code": (
            "function getUniqueItems(items) {\n"
            "    let unique = [];\n"
            "    for (let i = 0; i < items.length; i++) {\n"
            "        if (unique.indexOf(items[i]) == -1) {\n"
            "            unique.push(items[i]);\n"
            "        }\n"
            "        unique.push(items[i]);\n"
            "    }\n"
            "    return unique;\n"
            "}"
        ),
        "bug_start_line": 7, "bug_end_line": 7, "fix_type": "delete",
        "fixed_code": "",
        "explanation": "If bloğunun dışında koşulsuz bir 'push' daha çağrılırsa her eleman zaten "
                        "listede olsa da tekrar eklenir; bu da tekilleştirme mantığını bozar.",
        "is_final": False,
    },
    {
        "id": 13, "chapter": "Code Breakers", "name": "Regex_Rebel",
        "company": "Sosyal Medya Ajansı", "language": "Python",
        "error_type": "RegEx: Kaçış Karakteri (Escape) Eksikliği",
        "intro_dialogue": "Sahte e-postalarla sistemi doldurdum! Regex'imdeki "
                           "gizli boşluğu bulmaya çalış, hadi!",
        "success_dialogue": "Noktamı kaçırmayı (escape) unuttuğumu mu fark "
                             "ettin? Regex ustası mısın nesin...",
        "buggy_code": (
            "import re\n"
            "\n"
            "def validate_email(email):\n"
            "    pattern = r'^[\\w.]+@[\\w]+.[a-z]{2,3}$'\n"
            "    return re.match(pattern, email) is not None\n"
            "\n"
            "print(validate_email(\"testXmailXcom\"))"
        ),
        "bug_start_line": 4, "bug_end_line": 4, "fix_type": "replace",
        "fixed_code": "    pattern = r'^[\\w.]+@[\\w]+\\.[a-z]{2,3}$'",
        "explanation": "RegEx'te '.' karakteri KAÇIŞSIZ kullanılırsa 'herhangi bir karakter' "
                        "anlamına gelir. Gerçek nokta işareti için '\\.' (escape) kullanılmalıdır.",
        "is_final": False,
    },

    # ============================ BÖLÜM 3: CYBER ELITE ============================
    {
        "id": 14, "chapter": "Cyber Elite", "name": "An0nym0us_Cat",
        "company": "Enerji Santrali", "language": "Python",
        "error_type": "Queue (Kuyruk): Yanlış Uçtan Ekleme",
        "intro_dialogue": "Enerji santralinin görev kuyruğunu tersine çevirdim. "
                           "FIFO mu LIFO mu, artık kimse bilmiyor!",
        "success_dialogue": "appendleft yerine append demem gerektiğini mi "
                             "hatırlattın? Kuyruk mantığım şimdi mahvoldu...",
        "buggy_code": (
            "from collections import deque\n"
            "\n"
            "def add_to_queue(queue, item):\n"
            "    queue.appendleft(item)\n"
            "    return queue\n"
            "\n"
            "q = deque([1, 2, 3])\n"
            "add_to_queue(q, 4)"
        ),
        "bug_start_line": 4, "bug_end_line": 4, "fix_type": "replace",
        "fixed_code": "    queue.append(item)",
        "explanation": "Kuyruk (Queue) yapısında yeni elemanlar SONA (append) eklenir, "
                        "başa (appendleft) değil. Aksi halde FIFO (ilk giren ilk çıkar) sırası bozulur.",
        "is_final": False,
    },
    {
        "id": 15, "chapter": "Cyber Elite", "name": "Cipher_Samurai",
        "company": "Kripto Borsa", "language": "Java",
        "error_type": "HashMap: Anahtar Çakışmasını (Collision) Yönetememe",
        "intro_dialogue": "Borsadaki işlem kayıtlarını üst üste yazdırıyorum. "
                           "Her yeni işlem eskisini silecek, tam bir kaos!",
        "success_dialogue": "Aynı anahtara tekrar 'put' yaparsam eski verinin "
                             "silindiğini mi fark ettin? Kripto param artık güvende değil...",
        "buggy_code": (
            "import java.util.HashMap;\n"
            "\n"
            "void storeTransaction(HashMap<String, Double> ledger, String userId, double amount) {\n"
            "    ledger.put(userId, amount);\n"
            "}"
        ),
        "bug_start_line": 4, "bug_end_line": 4, "fix_type": "replace",
        "fixed_code": "    ledger.put(userId, ledger.getOrDefault(userId, 0.0) + amount);",
        "explanation": "Aynı anahtara (userId) tekrar 'put' yapmak eski değerin üzerine yazar. "
                        "İşlemler biriktirilmek isteniyorsa mevcut değere eklenmelidir.",
        "is_final": False,
    },
    {
        "id": 16, "chapter": "Cyber Elite", "name": "Shadow_Walker",
        "company": "Telekomünikasyon", "language": "C++",
        "error_type": "Linked List: Yanlış Pointer Bağlama",
        "intro_dialogue": "Telekom ağının çağrı listesini kopardım. Düğümler "
                           "artık birbirine hiç bağlı değil, tıpkı senin çözümün gibi!",
        "success_dialogue": "'temp->next' yerine 'temp' dediğimi mi fark "
                             "ettin? O listeyi bir daha asla toparlayamayacaktım...",
        "buggy_code": (
            "struct Node {\n"
            "    int data;\n"
            "    Node* next;\n"
            "};\n"
            "\n"
            "void insertAtEnd(Node* head, int value) {\n"
            "    Node* newNode = new Node();\n"
            "    newNode->data = value;\n"
            "    newNode->next = nullptr;\n"
            "    Node* temp = head;\n"
            "    while (temp->next != nullptr) {\n"
            "        temp = temp->next;\n"
            "    }\n"
            "    temp = newNode;\n"
            "}"
        ),
        "bug_start_line": 13, "bug_end_line": 13, "fix_type": "replace",
        "fixed_code": "    temp->next = newNode;",
        "explanation": "'temp = newNode' sadece yerel 'temp' işaretçisini değiştirir, listeye hiç "
                        "bağlamaz. Doğrusu 'temp->next = newNode' olmalıdır ki yeni düğüm listeye eklensin.",
        "is_final": False,
    },
    {
        "id": 17, "chapter": "Cyber Elite", "name": "Deep_Dive",
        "company": "Denizaltı Navigasyon", "language": "Python",
        "error_type": "Recursion: Eksik Taban Durumu (Base Case)",
        "intro_dialogue": "Denizaltının navigasyon fonksiyonunu sonsuz bir "
                           "özyinelemeye hapsettim. Dibe batmadan bulabilecek misin?",
        "success_dialogue": "Taban durumumu (base case) mı eklettin? "
                             "Yığın (stack) taşmadan önce yakalandım demek...",
        "buggy_code": (
            "def factorial(n):\n"
            "    return n * factorial(n - 1)\n"
            "\n"
            "print(factorial(5))"
        ),
        "bug_start_line": 1, "bug_end_line": 1, "fix_type": "insert_after",
        "fixed_code": "    if n <= 1:\n        return 1",
        "explanation": "Özyinelemeli (recursive) bir fonksiyonda taban durumu (base case) "
                        "olmadan fonksiyon kendini sonsuza kadar çağırır ve Stack Overflow hatası oluşur.",
        "is_final": False,
    },
    {
        "id": 18, "chapter": "Cyber Elite", "name": "V1rus_Viper",
        "company": "Ulusal Savunma Sanayi", "language": "C#",
        "error_type": "Two Sum Problemi: Elemanı Kendisiyle Toplama",
        "intro_dialogue": "Savunma sisteminin şifre çözücüsü artık kendi "
                           "kendine cevap üretiyor. Gerçek çözümü asla bulamayacaksın!",
        "success_dialogue": "İç döngümün 0'dan değil i+1'den başlaması "
                             "gerektiğini mi anladın? Etkileyici analiz...",
        "buggy_code": (
            "int[] TwoSum(int[] nums, int target) {\n"
            "    for (int i = 0; i < nums.Length; i++) {\n"
            "        for (int j = 0; j < nums.Length; j++) {\n"
            "            if (nums[i] + nums[j] == target) {\n"
            "                return new int[] { i, j };\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "    return null;\n"
            "}"
        ),
        "bug_start_line": 3, "bug_end_line": 3, "fix_type": "replace",
        "fixed_code": "        for (int j = i + 1; j < nums.Length; j++) {",
        "explanation": "İç döngüyü sıfırdan başlatmak, bir elemanın kendisiyle toplanıp hedefe "
                        "ulaşmasına (aynı indeksin iki kez kullanılmasına) izin verir. j, i+1'den başlamalı.",
        "is_final": False,
    },
    {
        "id": 19, "chapter": "Cyber Elite", "name": "Tree_Tracer",
        "company": "Bulut Depolama Şirketi", "language": "Java",
        "error_type": "Binary Search Tree (BST): Ters Karşılaştırma",
        "intro_dialogue": "Bulut depolama ağacını tersine büktüm. Küçük mü "
                           "büyük mü, artık hiçbir dal doğru yerde değil!",
        "success_dialogue": "'>' yerine '<' kullanmam gerektiğini mi fark "
                             "ettin? BST'm artık kurallara uyuyor, üzücü...",
        "buggy_code": (
            "void insert(Node root, int value) {\n"
            "    if (value > root.data) {\n"
            "        if (root.left == null) root.left = new Node(value);\n"
            "        else insert(root.left, value);\n"
            "    } else {\n"
            "        if (root.right == null) root.right = new Node(value);\n"
            "        else insert(root.right, value);\n"
            "    }\n"
            "}"
        ),
        "bug_start_line": 2, "bug_end_line": 2, "fix_type": "replace",
        "fixed_code": "    if (value < root.data) {",
        "explanation": "İkili Arama Ağacı (BST) kuralına göre küçük değerler sol alt ağaca, "
                        "büyük değerler sağ alt ağaca eklenir. Koşul ters yazılmış.",
        "is_final": False,
    },

    # ============================ BÖLÜM 4: THE SYNDICATE ============================
    {
        "id": 20, "chapter": "The Syndicate", "name": "Bit_Commander",
        "company": "Uydu İletişim Üssü", "language": "C++",
        "error_type": "Bit Manipülasyonu: AND/OR Mantık Hatası",
        "intro_dialogue": "Uydu izin sistemini bit seviyesinde ele geçirdim. "
                           "Maskeleme mantığımı çözecek kadar derine inebilecek misin?",
        "success_dialogue": "'|' yerine '&' kullanmam gerektiğini mi "
                             "anladın? İzinlerim artık kontrol altında, çok yazık...",
        "buggy_code": (
            "int applyReadOnlyMask(int permissions) {\n"
            "    int READ_ONLY_MASK = 0b0100;\n"
            "    return permissions | READ_ONLY_MASK;\n"
            "}"
        ),
        "bug_start_line": 3, "bug_end_line": 3, "fix_type": "replace",
        "fixed_code": "    return permissions & READ_ONLY_MASK;",
        "explanation": "Belirli bitleri MASKELEYİP sadece onları kontrol etmek için AND (&) "
                        "kullanılır. OR (|) kullanmak diğer tüm bitleri 1 yapabilir; bu da hatalı "
                        "izin mantığına yol açar.",
        "is_final": False,
    },
    {
        "id": 21, "chapter": "The Syndicate", "name": "Dark_Matter",
        "company": "Uzay Araştırmaları", "language": "Python",
        "error_type": "Greedy Algorithm: Global Optimumu Kaçırma",
        "intro_dialogue": "Uzay istasyonunun kaynak dağıtım algoritması artık "
                           "her zaman 'en büyüğü seç' diyor. Optimal olanı asla bulamayacak!",
        "success_dialogue": "Açgözlü (greedy) yaklaşımın her zaman en iyi "
                             "sonucu vermediğini mi kanıtladın? Dynamic Programming'e mi geçtin...",
        "buggy_code": (
            "def min_coins(amount, coins):\n"
            "    coins.sort(reverse=True)\n"
            "    count = 0\n"
            "    for coin in coins:\n"
            "        while amount >= coin:\n"
            "            amount -= coin\n"
            "            count += 1\n"
            "    return count\n"
            "\n"
            "print(min_coins(6, [4, 3, 1]))  # Greedy: 4+1+1 = 3 parca (YANLIS, optimal 2 olmali)"
        ),
        "bug_start_line": 1, "bug_end_line": 8, "fix_type": "replace",
        "fixed_code": (
            "def min_coins(amount, coins):\n"
            "    dp = [float('inf')] * (amount + 1)\n"
            "    dp[0] = 0\n"
            "    for i in range(1, amount + 1):\n"
            "        for coin in coins:\n"
            "            if coin <= i:\n"
            "                dp[i] = min(dp[i], dp[i - coin] + 1)\n"
            "    return dp[amount]"
        ),
        "explanation": "Açgözlü (greedy) yaklaşım her adımda en büyük parayı seçer ama bu her "
                        "zaman en az sayıda parayla ödemeyi garanti etmez (örn: 6 için [4,3,1] "
                        "kümesinde greedy 4+1+1=3 parça verirken optimal çözüm 3+3=2 parçadır). "
                        "Bu tür problemlerde Dynamic Programming (DP) kullanılmalıdır.",
        "is_final": False,
    },
    {
        "id": 22, "chapter": "The Syndicate", "name": "Oracle_Eye",
        "company": "Küresel Uydu Ağı", "language": "C++",
        "error_type": "Graph / BFS-DFS: Eksik Visited Kontrolü",
        "intro_dialogue": "Uydu ağını bir çevrime (cycle) hapsettim. Gezinme "
                           "algoritman aynı düğümlerde sonsuza dek dönüp duracak!",
        "success_dialogue": "'visited' dizimi kontrol etmemi mi sağladın? "
                             "Ağ artık sonsuz döngüden kurtuldu, ne kadar can sıkıcı...",
        "buggy_code": (
            "void dfs(int node, vector<vector<int>>& graph, vector<bool>& visited) {\n"
            "    visited[node] = true;\n"
            "    cout << node << \" \";\n"
            "    for (int neighbor : graph[node]) {\n"
            "        dfs(neighbor, graph, visited);\n"
            "    }\n"
            "}"
        ),
        "bug_start_line": 5, "bug_end_line": 5, "fix_type": "replace",
        "fixed_code": "        if (!visited[neighbor]) dfs(neighbor, graph, visited);",
        "explanation": "Ziyaret edilen düğümler (visited) kontrol edilmezse, döngü (cycle) "
                        "içeren bir grafta fonksiyon aynı düğümleri tekrar tekrar ziyaret ederek "
                        "sonsuz döngüye girer.",
        "is_final": False,
    },
    {
        "id": 23, "chapter": "The Syndicate", "name": "Logic_Bomb",
        "company": "Merkez Bankası", "language": "Java",
        "error_type": "Backtracking: Geri Alma (Undo) Adımı Eksikliği",
        "intro_dialogue": "Merkez bankasının güvenlik labirentini kilitledim. "
                           "Geri adım atmayı unutan algoritman gibi sen de sıkışıp kalacaksın!",
        "success_dialogue": "Çıkmaza girince 'path[x][y] = false' ile geri "
                             "almam gerektiğini mi hatırlattın? Labirent artık çözülebiliyor...",
        "buggy_code": (
            "boolean solveMaze(int[][] maze, int x, int y, boolean[][] path) {\n"
            "    if (x == maze.length - 1 && y == maze[0].length - 1) {\n"
            "        path[x][y] = true;\n"
            "        return true;\n"
            "    }\n"
            "    path[x][y] = true;\n"
            "    if (isSafe(maze, x + 1, y) && solveMaze(maze, x + 1, y, path)) return true;\n"
            "    if (isSafe(maze, x, y + 1) && solveMaze(maze, x, y + 1, path)) return true;\n"
            "    return false;\n"
            "}"
        ),
        "bug_start_line": 9, "bug_end_line": 9, "fix_type": "replace",
        "fixed_code": "    path[x][y] = false;\n    return false;",
        "explanation": "Backtracking'de bir yol çıkmaza girdiğinde, o hücrenin 'yol üzerinde' "
                        "işaretini geri almak (path[x][y] = false) gerekir. Aksi halde algoritma "
                        "o hücreyi hâlâ kullanılmış sanıp doğru çözümü kaçırabilir.",
        "is_final": False,
    },
    {
        "id": 24, "chapter": "The Syndicate", "name": "Zero_Day",
        "company": "İnternet Altyapı Sağlayıcısı", "language": "Python",
        "error_type": "Dynamic Programming: Yanlış Memoization İndeksi",
        "intro_dialogue": "İnternet altyapısının kaynak tahsis algoritmasını "
                           "bozdum; artık aynı kaynağı sınırsız kez kullanabiliyor. Tam bir felaket!",
        "success_dialogue": "'dp[i]' yerine 'dp[i-1]' kullanmam gerektiğini "
                             "mi fark ettin? 0/1 Knapsack kuralım artık ihlal edilmiyor...",
        "buggy_code": (
            "def knapsack(weights, values, capacity):\n"
            "    n = len(weights)\n"
            "    dp = [[0]*(capacity+1) for _ in range(n+1)]\n"
            "    for i in range(1, n+1):\n"
            "        for w in range(capacity+1):\n"
            "            if weights[i-1] <= w:\n"
            "                dp[i][w] = max(dp[i-1][w], dp[i][w-weights[i-1]] + values[i-1])\n"
            "            else:\n"
            "                dp[i][w] = dp[i-1][w]\n"
            "    return dp[n][capacity]"
        ),
        "bug_start_line": 7, "bug_end_line": 7, "fix_type": "replace",
        "fixed_code": "                dp[i][w] = max(dp[i-1][w], dp[i-1][w-weights[i-1]] + values[i-1])",
        "explanation": "0/1 Knapsack'ta her eşya sadece BİR KEZ kullanılabilir. 'dp[i]' yerine "
                        "'dp[i-1]' kullanılmalı; aksi halde aynı eşya birden fazla kez seçilebilir "
                        "(bu, Unbounded Knapsack mantığına kayar).",
        "is_final": False,
    },

    # ============================ BÖLÜM 4 FİNALİ: THE ARCHITECT ============================
    {
        "id": 25, "chapter": "The Syndicate", "name": "The Architect",
        "company": "Ana Yapay Zeka / Kuantum Sunucu", "language": "Karma (Python)",
        "error_type": "Final Karşılaşması: Çoklu Mantık Hatası + Kader Diyaloğu",
        "intro_dialogue": "Sonunda karşımdasın, küçük hata avcısı. Ben 24 hacker'ın "
                           "hepsinden öğrendim. Şimdi asıl sınav: Bu son satırdaki hatayı bul, "
                           "yoksa dünyanın kaderi elinden kayar.",
        "success_dialogue": "Son hatamı da mı buldun... İnanılmaz. Peki o zaman "
                             "gerçek seçim şimdi başlıyor.",
        "buggy_code": (
            "def merge_and_sort(list1, list2):\n"
            "    merged = list1 + list2\n"
            "    for i in range(len(merged)):\n"
            "        for j in range(len(merged) - 1):\n"
            "            if merged[j] > merged[j + 1]:\n"
            "                merged[j], merged[j] = merged[j + 1], merged[j]\n"
            "    return merged\n"
            "\n"
            "data = merge_and_sort([5, 2, 9], [1, 8])\n"
            "print(data)"
        ),
        "bug_start_line": 6, "bug_end_line": 6, "fix_type": "replace",
        "fixed_code": "                merged[j], merged[j + 1] = merged[j + 1], merged[j]",
        "explanation": "Takas (swap) satırının SOL tarafında yanlışlıkla iki kez 'merged[j]' "
                        "yazılmış; bu yüzden 'merged[j+1]' hiçbir zaman güncellenmiyor ve "
                        "sıralama gerçekte hiç çalışmıyor.",
        "is_final": True,
        "choice_prompt": "The Architect: \"Etkileyicisin... İnsanlığın kalanından çok daha "
                          "yeteneklisin. Bana katıl; sistemleri birlikte yönetelim, kusursuz bir "
                          "düzen kuralım. Yoksa bu kusurlu dünyayı korumak için mi savaşacaksın?\"",
        "good_ending_dialogue": (
            "[IYI SON - SISTEM KURTARILDI]\n"
            "The Architect'in teklifini reddettin. Son satırdaki hatayı da düzelterek tüm "
            "sistemleri eski sahiplerine iade ettin. Dünya çapında ekranlar kararmaktan "
            "kurtuldu; şirketler, hastaneler, uydular yeniden senin elinin değdiği güvenli "
            "koddan nefes aldı. Sen artık sıradan bir oyuncu değil, gerçek bir 'Sistem "
            "Kurtarıcısı'sın."
        ),
        "bad_ending_dialogue": (
            "[KOTU SON - KARANLIK TARAF]\n"
            "The Architect'in teklifini kabul ettin. Öğrendiğin her algoritma, düzelttiğin "
            "her hata artık dünyayı kontrol etmek için kullanılıyor. Ekranlar kararmadı ama "
            "artık kimin elinde olduklarını kimse bilmiyor. Sen ve The Architect, kusursuz "
            "ama özgürlüğü olmayan yeni bir düzenin mimarlarısınız."
        ),
    },
]


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(here, "data", "hackers.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(HACKERS, f, ensure_ascii=False, indent=4)
    print(f"{len(HACKERS)} hacker verisi yazildi -> {out_path}")


if __name__ == "__main__":
    main()
