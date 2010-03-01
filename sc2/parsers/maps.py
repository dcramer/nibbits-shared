import mpq

class AttrDict(object):
    # TODO: replace this with something better
    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

class StringParser(object):
    """Parses out strings in the form of key=value"""
    def serialize(fp):
        strings = {}
        for l in data:
            l = l.split('=', 1)
            strings[l[0]] = l[1].strip('\r\n')
    
        return strings

class Localization(object):
    def __init__(self, parser, lang):
        self.parser = parser
        self.lang = lang
    
    @property
    def GameStrings(self):
        parser = StringParser()
        value = parser.serialize(self.parser.mpq['%s.SC2Data\LocalizedData\GameStrings.txt' % (self.lang,)])
        setattr(self, 'GameStrings', value)
        return value

    @property
    def TriggerStrings(self):
        parser = StringParser()
        value = parser.serialize(self.parser.mpq['%s.SC2Data\LocalizedData\TriggerStrings.txt' % (self.lang,)])
        setattr(self, 'TriggerStrings', value)
        return value

class S2MA(object):
    LANGUAGES = ('enUS',)

    def __init__(self, filename):
        self.mpq = mpq.Archive(str(filename))
        for lang in self.langs:
            setattr(self, lang, Localization(self, lang))
    
    @property
    def Attributes(self):
        values = AttrDict(Variants=[])
        root = objectify.fromstring(str(self.mpq['Attributes']))
        for variant in root.iterchildren('Variant'):
            try:
                IsDefault = variant.IsDefault and True
            except AttributeError:
                IsDefault = False
            this = {
                'Id': int(variant.Id.get('Value')),
                'Genre': int(variant.Genre.get('Value')),
                'GameType': int(variant.GameType.get('Value')),
                'MaxTeamSize': int(variant.MaxTeamSize.get('Value')),
                'Name': self.gamestrings[variant.Name.get('Value')],
                'Description': self.gamestrings[variant.Description.get('Value')],
                'IsDefault': IsDefault,
            }
            for attr in variant.iterchildren('Attribute'):
                if attr.get('Id') == '3007':
                    # this is our players info
                    this['MaxPlayers'] = len([a for a in attr.Default if a.Value.get('Id') == '1348563572'])
            values.Variants.append(AttrDict(**this))
        setattr(self, 'Attributes', values)
        return values

    @property
    def Preload(self):
        values = {}
        root = objectify.fromstring(str(self.mpq['Preload.xml']))
        values['Actor'] = [a.get('id') for a in root.Actor]
        values['Unit'] = [a.get('id') for a in root.Unit]
        values['Terrain'] = root.Terrain.get('id')
        value = AttrDict(**values)
        setattr(self, 'Preload', value)
        return value