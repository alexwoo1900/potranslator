README: [ENGLIST](https://github.com/alexwoo1900/potranslator/blob/master/README.md) | [简体中文](https://github.com/alexwoo1900/potranslator/blob/master/README_CN.md)

## PO Translator

针对po或pot文件的自动化翻译脚本。

## 演示

![Demo](https://raw.githubusercontent.com/alexwoo1900/potranslator/master/demo.gif)

## 快速上手

假设你已经从gettext或者其他程序生成了po或者pot文件。

例子I

- 你将msgid的内容作为原始（待翻译）文本
- 你想将文本从A语言翻译成B语言

```shell
python main.py -s A -d B -f msgid -i pot_file -o po_file
```

例子II

- 你将msgstr的内容作为原始（待翻译）文本
- 你想将文本翻译成所有可支持的语言

```shell
python main.py -d all -f msgstr -i pot_file
```

例子III

- 你没有安装python，你只是个寻找傻瓜式工具的翻译人员
- 你使用Windows

1. 按下`win`和`r`并输入"cmd"打开命令行
2. 
    ```shell
    cd /d potranslator_folder
    main.exe -d all -i pot_file
    ```

## 细节

本项目默认使用（仅实现）谷歌翻译引擎，所以在使用前请在`translator/config.ini`中配置好网络环境。

## Q&A

Q: 翻译是怎么做的

A: 本项目基于[skywind3000](https://github.com/skywind3000)的[翻译器](https://github.com/skywind3000/translator)。它的基本原理是模拟浏览器给谷歌翻译引擎发送翻译请求。这种实现足够可靠、轻量，更重要地，它是免费的。

Q: 哪些部分可以定制化

A: 代码足够简单，你可以随意摆弄。你可以修改程序的全局变量来拓展翻译器的支持格式，也可以自行编写其他翻译引擎的实现。