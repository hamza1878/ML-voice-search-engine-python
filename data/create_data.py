import random
import csv

cities = ["tunis", "sousse", "sfax", "nabeul", "monastir", "bizerte", "kairouan", "hammamet"]
places = ["gare", "maison", "bureau", "aéroport", "hotel", ""]
times = ["sbeh", "dhuhr", "asr", "maghreb", "leyl", "matin", "après-midi", "soir", "now", ""]
days = ["lyoum", "ghodwa", "el-lahad", "el-jemaa", "el-talata", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche", "apres-demain", "next tuesday", ""]

templates = [
    "nemchi {city} {day} {time}",
    "khodni men {place} lel {city} {day} {time}",
    "take me from {place} to {city} {day} {time}",
    "I need a taxi to {city} {day} {time}",
    "أريد الذهاب إلى {city} {day} {time}",
    "aller à {city} {day} {time}"
]

samples = []
for i in range(1300): 
    template = random.choice(templates)
    city = random.choice(cities)
    place = random.choice(places)
    time = random.choice(times)
    day = random.choice(days)
    
    sentence = template.format(city=city, place=place, time=time, day=day).strip()
    
    samples.append([sentence, city, place, day, time])

with open("generated_dataset.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["sentence","city","place","day","time"])
    writer.writerows(samples)

print("Dataset généré avec succès : generated_dataset.csv")