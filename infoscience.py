import xml.dom.minidom
import logging

class InfoscienceEntry:
    def __init__(self):
        self.id = None
        self.title = None
        self.authors = []
        self.venue = None
        self.paperurl = None
        self.year = None

class InfoscienceParser:
    def __init__(self, collection):
        self.collection = collection
        self._total = 0

    def _getText(self, nodelist):
        return "".join([node.data for node in nodelist 
                        if node.nodeType == node.TEXT_NODE])

    def _handleURLSubfield(self, subfield, entry):
        code = subfield.getAttribute("code")
        if code == "x" and self._getText(subfield.childNodes) != "PUBLIC": # Visibility
            logging.warning("Non-public URL for entry %d" % entry.id)
        if code == "u": # Actual title
            entry.paperurl = self._getText(subfield.childNodes)                

    def _handleTitleSubfield(self, subfield, entry):
        code = subfield.getAttribute("code")
        if code == "a": # Main title
            entry.title = self._getText(subfield.childNodes)
        elif code == "b":
            entry.title += ": " + self._getText(subfield.childNodes)

    def _handleAuthorSubfield(self, subfield, entry):
        code = subfield.getAttribute("code")
        if code == "a":
            author = self._getText(subfield.childNodes).split(",")
            entry.authors.append((author[0].strip(), author[1].strip()))

    def _handleLocationSubfield(self, subfield, entry):
        code = subfield.getAttribute("code")
        if code == "a": # Place
            pass
        elif code == "b": # Publisher
            pass
        elif code == "c": # Year
            entry.year = int(self._getText(subfield.childNodes))

    def _handleConferenceSubfield(self, subfield, entry):
        code = subfield.getAttribute("code")
        if code == "a": # Name
            entry.venue = self._getText(subfield.childNodes)
        elif code == "c": # Place
            entry.venue += ", " + self._getText(subfield.childNodes)
        elif code == "d": # Date
            entry.venue += ", " + self._getText(subfield.childNodes)

    def _handleJournalSubfield(self, datafield, entry):
        pass

    def _handleDatafield(self, datafield, entry):
        tag = int(datafield.getAttribute("tag"))

        for subfield in datafield.getElementsByTagName("subfield"):
            if tag == 245: # Title
                self._handleTitleSubfield(subfield, entry)
            elif tag == 260: # Publication date & place
                self._handleLocationSubfield(subfield, entry)
            elif tag == 700: # Authors
                self._handleAuthorSubfield(subfield, entry)
            elif tag == 711: # Conference
                self._handleConferenceSubfield(subfield, entry)
            elif tag == 773: # Journal
                self._handleJournalSubfield(subfield, entry)
            elif tag == 856: # Paper URL
                self._handleURLSubfield(subfield, entry)

    def _handleRecord(self, record):
        controlfield = int(self._getText(
                record.getElementsByTagName("controlfield")[0].childNodes
                    ))

        entry = InfoscienceEntry()
        entry.id = controlfield

        if entry.id not in self.collection:
            self.collection[entry.id] = entry
            self._total += 1
            
            for datafield in record.getElementsByTagName("datafield"):
                self._handleDatafield(datafield, entry)
                
            assert entry.year, "No publication year"
            assert entry.title, "No publication title"
            assert entry.authors, "No publication authors"
            # print entry.id, entry.year

    def _handleCollection(self, collection):
        for record in collection.getElementsByTagName("record"):
            self._handleRecord(record)

    def parseXML(self, data):
        xmldata = xml.dom.minidom.parseString(data)

        self._total = 0
        self._handleCollection(xmldata)

        return self._total

