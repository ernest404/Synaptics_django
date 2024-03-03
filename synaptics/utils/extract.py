import fitz
from ..utils.keywords_extraction import extract_keywords

triggerwords = ["Kenya Defence Forces", "KDF", "Military", "Army", "Airforce", "Navy", "National Security", "Security", "Terrorism", "Terror","Terrorist",
                "AlShabaab","Al-Shabaab","Al Shabaab","Al-Shabab", "bandits", "gunshot", "gun", "firearm", "bomb", "bombing", "bombed", "Taliban","Department of Defence", 
                "militia", "threat", "Al Qaeda", "weapons", "bomber", "extremist", "extremism", "pirates"]

def article_extractor(pdf_file):
    
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")

    def createList(r2):
        return [i for i in range(1, r2)]

    s = createList(doc.page_count)

    text_by_page = [(doc.load_page(i)).get_text("text") for i in s]


    x = [i for i in range(0, doc.page_count-1)]
   
   
    filtered_articles = []
    for i in x:
        text_by_page[i] = text_by_page[i].replace('\n', '')
        text_by_page[i] = text_by_page[i].replace('-', '')
        text_by_page[i] = text_by_page[i].replace('�', '')
        text_by_page[i] = text_by_page[i].replace('  ', '\n')
        text_by_page[i] = text_by_page[i].split('@PeopleDailyKe')

        for j in text_by_page[i]:
            keyword = extract_keywords(j)
            for triggerword in triggerwords:
                if triggerword.lower() in [x.lower() for x in keyword]:
                    filtered_articles.append(j)
    return filtered_articles