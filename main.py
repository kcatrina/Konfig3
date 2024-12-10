import re
import sys
import yaml
import argparse


class ConfigParser:
    def __init__(self):
        self.constants = {}

    def parse(self, text):
        text = self.remove_comments(text)
        lines = text.strip().splitlines()
        return self.process_lines(lines)

    def remove_comments(self, text):
        """Удаляет однострочные комментарии."""
        return re.sub(r'\\.*', '', text)

    def process_lines(self, lines):
        result = []
        for line in lines:
            line = line.strip()
            if "->" in line:
                self.define_constant(line)
            elif line.startswith("@{"):
                result.append(self.parse_constant_usage(line))
            elif line.startswith("(list"):
                result.append(self.parse_list(line))
            elif line.startswith("["):
                result.append(self.parse_dict(line))
            else:
                raise SyntaxError(f"Неизвестная конструкция: {line}")
        return result

    def define_constant(self, line):
        match = re.match(r"(.*)->\s*([a-z][a-z0-9_]*)\s*;", line)
        if not match:
            raise SyntaxError(f"Некорректное объявление константы: {line}")
        value, name = match.groups()
        value = self.parse_value(value.strip())
        print(f"Defining constant: {name} = {value}")
        self.constants[name] = value

    def parse_constant_usage(self, line):
        match = re.match(r"@{([a-z][a-z0-9_]*)}", line)
        if not match:
            raise SyntaxError(f"Invalid constant usage: {line}")
        name = match.group(1)
        if name not in self.constants:
            raise NameError(f"Constant '{name}' not declared")
        return self.constants[name]

    def parse_list(self, value):
        match = re.match(r"\(list (.+?)\)", value)
        if not match:
            raise SyntaxError(f"Invalid list syntax: {value}")
        items = match.group(1).split()
        return [self.parse_value(item) for item in items]

    def parse_dict(self, value):
        value = value.strip()
        if not value.startswith("[") or not value.endswith("]"):
            raise SyntaxError(f"Invalid dictionary syntax: {value}")

        content = value[1:-1].strip()  # Убираем квадратные скобки
        items = self.split_dict_items(content)  # Разбиваем элементы верхнего уровня

        result = {}
        for item in items:
            key_value = item.split("=>", 1)
            if len(key_value) != 2:
                raise SyntaxError(f"Invalid dictionary item: {item}")
            key = key_value[0].strip()
            val = self.parse_value(key_value[1].strip())  # Рекурсивно разбираем значение
            result[key] = val
        return result

    def split_dict_items(self, content):
        """Разбивает элементы словаря на верхнем уровне."""
        items = []
        bracket_level = 0
        current_item = []

        for char in content:
            if char in "[(":
                bracket_level += 1
            elif char in "])":
                bracket_level -= 1

            if char == "," and bracket_level == 0:
                items.append("".join(current_item).strip())
                current_item = []
            else:
                current_item.append(char)

        if current_item:
            items.append("".join(current_item).strip())

        return items


    def parse_value(self, value):
        value = value.strip()
        print(f"Parsing value: {value}")
        if value.startswith("@{"):  # Использование констант
            return self.parse_constant_usage(value)
        elif value.startswith("(list"):  # Обработка массивов
            return self.parse_list(value)
        elif value.startswith("["):  # Обработка словарей
            return self.parse_dict(value)
        elif value.isdigit():  # Числа
            return int(value)
        elif value.startswith('"') and value.endswith('"'):  # Строки
            return value[1:-1]  # Удаляем кавычки
        elif re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", value):  # Обработка идентификаторов
            return value  # Вернуть идентификатор как есть
        else:
            raise SyntaxError(f"Invalid value: {value}")


def main():
    parser = argparse.ArgumentParser(description="Конвертер конфигурационного языка в YAML.")
    parser.add_argument("input_file", help=r"C:\Users\Vovawork\PycharmProjects\kari3\input.txt")
    parser.add_argument("output_file", help=r"C:\Users\Vovawork\PycharmProjects\kari3\output.yaml")
    args = parser.parse_args()

    try:
        with open(args.input_file, "r", encoding="utf-8") as infile:
            text = infile.read().replace("\r", "")
        config_parser = ConfigParser()
        parsed_data = config_parser.parse(text)
        with open(args.output_file, "w", encoding="utf-8") as outfile:
            yaml.dump(parsed_data, outfile, allow_unicode=True)
        print(f"Конфигурация успешно сохранена в {args.output_file}")
    except FileNotFoundError:
        print(f"Ошибка: файл {args.input_file} не найден.", file=sys.stderr)
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
