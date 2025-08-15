from django.shortcuts import render
import requests
from django.conf import settings
# Create your views here.
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import json
import requests
from datetime import datetime
from collections import Counter

def parse_fecha(fecha):
    try:
        return datetime.fromisoformat(fecha.replace('Z', '+00:00'))
    except Exception:
        return None


@login_required
def index(request):
    response = requests.get(settings.API_URL)
    posts = response.json()
    # Adaptar a la nueva API: se asume que la respuesta es una lista de dicts con campos 'id', 'frase', 'usuario', etc.
    # La API devuelve un dict cuyas claves son IDs y los valores son los datos
    data_dict = posts if isinstance(posts, dict) else {}
    registros = list(data_dict.values())
    total_mensajes = len(registros)

    # Programa más popular
    
    programas = [r.get('programa', 'N/A') for r in registros if 'programa' in r]
    programa_popular = Counter(programas).most_common(1)[0][0] if programas else 'N/A'

    # Estado de los mensajes (pendiente, respondido, etc.)
    estados = [r.get('estado', 'N/A') for r in registros if 'estado' in r]
    estado_conteo = Counter(estados)
    estado_mas_frecuente = estado_conteo.most_common(1)[0][0] if estados else 'N/A'
    cantidad_estado_mas_frecuente = estado_conteo.most_common(1)[0][1] if estados else 0

    # Usuario más activo (por email)
    emails = [r.get('email', 'N/A') for r in registros if 'email' in r]
    usuario_mas_activo = Counter(emails).most_common(1)[0][0] if emails else 'N/A'

    # Mensaje más reciente
    
    mensajes_con_fecha = [(r.get('mensaje', ''), parse_fecha(r.get('fechaEnvio', ''))) for r in registros if 'fechaEnvio' in r]

    # Promedio de longitud de mensaje
    longitudes = [len(r.get('mensaje', '')) for r in registros if 'mensaje' in r]
    promedio_longitud = round(sum(longitudes) / len(longitudes), 2) if longitudes else 0

    # Día con más mensajes
    fechas = [parse_fecha(r.get('fechaEnvio', '')) for r in registros if 'fechaEnvio' in r]
    dias = [f.date().isoformat() for f in fechas if f]
    dia_mas_mensajes = Counter(dias).most_common(1)[0][0] if dias else 'N/A'

    indicadores = [
        {
            'label': 'Total de mensajes',
            'titulo': 'Mensajes recibidos',
            'valor': total_mensajes,
            'icon': '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path d="M2 5a2 2 0 012-2h12a2 2 0 012 2v10a2 2 0 01-2 2H4a2 2 0 01-2-2V5zm2 0v10h12V5H4zm2 2h8v2H6V7z"/></svg>',
            'icon_color': 'text-orange-500',
            'icon_bg': 'bg-orange-100',
            'icon_dark_color': 'dark:text-orange-100',
            'icon_dark_bg': 'dark:bg-orange-500',
        },
        {
            'label': 'Programa más popular',
            'titulo': 'Programa top',
            'valor': programa_popular,
            'icon': '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path d="M10 2a8 8 0 100 16 8 8 0 000-16zm1 12.93V17h-2v-2.07A6.002 6.002 0 014 11h2a4 4 0 008 0h2a6.002 6.002 0 01-5 3.93z"/></svg>',
            'icon_color': 'text-green-500',
            'icon_bg': 'bg-green-100',
            'icon_dark_color': 'dark:text-green-100',
            'icon_dark_bg': 'dark:bg-green-500',
        },
        {
            'label': f"Mensajes '{estado_mas_frecuente}'", # Estado más frecuente
            'titulo': f"{estado_mas_frecuente.capitalize()}s",
            'valor': cantidad_estado_mas_frecuente,
            'icon': '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path d="M9 12h2v2H9v-2zm0-8h2v6H9V4zm1-2a9 9 0 100 18 9 9 0 000-18z"/></svg>',
            'icon_color': 'text-blue-500',
            'icon_bg': 'bg-blue-100',
            'icon_dark_color': 'dark:text-blue-100',
            'icon_dark_bg': 'dark:bg-blue-500',
        },
        {
            'label': 'Promedio longitud',
            'titulo': 'Longitud mensaje',
            'valor': promedio_longitud,
            'icon': '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><circle cx="10" cy="10" r="8"/><text x="10" y="15" font-size="8" text-anchor="middle" fill="#fff">Σ</text></svg>',
            'icon_color': 'text-yellow-500',
            'icon_bg': 'bg-yellow-100',
            'icon_dark_color': 'dark:text-yellow-100',
            'icon_dark_bg': 'dark:bg-yellow-500',
        },
        {
            'label': 'Día con más mensajes',
            'titulo': 'Día top',
            'valor': dia_mas_mensajes,
            'icon': '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><rect x="3" y="4" width="14" height="12" rx="2"/><rect x="7" y="2" width="6" height="2" rx="1"/></svg>',
            'icon_color': 'text-indigo-500',
            'icon_bg': 'bg-indigo-100',
            'icon_dark_color': 'dark:text-indigo-100',
            'icon_dark_bg': 'dark:bg-indigo-500',
        },
    ]

    # Tabla de mensajes (puedes personalizar las columnas)
    tabla = [
        {
            'valor1': r.get('nombre', ''),
            'valor2': r.get('email', ''),
            'valor3': r.get('programa', ''),
            'valor4': r.get('mensaje', ''),
            'valor5': r.get('fechaEnvio', ''),
        }
        for r in registros[:10]
    ]

    # Datos para el gráfico: cantidad de mensajes por programa (top 5)
    top_programas = Counter([r.get('programa', 'N/A') for r in registros if 'programa' in r]).most_common(5)
    chart_labels = [p[0] for p in top_programas]

    # Promedio de longitud de mensaje por programa (solo para los top 5)
    promedio_longitud_por_programa = []
    for programa in chart_labels:
        mensajes = [r.get('mensaje', '') for r in registros if r.get('programa', 'N/A') == programa]
        longitudes = [len(m) for m in mensajes if m]
        promedio = round(sum(longitudes) / len(longitudes), 2) if longitudes else 0
        promedio_longitud_por_programa.append(promedio)

    chart_datasets = [
        {
            'label': 'Mensajes por programa',
            'backgroundColor': '#0694a2',
            'borderColor': '#0694a2',
            'data': [p[1] for p in top_programas],
            'fill': False,
        },
        {
            'label': 'Promedio longitud de mensaje',
            'backgroundColor': '#7e3af2',
            'borderColor': '#7e3af2',
            'data': promedio_longitud_por_programa,
            'fill': False,
        }
    ]

    
    data = {
        'title': "Landing Page Dashboard",
        'indicadores': indicadores,
        'tabla': tabla,
        'chart_title': 'Evolución de respuestas',
        'chart_labels': json.dumps(chart_labels),
        'chart_datasets': json.dumps(chart_datasets),
    }
    return render(request, "dashboard/index.html", data)