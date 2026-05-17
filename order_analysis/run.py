from src.analyzer import OrderAnalyzer

def main():
    """Основная функция для запуска анализа заказов"""
    # Создаём экземпляр анализатора
    analyzer = OrderAnalyzer()

    # Обрабатываем все файлы
    results, processed_count, error_count = analyzer.process_all_files()

    # Выводим итоговую статистику в консоль
    print("\n" + "="*50)
    print("РЕЗУЛЬТАТЫ ОБРАБОТКИ")
    print("="*50)
    print(f"Обработано файлов: {processed_count}")
    print(f"Файлов с ошибками: {error_count}")
    total_files = processed_count + error_count
    print(f"Всего файлов проанализировано: {total_files}")
    print("="*50)

if __name__ == "__main__":
     main()