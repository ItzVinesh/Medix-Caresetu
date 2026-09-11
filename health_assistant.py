import os
import re

try:
    from PyPDF2 import PdfReader
except Exception:
    PdfReader = None


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_DIR = os.path.join(BASE_DIR, "knowledge")
CHUNKS = []

STOPWORDS = set(
    """
    a an and are as at be by can could did do does for from had has have how
    i if in into is it its of on or our should so than that the their them
    then there these they this to was were what when where which who will
    with would you your yours
    """.split()
)

EMERGENCY = {
    "keys": [
        "chest pain",
        "heart attack",
        "stroke",
        "severe breathing difficulty",
        "cannot breathe",
        "can't breathe",
        "unconscious",
        "severe bleeding",
        "vomiting blood",
        "seizure",
        "suicidal",
        "सीने में दर्द",
        "दिल का दौरा",
        "सांस लेने में दिक्कत",
        "बेहोश",
        "गंभीर खून बहना"
    ],
    "en": (
        "Emergency warning:\n"
        "- This may be a medical emergency.\n"
        "- Please call emergency services immediately.\n"
        "- Do not wait for a chatbot response.\n\n"
        "This assistant is not a substitute for emergency medical care."
    ),
    "hi": (
        "आपातकालीन चेतावनी:\n"
        "- यह एक मेडिकल आपातस्थिति हो सकती है।\n"
        "- कृपया तुरंत आपातकालीन सेवाओं को कॉल करें।\n"
        "- चैटबॉट के जवाब का इंतज़ार न करें।\n\n"
        "यह सहायक आपातकालीन चिकित्सा का विकल्प नहीं है।"
    )
}

