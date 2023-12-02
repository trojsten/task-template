import datetime
import itertools
from enschema import Schema, And, Or, Optional, Regex

import core.utilities.globals as glob
from core.utilities import lists
from core.utilities.schema import string, valid_language
from .base import ContextNaboj


class ContextCompetition(ContextNaboj):
    _schema = Schema({
        'id': string,
        'founded': And(int, lambda x: x >= 1950),
        'tearoff': {
            'per_page': int,
            'height': int,
            'team_space': int,
            'barcode_space': int,
            'bottomsep': int,
            'inner': int,
        },
        'organisation': {
            'name': string,
            'address': string,
        },
        'constants': {
            str: {
                'symbol': str,
                'value': Or(str, int, float),
                'unit': str,
                Optional('siextra'): str,
            }
        },
        'URL': string,
        'hacks': dict,
    })

    def populate(self, competition):
        super().populate(competition)
        self.load_meta(competition) \
            .add_id(competition)


class ContextLanguage(ContextNaboj):
    target = 'language'
    subdir = 'languages'
    _schema = Schema({
        'id': valid_language,
        'booklet': {
            'contents': {
                'intro': bool,
                'problems': bool,
                'solutions': bool,
                'answers': bool,
            }
        },
        'polyglossia': lambda x: x in [lang['polyglossia'] for lang in glob.languages.values()],
        'rtl': bool,
    })

    def populate(self, competition, volume, language):
        super().populate(competition)
        self.load_meta(competition, volume, self.subdir, language) \
            .add_id(language)
        self.add({'polyglossia': glob.languages[language]['polyglossia']})
        self.add({'rtl': glob.languages[language].get('rtl', False)}),


class ContextVenue(ContextNaboj):
    target = 'venue'
    subdir = 'venues'
    _schema = Schema({
        'id': And(str, len),
        'code': Regex(r'[A-Z]{5}'),
        'name': And(str, len),
        'language': valid_language,
        'teams': [ContextNaboj.team],
        'teams_grouped': [[ContextNaboj.team]],
        'problems_modulo': [[ContextNaboj.problem]],
        Optional('orgs'): [And(str, len)],
        'evaluators': int,
        'start': And(int, lambda x: 0 <= x < 1440),
    })

    def _add_extra_teams(self, competition, venue):
        code = 0
        while len(self.data['teams']) % competition.data['tearoff']['per_page'] != 0:
            self.data['teams'].append({
                'id': 0,
                'code': f'SKBAS{999 - code}',
                'contact_email': "none@none.none",
                'contact_name': "Unnamed",
                'contact_phone': "",
                'contestants': "unknown",
                'display_name': f"Extra set {999 - code}",
                'in_school_symbol': "",
                'language': self.data['language'],
                'name': "",
                'number': 0,
                'school': "",
                'school_address': "",
                'school_id': 0,
                'school_name': "",
                'status': 'R',
                'venue': venue.data['id'],
                'venue_code': venue.data['code'],
                'venue_id': venue.data['id'],
            })
            code += 1

    def populate(self, competition, volume, venue):
        super().populate(competition)
        comp = ContextCompetition(self.root, competition)
        vol = ContextVolume(self.root, competition, volume)
        self.load_meta(competition, volume, self.subdir, venue) \
            .add_id(venue)
        self._add_extra_teams(comp, vol)
        self.add({
            'teams': lists.numerate(self.data.get('teams'), itertools.count(0)),
            'teams_grouped': lists.split_div(
                lists.numerate(self.data.get('teams')), comp.data['tearoff']['per_page']
            ),
            'problems_modulo': lists.split_mod(
                lists.add_numbers([x['id'] for x in vol.data['problems']], itertools.count(1)),
                self.data['evaluators'], first=1,
            ),
        })


class ContextVolume(ContextNaboj):
    _schema = Schema({
        'id': And(str, len),
        'number': And(int, lambda x: x > 0),
        'date': datetime.date,
        'orgs': [str],
        'problems': [ContextNaboj.problem],
        'constants': dict,
        'table': int,
        'start': And(int, lambda x: 0 <= x < 1440),
        'year': And(int, lambda x: x >= 1950),
    })

    def populate(self, competition, volume):
        super().populate(competition)
        comp = ContextCompetition(self.root, competition)
        self.load_meta(competition, volume) \
            .add_id(f'{volume:02d}') \
            .add_number(volume)

        self.add(dict(
            year=self.data['number'] + comp.data['founded'] - 1,
            problems=lists.add_numbers(self.data['problems'], itertools.count(1)),
        ))
