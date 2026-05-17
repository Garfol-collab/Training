import pandas as pd
from pathlib import Path
import logging
from config import (
    DATA_DIR,
    REPORTS_DIR,
    LOGS_DIR,
    STATUS_COLUMN,
    DELIVERED_STATUS,
    TOTAL_AMOUNT_COLUMN,
    OUTPUT_FILE,
    LOG_FILE
)

class OrderAnalyzer:
    def __init__(self):
        """Инициализация системы логирования"""
        self.setup_logging()

    def setup_logging(self):
        """Настройка системы логирования"""
        logs_path = Path(LOGS_DIR)
        self.logger = logging.getLogger('OrderAnalyzer')
        self.logger.setLevel(logging.INFO)

        # Обработчик для файла с ошибками
        log_file_path = logs_path / LOG_FILE
        file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
        file_handler.setLevel(logging.WARNING)

        # Формат вывода для файлового обработчика
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)

        # Обработчик для консоли
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Формат для консольного вывода
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        console_handler.setFormatter(console_formatter)

        # Добавляем обработчики
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)


    def load_file(self, file_path):
        """Загрузка CSV-файла с обработкой ошибок""" 
        try:
            df = pd.read_csv(file_path)
            if df.empty:
                self.logger.warning(f"Файл {file_path} пуст")
                return None
            return df
        except FileNotFoundError:
            self.logger.error(f"Файл не найден: {file_path}")
        except pd.errors.EmptyDataError:
            self.logger.error(f"Файл пуст или имеет неверный формат: {file_path}")
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке файла {file_path}: {e}")
        return None

    def filter_delivered_orders(self, df, file_name):
        """Фильтрация заказов со статусом 'Delivered'"""
        if df is None:
            return None

        try:
            filtered_df = df[df[STATUS_COLUMN] == DELIVERED_STATUS]
            return filtered_df
        except Exception as e:
            self.logger.error(
                f"Ошибка при фильтрации заказов в файле '{file_name}': {str(e)}"
            )
            return None

    def calculate_metrics(self, filtered_df):
        """Расчёт метрик: общая выручка, средний чек, количество заказов"""
        if filtered_df is None or filtered_df.empty:
            return {
                'total_revenue': 0,
                'average_check': 0,
                'order_count': 0
            }

        total_revenue = filtered_df[TOTAL_AMOUNT_COLUMN].sum()
        order_count = len(filtered_df)
        average_check = filtered_df[TOTAL_AMOUNT_COLUMN].mean()

        return {
            'total_revenue': total_revenue,
            'average_check': average_check,
            'order_count': order_count
        }

    def process_single_file(self, file_path):
        """Обработка одного CSV-файла"""
        self.logger.info(f"Начинаем обработку файла: {file_path}")

        # Загрузка данных
        df = self.load_file(file_path)
        if df is None:
            self.logger.error(f"Не удалось загрузить файл: {file_path}")
            return None, False

        file_name = Path(file_path).name

        # Проверяем наличие необходимых колонок
        required_columns = [STATUS_COLUMN, TOTAL_AMOUNT_COLUMN]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            self.logger.error(f"Отсутствуют необходимые колонки: {missing_columns} в файле '{file_name}'")
            return None, False

        # Проверка на нечисловые значения в колонке total_amount
        try:
            df[TOTAL_AMOUNT_COLUMN] = pd.to_numeric(df[TOTAL_AMOUNT_COLUMN], errors='coerce')
            if df[TOTAL_AMOUNT_COLUMN].isna().any():
                non_numeric_count = df[TOTAL_AMOUNT_COLUMN].isna().sum()
                self.logger.error(
                    f"В колонке '{TOTAL_AMOUNT_COLUMN}' обнаружены нечисловые значения "
                    f"(всего: {non_numeric_count}). Файл '{file_name}' будет пропущен."
                )
                return None, False
        except Exception as e:
            self.logger.error(f"Ошибка при преобразовании данных в колонке {TOTAL_AMOUNT_COLUMN} файла '{file_name}': {str(e)}")
            return None, False

        # Фильтрация доставленных заказов 
        filtered_df = self.filter_delivered_orders(df, file_name)
        if filtered_df is None:
            return None, False

        # Расчёт метрик
        metrics = self.calculate_metrics(filtered_df)

        # Формирование результата
        result = {
            'file_name': file_name,
            'total_revenue': metrics['total_revenue'],
            'average_check': metrics['average_check'],
            'order_count': metrics['order_count']
        }

        self.logger.info(
            f"Файл обработан: {file_path}. "
            f"Заказы: {metrics['order_count']}, "
            f"Выручка: {metrics['total_revenue']:.2f}, "
            f"Средний чек: {metrics['average_check']:.2f}"
        )
        return result, True

    def process_all_files(self):
        """Обработка всех CSV-файлов в папке data"""
        results = []
        error_count = 0

        # Поиск всех CSV-файлов в директории
        data_path = Path(DATA_DIR)
        csv_files = list(data_path.glob("*.csv"))

        if not csv_files:
            self.logger.warning("В папке data не найдено CSV-файлов")
            return results, 0, len(csv_files)

        self.logger.info(f"Найдено CSV-файлов для обработки: {len(csv_files)}")

        # Обработка каждого файла
        for file_path in csv_files:
            result, success = self.process_single_file(str(file_path))
            if success:
                results.append(result)
            else:
                error_count += 1

        return results, len(results), error_count

    def save_results(self, results):
        """Сохранение результатов в CSV-файл"""
        if not results:
            self.logger.warning("Нет данных для сохранения")
            return

        reports_path = Path(REPORTS_DIR)

        # Преобразуем результаты в DataFrame
        df_results = pd.DataFrame(results)

        # Сохраняем в CSV
        output_path = reports_path / OUTPUT_FILE
        df_results.to_csv(output_path, index=False, encoding='utf-8')

        self.logger.info(f"Результаты сохранены в: {output_path}")