TOPICS = [
    {
        "keys": ["fever", "temperature", "bukhar", "बुखार"],
        "en": (
            "Fever guidance:\n"
            "- Rest and drink plenty of fluids.\n"
            "- Wear light clothing.\n"
            "- Monitor temperature regularly.\n"
            "- Use fever medicine only if advised or normally safe for you.\n\n"
            "Warning signs:\n"
            "- Very high fever\n"
            "- Confusion\n"
            "- Difficulty breathing\n"
            "- Rash\n"
            "- Stiff neck\n\n"
            "Please consult a doctor if symptoms persist."
        ),
        "hi": (
            "बुखार मार्गदर्शन:\n"
            "- आराम करें और पर्याप्त तरल पदार्थ लें।\n"
            "- हल्के कपड़े पहनें।\n"
            "- समय-समय पर तापमान जांचें।\n"
            "- बुखार की दवा केवल सलाह पर या सुरक्षित होने पर ही लें।\n\n"
            "खतरे के संकेत:\n"
            "- बहुत तेज़ बुखार\n"
            "- उलझन\n"
            "- सांस लेने में दिक्कत\n"
            "- चकत्ते\n"
            "- गर्दन में अकड़न\n\n"
            "यदि लक्षण बने रहें तो डॉक्टर से संपर्क करें।"
        )
    },
    {
        "keys": ["cold", "sardi", "jukam", "runny nose", "sore throat", "सर्दी", "जुकाम"],
        "en": (
            "Common cold guidance:\n"
            "- Rest well.\n"
            "- Drink warm fluids.\n"
            "- Use saline gargles if needed.\n"
            "- Avoid close contact with others to reduce spread.\n\n"
            "Consult a doctor if fever persists or breathing difficulty develops."
        ),
        "hi": (
            "सर्दी-जुकाम मार्गदर्शन:\n"
            "- अच्छी तरह आराम करें।\n"
            "- गर्म तरल पदार्थ लें।\n"
            "- आवश्यक हो तो नमक पानी से गरारे करें।\n"
            "- संक्रमण फैलने से बचाने के लिए दूसरों से निकट संपर्क कम करें।\n\n"
            "यदि बुखार बना रहे या सांस लेने में दिक्कत हो तो डॉक्टर से संपर्क करें।"
        )
    },
    {
        "keys": ["cough", "khansi", "खांसी"],
        "en": (
            "Cough guidance:\n"
            "- Stay hydrated.\n"
            "- Avoid smoke, dust, and pollution.\n"
            "- Use warm saline gargles if throat irritation is present.\n\n"
            "Consult a doctor if cough persists, blood appears, or breathing difficulty develops."
        ),
        "hi": (
            "खांसी मार्गदर्शन:\n"
            "- पर्याप्त पानी पीएं।\n"
            "- धुएं, धूल और प्रदूषण से बचें।\n"
            "- गले में खराश हो तो नमक पानी से गरारे करें।\n\n"
            "यदि खांसी बनी रहे, खून आए या सांस लेने में दिक्कत हो तो डॉक्टर से संपर्क करें।"
        )
    },
    {
        "keys": ["headache", "migraine", "सिरदर्द"],
        "en": (
            "Headache guidance:\n"
            "- Rest in a quiet, dim room.\n"
            "- Stay hydrated.\n"
            "- Avoid screen strain and stress triggers.\n\n"
            "Seek urgent care if headache is sudden and severe, or associated with weakness, speech difficulty, vision changes, or vomiting."
        ),
        "hi": (
            "सिरदर्द मार्गदर्शन:\n"
            "- शांत और हल्की रोशनी वाले कमरे में आराम करें।\n"
            "- पर्याप्त पानी पीएं।\n"
            "- स्क्रीन और तनाव से बचें।\n\n"
            "यदि सिरदर्द अचानक और बहुत तेज़ हो, या कमजोरी, बोलने में दिक्कत, दृष्टि बदलाव या उल्टी के साथ हो तो तुरंत डॉक्टर से संपर्क करें।"
        )
    },
    {
        "keys": ["diarrhea", "loose motion", "vomiting", "food poisoning", "दस्त", "उल्टी"],
        "en": (
            "Diarrhea / vomiting guidance:\n"
            "- Take small frequent sips of fluids.\n"
            "- Use ORS if available.\n"
            "- Avoid heavy, oily, or spicy food initially.\n\n"
            "Seek medical care if there is blood in stool, severe pain, persistent vomiting, dizziness, or reduced urination."
        ),
        "hi": (
            "दस्त / उल्टी मार्गदर्शन:\n"
            "- थोड़ी-थोड़ी देर में तरल पदार्थ लें।\n"
            "- उपलब्ध हो तो ओआरएस लें।\n"
            "- शुरुआत में भारी, तैलीय या मसालेदार भोजन से बचें।\n\n"
            "यदि मल में खून, तेज़ पेट दर्द, लगातार उल्टी, चक्कर या पेशाब कम हो तो डॉक्टर से संपर्क करें।"
        )
    },
    {
        "keys": ["diabetes", "blood sugar", "sugar level", "डायबिटीज", "शुगर"],
        "en": (
            "General diabetes guidance:\n"
            "- Take medicines as prescribed.\n"
            "- Monitor blood sugar if advised.\n"
            "- Prefer balanced meals with controlled carbohydrates.\n"
            "- Stay hydrated and physically active if safe.\n"
            "- Avoid skipping meals or medicines without medical advice.\n\n"
            "Contact your doctor if sugar levels are repeatedly very high or very low."
        ),
        "hi": (
            "डायबिटीज़ सामान्य मार्गदर्शन:\n"
            "- दवाएं डॉक्टर की सलाह के अनुसार लें।\n"
            "- सलाह दी गई हो तो ब्लड शुगर मॉनिटर करें।\n"
            "- संतुलित भोजन और नियंत्रित कार्बोहाइड्रेट लें।\n"
            "- सुरक्षित हो तो पर्याप्त पानी पीएं और हल्की गतिविधि करें।\n"
            "- बिना सलाह भोजन या दवा न छोड़ें।\n\n"
            "यदि शुगर बार-बार बहुत अधिक या बहुत कम हो तो डॉक्टर से संपर्क करें।"
        )
    },
    {
        "keys": ["blood pressure", "bp", "hypertension", "ब्लड प्रेशर", "रक्तचाप"],
        "en": (
            "General blood pressure guidance:\n"
            "- Take prescribed medication regularly.\n"
            "- Reduce excess salt.\n"
            "- Stay physically active if advised.\n"
            "- Manage stress and sleep.\n"
            "- Avoid smoking and limit alcohol.\n\n"
            "Seek urgent care for chest pain, severe headache, breathlessness, or sudden weakness."
        ),
        "hi": (
            "ब्लड प्रेशर सामान्य मार्गदर्शन:\n"
            "- दी गई दवा नियमित रूप से लें।\n"
            "- अधिक नमक कम करें।\n"
            "- सलाह हो तो शारीरिक गतिविधि करें।\n"
            "- तनाव और नींद को नियंत्रित करें।\n"
            "- धूम्रपान से बचें और शराब सीमित करें।\n\n"
            "यदि सीने में दर्द, तेज़ सिरदर्द, सांस लेने में दिक्कत या अचानक कमजोरी हो तो तुरंत डॉक्टर से संपर्क करें।"
        )
    },
    {
        "keys": ["asthma", "wheezing", "breathlessness", "अस्थमा", "दमा"],
        "en": (
            "General asthma guidance:\n"
            "- Avoid dust, smoke, pollution, and known triggers.\n"
            "- Use prescribed reliever inhaler as directed.\n"
            "- Continue controller medicines if prescribed.\n"
            "- Monitor symptoms and peak flow if advised.\n\n"
            "Seek emergency care if breathing difficulty is severe or reliever inhaler is not helping."
        ),
        "hi": (
            "अस्थमा सामान्य मार्गदर्शन:\n"
            "- धूल, धुएं, प्रदूषण और ज्ञात ट्रिगर्स से बचें।\n"
            "- दिए गए राहत इनहेलर का उपयोग निर्देशानुसार करें।\n"
            "- यदि लिखी गई हो तो नियंत्रक दवाएं जारी रखें।\n"
            "- सलाह हो तो लक्षणों की निगरानी करें।\n\n"
            "यदि सांस लेने में तेज़ दिक्कत हो या राहत इनहेलर काम न करे तो तुरंत आपातकालीन सहायता लें।"
        )
    },
    {
        "keys": ["medicine", "medication", "tablet", "dose", "side effect", "दवा", "गोली"],
        "en": (
            "Medication safety guidance:\n"
            "- Take medicines exactly as prescribed.\n"
            "- Do not stop or change medicine without doctor advice.\n"
            "- Inform your doctor about allergies and other medications.\n"
            "- Avoid self-prescribing antibiotics or painkillers.\n"
            "- Store medicines properly and check expiry dates.\n\n"
            "For dose-related or side-effect concerns, contact your doctor or pharmacist."
        ),
        "hi": (
            "दवा सुरक्षा मार्गदर्शन:\n"
            "- दवाएं बिल्कुल बताए अनुसार लें।\n"
            "- बिना डॉक्टर की सलाह दवा बंद या बदलें नहीं।\n"
            "- अपनी एलर्जी और अन्य दवाओं के बारे में डॉक्टर को बताएं।\n"
            "- खुद से एंटीबायोटिक या पेनकिलर न लें।\n"
            "- दवाओं को सही तरीके से रखें और एक्सपायरी जांचें।\n\n"
            "यदि खुराक या साइड इफेक्ट की चिंता हो तो डॉक्टर या फार्मासिस्ट से संपर्क करें।"
        )
    }
]


