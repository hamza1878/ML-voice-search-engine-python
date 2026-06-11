"""
MOVIROO — config/templates.py

Templates de phrases pour l'augmentation de données.
Un template = (pattern, [(slot, LABEL), ...])

Stratégie de couverture :
  - Varier l'ORDER des slots (dest avant dep, dep avant dest, date en fin…)
  - Varier la DENSITÉ (1 slot, 2 slots, 3 slots, 4 slots)
  - Varier le REGISTRE (poli, familier, brusque, question, impératif)
  - Couvrir les SLOTS OPTIONNELS (sans date, sans heure, sans départ)
  - Couvrir les REFORMULATIONS (synonymes, ellipses, inversions)
"""

from typing import TypeAlias

# (pattern_str, [(slot_name, LABEL), ...])
Template: TypeAlias = tuple[str, list[tuple[str, str]]]

TEMPLATES: dict[str, list[Template]] = {

    # ═══════════════════════════════════════════════════════════
    # TUNISIEN (TN)
    # ═══════════════════════════════════════════════════════════
    "TN": [
        # ── 3 slots : dest + date + time ──────────────────────
        ("nheb nemchi {dest} {date} {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("bch nemchi {dest} {date} {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("khodni lel {dest} {date} {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("nemchi {dest} {date} fel {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("wein taxi lel {dest} {date} {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("3aybni taxi {dest} {date} {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("lazem nkoun fel {dest} {date} {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("roh {dest} {date} {time} 3andek",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("tnajem tjibli taxi lel {dest} {date} {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),

        # ── 4 slots : dep + dest + date + time ────────────────
        ("taxi men {dep} lel {dest} {date} {time}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("3aybni taxi men {dep} lel {dest} {date} {time}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("khodni men {dep} lel {dest} {date} {time}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("men {dep} lel {dest} {date} fel {time}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("fama taxi yekhdhem men {dep} lel {dest} {date} {time}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("chhal el taxi men {dep} lel {dest} {date} {time}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE"),("time","TIME")]),

        # ── current_location + dest + date + time ─────────────
        ("taxi men hne lel {dest} {date} {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("khodni men hne lel {dest} {date} {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("3aybli taxi men hne lel {dest} {date} fel {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("men makeni lel {dest} {date} {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("men wein ena lel {dest} {date} {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),

        # ── current_location + dest + date (sans heure) ───────
        ("taxi men hne lel {dest} {date}",
         [("dest","DESTINATION"),("date","DATE")]),
        ("khodni men hne lel {dest} {date}",
         [("dest","DESTINATION"),("date","DATE")]),
        ("men makeni lel {dest} {date}",
         [("dest","DESTINATION"),("date","DATE")]),

        # ── dep + dest + date (sans heure) ────────────────────
        ("nemchi {dest} min {dep} {date}",
         [("dest","DESTINATION"),("dep","DEPARTURE"),("date","DATE")]),
        ("taxi men {dep} lel {dest} {date}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE")]),
        ("khodni men {dep} lel {dest} {date}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE")]),
        ("men {dep} lel {dest} {date}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE")]),
        ("3aybni taxi men {dep} lel {dest} {date}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE")]),
        ("chkoun ynajem yakhdheni men {dep} lel {dest} {date}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE")]),

        # ── dest + date (sans heure ni départ) ────────────────
        ("nheb nemchi {dest} {date}",
         [("dest","DESTINATION"),("date","DATE")]),
        ("taxi lel {dest} {date}",
         [("dest","DESTINATION"),("date","DATE")]),
        ("khodni {dest} {date}",
         [("dest","DESTINATION"),("date","DATE")]),
        ("lazem nemchi {dest} {date}",
         [("dest","DESTINATION"),("date","DATE")]),
        ("fama taxi lel {dest} {date}",
         [("dest","DESTINATION"),("date","DATE")]),
        ("fama taxi yemchi lel {dest} {date}",
         [("dest","DESTINATION"),("date","DATE")]),

        # ── dest + time (sans date) ────────────────────────────
        ("taxi lel {dest} {time}",
         [("dest","DESTINATION"),("time","TIME")]),
        ("khodni {dest} fel {time}",
         [("dest","DESTINATION"),("time","TIME")]),
        ("nemchi {dest} {time}",
         [("dest","DESTINATION"),("time","TIME")]),

        # ── dest seule ─────────────────────────────────────────
        ("taxi lel {dest}",
         [("dest","DESTINATION")]),
        ("khodni lel {dest}",
         [("dest","DESTINATION")]),
        ("wein taxi lel {dest}",
         [("dest","DESTINATION")]),
        ("nemchi {dest} tawwa",
         [("dest","DESTINATION")]),

        # ── date + time seuls (sans dest connue) ───────────────
        ("wein taxi {date} {time}",
         [("date","DATE"),("time","TIME")]),
        ("3aybni taxi {date} fel {time}",
         [("date","DATE"),("time","TIME")]),

        # ── ellipse brusque ────────────────────────────────────
        ("{dest} {date} {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("{dep} lel {dest} {date}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE")]),
        ("{dest} tawwa",
         [("dest","DESTINATION")]),
        ("{dest} {date}",
         [("dest","DESTINATION"),("date","DATE")]),
    ],

    # ═══════════════════════════════════════════════════════════
    # FRANÇAIS (FR)
    # ═══════════════════════════════════════════════════════════
    "FR": [
        # ── 3 slots : dest + date + time ──────────────────────
        ("je veux aller a {dest} {date} {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("taxi vers {dest} {date} a {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("je dois arriver a {dest} {date} a {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("reserver un taxi {date} {time} pour {dest}",
         [("date","DATE"),("time","TIME"),("dest","DESTINATION")]),
        ("emmene moi a {dest} {date} a {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("il me faut un taxi pour {dest} {date} a {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("je dois etre a {dest} {date} avant {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("pouvez vous m amener a {dest} {date} a {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("un taxi pour {dest} {date} a {time} s il vous plait",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("j ai besoin d un taxi pour {dest} {date} a {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("commande un taxi direction {dest} {date} {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("je dois rejoindre {dest} {date} pour {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),

        # ── 4 slots : dep + dest + date + time ────────────────
        ("taxi de {dep} vers {dest} {date} a {time}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("je pars de {dep} vers {dest} {date} a {time}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("conduire de {dep} a {dest} {date} {time}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("de {dep} jusqu a {dest} {date} a {time}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("prise en charge a {dep} direction {dest} {date} a {time}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("depart de {dep} arrivee {dest} {date} {time}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("je veux un taxi de {dep} pour {dest} {date} a {time}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("pouvez vous me prendre a {dep} pour aller a {dest} {date} {time}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE"),("time","TIME")]),

        # ── current_location + dest + date + time ─────────────
        ("taxi de ma position vers {dest} {date} a {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("prenez moi ici pour {dest} {date} a {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("depuis ou je suis vers {dest} {date} a {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("taxi depuis ma localisation vers {dest} {date} a {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("je veux partir d ici vers {dest} {date} a {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),

        # ── current_location + dest + date (sans heure) ───────
        ("taxi de ma position vers {dest} {date}",
         [("dest","DESTINATION"),("date","DATE")]),
        ("depuis ici jusqu a {dest} {date}",
         [("dest","DESTINATION"),("date","DATE")]),
        ("je pars d ici pour {dest} {date}",
         [("dest","DESTINATION"),("date","DATE")]),

        # ── dep + dest + date (sans heure) ────────────────────
        ("taxi depuis {dep} jusqu a {dest} {date}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE")]),
        ("taxi de {dep} a {dest} {date}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE")]),
        ("besoin d un taxi de {dep} pour {dest} {date}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE")]),
        ("je pars de {dep} pour {dest} {date}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE")]),
        ("trajet {dep} {dest} {date}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE")]),
        ("un taxi de {dep} vers {dest} pour {date}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE")]),

        # ── dest + date (sans heure ni départ) ────────────────
        ("aller a {dest} {date}",
         [("dest","DESTINATION"),("date","DATE")]),
        ("taxi pour {dest} {date}",
         [("dest","DESTINATION"),("date","DATE")]),
        ("j ai besoin d aller a {dest} {date}",
         [("dest","DESTINATION"),("date","DATE")]),
        ("je vais a {dest} {date}",
         [("dest","DESTINATION"),("date","DATE")]),
        ("direction {dest} {date}",
         [("dest","DESTINATION"),("date","DATE")]),
        ("rendez vous a {dest} {date}",
         [("dest","DESTINATION"),("date","DATE")]),

        # ── dest + time (sans date) ────────────────────────────
        ("taxi vers {dest} a {time}",
         [("dest","DESTINATION"),("time","TIME")]),
        ("emmene moi a {dest} a {time}",
         [("dest","DESTINATION"),("time","TIME")]),
        ("je dois etre a {dest} pour {time}",
         [("dest","DESTINATION"),("time","TIME")]),

        # ── dest seule ─────────────────────────────────────────
        ("taxi pour {dest}",
         [("dest","DESTINATION")]),
        ("je veux aller a {dest}",
         [("dest","DESTINATION")]),
        ("direction {dest}",
         [("dest","DESTINATION")]),
        ("emmene moi a {dest}",
         [("dest","DESTINATION")]),

        # ── registre question ──────────────────────────────────
        ("est ce qu il y a un taxi pour {dest} {date} a {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("vous pouvez me conduire de {dep} a {dest} {date}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE")]),
        ("combien pour aller de {dep} a {dest} {date} {time}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE"),("time","TIME")]),

        # ── ellipse ────────────────────────────────────────────
        ("{dest} {date} {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("{dep} {dest} {date}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE")]),
        ("{dest} {date}",
         [("dest","DESTINATION"),("date","DATE")]),
    ],

    # ═══════════════════════════════════════════════════════════
    # ANGLAIS (EN)
    # ═══════════════════════════════════════════════════════════
    "EN": [
        # ── 3 slots : dest + date + time ──────────────────────
        ("take me to {dest} {date} at {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("book a ride to {dest} {date} at {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("I want to go to {dest} {date} at {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("get me a taxi to {dest} {date} at {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("please take me to {dest} this {date} at {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("I need to be at {dest} on {date} at {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("can you get me to {dest} by {time} on {date}",
         [("dest","DESTINATION"),("time","TIME"),("date","DATE")]),
        ("schedule a taxi to {dest} for {date} at {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("I have to reach {dest} {date} before {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("a cab to {dest} {date} at {time} please",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("heading to {dest} {date} at {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("I need a ride to {dest} on {date} at {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),

        # ── 4 slots : dep + dest + date + time ────────────────
        ("ride from {dep} to {dest} {date} at {time}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("I need a ride from {dep} to {dest} {date} at {time}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("pick me up at {dep} and take me to {dest} {date} at {time}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("from {dep} to {dest} on {date} at {time}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("taxi pickup from {dep} drop off at {dest} {date} {time}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("I need a cab leaving {dep} going to {dest} {date} at {time}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("can you drive me from {dep} to {dest} on {date} at {time}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE"),("time","TIME")]),

        # ── current_location + dest + date + time ─────────────
        ("taxi from here to {dest} {date} at {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("pick me up from my location to {dest} {date} at {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("from my current location to {dest} {date} at {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("from where I am to {dest} {date} at {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("ride from my position to {dest} {date} at {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),

        # ── current_location + dest + date (sans heure) ───────
        ("taxi from here to {dest} {date}",
         [("dest","DESTINATION"),("date","DATE")]),
        ("from my location to {dest} {date}",
         [("dest","DESTINATION"),("date","DATE")]),
        ("pick me up here for {dest} {date}",
         [("dest","DESTINATION"),("date","DATE")]),

        # ── dep + dest + date (sans heure) ────────────────────
        ("take me from {dep} to {dest} {date}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE")]),
        ("I need a cab from {dep} to {dest} {date}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE")]),
        ("drop me at {dest} from {dep} {date}",
         [("dest","DESTINATION"),("dep","DEPARTURE"),("date","DATE")]),
        ("can you drive me from {dep} to {dest} {date}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE")]),
        ("from {dep} to {dest} {date}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE")]),
        ("taxi {dep} to {dest} {date}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE")]),
        ("trip from {dep} to {dest} on {date}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE")]),

        # ── dest + date (sans heure ni départ) ────────────────
        ("I need a taxi to {dest} {date}",
         [("dest","DESTINATION"),("date","DATE")]),
        ("going to {dest} on {date}",
         [("dest","DESTINATION"),("date","DATE")]),
        ("taxi to {dest} {date}",
         [("dest","DESTINATION"),("date","DATE")]),
        ("I want to go to {dest} {date}",
         [("dest","DESTINATION"),("date","DATE")]),
        ("book a taxi to {dest} for {date}",
         [("dest","DESTINATION"),("date","DATE")]),
        ("need to get to {dest} by {date}",
         [("dest","DESTINATION"),("date","DATE")]),

        # ── dest + time (sans date) ────────────────────────────
        ("take me to {dest} at {time}",
         [("dest","DESTINATION"),("time","TIME")]),
        ("I need a taxi to {dest} at {time}",
         [("dest","DESTINATION"),("time","TIME")]),
        ("drop me at {dest} at {time}",
         [("dest","DESTINATION"),("time","TIME")]),

        # ── dest seule ─────────────────────────────────────────
        ("taxi to {dest}",
         [("dest","DESTINATION")]),
        ("I need a ride to {dest}",
         [("dest","DESTINATION")]),
        ("take me to {dest}",
         [("dest","DESTINATION")]),
        ("going to {dest}",
         [("dest","DESTINATION")]),

        # ── registre question ──────────────────────────────────
        ("is there a taxi to {dest} on {date} at {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("how much from {dep} to {dest} {date}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE")]),
        ("can I get a cab from {dep} to {dest} {date}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE")]),

        # ── ellipse ────────────────────────────────────────────
        ("{dest} {date} {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("{dep} to {dest} {date}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE")]),
        ("{dest} {date}",
         [("dest","DESTINATION"),("date","DATE")]),
    ],

    # ═══════════════════════════════════════════════════════════
    # ARABE (AR)
    # ═══════════════════════════════════════════════════════════
    "AR": [
        # ── 3 slots : dest + date + time ──────────────────────
        ("أريد تاكسي إلى {dest} {date} في {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("خذني إلى {dest} {date} في {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("أريد الذهاب إلى {dest} {date} {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("تاكسي إلى {dest} {date} في {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("أحتاج تاكسي نحو {dest} {date} الساعة {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("أريد الوصول إلى {dest} {date} قبل {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("احجز لي تاكسي إلى {dest} يوم {date} في {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("هل يمكنني الذهاب إلى {dest} {date} في {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("أنا في حاجة إلى تاكسي باتجاه {dest} {date} {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),

        # ── 4 slots : dep + dest + date + time ────────────────
        ("من {dep} إلى {dest} {date} {time}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("احتاج تاكسي من {dep} إلى {dest} {date} في {time}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("خذني من {dep} إلى {dest} {date} الساعة {time}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("أريد تاكسي ينطلق من {dep} باتجاه {dest} {date} {time}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("انطلاق من {dep} وصول {dest} {date} في {time}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("هل يوجد تاكسي من {dep} إلى {dest} {date} {time}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE"),("time","TIME")]),

        # ── current_location + dest + date + time ─────────────
        ("تاكسي من هنا إلى {dest} {date} في {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("خذني من موقعي إلى {dest} {date} الساعة {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("من مكاني إلى {dest} {date} في {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("أحتاج تاكسي من هنا إلى {dest} {date} {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("انطلق من موقعي الحالي نحو {dest} {date} في {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),

        # ── current_location + dest + date (sans heure) ───────
        ("تاكسي من هنا إلى {dest} {date}",
         [("dest","DESTINATION"),("date","DATE")]),
        ("من موقعي إلى {dest} {date}",
         [("dest","DESTINATION"),("date","DATE")]),
        ("خذني من هنا إلى {dest} {date}",
         [("dest","DESTINATION"),("date","DATE")]),

        # ── dep + dest + date (sans heure) ────────────────────
        ("احتاج تاكسي من {dep} إلى {dest} {date}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE")]),
        ("من {dep} إلى {dest} {date}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE")]),
        ("تاكسي من {dep} إلى {dest} يوم {date}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE")]),
        ("أريد الانتقال من {dep} إلى {dest} {date}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE")]),
        ("رحلة من {dep} إلى {dest} {date}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE")]),

        # ── dest + date (sans heure ni départ) ────────────────
        ("أريد تاكسي إلى {dest} {date}",
         [("dest","DESTINATION"),("date","DATE")]),
        ("تاكسي إلى {dest} {date}",
         [("dest","DESTINATION"),("date","DATE")]),
        ("أنا ذاهب إلى {dest} {date}",
         [("dest","DESTINATION"),("date","DATE")]),
        ("أحتاج أن أصل إلى {dest} {date}",
         [("dest","DESTINATION"),("date","DATE")]),
        ("موعد في {dest} {date}",
         [("dest","DESTINATION"),("date","DATE")]),

        # ── dest + time (sans date) ────────────────────────────
        ("تاكسي إلى {dest} في {time}",
         [("dest","DESTINATION"),("time","TIME")]),
        ("خذني إلى {dest} الساعة {time}",
         [("dest","DESTINATION"),("time","TIME")]),
        ("أحتاج تاكسي إلى {dest} قبل {time}",
         [("dest","DESTINATION"),("time","TIME")]),

        # ── dest seule ─────────────────────────────────────────
        ("تاكسي إلى {dest}",
         [("dest","DESTINATION")]),
        ("أريد الذهاب إلى {dest}",
         [("dest","DESTINATION")]),
        ("خذني إلى {dest}",
         [("dest","DESTINATION")]),

        # ── ellipse ────────────────────────────────────────────
        ("{dest} {date} {time}",
         [("dest","DESTINATION"),("date","DATE"),("time","TIME")]),
        ("{dep} {dest} {date}",
         [("dep","DEPARTURE"),("dest","DESTINATION"),("date","DATE")]),
        ("{dest} {date}",
         [("dest","DESTINATION"),("date","DATE")]),
    ],
}