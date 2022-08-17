README: [ENGLIST](https://github.com/alexwoo1900/potranslator/blob/main/README.md) | [简体中文](https://github.com/alexwoo1900/potranslator/blob/main/README_CN.md)

## PO Translator

Automated translation scripts for .po or .pot file.

## Demo

![Demo](https://raw.githubusercontent.com/alexwoo1900/potranslator/main/demo.gif)

## Quick start

Assuming you have generated a po or pot file from gettext or some other program.

Case I

- you treat msgid as original text
- you want to translate text from language A to language B

```shell
python main.py -s A -d B -f msgid -i pot_file -o po_file
```

Case II

- you treat msgstr as original text
- you want to translate text to all supported languages

```shell
python main.py -d all -f msgstr -i pot_file
```

Case III

- You don't have python installed, you just a translator looking for a dummy tool
- You use Windows

1. Press `win` + `r` and type "cmd" to open the command line
2. 
    ```shell
    cd /d potranslator_folder
    main.exe -d all -i pot_file
    ```

## Detail

The project uses (only implements) Google translation engine by default. Please configure your network environment in `translator/config.ini` before using it.

## Q&A

Q: How the translation part works

A: This project uses the [translator](https://github.com/skywind3000/translator) from [skywind3000](https://github.com/skywind3000). It simulates a browser sending a translation request to the Google translation engine. This implementation is reliable enough, lightweight, and more importantly, it's free.

Q: Which parts can be customized

A: Because the code is simple enough, you can modify almost everything. You can modify global variables to extend the supported formats of the program. You can also write the implementation of other translation engines yourself.