import datetime
from datetime import timedelta
import random

from django.contrib.auth.models import User

from django.core.management.base import BaseCommand

from rehab.models import Patient, Rehabilitator

female_names = ['Anna', 'Maria', 'Katarzyna', 'Małgorzata', 'Agnieszka', 'Krystyna', 'Barbara', 'Ewa', 'Elżbieta',
                'Zofia', 'Janina', 'Teresa', 'Joanna', 'Magdalena', 'Monika', 'Jadwiga', 'Danuta', 'Irena', 'Halina',
                'Helena', 'Beata', 'Aleksandra', 'Marta', 'Dorota', 'Marianna', 'Grażyna', 'Jolanta', 'Stanisława',
                'Iwona', 'Karolina', 'Bożena', 'Urszula', 'Justyna', 'Renata', 'Alicja', 'Paulina', 'Sylwia',
                'Natalia', 'Wanda', 'Agata', 'Aneta', 'Izabela', 'Ewelina', 'Marzena', 'Wiesława', 'Genowefa',
                'Patrycja', 'Kazimiera', 'Edyta', 'Stefania']

male_names = ['Jan', 'Andrzej', 'Piotr', 'Krzysztof', 'Stanisław', 'Tomasz', 'Paweł', 'Józef', 'Marcin', 'Marek',
              'Michał', 'Grzegorz', 'Jerzy', 'Tadeusz', 'Adam', 'Łukasz', 'Zbigniew', 'Ryszard', 'Dariusz', 'Henryk',
              'Mariusz', 'Kazimierz', 'Wojciech', 'Robert', 'Mateusz', 'Marian', 'Rafał', 'Jacek', 'Janusz',
              'Mirosław', 'Maciej', 'Sławomir', 'Jarosław', 'Kamil', 'Wiesław', 'Roman', 'Władysław', 'Jakub',
              'Artur', 'Zdzisław', 'Edward', 'Mieczysław', 'Damian', 'Dawid', 'Przemysław', 'Sebastian', 'Czesław',
              'Leszek', 'Daniel', 'Waldemar']

surnames = ['Nowak', 'Kowalski', 'Wiśniewski', 'Dąbrowski', 'Lewandowski', 'Wójcik', 'Kamiński', 'Kowalczyk',
            'Zieliński', 'Szymański', 'Woźniak', 'Kozłowski', 'Jankowski', 'Wojciechowski', 'Kwiatkowski', 'Kaczmarek',
            'Mazur', 'Krawczyk', 'Piotrowski', 'Grabowski', 'Nowakowski', 'Pawłowski', 'Michalski', 'Nowicki',
            'Adamczyk', 'Dudek', 'Zając', 'Wieczorek', 'Jabłoński', 'Król', 'Majewski', 'Olszewski', 'Jaworski',
            'Wróbel', 'Malinowski', 'Pawlak', 'Witkowski', 'Walczak', 'Stępień', 'Górski', 'Rutkowski', 'Michalak',
            'Sikora', 'Ostrowski', 'Baran', 'Duda', 'Szewczyk', 'Tomaszewski', 'Pietrzak', 'Marciniak', 'Wróblewski',
            'Zalewski', 'Jakubowski', 'Jasiński', 'Zawadzki', 'Sadowski', 'Bąk', 'Chmielewski', 'Włodarczyk',
            'Borkowski', 'Czarnecki', 'Sawicki', 'Sokołowski', 'Urbański', 'Kubiak', 'Maciejewski', 'Szczepański',
            'Kucharski', 'Wilk', 'Kalinowski', 'Lis', 'Mazurek', 'Wysocki', 'Adamski', 'Kaźmierczak', 'Wasilewski',
            'Sobczak', 'Czerwiński', 'Andrzejewski', 'Cieślak', 'Głowacki', 'Zakrzewski', 'Kołodziej', 'Sikorski',
            'Krajewski', 'Gajewski', 'Szymczak', 'Szulc', 'Baranowski', 'Laskowski', 'Brzeziński', 'Makowski',
            'Ziółkowski', 'Przybylski']

expertises = ['Ortopeda', 'Fizjoterapeuta']

