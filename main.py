import os
import sys
import getopt
import pathlib
from contextlib import contextmanager
from translator.translator import ENGINES

@contextmanager
def opened_w_error(filename, mode='r'):
    try:
        f = open(filename, mode, encoding="utf-8")
    except IOError as err:
        yield None, err
    else:
        try:
            yield f, None
        finally:
            f.close()

SUPPORT_ENGINES = ["google"]
SUPPORT_LANGUAGES = ["auto", "zh-cn", "en", "fr", "de", "it", "ja", "ru", "es", "all"]
SUPPORT_OUTPUT_FORMAT = ["po"]
POT_TEXT_FIELD = ["msgid", "msgstr"]

class POTranslator:
    def __init__(self, engine_type):
        self._engine = None
        self._engine_type = engine_type
        assert self._init_t_engine(engine_type), "Translation engine initialization failed!"

    def _init_t_engine(self, engine):
        cls = ENGINES.get(engine)
        self._engine = cls()
        return self._engine is not None

    def _parse_pot(self, pot_name):
        with opened_w_error(pot_name, 'r') as (f, err):
            pot_data = []
            msgctxt_data = []
            msgid_data = []
            msgstr_data = []
            
            msg_section = {}
            if not err:
                processing_field = ""

                lines = f.readlines()

                for line in lines:

                    # normal line
                    if line != '\n':

                        # comment line
                        if line[0] == '#':
                            if "comment" not in msg_section:
                                msg_section["comment"] = []
                            msg_section["comment"].append(line)

                        # msgctxt line
                        elif line.startswith("msgctxt"):
                            processing_field = "msgctxt"
                            if "msgctxt" not in msg_section:
                                msg_section["msgctxt"] = []
                            msg_section["msgctxt"].append(len(msgctxt_data))
                            msgctxt_data.append(line[8:].strip().strip('"'))
                        
                        # msgid line
                        elif line.startswith("msgid"):
                            processing_field = "msgid"
                            if "msgid" not in msg_section:
                                msg_section["msgid"] = []
                            msg_section["msgid"].append(len(msgid_data))
                            msgid_data.append(line[6:].strip().strip('"'))

                        # msgstr line
                        elif line.startswith("msgstr"):
                            processing_field = "msgstr"
                            if "msgstr" not in msg_section:
                                msg_section["msgstr"] = []
                            msg_section["msgstr"].append(len(msgstr_data))
                            msgstr_data.append(line[7:].strip().strip('"'))

                        # sentence
                        elif line[0] == '"' and processing_field != "":
                            if processing_field == "msgctxt":
                                msg_section["msgctxt"].append(len(msgctxt_data))
                                msgctxt_data.append(line.strip().strip('"'))
                            elif processing_field == "msgid":
                                msg_section["msgid"].append(len(msgid_data))
                                msgid_data.append(line.strip().strip('"'))
                            elif processing_field == "msgstr":
                                msg_section["msgstr"].append(len(msgstr_data))
                                msgstr_data.append(line.strip().strip('"'))
                    
                    # blank line
                    else:
                        if msg_section:
                            pot_data.append(msg_section)
                            msg_section = {}
                            processing_field = ""

            return pot_data, msgctxt_data, msgid_data, msgstr_data

    def _translate(self, sl, dl, texts):

        bulk_translated_texts = []

        if self._engine_type == "google":

            if len(texts) > 0:
                msgs = ""
                bulk_len = 0
                bulk_idx = 0
                next_bulk_idx = 0
                
                while True:
                    # Google Translate character limit: 5000
                    while next_bulk_idx < len(texts) and bulk_len + len(texts[next_bulk_idx]) + 1 < 5000:
                        bulk_len += len(texts[next_bulk_idx]) + 1
                        msgs = msgs + '\n' + texts[next_bulk_idx]
                        next_bulk_idx += 1

                    res = self._engine.translate(sl, dl, msgs)

                    print("\r[%6.2f%%][%-50s]\r" % (100 * (next_bulk_idx) / len(texts), '>' * (50 * (next_bulk_idx) // len(texts))), end='', flush=True)

                    if res and "definition" in res and res["definition"]:
                        bulk_translated_text = res["definition"].split('\n')

                        '''
                        The Google translation engine will ignore the empty lines at the beginning and end of the search string,
                        We need to fill in the blank lines to match the number of strings before and after translation.
                        '''
                        idx = bulk_idx
                        while not texts[idx]:
                            bulk_translated_text.insert(0, "")
                            idx += 1
                        idx = next_bulk_idx - 1
                        while not texts[idx]:
                            bulk_translated_text.append("")
                            idx -= 1

                        if len(bulk_translated_text) != next_bulk_idx - bulk_idx:
                            print("Translation error, please debug the program!")
                            return []
                        else:
                            bulk_translated_texts.extend(bulk_translated_text)
                    else:
                        return []
                            
                    if next_bulk_idx != len(texts):
                        bulk_len = 0
                        msgs = ""
                        bulk_idx = next_bulk_idx
                    else:
                        break

            print("")

        else:
            print("Currently POTranslator doesn't support this translation engine: ", self._engine_type)

        return bulk_translated_texts

    def _write_po(self, output_file_path, pot_data, msgctxt_data, msgid_data, msgstr_data, pot_target_field, translated_texts):
        with opened_w_error(output_file_path, 'w') as (f, err):
            if not err:
                for msg_section in pot_data:
                    # write comment
                    if "comment" in msg_section:
                        for comment in msg_section["comment"]:
                            f.write(comment)
                    
                    #write msgctxt
                    if "msgctxt" in msg_section:
                        for i, msgctxt_idx in enumerate(msg_section["msgctxt"]):
                            if i == 0:
                                f.write("msgctxt \"{}\"\n".format(msgctxt_data[msgctxt_idx]))
                            else:
                                f.write("\"{}\"\n".format(msgctxt_data[msgctxt_idx]))
                    
                    # write msgid
                    if "msgid" in msg_section:
                        for i, msgid_idx in enumerate(msg_section["msgid"]):
                            if i == 0:
                                f.write("msgid \"{}\"\n".format(msgid_data[msgid_idx]))
                            else:
                                f.write("\"{}\"\n".format(msgid_data[msgid_idx]))

                    # no translatation for header
                    if "msgid" in msg_section and len(msg_section["msgid"]) == 1 and msgid_data[msg_section["msgid"][0]] == "":
                        for i, msgstr_idx in enumerate(msg_section["msgstr"]):
                            if i == 0:
                                f.write("msgstr \"{}\"\n".format(msgstr_data[msgstr_idx]))
                            else:
                                f.write("\"{}\"\n".format(msgstr_data[msgstr_idx]))
                    
                    # write msgstr
                    else:
                        if pot_target_field == "msgid":
                            if "msgid" in msg_section:
                                for i, msgid_idx in enumerate(msg_section["msgid"]):
                                    if i == 0:
                                        f.write("msgstr \"{}\"\n".format(translated_texts[msgid_idx]))
                                    else:
                                        f.write("\"{}\"\n".format(translated_texts[msgid_idx]))
                        else:
                            if "msgstr" in msg_section:
                                for i, msgstr_idx in enumerate(msg_section["msgstr"]):
                                    if i == 0:
                                        f.write("msgstr \"{}\"\n".format(translated_texts[msgstr_idx]))
                                    else:
                                        f.write("\"{}\"\n".format(translated_texts[msgstr_idx]))

                    # write blank line
                    f.write('\n')

    def generate_po(self, pot_file_path, pot_target_field, source_lang, dest_lang, output_file_path):
        pot_data, msgctxt_data, msgid_data, msgstr_data = self._parse_pot(pot_file_path)

        translated_data = []
        if pot_target_field == "msgid":
            translated_data = self._translate(source_lang, dest_lang, msgid_data)
        else:
            translated_data = self._translate(source_lang, dest_lang, msgstr_data)
            
        self._write_po(output_file_path, pot_data, msgctxt_data, msgid_data, msgstr_data, pot_target_field, translated_data)
        print("{} generated".format(output_file_path))

    def generate_pos(self, pot_file_path, pot_target_field, pos_d_path):
        for lang in SUPPORT_LANGUAGES[1:-1]:
            try:
                self.generate_po(pot_file_path, pot_target_field, "auto", lang, pos_d_path + "{}.po".format(lang))
            except IndexError as err:
                print("Error occur in {}.po: {}".format(lang, err))

def print_usage():
    print("Usage: main.py [options] -i template.pot -o translated.po")
    print("Options:")
    print("  -e <arg>      Translation Engine        ", SUPPORT_ENGINES)
    print("  -s <arg>      Source Language           ", SUPPORT_LANGUAGES[:-1])
    print("  -d <arg>      Destination Language      ", SUPPORT_LANGUAGES)
    print("  -f <arg>      Treat msgid or msgstr     ", POT_TEXT_FIELD)
    print("                as the original text")
    print("                Default: msgid")
    print("  -t <arg>      Output file format        ", SUPPORT_OUTPUT_FORMAT)

def print_version():
    print("Version 0.01")

def is_pot(name):
    return pathlib.Path(name).is_file() and os.path.splitext(name)[-1].lower() in (".pot", ".po")

def main(argv=None):
    if argv is None:
        argv = sys.argv
    argv = [ n for n in argv ]

    try:
        opts, args = getopt.getopt(argv[1:], 
            "-e:-s:-d:-f:-i:-o:-v-h", 
            ["engine=", "source=", "dest=", "field=", "input=", "output=", "version", "help"])
    except getopt.GetoptError as err:
        print(err)
        print_usage()
        return -1


    engine_type = SUPPORT_ENGINES[0]
    source_lang = SUPPORT_LANGUAGES[0]
    dest_lang = SUPPORT_LANGUAGES[0]
    pot_target_field = POT_TEXT_FIELD[0]
    output_file_format = SUPPORT_OUTPUT_FORMAT[0]
    pot_file_path = ""
    output_dir_path = "locale/"
    output_file_path = ""

    for opt_name, opt_value in opts:
        if opt_name in ("-h", "--help"):
            print_usage()
        elif opt_name in ("-v", "--version"):
            print_version()
        elif opt_name in ("-e", "--engine"):
            if opt_value in SUPPORT_ENGINES:
                engine_type = opt_value
        elif opt_name in ("-s", "--source"):
            if opt_value in SUPPORT_LANGUAGES[:-1]:
                source_lang = opt_value
        elif opt_name in ("-d", "--dest"):
            if opt_value in SUPPORT_LANGUAGES:
                dest_lang = opt_value
        elif opt_name in ("-f", "--field"):
            if opt_value in POT_TEXT_FIELD:
                pot_target_field = opt_value
        elif opt_name in ("-i", "--input"):
            pot_file_path = opt_value
        elif opt_name in ("-o", "--output"):
            output_file_path = opt_value

    if not is_pot(pot_file_path):
        print("Illegal input file: ", pot_file_path)
        print_usage()
        return -1

    if dest_lang != "all" and not output_file_path:
        print("Missing output file path.")
        print_usage()
        return -1

    translator = POTranslator(engine_type)

    if dest_lang != "all":
        if output_file_format == "po":
            translator.generate_po(pot_file_path, pot_target_field, source_lang, dest_lang, output_file_path)
    else:
        if output_file_format == "po":
            translator.generate_pos(pot_file_path, pot_target_field, output_dir_path)
        
    return 0

if __name__ == "__main__":
    main()
