import os
import threading
from queue import Queue, Empty
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import Command
from assistive.states import all
import subprocess
from assistive.config_read import config

class ShellSession:
    def __init__(self):
        try:
            # Определяем кодировку системы
            if os.name == "nt":
                self.encoding = "cp866"  # Для Windows CMD
            else:
                self.encoding = "utf-8"  # Для Linux

            # Определяем команду для запуска консоли
            shell_command = "cmd" if os.name == "nt" else "bash"

            # Создаем процесс консоли
            self.process = subprocess.Popen(
                shell_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=1,
                universal_newlines=False,  # Чтение в байтах для последующего декодирования
                shell=True
            )

            # Очереди для потоков stdout и stderr
            self.output_queue = Queue()
            self.error_queue = Queue()

            # Потоки для чтения stdout и stderr
            threading.Thread(target=self._enqueue_output, args=(self.process.stdout, self.output_queue), daemon=True).start()
            threading.Thread(target=self._enqueue_output, args=(self.process.stderr, self.error_queue), daemon=True).start()

            self.current_path = os.getcwd()  # Устанавливаем начальный путь
        except Exception as e:
            raise RuntimeError(f"Не удалось запустить консоль: {e}")

    def _enqueue_output(self, stream, queue):
        """Чтение данных из потока в очередь"""
        for line in iter(stream.readline, b''):
            queue.put(line)
        stream.close()

    def execute_command(self, command: str) -> str:
        """Выполнение команды и получение результата"""
        try:
            if not self.process:
                raise RuntimeError("Сессия консоли не активна.")

            # Отправляем команду в консоль
            self.process.stdin.write((command + "\n").encode(self.encoding))
            self.process.stdin.flush()

            # Читаем результат из очередей
            output_lines = []
            while True:
                try:
                    # Считываем строку из stdout
                    line = self.output_queue.get(timeout=0.5)
                    output_lines.append(line.decode(self.encoding))
                except Empty:
                    break  # Если данных больше нет, выходим из цикла

            # Обновляем текущий путь, если команда изменила его
            if "cd " in command or command.strip() == "cd":
                new_path = command.split("cd", 1)[-1].strip()
                self.current_path = os.path.abspath(os.path.expanduser(new_path))
            elif command.strip() in ["pwd", "chdir"]:
                self.current_path = "".join(output_lines).strip()

            # Возвращаем результат выполнения
            return "".join(output_lines).strip() + f"\n\nТекущий путь: {self.current_path}"
        except Exception as e:
            return f"Ошибка: {e}"

    def close(self):
        """Закрытие консольной сессии"""
        if self.process:
            self.process.terminate()
            self.process = None











router = Router()
console = ShellSession()

@router.message(F.text, Command("console"))
async def console_manegement_start(message: types.Message, state: FSMContext):
    try:
        if str(message.from_user.id) in config["ADMIN"].split(","):
            await state.set_state(state=all.console_state)
            await message.answer("Переход в режим управления консолью")
        else:
            await message.answer("Не админ")
    except Exception as e:
        await message.answer(f"Произошла ошибка 1001: {str(e)}")
        await state.clear()

@router.message(F.text, all.console_state)
async def console_manegement(message: types.Message, state: FSMContext):
    try:
        await message.answer("Начало выполнения команды...")
        result = console.execute_command(message.tex)
        await message.answer("Конец выполнения команды.")
        await message.answer(str(result), parse_mode=types.ParseMode.MARKDOWN)
    except Exception as e:
        await message.answer(f"Произошла ошибка 1002: {str(e)}")
        await state.clear()

@router.message(F.text, Command("exit"), all.console_state)
async def console_manegement_start(message: types.Message, state: FSMContext):
    try:
        await state.set_state(state=all.console_state)
        await message.answer("Переход в обычный режим")
    except Exception as e:
        await message.answer(f"Произошла ошибка 1003: {str(e)}")
        await state.clear()
    




