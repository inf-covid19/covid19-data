import requests
import re
from bs4 import BeautifulSoup
from os import getcwd, path, rename

import datetime
from helpers import ensure_dirs, ensure_consistency

URL = 'https://es.wikipedia.org/wiki/Pandemia_de_enfermedad_por_coronavirus_de_2020_en_Uruguay'


def scrape_uruguay():
    cwd = getcwd()
    uruguay_dir = path.join(cwd, 'data', 'uruguay')
    tmp_dir = path.join(cwd, 'tmp')
    ensure_dirs(uruguay_dir, tmp_dir)

    not_number_regexp = re.compile(r'\D')

    today = str(datetime.date.today())
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    tables = soup.find_all('table', {'class': 'wikitable'})
    per_departament_table = None

    for table in tables:
        headers = [th.get_text().strip() for th in table.find_all('th')]
        if len(headers) > 0 and 'Departamento' == headers[0]:
            per_departament_table = table

    updated_files = []
    header = 'date,iso,region,city,place_type,cases,deaths,recovered\n'

    for tr in per_departament_table.tbody.find_all('tr'):
        cols = [td.get_text().strip() for td in tr.find_all('td')]
        if len(cols) != 5:
            continue

        departament = cols[0]
        iso = DEPARTAMENT_ISO[departament]

        line = ','.join([
            today,
            iso,
            departament,
            '',
            'departamento',
            not_number_regexp.sub('', cols[1]),
            not_number_regexp.sub('', cols[3]),
            not_number_regexp.sub('', cols[2]),
        ])

        departament_file = path.join(uruguay_dir, f'{iso.lower()}.csv')
        is_empty = not path.exists(departament_file)

        with open(departament_file, 'a+') as f:
            if is_empty:
                f.write(header)
            f.write(f'{line}\n')

        if not is_empty:
            updated_files.append(departament_file)

    ensure_consistency(updated_files, lambda row: row[:4])

    with open(path.join(getcwd(), 'data', 'uruguay', 'README.md'), 'w') as readme_f:
        readme_f.write(get_readme_contents())


def get_readme_contents():
    toc = [f'| {name} | [`{iso.lower()}.csv`]({iso.lower()}.csv) |' for name,
           iso in DEPARTAMENT_ISO.items()]
    toc_contents = '\n'.join(toc)

    return f"""## Uruguay

> Last updated at {datetime.datetime.now(datetime.timezone.utc).strftime('%b %d %Y %H:%M:%S UTC')}.


| Departament | Dataset |
| ----------- | ------- |
{toc_contents}

"""


DEPARTAMENT_ISO = {
    'Artigas': 'UY-AR',
    'Canelones': 'UY-CA',
    'Cerro Largo': 'UY-CL',
    'Colonia': 'UY-CO',
    'Durazno': 'UY-DU',
    'Flores': 'UY-FS',
    'Florida': 'UY-FD',
    'Lavalleja': 'UY-LA',
    'Maldonado': 'UY-MA',
    'Montevideo': 'UY-MO',
    'Paysandú': 'UY-PA',
    'Río Negro': 'UY-RN',
    'Rivera': 'UY-RV',
    'Rocha': 'UY-RO',
    'Salto': 'UY-SA',
    'San José': 'UY-SJ',
    'Soriano': 'UY-SO',
    'Tacuarembó': 'UY-TA',
    'Treinta y Tres': 'UY-TT',
}
