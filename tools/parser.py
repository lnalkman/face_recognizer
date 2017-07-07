from xml.dom.minidom import parse
import os

def parse_settings(filepath='settings.xml'):
    """
    Parse settings for recognizer from xml file.
    Return dictionary with all properties.
    If some exceptions while parsing will return default properties.
    (Code can be shorter if use list of tags)
    """
    def int_or_none(string=None):
        if string:
            try:
                return int(string)
            except ValueError:
                pass

    properties = {
        'formats': None,
        'maxCoefficient': 60,
        'minSize': None, # (min_width or None, min_height or None) or None
        'maxSize': None, # (max_width or None, max_height or None) or None
        'notRecognizedDir': None,
        'notSureRecognizedDir': None
    }
    try:
        if os.path.isfile(filepath):
            dom = parse(filepath)

            # Formats get from <format> tags.
            properties['formats'] = [
                x.firstChild.data
                for x in dom.getElementsByTagName('format')
                if x.firstChild
                ]

            # Get maxCoefficient
            maxCoef = dom.getElementsByTagName('maxCoefficient')
            if maxCoef and maxCoef.firstChild:
                try:
                    properties['maxCoefficient'] = int(maxCoef.firstChild.data)
                except ValueError:
                    pass

            # Get minimal photo size
            minSize = (
                dom.getElementsByTagName('minWidth'),
                dom.getElementsByTagName('minHeight')
                )
            minSize = (
                minSize[0][0].firstChild if minSize[0] else None,
                minSize[1][0].firstChild if minSize[1] else None
                )
            if any(minSize):
                properties['minSize'] = [
                    minSize[0].data if minSize[0] else None,
                    minSize[1].data if minSize[1] else None
                    ]
                properties['minSize'] = map(int_or_none, properties['minSize'])

            # Get maximal photo size
            maxSize = (
                dom.getElementsByTagName('maxWidth'),
                dom.getElementsByTagName('maxHeight')
                )
            maxSize = (
                maxSize[0][0].firstChild if maxSize[0] else None,
                maxSize[1][0].firstChild if maxSize[1] else None
                )
            if any(maxSize):
                properties['maxSize'] = [
                    maxSize[0].data if maxSize[0] else None,
                    maxSize[1].data if maxSize[1] else None
                    ]
                properties['maxSize'] = map(int_or_none, properties['maxSize'])


            d = dom.getElementsByTagName('notRecognizedDir')[0]
            if d.firstChild:
                properties['notRecognizedDir'] = d.firstChild.data

            d = dom.getElementsByTagName('notSureRecognizedDir')[0]
            if d.firstChild:
                properties['notSureRecognizedDir'] = d.firstChild.data
    finally:
        return properties
