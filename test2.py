import sys
import time


class DynamicStdout:
    def __init__(self):
        self.original_stdout = sys.stdout
        self.last_line = None
        self.count = 0
        self.first_line = True

    def write(self, text):
        if text.strip():  # Игнорируем пустые строки
            # Обработка новой строки
            if text != self.last_line:
                # Сброс счетчика для новой строки
                self.count = 0
                self.last_line = text
                self.first_line = False

            # Увеличиваем счетчик для повторяющихся строк
            self.count += 1

            # Формируем текст с счетчиком
            output = f"{text.rstrip()} x{self.count}\r"

            # Для первой строки выводим без возврата каретки
            if self.first_line:
                output = f"{text.rstrip()} x{self.count}\n"

            self.original_stdout.write(output)
            self.original_stdout.flush()

    def flush(self):
        self.original_stdout.flush()


# Пример использования
if __name__ == "__main__":
    # Сохраняем оригинальный stdout
    original_stdout = sys.stdout

    try:
        # Заменяем stdout на наш кастомный объект
        sys.stdout = DynamicStdout()

        # Тестовые вызовы print
        print('Hi')
        time.sleep(0.5)  # Задержка для наглядности
        print('Hi')
        time.sleep(0.5)
        print('Hi')
        time.sleep(0.5)
        print('Hi')
        time.sleep(0.5)
        print('Hi')
        print('Hello')
        time.sleep(0.5)
        print('Hi')
        time.sleep(0.5)
        print('Hi')
        time.sleep(0.5)
        print('Hi')
        time.sleep(0.5)
        print('Hi')
        time.sleep(0.5)
        print('Hi')

        # Добавим перевод строки в конце
        sys.stdout.original_stdout.write('\n')

    finally:
        # Восстанавливаем оригинальный stdout
        sys.stdout = original_stdout