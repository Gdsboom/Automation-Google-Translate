import time
import psutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
import win32clipboard
import io

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import keyboard
from PIL import ImageGrab, Image

import threading
import base64
import requests
import tempfile
import json

class DuckChat_Tor:
    """
    Класс для работы с браузером.

    Параметры:
    ----------
    tor_browser_path : str
        Путь к исполняемому файлу браузера.
    headless : bool
        Режим работы браузера (без графического интерфейса, если True).
    url : str, optional
        URL-адрес для открытия (например, "https://duckduckgo.com/?q=DuckDuckGo+AI+Chat&ia=chat&duckai=1").
    browser : str
        Название браузера (например, "firefox").
    service : str, optional
        Путь к драйверу браузера (например, "D:/geckodriver.exe").
    """
    def __init__(self, tor_browser_path, headless, url, browser, service, model="GPT-4o"):

        try:
            self.original_clipboard = ImageGrab.grabclipboard()
            print(self.original_clipboard)
        except:
            pass

        self.browser = browser
        self.model = model
        self.headless = headless
        self.tor_browser_path = tor_browser_path  # "D:/Tor Browser/Browser/"
        self.service = service
        self.url = url

        self.local_clipboard = []

        self.original_data = None
        self.original_format = None  # 'text' или 'image'

        self.stop_processing = False

    def inizalization(self):
        try:
            self.__close_tor_browser()
        except:
            pass
        try:
            self.__close_tor_browser()
        except:
            pass


        #profile_dir = self.tor_browser_path+"TorBrowser/Data/Browser/profile.default"

        self.chrome_options = webdriver.ChromeOptions()

        # Установка профиля (для Chrome используется user-data-dir)
        #if profile_dir:
        #    self.chrome_options.add_argument(f"--user-data-dir={profile_dir}")

        # Настройки для скрытия WebDriver и изменения поведения браузера
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option("useAutomationExtension", False)

        # Отключаем WebGL
        self.chrome_options.add_argument("--disable-webgl")
        self.chrome_options.add_argument("--disable-3d-apis")
        self.chrome_options.add_argument("--disable-browser-side-navigation")
        #self.chrome_options.add_argument('--ignore-certificate-errors')
        #self.chrome_options.add_argument('--disable-gpu')


        # Включаем события буфера обмена
        prefs = {
            "profile.default_content_setting_values.clipboard": 1,
            "profile.managed_default_content_settings.clipboard": 1
        }
        self.chrome_options.add_experimental_option("prefs", prefs)

        # Блокировка изображений (раскомментируйте при необходимости)
        # prefs["profile.managed_default_content_settings.images"] = 2
        # prefs["profile.default_content_setting_values.images"] = 2

        # Установка пути к исполняемому файлу браузера
        if self.browser:
            self.chrome_options.binary_location = f"{self.tor_browser_path}/{self.browser}"

        # Настройки User-Agent
        #user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        #self.chrome_options.add_argument(f"user-agent={user_agent}")

        # Параметры приватности
        self.chrome_options.add_argument("--incognito")  # Режим инкогнито
        self.chrome_options.add_argument("--disable-features=TrackingProtection")

        if self.headless:
            #self.chrome_options.add_argument("--headless")
            # если прям очень нужен headless, то пробуем "новый" headless:
            self.chrome_options.add_argument('--headless=new')
            self.chrome_options.add_argument('--disable-gpu')
            self.chrome_options.add_argument('--no-sandbox')
            self.chrome_options.add_argument('--window-size=1920,1080')
            # Отключаем автоматизационные флаги (чтобы сайт не распознал Selenium)
            self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

            # очень важно: эмулируем user-agent настоящего браузера
            self.chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                 'AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/135.0.7049.41 Safari/537.36')
        # Параметры приватности
        self.chrome_options.add_argument("--incognito")  # Режим инкогнито
        self.chrome_options.add_argument("--disable-features=TrackingProtection")
        # Инициализация драйвера Chrome
        self.driver = webdriver.Chrome(service=ChromeService(self.service), options=self.chrome_options)
        while True:
            # Ожидание появления элемента <head>
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "head"))
                )
                # Проверка, что <head> пустой
                head_content = self.driver.execute_script("return document.head.innerHTML;")
                if not head_content.strip():  # Проверяем, что содержимое пустое
                    break
                else:
                    pass
                    #print("<head> элемент не пуст:", head_content)
            except Exception as e:
                pass
                #print(f"Ошибка при ожидании <head>: {e}")

            # Ожидание появления элемента <body>
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                # Проверка, что <body> пустой
                body_content = self.driver.execute_script("return document.body.innerHTML;")
                if not body_content.strip():  # Проверяем, что содержимое пустое
                    break
                else:
                    pass
                    #print("<body> элемент не пуст:", body_content)
            except Exception as e:
                pass
                #print(f"Ошибка при ожидании <body>: {e}")

        # print("Произошла ошибка ожидания:", e)
        # Ожидание полной загрузки страницы
        WebDriverWait(self.driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        # Открываем сайт
        self.driver.get(self.url)
        self.wait_page()

    def wait_page(self):
        while True:
            try:
                WebDriverWait(self.driver, 10).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                return
            except:
                pass

    def get_next_filename(self, extension='png'):
        """Генерирует следующее имя файла, проверяя существующие файлы."""
        i = 1
        while True:
            #filename = f"{base_name}_{i}.{extension}"
            filename = f"{i}.{extension}"
            if not os.path.exists(filename):
                return filename
            i += 1

    def save_to_local_clipboard(self, pil_image):
        """Сохраняет изображение в локальный буфер (не трогает системный)"""
        self.local_clipboard.append(pil_image)

    def get_image(self):
        #print("1!")
        wait_time = 20
        start_time = time.time()
        while True:
            # Попробуем получить изображение из буфера обмена
            try:
                image = ImageGrab.grabclipboard()
                if isinstance(image, ImageGrab.Image.Image) and self.original_clipboard != image:  # Проверяем, что это изображение



                    #filename = self.get_next_filename()  # Получаем следующее имя файла
                    #image.save(filename)  # Укажите полный путь, если нужно сохранить в другой директории
                    #print(f"Скриншот сохранен как {filename}")

                    self.original_clipboard = image
                    #print("2!")
                    self.save_to_local_clipboard(image)
                    break
                else:
                    pass
                    #print("В буфере обмена нет изображения.")
            except Exception as e:
                print(f"Ошибка: {e}")
            ''''''
            if time.time() - start_time > wait_time:
                print("Время вышло")
                break




    def set_image(self):
        while True:
            if len(self.local_clipboard) > 0:
                # Задержка перед выполнением (если нужно)
                self.inizalization()
                #self.__agree()
                try:
                    self.send_image_to_page(0) #self.original_clipboard
                except:
                    pass
                time.sleep(1)
                self.local_clipboard.pop(0)
                print("Браузер закрыт")
                self.__close_tor_browser()


    def __agree(self):
        self.wait_page()
        try:
            # Локатор кнопки (например, по атрибуту aria-label)
            button_locator = (By.CSS_SELECTOR, 'button[aria-label="Reject all"]')

            # Ждём, пока кнопка станет включённой (атрибут 'disabled' исчезнет)
            buttons = WebDriverWait(self.driver, 20).until(
                lambda d: [btn for btn in d.find_elements(*button_locator) if
                           "Reject all" in btn.text]
            )

            if buttons:
                for button in buttons:
                    button.click()  # Нажимаем на каждую доступную кнопку
                    # print("Кнопка нажата.")
            else:
                pass
                # print("Кнопка не найдена или не доступна для нажатия.")

        except Exception as e:
            print("Произошла ошибка в согласии:", e)

    def _open_clipboard(self, max_retries=5):
        """Пытается открыть буфер обмена с обработкой блокировок"""
        for _ in range(max_retries):
            try:
                win32clipboard.OpenClipboard()
                return True
            except Exception as e:
                #time.sleep(delay)
                pass
        return False

    def safe_close_clipboard(self):
        try:
            win32clipboard.CloseClipboard()
        except Exception:
            pass

    def save_clipboard(self):
        """Сохраняет текущее содержимое буфера"""
        self.original_data = None
        self.original_format = None

        if not self._open_clipboard():
            print("Не удалось открыть буфер для сохранения")
            return
        try:
            data = ImageGrab.grabclipboard()
            if data is None:
                # Работаем с текстом
                try:
                    text_data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
                    self.original_format = 'text'
                    self.original_data = text_data
                except Exception as ex:
                    print("Ошибка при получении текста:", ex)
            else:
                # Обработка изображений: ImageGrab может вернуть как одиночное изображение, так и список:
                if isinstance(data, list):
                    # Если возвращается список изображений, берем первое (или же можно сохранить весь список)
                    self.original_data = data[0]
                else:
                    self.original_data = data
                self.original_format = 'image'

        except Exception as e:
            print(f"Ошибка сохранения буфера: {e}")
            self.original_format = None
            self.original_data = None

    def set_to_clipboard(self, content):
        """Устанавливает новое содержимое в буфер"""
        try:
            if not self._open_clipboard():
                print("Не удалось открыть буфер для установки")
                return

            win32clipboard.EmptyClipboard()

            if isinstance(content, str):
                win32clipboard.SetClipboardText(content, win32clipboard.CF_UNICODETEXT)
            elif isinstance(content, Image.Image):
                output = io.BytesIO()
                # Сохранение BMP; обратите внимание, что BMP формируется с заголовком,
                # и CF_DIB ожидает DIB (без BITMAPFILEHEADER)
                content.convert("RGB").save(output, "BMP")
                data = output.getvalue()[14:]  # Отбрасываем первые 14 байт заголовка BMP
                win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            else:
                print("Неподдерживаемый тип данных для буфера обмена")
        except Exception as e:
            print(f"Ошибка установки: {e}")
        finally:
            self.safe_close_clipboard()

    def restore_clipboard(self):
        """Восстанавливает оригинальное содержимое"""
        try:
            if not self._open_clipboard():
                print("Не удалось открыть буфер для восстановления")
                return

            win32clipboard.EmptyClipboard()

            if self.original_format == 'text' and self.original_data:
                win32clipboard.SetClipboardText(self.original_data, win32clipboard.CF_UNICODETEXT)
            elif self.original_format == 'image' and self.original_data:
                output = io.BytesIO()
                self.original_data.convert("RGB").save(output, "BMP")
                data = output.getvalue()[14:]
                win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            else:
                print("Нет данных для восстановления")
        except Exception as e:
            print(f"Ошибка восстановления: {e}")
        finally:
            self.safe_close_clipboard()

    def download_and_open_image(self):

        try:
            print("Начало процесса загрузки изображений.")

            # Ожидание загрузки страницы
            self.wait_page()
            #time.sleep(10)
            #print("YES1")
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            #print("YES2")
            # Находим все изображения на странице
            #img_elements = self.driver.find_elements(By.CSS_SELECTOR, 'img[loading="lazy"]')

            # Ожидаем, пока все изображения с атрибутом "loading=lazy" станут видимыми
            img_elements = WebDriverWait(self.driver, 30).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'img[loading="lazy"]'))
            )
            #print("YES3")
            if not img_elements:
                print("Изображения не найдены.")
                return
            #print("YES4")
            #print(f"Найдено {len(img_elements)} изображений.")

            for img_element in img_elements:
                # Проверяем, что изображение загружено
                is_complete = self.driver.execute_script(
                    "return arguments[0].complete && arguments[0].naturalWidth > 0", img_element)

                if not is_complete:
                    print("Изображение не полностью загружено, пропускаем.")
                    continue

                #print("Изображение найдено и полностью загружено.")

                # Получаем атрибут src
                img_src = img_element.get_attribute("src")

                if img_src.startswith("blob:"):
                    # JavaScript для преобразования blob в data URL
                    script = """
                                var img = arguments[0];
                                var canvas = document.createElement('canvas');
                                canvas.width = img.naturalWidth;
                                canvas.height = img.naturalHeight;
                                var ctx = canvas.getContext('2d');
                                ctx.drawImage(img, 0, 0);
                                return canvas.toDataURL('image/png').split(',')[1];
                                """
                    img_base64 = self.driver.execute_script(script, img_element)
                    img_data = io.BytesIO(base64.b64decode(img_base64))
                    img = Image.open(img_data)
                else:
                    img = Image.open(io.BytesIO(requests.get(img_src).content))

                # Сохраняем изображение во временный файл
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
                    img.save(temp_file, format="PNG")
                    temp_file_path = temp_file.name

                print(f"Изображение сохранено во временный файл в папке Temp: {temp_file_path}")

                # Открываем изображение с помощью стандартной программы просмотра
                os.startfile(temp_file_path)

                #print("Изображение открыто в стандартной программе просмотра.")

        except Exception as e:
            print(f"Ошибка: {e}")
            # Экстренный скриншот всей страницы для диагностики


            html = self.driver.page_source
            print(html)
            self.driver.save_screenshot("debug_screenshot.png")
            print("Скриншот страницы сохранён как debug_screenshot.png")

    def convert_png_to_dib(self, file_path) -> bytes:
        """Конвертирует изображение PNG в формат DIB (используемый в буфере обмена)"""
        output = io.BytesIO()
        try:
            with open(file_path, "rb") as f:
                image = Image.open(f)
                #print(110)
                # Проверим размер изображения
                #print(f"Размер изображения: {image.size}")

                # Убедимся, что изображение не имеет альфа-канала
                if image.mode == "RGBA":
                    image = image.convert("RGB")

                # Преобразуем изображение в формат BMP
                image.convert("RGB").save(output, "BMP")
                #print(120)

                # Получаем данные BMP
                bmp_data = output.getvalue()
                #print(130)

                # DIB данные начинаются с 14 байт (заголовок BMP), нужно их отбросить
                dib_data = bmp_data[14:]
                #print(140)

                return dib_data
        except Exception as e:
            print(f"Ошибка при конвертации изображения: {e}")
            return None

    def emulate_drag_and_drop(self, driver, file_path, drop_target_selector):
        try:
            # Подготовка данных файла
            file_name = os.path.basename(file_path)
            with open(file_path, 'rb') as f:
                file_content = f.read()

            # Экранируем специальные символы в селекторе
            safe_selector = json.dumps(drop_target_selector)[1:-1]

            # JavaScript с абсолютно правильным синтаксисом
            script = """
                // Функция для создания файла
                function createFile(name, content) {
                    const array = new Uint8Array(content);
                    return new File([array], name, { type: 'image/png' });
                }

                // Получаем целевой элемент
                const selector = "%s";
                const target = document.querySelector(selector);
                if (!target) {
                    throw new Error('Element not found: ' + selector);
                }

                // Создаем DataTransfer
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(createFile("%s", new Uint8Array(%s)));

                // Получаем координаты
                const rect = target.getBoundingClientRect();
                const clientX = rect.left + rect.width/2;
                const clientY = rect.top + rect.height/2;

                // Генерируем события
                function dispatchDragEvent(type) {
                    const event = new DragEvent(type, {
                        bubbles: true,
                        cancelable: true,
                        view: window,
                        clientX: clientX,
                        clientY: clientY,
                        dataTransfer: dataTransfer
                    });
                    target.dispatchEvent(event);
                }

                // Последовательность событий
                dispatchDragEvent('dragenter');
                dispatchDragEvent('dragover');
                dispatchDragEvent('drop');
                """ % (
                safe_selector,
                file_name.replace('"', '\\"'),
                list(file_content)
            )

            # Выполняем скрипт
            driver.execute_script(script)
            time.sleep(1)

            #print(f"Файл {file_name} успешно передан")
            return True

        except Exception as e:
            print(f"Ошибка: {str(e)}")
            return False

    def save_clipboard_image_to_temp(self, pil_image):
        """
            Сохраняет PIL.Image во временный файл PNG и возвращает путь к нему.

            :param pil_image: Объект PIL.Image (например, из ImageGrab.grabclipboard())
            :return: Путь к временному файлу
            """
        if not isinstance(pil_image, Image.Image):
            raise TypeError("Ожидается объект PIL.Image!")

        # Создаем временный файл с расширением .png
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
            temp_path = temp_file.name

        # Сохраняем изображение в файл
        pil_image.save(temp_path, format="PNG")

        return temp_path

    def send_image_to_page(self, image_index=0):

        """Отправляет изображение из локального буфера на страницу"""
        if not self.local_clipboard:
            raise ValueError("Локальный буфер пуст")

        pil_image = self.local_clipboard[image_index]

        # Конвертируем в base64
        #buffered = io.BytesIO()
        #pil_image.save(buffered, format="PNG")
        #img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

        '''
        # JavaScript для вставки
        js = """
        // Создаем input элемент
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/png';
        input.style.display = 'none';
        
        // Конвертируем base64 в файл
        const byteChars = atob('%s');
        const byteNumbers = new Array(byteChars.length);
        for (let i = 0; i < byteChars.length; i++) {
            byteNumbers[i] = byteChars.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], {type: 'image/png'});
        const file = new File([blob], 'image.png', {type: 'image/png'});
        
        // Создаем DataTransfer
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        input.files = dataTransfer.files;
        
        // Триггерим событие
        document.body.appendChild(input);
        const changeEvent = new Event('change', {bubbles: true});
        input.dispatchEvent(changeEvent);
        setTimeout(() => input.remove(), 500);
        """ % img_base64
        '''

        # Сохраняем оригинальное содержимое буфера
        #self.save_clipboard()
        # Устанавливаем новый образ (изображение)
        #self.set_to_clipboard(pil_image)

        #print( ImageGrab.grabclipboard() )

        # Нажимаем на поле для вставки
        #self.driver.find_element(By.CSS_SELECTOR, 'button[jsname="xcJrbc"]').click()
        #time.sleep(5)

        self.emulate_drag_and_drop(self.driver,
                                   self.save_clipboard_image_to_temp(pil_image),
                                   'div[class="rlWbvd"]')

        #self.emulate_drag_and_drop(self.driver, "D:/русификатор/Библиотеки/Библиотека перевод картинок/pythonProject/2.png", 'div[class="rlWbvd"]')

        '''
        # Локатор кнопки (например, по атрибуту aria-label)
        button_locator = (By.CSS_SELECTOR, 'button[jsname="xcJrbc"]')

        # Ждём, пока кнопка станет включённой (атрибут 'disabled' исчезнет)
        buttons = WebDriverWait(self.driver, 20).until(
            lambda d: [btn for btn in d.find_elements(*button_locator) if
                       "Вставить изображение из буфера обмена" in btn.get_attribute("aria-label")]
        )
        print( "Buttons найдено:", len(buttons) )
        if buttons:
            for button in buttons:
                button.click()  # Нажимаем на каждую доступную кнопку
                # print("Кнопка нажата.")
        else:
            pass
        '''

        self.wait_page()

        # Всегда восстанавливаем
        #self.restore_clipboard()



        self.download_and_open_image()

        # Выполняем вставку
        #self.driver.execute_script(js)


        '''
        """Отправляет изображение из локального буфера на страницу"""
        if not self.local_clipboard:
            raise ValueError("Локальный буфер пуст")

        pil_image = self.local_clipboard[image_index]

        # Конвертируем в base64
        buffered = io.BytesIO()
        pil_image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

        # JavaScript для вставки
        js = """
        // Создаем input элемент
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/png';
        input.style.display = 'none';
        
        // Конвертируем base64 в файл
        const byteChars = atob('%s');
        const byteNumbers = new Array(byteChars.length);
        for (let i = 0; i < byteChars.length; i++) {
            byteNumbers[i] = byteChars.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], {type: 'image/png'});
        const file = new File([blob], 'image.png', {type: 'image/png'});
        
        // Создаем DataTransfer
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        input.files = dataTransfer.files;
        
        // Триггерим событие
        document.body.appendChild(input);
        const changeEvent = new Event('change', {bubbles: true});
        input.dispatchEvent(changeEvent);
        setTimeout(() => input.remove(), 500);
        """ % img_base64

        # Кликаем на поле ввода
        self.driver.find_element(By.XPATH, '//button[@jsname="xcJrbc"]').click()
        time.sleep(0.5)

        # Выполняем вставку
        self.driver.execute_script(js)
        '''



    def __close_tor_browser(self):
        """Закрывает все экземпляры Tor Browser."""
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == self.browser or proc.info['name'] == "chromedriver.exe":  # Убедитесь, что имя процесса соответствует вашему Tor Browser
                try:
                    # Завершаем дочерние процессы
                    children = proc.children(recursive=True)
                    for child in children:
                        child.kill()  # или child.kill() для принудительного завершения

                    # Завершаем родительский процесс
                    proc.kill()  # или proc.kill() для принудительного завершения
                    # print(f"Процесс {proc.info['pid']} и его дочерние процессы успешно завершены.")
                except psutil.NoSuchProcess:
                    #pass
                    print(f"Процесс {proc.info['pid']} не найден.")
                except psutil.AccessDenied:
                    #pass
                    print(f"Нет доступа к процессу {proc.info['pid']}.")
                except Exception as e:
                    #pass
                    print(f"Ошибка при завершении процесса {proc.info['pid']}: {e}")
        try:
            self.__close_tor_browser()
        except:
            pass


    def __del__(self):
        try:
            self.driver.quit()
        except:
            pass
        try:
            self.__close_tor_browser()
        except:
            pass
        self.driver = None

