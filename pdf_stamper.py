from PIL import Image
import fitz  # PyMuPDF
import os
import PySimpleGUI as sg

STAMPS_DIR = os.path.join(os.path.dirname(__file__), "stamps")
STAMPS = {
    "ИГК №00000061630532257265820012": os.path.join(STAMPS_DIR, "stamp0.png"),
    "У меня пока нет других штампов 1": os.path.join(STAMPS_DIR, "red.png"),
    "У меня пока нет других штампов 2": os.path.join(STAMPS_DIR, "black.png"),
}

PLACEMENT_OPTIONS = [
    "Верхний левый угол",
    "Верхний правый угол",
    "Нижний левый угол",
    "Нижний правый угол"
]

layout = [
    [sg.Text('Ваш PDF документ:'),
     sg.InputText(key='-pdf-'),
     sg.FileBrowse("Выбрать")],
    [sg.Text('Выберите штамп:'),
     sg.Combo(list(STAMPS.keys()), default_value=list(STAMPS.keys())[0], key='-stamp_type-')],
    [sg.Text('Размещение штампа:'),
     sg.Combo(PLACEMENT_OPTIONS, default_value=PLACEMENT_OPTIONS[0], key='-placement-')],
    [sg.Submit("Поставить штамп"), sg.Cancel("Закрыть")]
]

window = sg.Window('Наложить штамп', layout, size=(600, 250))

while True:
    event, values = window.read()

    if event in (None, sg.WIN_CLOSED, 'Закрыть'):
        break

    if event == "Поставить штамп":
        stamp_type = values['-stamp_type-']
        stamp_path = STAMPS[stamp_type]
        png = Image.open(stamp_path)
        stamp_width = 28
        stamp_height = 140
        png = png.resize((stamp_width, stamp_height), resample=Image.LANCZOS)

        temp_dir = os.path.join(os.path.dirname(__file__), "temp")
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, "temp_stamp.png")
        png.save(temp_path)

        pdf_path = values['-pdf-']
        pdf = fitz.open(pdf_path)
        page = pdf[0]
        page_rect = page.rect
        page_width = page_rect.width
        page_height = page_rect.height

        placement = values['-placement-']
        w, h = stamp_width, stamp_height  # 28 x 140

        if placement == "Верхний левый угол":
            rect = fitz.Rect(0, 0, w, h)
        elif placement == "Верхний правый угол":
            rect = fitz.Rect(page_width - w, 0, page_width, h)
        elif placement == "Нижний левый угол":
            rect = fitz.Rect(0, page_height - h, w, page_height)
        elif placement == "Нижний правый угол":
            rect = fitz.Rect(page_width - w, page_height - h, page_width, page_height)
        else:
            rect = fitz.Rect(0, 0, w, h)

        page.insert_image(rect, filename=temp_path)

        pdf_name = os.path.basename(pdf_path)
        name_without_ext = os.path.splitext(pdf_name)[0]
        new_pdf_name = f"{name_without_ext}_штамп.pdf"
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        output_path = os.path.join(desktop_path, new_pdf_name)
        pdf.save(output_path)
        pdf.close()

        os.remove(temp_path)

        sg.popup("Готово!",
                 f"Файл сохранён на рабочий стол:\n{output_path}",
                 title="Успешно")

window.close()