locations = ['Warszawa', 'Kraków', 'Wrocław', 'Łódź', 'Poznań', 'Gdańsk', 'Szczecin', 'Bydgoszcz', 'Lublin',
             'Białystok', 'Katowice', 'Gdynia', 'Częstochowa', 'Radom', 'Rzeszów', 'Toruń', 'Sosnowiec', 'Kielce',
             'Gliwice', 'Olsztyn', 'Zabrze', 'Bielsk-Biała', 'Bytom', 'Zielona Góra', 'Rybnik', 'Ruda Śląska', 'Opole',
             'Tychy', 'Gorzów Wielkopolski', 'Elbląg', 'Płock', 'Dąbrowa Górnicza', 'Wałbrzych', 'Włocławek', 'Tarnów',
             'Chorzów', 'Koszalin', 'Kalisz', 'Legnica', 'Grudziądz', 'Jaworzno', 'Słupsk', 'Jastrzębie-Zdrój',
             'Nowy Sącz', 'Jelenia Góra', 'Siedlce', 'Mysłowice', 'Konin', 'Piła', ' Piotrków Trybunalski',
             'Lubin', 'Ostrów Wielkopolski', 'Suwałki', 'Stargard', 'Gniezno', 'Ostrowiec Świętokrzyski',
             'Siemianowice Śląskie', 'Głogów', 'Pabianice', 'Leszno', 'Żory', 'Zamość', 'Pruszków', 'Łomża', 'Ełk',
             'Tomaszów Mazowiecki', 'Chełm', 'Mielec', 'Kędzierzyn-Koźle', 'Przemyśl', 'Stalowa Wola', 'Tczew',
             'Biała Podlaska', 'Bełchatów', 'Świdnica', 'Będzin', 'Zgierz', 'Piekary Śląskie', 'Racibórz', 'Legionowo',
             'Ostrołęka', 'Świętochłowice', 'Wejherowo', 'Zawiercie', 'Skierniewice', 'Starachowice',
             'Wodzisław Śląski', 'Starogard Gdański', 'Puławy', 'Tarnobrzeg', 'Kołobrzeg', 'Krosno', 'Radomsko',
             'Otwock', 'Skarżysko-Kamienna', 'Ciechanów', 'Kutno', 'Sieradz', 'Zduńska Wola', 'Świnoujście', 'Żyrardów',
             'Bolesławiec', ' Nowa Sól', 'Knurów', 'Oświęcim', 'Sopot', 'Sanok', 'Inowrocław']

streets = ['Polna',
           'Leśna',
           'Słoneczna',
           'Krótka',
           'Szkolna',
           'Ogrodowa',
           'Lipowa',
           'Łąkowa',
           'Brzozowa',
           'Kwiatowa',
           'Kościelna',
           'Sosnowa',
           'Zielona',
           'Parkowa',
           'Akacjowa',
           'Kolejowa'
           ]

entity_names = [
    'Centrum rehabilitacyjne',
    'Rehab-Med',
    'Kilinika rehabilitacji',
    'Rehabilitacja św. Łukasza',
    'Gabinet Rehabilitacji'
]

rehabilitators = Rehabilitator.objects.all()


def random_birthday():
    start = datetime.date(1950, 1, 1)
    end = datetime.date(2007, 1, 1)
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + timedelta(seconds=random_second)


class Command(BaseCommand):
    help = "Adding N random rehabilitators"

    def add_arguments(self, parser):
        parser.add_argument("N", type=int)

    def handle(self, *args, **options):
        for i in range(options['N']):
            surname = random.choice(surnames)
            location = random.choice(locations)
            street = random.choice(streets)
            house_number = str(random.randint(1, 200))
            rehabilitator = random.choice(rehabilitators)
            if random.random() < 0.5:
                name = random.choice(male_names)
                sex = 'M'
            else:
                name = random.choice(female_names)
                sex = 'F'
                if surname.endswith('ski') or surname.endswith('cki') or surname.endswith('dzki'):
                    surname = surname.replace('ski', 'ska').replace('cki', 'cka').replace('dzki', 'dzka')

            # length = random.randint(8, 15)
            # lower = string.ascii_lowercase
            # upper = string.ascii_uppercase
            # num = string.digits
            # array_to_choose = lower + upper + num
            # temp = random.sample(array_to_choose, length)
            # password = "".join(temp)
            user = User(email=f'{name.lower()}.{surname.lower() + str(100*i + i * 2)}@gmail.com',
                        username=f'{name.lower()}.{surname.lower() + str(100*i + i * 2)}')
            user.set_password('Misiek123')
            user.save()

            patient = Patient(user=user,
                              rehabilitator=rehabilitator,
                              name=name,
                              surname=surname,
                              sex=sex,
                              birth_date=random_birthday(),
                              location=location,
                              house_number=house_number,
                              street=street,
                              )

            patient.save()
            print(patient)