'''
    def drag_and_drop_real_file(self, driver, file_input_xpath, region_xpath, file_path):
        """Эмулирует перетаскивание реального файла через Selenium"""

        # Находим инпут для загрузки файлов (обычно он скрытый)
        file_input = driver.find_element(By.XPATH, file_input_xpath)
        driver.execute_script("arguments[0].style.display = 'block';", file_input)  # Открываем скрытый input

        # Загружаем файл через input (это более надежно, чем drag_and_drop)
        file_input.send_keys(file_path)
        print(f"Файл {file_path} загружен через input!")

        time.sleep(1)  # Даем сайту обработать загрузку

        # Имитация перетаскивания файла (если сайт требует drag'n'drop)
        region = driver.find_element(By.XPATH, region_xpath)
        actions = ActionChains(driver)
        actions.click_and_hold(file_input).move_to_element(region).release().perform()

        print("Файл успешно перетащен в поле загрузки!")
        time.sleep(2)
'''



'''
    def send_image_to_page(self, pil_image):
        self.wait_page()
        # Путь к файлу, который вы хотите загрузить
        file_path = "C:/Users/Tolik/Pictures/1.png"  # Замените на путь к вашему файлу

        # Найдите элемент "Выбрать файл" (input type="file")
        #upload_element = self.driver.find_element(By.XPATH, '//input[@type="file"]')  # Замените на правильный XPATH
        #upload_element = self.driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Browse your files"]')



        wait_time = 5
        start_time = time.time()
        while True:
            # Попробуем получить изображение из буфера обмена
            try:
                # Ожидаем кнопку с таймаутом
                try:
                    WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//button[@aria-label="Paste an image from clipboard"]'))
                    )
                except:
                    #print("Кнопка не найдена на странице")
                    self.driver.quit()
                    exit()

                pil_image = Image.open(file_path)
                if pil_image:
                    # Проверка что изображение существует
                    if pil_image is None:
                        raise ValueError("PIL image cannot be None")

                    try:
                        # Конвертируем PIL Image в base64
                        img_byte_arr = BytesIO()
                        pil_image.save(img_byte_arr, format='PNG')
                        image_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

                        # JavaScript для вставки
                        js = """
                            // Создаем временный элемент для вставки
                            const tempElem = document.createElement('div');
                            tempElem.contentEditable = true;
                            tempElem.style.position = 'fixed';
                            tempElem.style.left = '-9999px';
                            document.body.appendChild(tempElem);
                            tempElem.focus();

                            // Вставляем изображение
                            const img = document.createElement('img');
                            img.src = 'data:image/png;base64,%s';
                            tempElem.appendChild(img);

                            // Выделяем изображение
                            const range = document.createRange();
                            range.selectNodeContents(tempElem);
                            const selection = window.getSelection();
                            selection.removeAllRanges();
                            selection.addRange(range);

                            // Копируем в буфер обмена
                            document.execCommand('copy');

                            // Удаляем временный элемент
                            document.body.removeChild(tempElem);

                            // Находим кнопку вставки и кликаем
                            const pasteBtn = document.querySelector('button[aria-label="Paste an image from clipboard"]');
                            pasteBtn.click();
                            """ % image_base64
                        self.driver.execute_script(js)

                    except AttributeError as e:
                        print(f"Ошибка: {e}. Проверьте что передаете корректный объект PIL.Image")
                    except Exception as e:
                        print(f"Неожиданная ошибка: {e}")
                else:
                    print("Не удалось загрузить изображение")

            except Exception as e:
                print(f"Ошибка: {e}")
            if time.time() - start_time > wait_time:
                print("Время вышло")
                break
            """
                            file_input = WebDriverWait(self.driver, 10).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]'))
                            )
                            file_input.send_keys(file_path)

                            # Находим кнопку
                            upload_element = self.driver.find_element(By.CSS_SELECTOR, 'button[jsname="DagSrd"]')
                            self.driver.execute_script("arguments[0].click();", upload_element)

                            # Ждём появление input type="file"
                            file_input = WebDriverWait(self.driver, 10).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
                            )

                            # Отправляем файл
                            file_input.send_keys(file_path)
                            """

        # Если нужно, можно добавить дополнительные действия, например, нажать кнопку "Отправить"
        # submit_button = driver.find_element(By.XPATH, 'XPATH_КНОПКИ_ОТПРАВИТЬ')
        # submit_button.click()

        time.sleep(60)  # Ждем, чтобы увидеть результат
        self.driver.quit()

        pass
    '''
if __name__ == "__main__":


    start_time = time.time()
    DT = DuckChat_Tor("C:/Program Files/Google/Chrome/Application/", True, "https://translate.google.com/?sl=auto&tl=ru&op=images", browser="chrome.exe",
                      service="D:/chromedriver.exe", model="GPT-4o")

    try:
        # Обработка Print Screen
        keyboard.on_press_key('print screen', lambda _: DT.get_image())
    except Exception as e:
        #pass
        print(f"Ошибка при обработке: {e}")
    set_thread = threading.Thread(target=DT.set_image())
    set_thread.daemon = True
    set_thread.start()
    # Обработка Win+Shift+S
    #keyboard.on_press_key('win+shift+s', run_get_image)

    # Отслеживание нажатия клавиши Print Screen
    #keyboard.on_press_key('print screen', lambda _: DT.get_image())



    keyboard.wait('esc')  # Ожидание нажатия клавиши ESC для выхода

    DT.stop_processing = True
    #set_thread.join()  # ждем завершения цикла
    #print(proverka.test("да", headless = False))
    print("Прога завершила работу, Time общее:", time.time() - start_time)
