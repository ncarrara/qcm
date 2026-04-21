from pyexpat.errors import messages

from anthropic import Anthropic
from bs4 import BeautifulSoup
import anthropic

if __name__ == '__main__':

    with open("main.html", "r", encoding="utf-8") as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, "lxml")

    form = soup.find("form")

    qas = form.find_all("div", class_="content")

    strs = []

    for i, qa in enumerate(qas):

        is_multichoice = qa.find("div", class_="content")
        question = qa.find("div", class_="qtext")
        question = question.find("p").get_text()
        question = " ".join(question.split())
        has_check_boxes = False
        if qa.find_all("input", attrs={"type": "checkbox"}):
            has_check_boxes = True

        checkbox_str = 'plusieurs réponses possible' if has_check_boxes else 'une seule réponse possible'
        strs.append(f"{i + 1}) [{checkbox_str}] {question}")

        answers = qa.find_all("div", attrs={"data-region": "answer-label"})
        labels = qa.find_all("span", class_="answernumber")
        for label, answer in zip(labels, answers):
            answer = answer.find("p").get_text()
            answer = " ".join(answer.split())
            label = label.get_text()
            label = " ".join(label.split())
            strs.append(f"{label} {answer}")

    qcm = "\n".join(strs)

    qcm = """
    1) [une seule réponse possible] Une infraction punie d'une peine contraventionnelle est:
    a. une infraction politique
    b. un délit
    c. un crime
    d. une contravention
    2) [une seule réponse possible] Le délai de prescription de l’action publique pour un délit est de?
    a. 1 an
    b. 3 ans
    c. 6 ans
    d. 20 ans
    3) [une seule réponse possible] Pour une infraction continue, le point de départ du délai de prescription est
    a. Le jour où l’acte a été commis
    b. Le jour où cesse l’activité délictuelle
    c. Le jour de la découverte de l’infraction
    d. Le jour du jugement
        """

    prompt = ("Tu es un avocat en droit pénal. "
              "Tu dois répondre à ce QCM en ajoutant une petite explication. "
              "Retourne un format html sans javascript, et met les réponses en gras et vert. "
              "Les mauvaises réponses en rouge:")

    client = Anthropic(
        api_key=key,  # This is the default and can be omitted
    )

    message = prompt + "\n\n" + qcm

    print(message)

    message = client.messages.create(
        max_tokens=1024*10,
        messages=[
            {
                "role": "user",
                "content": message,
            }
        ],
        # thinking={"type": "adaptive"},
        # output_config={"effort": "high"},
        model="claude-opus-4-7",
    )

    with open("answers.html", "w", encoding="utf-8") as file:
        file.write(message.content[0].text.replace("```html", "").replace("```", ""))

    with open("answers.html", "r", encoding="utf-8") as file:
        print(file.read())
