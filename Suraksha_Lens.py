import streamlit as st

st.set_page_config(page_title="Suraksha Lens", layout="wide")

# ---------------- Language Selection ----------------
language = st.sidebar.selectbox("Select Language", ["English", "Hindi"])

# ---------------- Content ----------------
if language == "English":

    st.title("Suraksha Lens")
    st.subheader("People. Protection. Platform.")

    st.write("""
    Suraksha Lens is an early warning platform that helps spot and prevent climate linked exploitation.

    When floods, droughts, heatwaves, or glacial floods hit, the danger doesn’t end when the waters go down.
    Families lose homes, jobs, and savings. People are forced to migrate. In this period of uncertainty,
    risks of human trafficking, labour exploitation, and gender-based violence often rise.
    """)

    st.write("""
    Suraksha Lens is developed by the South Asian Institute of Crime and Justice Studies to address this gap.
    Climate response systems often focus on rebuilding roads and homes. Protection risks — especially for
    women, children, and marginalised communities — are harder to see and are often missed.

    We connect these dots.
    """)

    st.header("What Powers Suraksha Lens")
    st.subheader("The Climate Exploitation Risk Index (CERI)")

    st.write("CERI combines three simple but powerful elements:")

    st.markdown("""
    **1. Climate hazards**
    - Floods, droughts, heatwaves, glacial lake outburst floods, and other shocks.

    **2. Impact pathways**
    - Displacement, job loss, distress migration, informal work.

    **3. Social vulnerabilities**
    - Gender, caste, lack of documentation, informal labour, unsafe digital recruitment.
    """)

    st.write("""
    By bringing these factors together, Suraksha Lens creates:
    - Location-based risk profiles  
    - Early warning signals  
    - Clear, visual dashboards for decision-makers  

    The goal is simple: make complex risks visible and usable.
    """)

    st.header("From Data to Action")

    st.write("""
    Suraksha Lens combines climate data, migration patterns, trafficking alerts, and local knowledge.

    This helps governments, CSOs, and communities:
    - Plan safer recovery efforts  
    - Monitor emerging risks  
    - Take preventive action before exploitation happens  

    The platform is built with:
    - Local language access  
    - Strong privacy protections  
    - Ethical data use  
    - Community validation of risk alerts  

    Most importantly, Suraksha Lens is designed so insights do not stay in reports —
    they support real decisions on the ground, where protection matters most.
    """)

# ---------------- Hindi Content ----------------
elif language == "Hindi":

    st.title("सुरक्षा लेंस")
    st.subheader("लोग। संरक्षण। मंच।")

    st.write("""
    सुरक्षा लेंस एक प्रारंभिक चेतावनी मंच है, जो जलवायु परिवर्तन से जुड़े शोषण के जोखिमों की पहचान करने और उन्हें रोकने में सहायता करता है।

    जब बाढ़, सूखा, लू अथवा हिमनदीय झील विस्फोट बाढ़ जैसी आपदाएँ आती हैं, तो संकट केवल जल के घट जाने के साथ समाप्त नहीं होता।
    परिवार अपने घर, आजीविका और बचत खो देते हैं। अनेक लोग मजबूरी में पलायन करते हैं।
    इस अनिश्चितता के दौर में मानव तस्करी, श्रम शोषण तथा लैंगिक आधारित हिंसा के जोखिम प्रायः बढ़ जाते हैं।
    """)

    st.write("""
    सुरक्षा लेंस का विकास दक्षिण एशियाई अपराध एवं न्याय अध्ययन संस्थान द्वारा इस कमी को दूर करने के उद्देश्य से किया गया है।
    प्रायः जलवायु प्रतिक्रिया प्रणालियाँ सड़कों और आवासों के पुनर्निर्माण पर केंद्रित रहती हैं।
    किंतु संरक्षण से जुड़े जोखिम — विशेषकर महिलाओं, बच्चों और हाशिए पर स्थित समुदायों के लिए —
    स्पष्ट रूप से दिखाई नहीं देते और अक्सर उपेक्षित रह जाते हैं।

    हम इन्हीं बिखरे हुए तथ्यों को एक साथ जोड़ते हैं।
    """)

    st.header("सुरक्षा लेंस की आधारशिला")
    st.subheader("जलवायु-जनित शोषण जोखिम सूचकांक")

    st.markdown("""
    **1. जलवायु जोखिम**
    - बाढ़, सूखा, लू, हिमनदीय झील विस्फोट बाढ़ तथा अन्य आकस्मिक आपदाएँ।

    **2. प्रभाव मार्ग**
    - विस्थापन, रोजगार की हानि, संकटजन्य पलायन तथा असंगठित श्रम।

    **3. सामाजिक संवेदनशीलताएँ**
    - लिंग, जाति, पहचान-पत्रों का अभाव, असंगठित श्रम व्यवस्था तथा असुरक्षित डिजिटल भर्ती।
    """)

    st.write("""
    इन सभी घटकों को एकीकृत कर सुरक्षा लेंस प्रदान करता है:
    - स्थान-आधारित जोखिम प्रोफ़ाइल  
    - प्रारंभिक चेतावनी संकेत  
    - निर्णयकर्ताओं हेतु स्पष्ट एवं दृश्य डैशबोर्ड  

    हमारा उद्देश्य सरल है — जटिल जोखिमों को स्पष्ट, समझने योग्य और उपयोगी बनाना।
    """)

    st.header("आँकड़ों से कार्रवाई तक")

    st.write("""
    सुरक्षा लेंस जलवायु संबंधी आँकड़ों, प्रवासन प्रवृत्तियों, तस्करी चेतावनियों तथा स्थानीय ज्ञान को एकीकृत करता है।

    यह सरकारों, नागरिक समाज संगठनों तथा समुदायों को सक्षम बनाता है कि वे:
    - सुरक्षित पुनर्वास एवं पुनर्निर्माण की योजना तैयार करें  
    - उभरते जोखिमों की सतत निगरानी करें  
    - शोषण घटित होने से पूर्व ही निवारक कदम उठाएँ  

    यह मंच निम्न सिद्धांतों पर आधारित है:
    - स्थानीय भाषाओं में सुलभता  
    - सुदृढ़ गोपनीयता संरक्षण  
    - नैतिक एवं उत्तरदायी आँकड़ा उपयोग  
    - जोखिम चेतावनियों का सामुदायिक सत्यापन  

    सबसे महत्वपूर्ण बात यह है कि इसकी अंतर्दृष्टियाँ केवल प्रतिवेदनों तक सीमित न रहें,
    बल्कि जमीनी स्तर पर वास्तविक निर्णयों का मार्गदर्शन करें — जहाँ संरक्षण सबसे अधिक आवश्यक है।
    """)
