import lxml.etree as etree
import json
from elasticsearch import Elasticsearch
from io import StringIO
import socket
import sys

NS = "{http://www.archives.ncdcr.gov/mail-account}"
ID = NS + "LocalId"
MESID = NS + "MessageId"
SUBJECT = NS + "Subject"
FROM = NS + "From"
TO = NS + "To"
CC = NS + "CC"
BCC = NS + "BCC"
TAG = NS + "TaggedContent"
STRIP = NS + "StrippedContent"
CONT = NS + "Content"


MAP = [ID, SUBJECT, MESID, FROM, TO, CC, BCC, TAG, STRIP, CONT]

ES_MAP = {ID: "EAXS_ID", SUBJECT: "SUBJECT", FROM: "FROM", TO: "TO", CC: "CC",
          BCC: "BCC", TAG: "TAG_C", MESID: "MESSAGE_ID", STRIP: "SCONTENT", CONT: "CONTENT"}


class EaxsToElastic:
    def __init__(self, file, container_ip: str, my_ns=NS, tag="Message") -> None:
        self.production = False
        self.file_to_parse = file
        self.NS = my_ns
        self.tag = tag
        self.elastic_ip = container_ip
        self.es = None
        self.search_tag = "{}{}".format(self.NS, self.tag)
        self.context = etree.iterparse(file, tag=self.search_tag)
        self.stats = {}
        self.entity_type_stats = {}
        self.has_pii = False
        self._get_ip()

    def _get_ip(self):
        if self.production:
            self.es = Elasticsearch([self.elastic_ip], port=9200)
        else:
            self.es = Elasticsearch(['192.168.99.100'], port=9200)

    def convert(self):
        for event, element in self.context:
            self.build_json(element)

    def strip_text(self, children: list, positions: list):
        new_child = None
        new_parent = etree.Element("{http://www.archives.ncdcr.gov/mail-account}TaggedContent")
        running_text = ''
        cur_pos = 0
        last_i = 0
        for i in range(len(children)):
            if i != last_i:
                continue
            child = children[i]
            if child.attrib:
                new_child = etree.Element(child.attrib['entity'], attrib={'authority': child.attrib['authority']})
                first_pos = positions.index(int(child.attrib['group']))
                last_i = len(positions) - 1 - positions[::-1].index(int(child.attrib['group']))
                t = ''
                for el in children[first_pos:last_i+1]:
                    t += "{} ".format(el.text)
                new_child.text = t
                # set cur_pos to last_i
                last_i += 1
                running_text += "{} ".format(etree.tostring(new_child).decode("utf-8"))
            else:
                running_text += "{} ".format(child.text)
                last_i += 1
        return running_text

    def clean_tokens(self, tokenized):
        positions = []
        children = []
        elm = etree.fromstring(tokenized)
        for child in elm:
            if child.attrib:
                a = child.attrib
                entity = a['entity']
                sp_e = entity.split(".")
                if len(sp_e) > 1 and sp_e[0] == "PII":
                    self.has_pii = True
                    entity = "{}_{}".format(sp_e[1], sp_e[0])
                elif len(sp_e) > 1 and sp_e[0] != "PII":
                    entity = "{}_{}".format(sp_e[1], sp_e[0])
                if entity not in self.stats:
                    self.stats[entity] = 1
                self.stats[entity] += 1
                try:
                    auth = a['authority']
                    group = a['group']
                    positions.append(int(a['group']))
                except KeyError as e:
                    pass
                if entity in self.stats:
                    self.stats[entity] += 1
                else:
                    self.stats[entity] = 1
            else:
                positions.append(0)
            children.append(child)

    def build_json(self, element: etree.Element):
        js = {}
        self.stats = {}
        self.has_pii = False
        for el in element.iter():
            # type: etree.Element
            if el.tag in MAP:
                t = ES_MAP[el.tag]
                if t in js:
                    continue
                if el.tag == CONT:
                    js[t] = el.text
                    continue
                if el.tag == TAG:
                    js[t] = el.text
                    self.clean_tokens(el.text)
                    continue
                if el.tag == STRIP:
                    js[t] = el.text
                    continue
                js[ES_MAP[el.tag]] = el.text
        js['PROCESSED'] = element.get('Processed')
        js['RECORD'] = element.get('Record')
        js['FOLDER'] = element.get('ParentFolder')
        js['RESTRICTED'] = element.get('Restricted')
        for k, v in self.stats.items():
            js[k] = v
        if self.has_pii:
            js['HAS_PII'] = 'true'
        else:
            js['HAS_PII'] = 'false'
        if 'SCONTENT' in js and 'CONTENT' in js:
            # Replace stripped with CONTENT
            js['CONTENT'] = js['SCONTENT']
            js.pop('SCONTENT', None)
        try:
            self.es.index(index="eaxs_index", doc_type="email", id=int(js['EAXS_ID']), body=json.dumps(js))
            print(json.dumps(js))
        except Exception as e:
            print(e)

    def get_stats(self, ele: etree.Element):
        st_el = etree.tostring(ele)
        elm = etree.fromstring(st_el)
        for event, child in etree.parse(StringIO(st_el.decode("utf-8"))):
            print(child.attrib)


if __name__ == "__main__":
    args = sys.argv
    eaxs2el = EaxsToElastic(args[1], args[2])
    eaxs2el.convert()
