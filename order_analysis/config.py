from pathlib import Path

# Пути проекта
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"

# Настройки для обработки данных
STATUS_COLUMN = 'status'
DELIVERED_STATUS = 'Delivered'
TOTAL_AMOUNT_COLUMN = 'total_amount'

# Имена выходных файлов
OUTPUT_FILE = 'summary_report.csv'
LOG_FILE = 'errors.log'