def refresh_chunks():
    """
    Kept for compatibility with app.py.
    If you have knowledge files, they can be loaded here.
    """
    global CHUNKS
    CHUNKS = []

    if not os.path.exists(KNOWLEDGE_DIR):
        os.makedirs(KNOWLEDGE_DIR, exist_ok=True)

    for root, _, files in os.walk(KNOWLEDGE_DIR):
        for filename in files:
            path = os.path.join(root, filename)

            try:
                text = ""

                if filename.lower().endswith(".txt") or filename.lower().endswith(".md"):
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        text = f.read()

                elif filename.lower().endswith(".pdf"):
                    if PdfReader is not None:
                        reader = PdfReader(path)
                        text = "\n".join((page.extract_text() or "") for page in reader.pages)

                else:
                    continue

                if text.strip():
                    CHUNKS.append({
                        "text": text.strip(),
                        "source": filename
                    })

            except Exception as e:
                print(f"Could not read {path}: {e}")


def _tokens(text):
    return [
        token
        for token in re.findall(r"[a-z0-9]+", (text or "").lower())
        if token not in STOPWORDS and len(token) > 2
    ]


def _search_chunks(query, top_k=3):
    if not CHUNKS:
        return []

    query_tokens = set(_tokens(query))

    if not query_tokens:
        return []

    scored = []

    for chunk in CHUNKS:
        chunk_tokens = set(_tokens(chunk.get("text", "")))
        overlap = query_tokens.intersection(chunk_tokens)

        if not overlap:
            continue

        scored.append((len(overlap), chunk))

    scored.sort(key=lambda item: item[0], reverse=True)

    return [chunk for _, chunk in scored[:top_k]]


def answer(message, language="en"):
    message = (message or "").strip()
    low = message.lower()

    if language not in ("en", "hi"):
        language = "en"

    if not message:
        if language == "hi":
            return "कृपया कोई प्रश्न पूछें।"
        return "Please ask a question."

    # Emergency detection
    if any(key in low for key in EMERGENCY["keys"]):
        return EMERGENCY[language]

    # Topic-based structured answers
    for topic in TOPICS:
        if any(key in low for key in topic["keys"]):
            return topic.get(language, topic["en"])

    # Knowledge base fallback
    results = _search_chunks(message, top_k=3)

    if results:
        lines = []

        for result in results:
            snippet = result.get("text", "").strip()
            snippet = snippet[:500]
            lines.append(f"- {snippet}")

        if language == "hi":
            return (
                "ज्ञान-आधार से मिली जानकारी:\n"
                + "\n".join(lines)
                + "\n\nनोट: यह सामान्य जानकारी है। कृपया डॉक्टर से पुष्टि करें।"
            )

        return (
            "Knowledge base summary:\n"
            + "\n".join(lines)
            + "\n\nThis is general information. Please verify with a doctor."
        )

    # Fallback
    if language == "hi":
        return (
            "मैं इन विषयों में मदद कर सकता हूँ:\n"
            "- बुखार\n"
            "- सर्दी-जुकाम\n"
            "- खांसी\n"
            "- सिरदर्द\n"
            "- डायबिटीज़\n"
            "- ब्लड प्रेशर\n"
            "- अस्थमा\n"
            "- दवा सुरक्षा\n"
            "- खतरे के संकेत\n\n"
            "कृपया अपना प्रश्न थोड़ा और स्पष्ट करें।"
        )

    return (
        "I can help with:\n"
        "- Fever\n"
        "- Common cold\n"
        "- Cough\n"
        "- Headache\n"
        "- Diabetes\n"
        "- Blood pressure\n"
        "- Asthma\n"
        "- Medication safety\n"
        "- Warning signs\n\n"
        "Please rephrase your question."
    )