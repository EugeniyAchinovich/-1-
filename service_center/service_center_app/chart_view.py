import base64
import matplotlib.pyplot as plt

from django.shortcuts import render
from io import BytesIO


def chart_view(request):
    categories = ['Group A', 'Group B', 'Group C']
    values = [23, 30, 18]

    plt.figure(figsize=(10, 5))
    plt.bar(categories, values, color='skyblue')
    plt.title('Распределение показателей по группам')
    plt.xlabel('Группы')
    plt.ylabel('Показатели')

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_png = buf.getvalue()
    buf.close()
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')

    return render(request, 'chart.html', {
        'categories': categories,
        'values': values
    })
