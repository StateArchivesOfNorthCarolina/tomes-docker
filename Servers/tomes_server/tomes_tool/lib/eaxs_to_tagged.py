#!/usr/bin/env python3

"""
This module contains a class for converting an EAXS file to a tagged EAXS document.

Todo:
    * Do you need to support <ExtBodyContent> messages?
        - I think "yes" and you'll need to append attributes/elements accordingly.
        - I think update_message MIGHT be doing this already?
            - Only one way to find out. :P
    * Do you really need huge_tree when iterparsing?
    * When you write the tagged block, I think you need to use 
    "decode(self.charset, errors="backslashreplace"" or JG's function to prevent XML writing
    errors. This is because the tagged XML is converted to a string in order to place it in
    a CDATA block. Otherwise, it seems OK. So nlp_to_xml is probably OK.
        - Update: For now, using "decode()" on the infamous "choke message" is working.
"""

# import modules.
import base64
import logging
import os
from lxml import etree
import unicodedata
import gc


class EAXSToTagged():
    """ A class for converting an EAXS file to a tagged EAXS document.

    Example:
        >>> html2text = def html2text(html) ... # convert HTML to plain text.
        >>> text2nlp = def text2nlp(text) ... # convert plain text to NLP output.
        >>> e2t = EAXSToTagged(html2text, text2nlp)
        >>> tagged = e2t.write_tagged(eaxs_file, "output.xml") # tagged EAXS to "output.xml".
    """

    def __init__(self, html_converter, nlp_tagger, charset="UTF-8"):
        """ Sets instance attributes.

        Args:
            - html_converter (function): Any function that accepts HTML text (str) as its
            only required argument and returns a plain text version (str).
            - nlp_tagger (function): Any function that accepts plain text (str) as its only
            required argument and returns an NLP-tagged XML message (lxml.etree_Element).
            - charset (str): Encoding with which to update EAXS message content. This is also
            the encoding used to write a tagged EAXS file with the write_tagged() method.
        """

        # set logger; suppress logging by default.
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # set attributes.
        self.html_converter = html_converter
        self.nlp_tagger = nlp_tagger
        self.charset = charset

        # set namespace attributes.
        self.ncdcr_uri = "http://www.archives.ncdcr.gov/mail-account"
        self.ns_map  = {"ncdcr":self.ncdcr_uri}

    def _get_global_id(self, eaxs_file):
        """ Gets <GlobalId> value for a given @eaxs_file. """

        # set full <GlobalId> name to include namespace URI.
        global_id_el = "{" + self.ncdcr_uri + "}GlobalId"

        # iterate through @eaxs_file until value is found.
        global_id = None
        for event, element in etree.iterparse(eaxs_file, tag=global_id_el):
            global_id_el = element
            global_id = global_id_el.text
            element.clear()

        return global_id


    def _get_message_id(self, message_el):
        """ Gets <Message/MessageId> value.

        Args:
            message_el (lxml.etree._Element): An EAXS <Message> element.

        Returns:
            str: The return value.
            The message identifier.
        """

        # get identifier value; strip whitespace.
        path = "ncdcr:LocalId"
        message_id = message_el.xpath(path, namespaces=self.ns_map)[0].text
        message_id = message_id.strip()

        return message_id

    def _get_single_body_element(self, message_el, name, value=""):
        """ Gets <Message/MultiBody/SingleBody/@name> element and its text value. Note that
        <SingleBody> elements for attachments are skipped.

        Args:
            - message_el (lxml.etree._Element): An EAXS <Message> element.
            - name (str): The element to retrieve.
            - value (str): The text value to return for @name if no text value found.

        Returns:
            tuple: The return value.
            The first item is an lxml.etree._Element, i.e. @name.
            The second item is a string, i.e. @name's value.
        """

        # set XPath for @name, omitting attachments.
        name = name.replace("/", "/ncdcr:")
        path = "ncdcr:MultiBody"
        path += "/ncdcr:SingleBody[(not(contains(ncdcr:Disposition, 'attachment')))][1]"
        path += "/ncdcr:{name}"
        path = path.format(name=name)

        # get element.
        name_el = message_el.xpath(path, namespaces=self.ns_map)

        # assume defaults; replace with actual values if element exists.
        el, el_text = None, value
        if len(name_el) > 0:
            name_el = name_el[0]
            el, el_text = name_el, name_el.text

        return (el, el_text)

    def tag_message(self, message_el, content_text):
        """ Tags a given <Message> element with a given text value.

        Args:
            - message_el (lxml.etree._Element): The <Message> element to be updated.
            - content_text (str): The text from which to extract NLP tags via 
            self.nlp_tagger.

        Returns:
            tuple: The return value.
            The first item is an lxml.etree._Element: the tagged XML tree.
            The second item is a string: the original message stripped of HTML tags and/or
            Base64-decoded. If the messages was unaltered, this value is None.
        """

        #self.logger.info("Tagging <Message> element content.")

        # get transfer encoding and MIME type.
        transfer_encoding_el, transfer_encoding_text = self._get_single_body_element(
                message_el, "TransferEncoding")
        content_type_el, content_type_text = self._get_single_body_element(message_el,
                "ContentType")

        # assume that content will be unaltered.
        is_stripped = False

        # decode Base64 <Content> if needed.
        if transfer_encoding_text.lower() == "base64":
            #self.logger.info("Decoding Base64 message content.")
            content_text = base64.b64decode(content_text)
            content_text = content_text.decode(self.charset, errors="backslashreplace")
            is_stripped = True

        # convert HTML to text if needed.
        if content_type_text.lower() in ["text/html", "application/xml+html"]:
            # self.logger.info("Requesting HTML to plain text conversion.")
            content_text = self.html_converter(content_text)
            is_stripped = True

        # get NLP tags.
        # self.logger.info("Requesting NER tags.")
        tagged_el = self.nlp_tagger(content_text)

        # set value of stripped content.
        stripped_content = None
        if is_stripped:
            stripped_content = content_text

        return (tagged_el, stripped_content)

    def update_message(self, message_el, folder_name):
        """ Updates a <Message> element's value with NLP-tagged content. Affixes the parent 
        @folder_name as an attribute to updated elment.

        Args:
            - message_el (lxml.etree._Element): The <Message> element to be updated.
            - folder_name (str): The name of the EAXS <Folder> element containing the 
            <Message> element.

        Returns:
            lxml.etree._Element: The return value.
            The updated <Message> element.
        """
        
        # self.logger.info("Updating <Message> element tree.")

        # set new attributes.
        message_el.set("ParentFolder", folder_name)
        message_el.set("Processed", "false")
        message_el.set("Record", "true")
        message_el.set("Restricted", "true")
        message_el.append(etree.Element("{" + self.ncdcr_uri + "}Restriction", 
            nsmap=self.ns_map))

        # get <Content> element value.
        content_el, content_text = self._get_single_body_element(message_el, 
                "BodyContent/Content")

        # if no <Content> sub-element exists, return <Message>.
        if content_el is None or content_text is None:
                return message_el

        # otherwise tag the message with NLP.
        tagged_content, stripped_content = self.tag_message(message_el, content_text)
        tagged_content = etree.tostring(tagged_content, encoding=self.charset)
        tagged_content = tagged_content.decode(self.charset, errors="backslashreplace")

        # create new <SingleBody> element with NLP-tagged content tree.
        single_body_el = etree.Element("{" + self.ncdcr_uri + "}SingleBody", 
                nsmap=self.ns_map)
        tagged_content_el = etree.Element("{" + self.ncdcr_uri + "}TaggedContent", 
                nsmap=self.ns_map)
        try:
            tagged_content_el.text = etree.CDATA(tagged_content)
        except ValueError as e:
            self.logger.error(e)
            self.logger.error("Attempting to clean the message.")
            tagged_content_el.text = etree.CDATA(self.remove_bad_characters(tagged_content))
        single_body_el.append(tagged_content_el)

        # if needed, append plain text version of content to new <SingleBody> element.
        if stripped_content is not None:
                stripped_content_el = etree.Element("{" + self.ncdcr_uri + 
                        "}StrippedContent", nsmap=self.ns_map)
                stripped_content_el.text = etree.CDATA(stripped_content)
                single_body_el.append(stripped_content_el)

        # append new <SingleBody> element to @message_el. 
        message_el.xpath("ncdcr:MultiBody", namespaces=self.ns_map)[0].append(single_body_el)

        return message_el

    def write_tagged(self, eaxs_file, tagged_eaxs_file):
        """ Converts an EAXS file to a tagged EAXS document and writes it to 
        @tagged_eaxs_file.

        Args:
            - eaxs_file (str): The filepath for the EAXS file to convert.
            - tagged_eaxs_file (str): The filepath that the tagged EAXS document will be
            written to.

        Returns:
            None

        Raises:
            - FileExistsError: If @tagged_eaxs_file already exists.
        """

        self.logger.info("Converting '{}' EAXS file to tagged EAXS file: {}".format(
            eaxs_file, tagged_eaxs_file))

        # raise error if output file already exists.
        if os.path.isfile(tagged_eaxs_file):
            err = "Destination file '{}' already exists.".format(tagged_eaxs_file)
            self.logger.error(err)
            raise FileExistsError(err)

        messages_to_process = 0
        mem_free = 0
        self.logger.info("Finding number of Messages.")

        for ev, el in etree.iterparse(eaxs_file, events=("end",),
                                          strip_cdata=False,
                                          tag="{http://www.archives.ncdcr.gov/mail-account}Message",
                                          huge_tree=True):
                messages_to_process += 1
                mem_free += 1
                self.logger.info("{}".format(mem_free))
                if mem_free > 50000:
                    gc.collect()
                    mem_free = 0
                ev = None
                el = None

        # write tagged EAXS file.
        with etree.xmlfile(tagged_eaxs_file, encoding=self.charset, close=True) as xfile:

            # write XML header; permanently register namespace prefix and URI.
            xfile.write_declaration()
            etree.register_namespace("ncdcr", self.ncdcr_uri)

            # create <Account> element with attributes.
            with xfile.element("ncdcr:Account", GlobalId=self._get_global_id(eaxs_file), 
                    SourceEAXS=os.path.basename(eaxs_file), nsmap=self.ns_map):
                # Loop through Messages and tag them.

                for event, element in etree.iterparse(eaxs_file, events=("end",),
                        strip_cdata=False, tag="{http://www.archives.ncdcr.gov/mail-account}Message", huge_tree=True):
                    # TODO: Remove this for production
                    # if messages_to_process > 3817:
                    #     messages_to_process -= 1
                    #     continue
                    fldr = element.getparent()
                    fldr_name = fldr.getchildren()[0].text
                    fldr = None
                    # if applicable, establish that a <Message> element is open.
                    self.logger.info("Messages Remaining: {}".format(messages_to_process))
                    message_id = self._get_message_id(element)
                    self.logger.info("Processing LocalId: {0:0>7}".format(message_id))
                    messages_to_process -= 1
                    tagged_message = self.update_message(element, fldr_name)
                    xfile.write(tagged_message)
                    element.clear()
        return



    @staticmethod
    def remove_bad_characters(s: bytes):
        s = s.decode("utf-8")
        return "".join(ch for ch in s if unicodedata.category(ch)[0] != "C")


if __name__ == "__main__":
    pass

