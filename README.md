Генератор файлов для Embox через STM32CubeMX. Для работы необходимо:
* скачать STM32CubeMX здесь: https://www.st.com/en/development-tools/stm32cubemx.html
* сам проект ОС https://github.com/embox/embox

ОСТОРОЖНО! ГЛЮЧНЫЙ И СЫРОЙ ПРОДУКТ!
-----------------
* Проверить сборки для проектов stm32f103
* Проверить сборки для проектов stm32f745
* 

Алгоритм:
-------------------
* Выбираем процессор через MCU selector
* Включаем необходимые интерфейсы, например, SPI1
* Сохраняем файл в папку board_projects , чтобы файл board_name сохранился по пути board_projects/board_name/board_name.ioc
* Настраиваем часы 
* В Project Manager
* В подпапке Project
* Выбираем Toolchain / IDE : Makefile
* В подпапке Code Generator
* Выбираем галку на Generate peripheral initialization as a pair ...
* Проверяем, что выбрано Copy only the necessary library files
* В подпапке Advanced settings 
* Выбираем для генерации тип LL
* В папке platform создадутся необходимые файлы

Проверенные интерфейсы:
-------------------
* SPI full duplex dma
* SPI half duplex
