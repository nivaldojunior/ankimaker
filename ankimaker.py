#!/usr/bin/env python3

import csv
import random
import genanki
import json
import requests

# Filename of the data file
data_filename = "Word List.txt"

# Filename of the Anki deck to generate
deck_filename = "Words in English to Learn.apkg"

# Title of the deck as shown in Anki
anki_deck_title = "Words in English to Learn"

# Name of the card model
anki_model_name = "Spelling or Pronunciation"

# Create the deck model

model_id = random.randrange(1 << 30, 1 << 31)

style = """
.card {
 font-family: "Arial Unicode MS", Arial;
 font-size: 20px;
 text-align: center;
 color: black;
 background-color: white;
}

.nounderline u {
text-decoration: none
}
"""

anki_model = genanki.Model(
    model_id,
    anki_model_name,
    fields=[{"name": "Word"}, {"name": "Meaning"}, {"name": "Recording"}, {"name": "IPA"}, {"name": "Example"}],
    templates=[
        {
            "name": "What's the spelling?",
            "qfmt": """
                    How do you spell this word?
                    <br>
                    {{#Recording}}{{Recording}}
                    {{/Recording}}<br>
                    <br>

                    {{type:Word}}
                    """,
            "afmt": """
                    {{FrontSide}}<br>

                    <hr id=answer>
                    <div class="nounderline" style='font-family: Arial; font-size: 30px'>"{{Word}}"</b></div>

                    <div style='font-family: Arial; font-size: 20px;color:blue'>[{{IPA}}]</div>
                    <br>
                    <div style='font-family: Arial; font-size: 15px;'><em>Meaning: <strong>{{Meaning}}</strong></div>
                    <br><br><div style='font-family: Arial; font-size: 15px;'><em>Example: <strong>"{{Example}}"</strong></div>
                    """,
        },
        {
            "name": "What's the pronunciation",
            "qfmt": """
                    How do you pronounce this word?<br><br>
                    <div style='font-family: Arial; font-size: 40px;'>{{Word}}</div>
                    """,
            "afmt": """
                    {{FrontSide}}
                    <hr id=answer>
                    <br>
                    <div style='font-family: Arial; font-size: 30px; color: blue;'>[{{IPA}}]</div>
                    <br><br>
                    {{Recording}}<br>
                    """,
        },
    ],
    css=style,
)

# The list of flashcards
anki_notes = []

# The list of medias
media_files = []

with open(data_filename, encoding ="utf8") as csv_file:

    csv_reader = csv.reader(csv_file, delimiter="\n")

    for row in csv_reader:
        response = requests.get("https://api.dictionaryapi.dev/api/v2/entries/en/" + row[0])
        json = response.json()
        print(json)
        url = json[0]["phonetics"][0]["audio"]
        audio = requests.get(url)
        audio_name = url.rsplit('/', 1)[1]

        with open(audio_name, 'wb') as f:
            f.write(audio.content)

        media_files.append(audio_name)

        anki_note = genanki.Note(
            model=anki_model,
            #{"name": "Word"}, {"name": "Meaning"}, {"name": "Recording"}, {"name": "IPA"}, {"name": "Example"}
            fields=[json[0]["word"],
                    json[0]["meanings"][0]["definitions"][0]["definition"],
                    '[sound:' + audio_name + ']',
                    json[0]["phonetics"][0]["text"],
                    json[0]["meanings"][0]["definitions"][0]["example"]
                    ],
        )
        anki_notes.append(anki_note)

# Shuffle flashcards
random.shuffle(anki_notes)

anki_deck = genanki.Deck(model_id, anki_deck_title)
anki_package = genanki.Package(anki_deck)

# Add media files
anki_package.media_files = media_files

# Add flashcards to the deck
for anki_note in anki_notes:
    anki_deck.add_note(anki_note)

# Save the deck to a file
anki_package.write_to_file(deck_filename)

print("Created deck with {} flashcards".format(len(anki_deck.notes)))