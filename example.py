from rutypograph import Typograph, get_default_environment

if __name__ == '__main__':
    settings = get_default_environment()
    settings.convert_html_entities_to_unicode = True
    print(Typograph.process("- Это \"типограф? \"Вторые кавычки\"\"\n- Да, это он...."))
