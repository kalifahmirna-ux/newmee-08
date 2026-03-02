"""
Data lengkap untuk 9 tipe kepribadian NEWME CLASS
Berdasarkan kombinasi Kepribadian (Introvert/Extrovert/Ambivert) dan 5 Element (Kayu/Api/Tanah/Logam/Air)
Dengan penjelasan sederhana dan rekomendasi karir spesifik
"""

PERSONALITY_DATA = {
    # ============= INTROVERT TYPES =============
    "iK": {
        "code": "iK",
        "fullName": "Introvert - KAYU",
        "personalityType": "INTROVERT",
        "dominantElement": "KAYU",
        "label": "Si KREATIF",
        "color": "#4CAF50",  # Green
        
        # Penjelasan sederhana untuk orang awam
        "penjelasanSederhana": "Anda adalah orang yang pendiam namun memiliki ide-ide kreatif yang luar biasa. Anda lebih suka bekerja sendiri dan menghasilkan karya yang unik dan berbeda dari yang lain.",
        
        "kepribadian": [
            "Pendiam tapi penuh ide", "Suka berimajinasi", "Teliti dan detail", 
            "Tenang dan kalem", "Penuh semangat tersembunyi", "Suka hal-hal unik"
        ],
        
        "karakter": [
            "Pengamat yang baik", "Suka tampil beda", "Penuh imajinasi", "Suka hal baru",
            "Percaya diri", "Romantis", "Perfeksionis", "Idealis",
            "Pemimpi", "Misterius", "Ekspresif terkontrol"
        ],
        
        "kekuatanJatidiri": {
            "tipe": "Si KREATIF",
            "kehidupan": "KAYA IDE & GAGASAN",
            "kesehatan": "Perhatikan pencernaan",
            "kontribusi": "Kreativitas tinggi",
            "kekhasan": "Selalu tampil berbeda",
            "kharisma": "Daya tarik alami"
        },
        
        "kompilasiAdaptasi": {
            "belajar": "Dengan cara membayangkan dan memvisualisasikan",
            "bekerja": "Lebih produktif saat diberi kebebasan",
            "kalibrasi": "Istirahat dengan menonton atau tidur",
            "memimpin": "Cocok memimpin organisasi kreatif",
            "jalurBisnis": "Cocok jadi pemilik usaha sendiri"
        },
        
        "ciriKhas": [
            "Penampilan menarik", "Selalu tampil beda", "Punya daya tarik", 
            "Wawasan luas", "Suka berkarya"
        ],
        
        "dibutuhkanPadaProfesi": "Yang memerlukan KREATIFITAS & SISTEM",
        
        # REKOMENDASI KARIR SPESIFIK
        "rekomendasiKarir": "Desainer Grafis, Arsitek, Penulis, Seniman, Animator, Content Creator, Fashion Designer, Interior Designer, Sutradara Film, Fotografer, Game Developer, UI/UX Designer"
    },
    
    "iT": {
        "code": "iT",
        "fullName": "Introvert - TANAH",
        "personalityType": "INTROVERT",
        "dominantElement": "TANAH",
        "label": "Si AKTIF",
        "color": "#FFC107",  # Yellow/Gold
        
        "penjelasanSederhana": "Anda adalah orang yang tekun, rajin, dan sangat bisa diandalkan. Meski pendiam, Anda selalu bekerja keras dan konsisten dalam mencapai tujuan.",
        
        "kepribadian": [
            "Pendiam tapi pekerja keras", "Suka fakta dan data", "Teliti",
            "Sabar", "Tidak mudah tersinggung", "Stabil dan konsisten"
        ],
        
        "karakter": [
            "Stabil", "Solidaritas", "Pekerja Ulet", "Sosial", "Menyerap",
            "Kolaboratif", "Dermawan", "Petarung", "Transaksional", "Faktual",
            "Kurang Percayaan", "Malas Mikir Dalam", "Gercep",
            "Pesohor", "Kekinian", "Jago Tangkap Peluang"
        ],
        
        "kekuatanJatidiri": {
            "tipe": "Si AKTIF",
            "kehidupan": "REALISTIS",
            "kesehatan": "OTOT GERAK",
            "kontribusi": "STAMINA",
            "kekhasan": "FISIK KUAT",
            "kharisma": "KEKAYAAN & DERMAWAN"
        },
        
        "kompilasiAdaptasi": {
            "belajar": "Menghapal",
            "bekerja": "Non Formal",
            "kalibrasi": "Belanja / Shoping",
            "dayaRaga": "Stamina",
            "memimpin": "Organisasi Sosial",
            "jalurBisnis": "Pedagang",
            "pendukungKarir": "Pendukung karir",
            "keahlian": "Jago Momentum",
            "karya": "Menjual",
            "keunggulan": "Inspirator dagang",
            "kemistri": "Gerak Cepat",
            "keutamaan": "Cuan Cepat",
            "kelimpahan": "Untung",
            "magnet": "Amanah Uang",
            "berbusana": "Kontras ideal",
            "kecepatan": "Meniru",
            "kesukaan": "Bergerak",
            "kebiasaan": "Menguras Energi",
            "semestaHidup": "Keberuntungan",
            "makanan": "Cemilan",
            "kehebatan": "Monetisasi produk nyata"
        },
        
        "ciriKhas": [
            "Fisik ideal", "Berotot", "Rajin Gerak",
            "Berat Badan cenderung bisa stabil", "Bicara dengan dipancing"
        ],
        
        "dibutuhkanPadaProfesi": "Yang memerlukan kekuatan OTOT & INGATAN",
        
        "penjelasanSederhana": "Anda adalah orang yang sangat aktif, energik, dan suka bergerak. Anda pandai melihat peluang dan cepat dalam mengambil tindakan.",
        
        "rekomendasiKarir": "Pedagang, Pengusaha Retail, Atlet, Pelatih Olahraga, Sales, Marketing, Event Organizer, Petani Modern, Peternak, Kontraktor, Tukang Bangunan, Mekanik, Sopir Truk/Bus"
    },
    
    "iL": {
        "code": "iL",
        "fullName": "Introvert - LOGAM",
        "personalityType": "INTROVERT",
        "dominantElement": "LOGAM",
        "label": "Si PEMIKIR",
        "color": "#9E9E9E",  # Grey/Silver
        
        "kepribadian": [
            "Minus Responsif", "bahasa LOGIKA", "investigatif",
            "Pasif Sosial", "Kurang sensitif", "Dingin / Cuek"
        ],
        
        "karakter": [
            "Tenang", "Serius", "Cuek", "Pemikir", "Sulit mengutarakan",
            "Kordinator", "Analis", "Data Oriented", "Mandiri", "Manajerial",
            "Kurang Percayaan", "Teritorial", "Ego Logik", "Tegas Hak",
            "Disiplin", "Workholic"
        ],
        
        "kekuatanJatidiri": {
            "tipe": "Si PEMIKIR",
            "kehidupan": "PEMIKIR",
            "kesehatan": "TULANG YANG PADAT",
            "kontribusi": "ADIL",
            "kekhasan": "DINGIN",
            "kharisma": "KETEGASAN"
        },
        
        "kompilasiAdaptasi": {
            "belajar": "Menalar Materi",
            "bekerja": "Formal",
            "kalibrasi": "Wisata Alam",
            "dayaRaga": "Otak",
            "memimpin": "Organisasi Korporasi",
            "jalurBisnis": "C.E.O",
            "pendukungKarir": "Kesabaran",
            "keahlian": "Analisis Strategi",
            "karya": "Inspirator Manajerial",
            "keunggulan": "Menata",
            "kemistri": "Mengatur",
            "keutamaan": "Logika",
            "kelimpahan": "Tanggung Jawab",
            "magnet": "Kedudukan",
            "berbusana": "Stylis",
            "kecepatan": "Menganalisa",
            "kesukaan": "Bekerja",
            "kebiasaan": "Menguras Pikiran",
            "semestaHidup": "Otorisasi",
            "makanan": "Fast Food",
            "kehebatan": "Sabar dlm Membangun"
        },
        
        "ciriKhas": [
            "Fisik ideal", "Wibawa", "Rapih",
            "Berat Badan cenderung mudah naik", "Bicara bikin Mikir"
        ],
        
        "dibutuhkanPadaProfesi": "Yang memerlukan kekuatan ANALISA & DATA"
    },
    
    "iA": {
        "code": "iA",
        "fullName": "Introvert - API",
        "personalityType": "INTROVERT",
        "dominantElement": "API",
        "label": "Si PERASA",
        "color": "#F44336",  # Red
        
        "kepribadian": [
            "Kurang Responsif", "bahasa HATI", "investigatif",
            "Reaktif dalam", "Sangat sensitif", "Mendalam"
        ],
        
        "karakter": [
            "Hangat", "Empatik", "Intuitif", "Penuh perasaan",
            "Loyal", "Setia", "Romantis mendalam", "Peka",
            "Mudah terluka", "Tertutup", "Misterius", "Dalam"
        ],
        
        "kekuatanJatidiri": {
            "tipe": "Si PERASA",
            "kehidupan": "KEDALAMAN RASA",
            "kesehatan": "JANTUNG & DARAH",
            "kontribusi": "EMPATI",
            "kekhasan": "MENDALAM",
            "kharisma": "KEHANGATAN TULUS"
        },
        
        "kompilasiAdaptasi": {
            "belajar": "Merasakan",
            "bekerja": "Bermakna",
            "kalibrasi": "Meditasi / Refleksi",
            "dayaRaga": "Energi Hati",
            "memimpin": "Organisasi Kemanusiaan",
            "jalurBisnis": "Healing & Coaching",
            "pendukungKarir": "Intuisi",
            "keahlian": "Membaca Orang",
            "karya": "Inspiratif",
            "keunggulan": "Menyentuh Hati",
            "kemistri": "Koneksi Mendalam",
            "keutamaan": "Ketulusan",
            "kelimpahan": "Cinta",
            "magnet": "Kedalaman",
            "berbusana": "Hangat & Lembut",
            "kecepatan": "Meresapi",
            "kesukaan": "Musik & Puisi",
            "kebiasaan": "Merenung",
            "semestaHidup": "Menyembuhkan",
            "makanan": "Comfort Food",
            "kehebatan": "Memahami Tanpa Kata"
        },
        
        "ciriKhas": [
            "Mata berbicara", "Hangat dalam diam", "Mendalam",
            "Fisik sensitif", "Bicara menyentuh hati"
        ],
        
        "dibutuhkanPadaProfesi": "Yang memerlukan EMPATI & KEDALAMAN"
    },
    
    "iAi": {
        "code": "iAi",
        "fullName": "Introvert - AIR",
        "personalityType": "INTROVERT",
        "dominantElement": "AIR",
        "label": "Si BIJAK",
        "color": "#2196F3",  # Blue
        
        "kepribadian": [
            "Sangat Un_Responsif", "bahasa FILOSOFI", "sangat investigatif",
            "Pasif total", "Sensitif pilihan", "Sangat kalem"
        ],
        
        "karakter": [
            "Bijaksana", "Reflektif", "Filosofis", "Mendalam",
            "Penyendiri", "Kontemplatif", "Observan", "Tenang",
            "Misterius", "Berwawasan", "Sabar", "Dalam"
        ],
        
        "kekuatanJatidiri": {
            "tipe": "Si BIJAK",
            "kehidupan": "KEBIJAKSANAAN",
            "kesehatan": "GINJAL & KANDUNG KEMIH",
            "kontribusi": "WAWASAN",
            "kekhasan": "KEDALAMAN PIKIR",
            "kharisma": "KETENANGAN"
        },
        
        "kompilasiAdaptasi": {
            "belajar": "Merenungkan",
            "bekerja": "Independen",
            "kalibrasi": "Sendirian",
            "dayaRaga": "Energi Pikir",
            "memimpin": "Organisasi Riset",
            "jalurBisnis": "Konsultan Strategi",
            "pendukungKarir": "Kedalaman",
            "keahlian": "Visi Jauh",
            "karya": "Filosofis",
            "keunggulan": "Melihat Esensi",
            "kemistri": "Memahami Pola",
            "keutamaan": "Kebijaksanaan",
            "kelimpahan": "Pengetahuan",
            "magnet": "Misteri",
            "berbusana": "Sederhana Elegan",
            "kecepatan": "Merenungi",
            "kesukaan": "Buku & Alam",
            "kebiasaan": "Berkontemplasi",
            "semestaHidup": "Memahami",
            "makanan": "Sederhana",
            "kehebatan": "Melihat Yang Tak Terlihat"
        },
        
        "ciriKhas": [
            "Aura tenang", "Mata dalam", "Bijaksana",
            "Fisik kering", "Bicara bermakna"
        ],
        
        "dibutuhkanPadaProfesi": "Yang memerlukan KEBIJAKSANAAN & VISI"
    },
    
    # ============= EXTROVERT TYPES =============
    "eK": {
        "code": "eK",
        "fullName": "Extrovert - KAYU",
        "personalityType": "EXTROVERT",
        "dominantElement": "KAYU",
        "label": "Si KREATIF",
        "color": "#4CAF50",
        
        "kepribadian": [
            "Extra Responsif", "bahasa IMAGINASI", "kurang investigatif",
            "extra aktif", "lebih sensitif", "mudah tersinggung"
        ],
        
        "karakter": [
            "Ekspresif", "Kreatif terbuka", "Inovatif", "Suka pamer ide",
            "Percaya diri tinggi", "Antusias", "Perfectsionis vokal",
            "Idealis aktif", "Optimis", "Berani", "Ekspansif"
        ],
        
        "kekuatanJatidiri": {
            "tipe": "Si KREATIF",
            "kehidupan": "KAYA GAGASAN",
            "kesehatan": "PENCERNAAN",
            "kontribusi": "KREATIFITAS",
            "kekhasan": "BERBEDA",
            "kharisma": "MEMPESONA"
        },
        
        "kompilasiAdaptasi": {
            "belajar": "Diskusi Kreatif",
            "bekerja": "Tim Kreatif",
            "kalibrasi": "Traveling",
            "dayaRaga": "Otak kanan aktif",
            "memimpin": "Startup",
            "jalurBisnis": "Founder",
            "pendukungKarir": "Networking",
            "keahlian": "Pitching",
            "karya": "Disruptif",
            "keunggulan": "Menginspirasi",
            "kemistri": "Kolaborasi Kreatif",
            "keutamaan": "Inovasi",
            "kelimpahan": "Ide",
            "magnet": "Kebaruan",
            "berbusana": "Statement",
            "kecepatan": "Ideasi",
            "kesukaan": "Brainstorming",
            "kebiasaan": "Eksplorasi",
            "semestaHidup": "Menciptakan Tren",
            "makanan": "Eksotis",
            "kehebatan": "Memvisualisasikan Masa Depan"
        },
        
        "ciriKhas": [
            "Karismatik", "Penuh Ide", "Energik",
            "Ekspresif", "Bicara memotivasi"
        ],
        
        "dibutuhkanPadaProfesi": "Yang memerlukan KREATIFITAS & KOMUNIKASI"
    },
    
    "eT": {
        "code": "eT",
        "fullName": "Extrovert - TANAH",
        "personalityType": "EXTROVERT",
        "dominantElement": "TANAH",
        "label": "Si AKTIF",
        "color": "#FFC107",
        
        "kepribadian": [
            "Extra Responsif", "bahasa FAKTA", "kurang investigatif",
            "extra aktif", "lebih sensitif", "mudah tersinggung"
        ],
        
        "karakter": [
            "Stabil", "Solidaritas", "Pekerja Ulet", "Sosial", "Menyerap",
            "Kolaboratif", "Dermawan", "Petarung", "Transaksional", "Faktual",
            "Kurang Percayaan", "Malas Mikir Dalam", "Gercep",
            "Pesohor", "Kekinian", "Jago Tangkap Peluang"
        ],
        
        "kekuatanJatidiri": {
            "tipe": "Si AKTIF",
            "kehidupan": "REALISTIS",
            "kesehatan": "OTOT GERAK",
            "kontribusi": "STAMINA",
            "kekhasan": "FISIK KUAT",
            "kharisma": "KEKAYAAN & DERMAWAN"
        },
        
        "kompilasiAdaptasi": {
            "belajar": "Menghapal",
            "bekerja": "Non Formal",
            "kalibrasi": "Belanja / Shoping",
            "dayaRaga": "Stamina",
            "memimpin": "Organisasi Sosial",
            "jalurBisnis": "Pedagang",
            "pendukungKarir": "Pendukung karir",
            "keahlian": "Jago Momentum",
            "karya": "Menjual",
            "keunggulan": "Inspirator dagang",
            "kemistri": "Gerak Cepat",
            "keutamaan": "Cuan Cepat",
            "kelimpahan": "Untung",
            "magnet": "Amanah Uang",
            "berbusana": "Kontras ideal",
            "kecepatan": "Meniru",
            "kesukaan": "Bergerak",
            "kebiasaan": "Menguras Energi",
            "semestaHidup": "Keberuntungan",
            "makanan": "Cemilan",
            "kehebatan": "Monetisasi produk nyata"
        },
        
        "ciriKhas": [
            "Fisik ideal", "Berotot", "Rajin Gerak",
            "Berat Badan cenderung bisa stabil", "Bicara tanpa dipancing"
        ],
        
        "dibutuhkanPadaProfesi": "Yang memerlukan kekuatan OTOT & INGATAN"
    },
    
    "eL": {
        "code": "eL",
        "fullName": "Extrovert - LOGAM",
        "personalityType": "EXTROVERT",
        "dominantElement": "LOGAM",
        "label": "Si PEMIKIR",
        "color": "#9E9E9E",
        
        "kepribadian": [
            "Extra Responsif", "bahasa LOGIKA", "kurang investigatif",
            "extra aktif", "lebih sensitif", "mudah tersinggung"
        ],
        
        "karakter": [
            "Tenang", "Serius", "Cuek", "Pemikir", "Sulit mengutarakan",
            "Kordinator", "Analis", "Data Oriented", "Mandiri", "Manajerial",
            "Kurang Percayaan", "Teritorial", "Ego Logik", "Tegas Hak",
            "Disiplin", "Workholic"
        ],
        
        "kekuatanJatidiri": {
            "tipe": "Si PEMIKIR",
            "kehidupan": "PEMIKIR",
            "kesehatan": "TULANG YANG PADAT",
            "kontribusi": "ADIL",
            "kekhasan": "DINGIN",
            "kharisma": "KETEGASAN"
        },
        
        "kompilasiAdaptasi": {
            "belajar": "Menalar Materi",
            "bekerja": "Formal",
            "kalibrasi": "Wisata Alam",
            "dayaRaga": "Otak",
            "memimpin": "Organisasi Korporasi",
            "jalurBisnis": "C.E.O",
            "pendukungKarir": "Kesabaran",
            "keahlian": "Analisis Strategi",
            "karya": "Inspirator Manajerial",
            "keunggulan": "Menata",
            "kemistri": "Mengatur",
            "keutamaan": "Logika",
            "kelimpahan": "Tanggung Jawab",
            "magnet": "Kedudukan",
            "berbusana": "Stylis",
            "kecepatan": "Menganalisa",
            "kesukaan": "Bekerja",
            "kebiasaan": "Menguras Pikiran",
            "semestaHidup": "Otorisasi",
            "makanan": "Fast Food",
            "kehebatan": "Sabar dlm Membangun"
        },
        
        "ciriKhas": [
            "Fisik ideal", "Wibawa", "Rapih",
            "Berat Badan cenderung bisa stabil", "Bicara bikin Mikir"
        ],
        
        "dibutuhkanPadaProfesi": "Yang memerlukan kekuatan ANALISA & DATA"
    },
    
    "eA": {
        "code": "eA",
        "fullName": "Extrovert - API",
        "personalityType": "EXTROVERT",
        "dominantElement": "API",
        "label": "Si PERASA",
        "color": "#F44336",
        
        "kepribadian": [
            "Extra Responsif", "bahasa HATI", "kurang investigatif",
            "extra aktif", "lebih sensitif", "mudah tersinggung"
        ],
        
        "karakter": [
            "Hangat terbuka", "Empatik aktif", "Intuitif vokal",
            "Ekspresif perasaan", "Loyal publik", "Romantis terbuka",
            "Antusias", "Passionate", "Inspiratif", "Memotivasi"
        ],
        
        "kekuatanJatidiri": {
            "tipe": "Si PERASA",
            "kehidupan": "SEMANGAT HIDUP",
            "kesehatan": "JANTUNG & DARAH",
            "kontribusi": "INSPIRASI",
            "kekhasan": "HANGAT",
            "kharisma": "MEMBAKAR SEMANGAT"
        },
        
        "kompilasiAdaptasi": {
            "belajar": "Diskusi Emosional",
            "bekerja": "Tim Hangat",
            "kalibrasi": "Gathering",
            "dayaRaga": "Energi Sosial",
            "memimpin": "Organisasi Motivasi",
            "jalurBisnis": "Motivator",
            "pendukungKarir": "Koneksi Hangat",
            "keahlian": "Public Speaking",
            "karya": "Memotivasi",
            "keunggulan": "Menggerakkan Orang",
            "kemistri": "Energi Positif",
            "keutamaan": "Semangat",
            "kelimpahan": "Relasi",
            "magnet": "Kehangatan",
            "berbusana": "Cerah & Hangat",
            "kecepatan": "Merespon",
            "kesukaan": "Event Sosial",
            "kebiasaan": "Berbagi",
            "semestaHidup": "Menginspirasi",
            "makanan": "Sharing Food",
            "kehebatan": "Membakar Semangat"
        },
        
        "ciriKhas": [
            "Karismatik hangat", "Ekspresif", "Passionate",
            "Fisik energik", "Bicara membakar semangat"
        ],
        
        "dibutuhkanPadaProfesi": "Yang memerlukan SEMANGAT & INSPIRASI"
    },
    
    # ============= AMBIVERT TYPES =============
    "aL": {
        "code": "aL",
        "fullName": "Ambivert - LOGAM",
        "personalityType": "AMBIVERT",
        "dominantElement": "LOGAM",
        "label": "Si TEGAS",
        "color": "#9E9E9E",
        
        "kepribadian": [
            "Seimbang Responsif", "bahasa LOGIKA", "cukup investigatif",
            "Fleksibel aktif", "Sensitif situasional", "Adaptif"
        ],
        
        "karakter": [
            "Seimbang", "Fleksibel", "Tegas situasional", "Adaptif",
            "Logis namun hangat", "Terstruktur tapi luwes",
            "Mandiri tapi kooperatif", "Disiplin fleksibel"
        ],
        
        "kekuatanJatidiri": {
            "tipe": "Si TEGAS",
            "kehidupan": "KESEIMBANGAN",
            "kesehatan": "PARU & USUS BESAR",
            "kontribusi": "KETEGASAN",
            "kekhasan": "SEIMBANG",
            "kharisma": "PROFESIONAL"
        },
        
        "kompilasiAdaptasi": {
            "belajar": "Kombinasi",
            "bekerja": "Hybrid",
            "kalibrasi": "Variasi",
            "dayaRaga": "Seimbang",
            "memimpin": "Organisasi Profesional",
            "jalurBisnis": "Manager",
            "pendukungKarir": "Adaptasi",
            "keahlian": "Mediasi",
            "karya": "Terstruktur",
            "keunggulan": "Menyeimbangkan",
            "kemistri": "Harmoni",
            "keutamaan": "Keadilan",
            "kelimpahan": "Stabilitas",
            "magnet": "Kepercayaan",
            "berbusana": "Profesional",
            "kecepatan": "Situasional",
            "kesukaan": "Keseimbangan",
            "kebiasaan": "Menyesuaikan",
            "semestaHidup": "Harmonisasi",
            "makanan": "Balanced Diet",
            "kehebatan": "Menjembatani"
        },
        
        "ciriKhas": [
            "Seimbang", "Profesional", "Adaptif",
            "Fisik proporsional", "Bicara tegas tapi hangat"
        ],
        
        "dibutuhkanPadaProfesi": "Yang memerlukan KETEGASAN & FLEKSIBILITAS"
    },
    
    "aAi": {
        "code": "aAi",
        "fullName": "Ambivert - AIR",
        "personalityType": "AMBIVERT",
        "dominantElement": "AIR",
        "label": "Si ADAPTIF",
        "color": "#2196F3",
        
        "kepribadian": [
            "Seimbang Responsif", "bahasa ADAPTASI", "cukup investigatif",
            "Fleksibel aktif", "Sensitif pilihan", "Sangat adaptif"
        ],
        
        "karakter": [
            "Adaptif", "Fleksibel", "Bijak situasional", "Mengalir",
            "Intuitif seimbang", "Reflektif aktif", "Menyesuaikan",
            "Tenang tapi aktif", "Berwawasan luas"
        ],
        
        "kekuatanJatidiri": {
            "tipe": "Si ADAPTIF",
            "kehidupan": "FLEKSIBILITAS",
            "kesehatan": "GINJAL & KANDUNG KEMIH",
            "kontribusi": "ADAPTASI",
            "kekhasan": "MENGALIR",
            "kharisma": "KELUWESAN"
        },
        
        "kompilasiAdaptasi": {
            "belajar": "Menyesuaikan",
            "bekerja": "Fleksibel",
            "kalibrasi": "Air & Alam",
            "dayaRaga": "Flow",
            "memimpin": "Organisasi Dinamis",
            "jalurBisnis": "Konsultan",
            "pendukungKarir": "Fleksibilitas",
            "keahlian": "Problem Solving",
            "karya": "Adaptif",
            "keunggulan": "Menyesuaikan",
            "kemistri": "Mengalir",
            "keutamaan": "Fleksibilitas",
            "kelimpahan": "Peluang",
            "magnet": "Kemudahan",
            "berbusana": "Situasional",
            "kecepatan": "Mengalir",
            "kesukaan": "Variasi",
            "kebiasaan": "Beradaptasi",
            "semestaHidup": "Menyesuaikan",
            "makanan": "Bervariasi",
            "kehebatan": "Selalu Siap"
        },
        
        "ciriKhas": [
            "Fleksibel", "Adaptif", "Mengalir",
            "Fisik menyesuaikan", "Bicara situasional"
        ],
        
        "dibutuhkanPadaProfesi": "Yang memerlukan ADAPTASI & FLEKSIBILITAS"
    },
    
    "aT": {
        "code": "aT",
        "fullName": "Ambivert - TANAH",
        "personalityType": "AMBIVERT",
        "dominantElement": "TANAH",
        "label": "Si STABIL",
        "color": "#FFC107",
        
        "kepribadian": [
            "Seimbang Responsif", "bahasa PRAKTIS", "cukup investigatif",
            "Fleksibel aktif", "Sensitif situasional", "Stabil adaptif"
        ],
        
        "karakter": [
            "Stabil seimbang", "Praktis fleksibel", "Realistis adaptif",
            "Konsisten tapi luwes", "Dapat diandalkan", "Down to earth",
            "Pekerja keras", "Bertanggung jawab"
        ],
        
        "kekuatanJatidiri": {
            "tipe": "Si STABIL",
            "kehidupan": "KESTABILAN",
            "kesehatan": "LIMPA & LAMBUNG",
            "kontribusi": "KONSISTENSI",
            "kekhasan": "STABIL",
            "kharisma": "DAPAT DIANDALKAN"
        },
        
        "kompilasiAdaptasi": {
            "belajar": "Praktik",
            "bekerja": "Stabil",
            "kalibrasi": "Aktivitas Fisik",
            "dayaRaga": "Kestabilan",
            "memimpin": "Organisasi Operasional",
            "jalurBisnis": "Operasional",
            "pendukungKarir": "Konsistensi",
            "keahlian": "Eksekusi",
            "karya": "Nyata",
            "keunggulan": "Menyelesaikan",
            "kemistri": "Kepercayaan",
            "keutamaan": "Kestabilan",
            "kelimpahan": "Keamanan",
            "magnet": "Keandalan",
            "berbusana": "Praktis",
            "kecepatan": "Steady",
            "kesukaan": "Rutinitas produktif",
            "kebiasaan": "Konsisten",
            "semestaHidup": "Membangun",
            "makanan": "Sehat Teratur",
            "kehebatan": "Menyelesaikan Dengan Tuntas"
        },
        
        "ciriKhas": [
            "Stabil", "Dapat diandalkan", "Konsisten",
            "Fisik kuat", "Bicara praktis"
        ],
        
        "dibutuhkanPadaProfesi": "Yang memerlukan KESTABILAN & KONSISTENSI"
    }
}


def get_personality_data(code: str) -> dict:
    """Get personality data by code"""
    return PERSONALITY_DATA.get(code, PERSONALITY_DATA.get("iK"))


def determine_personality_code(personality_type: str, dominant_element: str) -> str:
    """Determine personality code based on type and dominant element"""
    # Map personality type to prefix
    prefix_map = {
        "INTROVERT": "i",
        "EXTROVERT": "e",
        "AMBIVERT": "a"
    }
    
    # Map element to suffix
    element_map = {
        "KAYU": "K",
        "API": "A",
        "TANAH": "T",
        "LOGAM": "L",
        "AIR": "Ai"
    }
    
    prefix = prefix_map.get(personality_type.upper(), "a")
    suffix = element_map.get(dominant_element.upper(), "T")
    
    code = f"{prefix}{suffix}"
    
    # Check if code exists, otherwise return closest match
    if code in PERSONALITY_DATA:
        return code
    
    # Fallback mappings
    if code == "iAi":
        return "iAi"
    elif code == "eAi":
        return "aAi"  # No eAi, use ambivert version
    elif code == "aK":
        return "eK"  # No aK, use extrovert version
    elif code == "aA":
        return "eA"  # No aA, use extrovert version
    
    return "iK"  # Default fallback
