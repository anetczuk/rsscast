#!/usr/bin/python3
#
# MIT License
#
# Copyright (c) 2021 Arkadiusz Netczuk <dev.arnet@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

try:
    ## following import success only when file is directly executed from command line
    ## otherwise will throw exception when executing as parameter for "python -m"
    # pylint: disable=W0611
    import __init__
except ImportError:
    ## when import fails then it means that the script was executed indirectly
    ## in this case __init__ is already loaded
    pass

import sys
import json

from rsscast import logger
from rsscast.source.youtube.ytconverter import convert_to_audio, parse_playlist
from rsscast.rss.rsschannel import RSSChannel


def get_json(obj):
    return json.loads(
        json.dumps(obj, default=lambda o: getattr(o, '__dict__', str(o)))
    )


def test_convert_to_audio():
    converted = convert_to_audio( "https://www.youtube.com/watch?v=BLRUiVXeZKU", "/tmp/yt_example.mp3" )

    ## long file: 3h 58m
    # converted = convert_to_audio( "https://www.youtube.com/watch?v=C9HrMN9BjfY", "/tmp/yt_example.mp3" )

    # converted = convert_to_audio( "https://www.youtube.com/watch?v=cJuO985zF8E", "/tmp/yt_example.mp3" )

    print("converted:", converted)
    if not converted:
        sys.exit(1)


def test_parse_playlist():
    # ## playlist - gwiazdowski
    # url = "https://www.youtube.com/playlist?list=PLC9xjKm8G0LpgFgi-eF4YgvtMuogd1dHw"
    # info_dict = fetch_info(url, items_num=999999)
    # info_dict["entries"] = "xxx"
    # pprint.pprint( info_dict )
    # return

    ## playlist - youtube latino
    url = "https://www.youtube.com/playlist?list=PL1ebpFrA3ctH0QN6bribofTNpG4z2loWy"
    known = ["https://www.youtube.com/watch?v=aAbfzUJLJJE", "https://www.youtube.com/watch?v=3Q1DIHK2AIw"]

    channel_data: RSSChannel = parse_playlist(url, known)
    channel_data.sort()
    print("playlist case found items:", channel_data.size())

    if channel_data.size() < 1:
        sys.exit(1)

    ret_dict = get_json(channel_data)
    expected = {'items': [
                           {'enabled': True,
                            'id': 'yt:video:xxkpIbP6iEQ',
                            'link': 'https://www.youtube.com/watch?v=xxkpIbP6iEQ',
                            'mediaSize': -1,
                            'publishDate': '2021-06-28 00:00:00+00:00',
                            'summary': 'Aquí les dejo el video con el doctor Ricardo Cortés en '
                                       'donde nos va a resolver algunas de nuestras dudas '
                                       'sobre el COVID19.\n'
                                       '\n'
                                       'El doctor Ricardo es Titular de la Direction general '
                                       'de promotion de la salud.',
                            'thumb_height': None,
                            'thumb_url': 'https://i.ytimg.com/vi_webp/xxkpIbP6iEQ/maxresdefault.webp',
                            'thumb_width': None,
                            'title': 'El Dr. Ricardo Cortés resuelve nuestras dudas sobre el '
                                     'COVID-19'},
                           {'enabled': True,
                            'id': 'yt:video:jWKe98MURcw',
                            'link': 'https://www.youtube.com/watch?v=jWKe98MURcw',
                            'mediaSize': -1,
                            'publishDate': '2021-06-30 00:00:00+00:00',
                            'summary': 'Hola amigos, yo soy la Dra. Pau Zúñiga y el día de hoy '
                                       'les preparé un video muy interesante en colaboración '
                                       'con el Dr. Ricardo Cortés Médico Epidemiólogo, juntos '
                                       'responderemos las dudas más frecuentes sobre COVID-19 '
                                       'y así como las dudas que han surgido respecto a las '
                                       'vacunas.\n'
                                       '\n'
                                       'En este video responderemos preguntas acerca de la '
                                       'nueva variante Delta, qué tan efectivas son la vacunas '
                                       'y si nos protegen contra esta nueva variante, por qué '
                                       'algunas personas a pesar de contar con el esquema '
                                       'completo de vacunación pueden enfermar y morir, '
                                       'desmentimos también mitos que han ganado popularidad '
                                       'en las últimas semanas tales como el por qué a las '
                                       'personas aparentemente se les pueden pegar objetos '
                                       'metálicos en la piel después de la vacuna, entre otras '
                                       'cosas.\n'
                                       '\n'
                                       'Espero que la información les sea de utilidad y '
                                       'cualquier duda que tengan por favor déjenme en los '
                                       'comentarios, les estaré respondiendo.\n'
                                       '\n'
                                       'No olviden compartir el video con sus familiares y '
                                       'amigos.\n'
                                       '\n'
                                       'Los quiero mucho 👩🏻\u200d⚕️💕\n'
                                       '\n'
                                       '\u200b#DraPauZuñiga\u200b\u200b\u200b\u200b '
                                       '#PauZuñiga\u200b\u200b\u200b #Vacunación\n'
                                       '\n'
                                       '0:00 Intro\n'
                                       '\n'
                                       '02:44 ¿Cuál es la mejor vacuna contra COVID?\n'
                                       '\n'
                                       '03:52 ¿Las vacunas contra COVID-19 son seguras pese a '
                                       'haber sido desarrolladas en un periodo corto a '
                                       'comparación de otras vacunas?\n'
                                       '\n'
                                       '6:07 ¿Es mejor la inmunidad que se obtiene después de '
                                       'contagiarse o la que se obtiene al vacunarse?\n'
                                       '\n'
                                       '9:52 ¿Existe riesgo de presentar trombosis después de '
                                       'aplicar la vacuna?\n'
                                       '\n'
                                       '13:08 ¿Existe riesgo de enfermarse para quienes ya '
                                       'tienen el esquema de vacunación completo?\n'
                                       '\n'
                                       '17:25 ¿Cuánto tiempo después de haberme vacunado puedo '
                                       'considerar que estoy protegido?\n'
                                       '\n'
                                       '20:33 ¿Existen remedio caseros que sean efectivos '
                                       'contra el COVID-19?\n'
                                       '\n'
                                       '21:27 ¿Cuáles son las principales secuelas del '
                                       'COVID-19, son reversibles?\n'
                                       '\n'
                                       '24:59 En el caso de las que requieren 2 dosis, ¿es '
                                       'seguro mezclar las vacunas?\n'
                                       '\n'
                                       '27:09 Sobre la variante Delta, ¿es más contagiosa? ¿es '
                                       'más letal? ¿las vacunas con las que contamos nos '
                                       'protegen contra esta nueva variante?\n'
                                       '\n'
                                       '28:52 Tomar alcohol después de haberse aplicado la '
                                       'vacuna, ¿afecta su efectividad?\n'
                                       '\n'
                                       '31:10 En el caso de las mujeres que están embarazadas, '
                                       '¿es seguro vacunarse?\n'
                                       '\n'
                                       '32:35 Una mujer que está en lactancia, ¿puede '
                                       'vacunarse?\n'
                                       '\n'
                                       '34:40 ¿Las vacunas pueden causar infertilidad? ¿es '
                                       'real que tienen chips? ¿tienen imanes?\n'
                                       '\n'
                                       '38:23 ¿Es seguro vacunarse para quienes padecen '
                                       'alergias?\n'
                                       '\n'
                                       '41:06 ¿Será necesario aplicarse un refuerzo cada año?\n'
                                       '\n'
                                       '42:34 ¿Se planea que la vacuna esté disponible para '
                                       'niños próximamente?\n'
                                       '\n'
                                       '44:02 ¿Es necesario aplicarse la vacuna para quienes '
                                       'ya se contagiaron? o pueden considerarse inmunizados\n'
                                       '\n'
                                       '45:22 ¿Es necesario seguir usando cubrebocas después '
                                       'de estar vacunado?\n'
                                       '\n'
                                       '\n'
                                       'CONTACTO► contacto.paulinazuniga@gmail.com\n'
                                       '\n'
                                       'Redes sociales del Dr. Ricardo Cortés:\n'
                                       '\n'
                                       'Instagram ► https://www.instagram.com/ricardodgps/\n'
                                       'Twitter ► https://twitter.com/Ricardodgps\n'
                                       'Facebook ► https://www.facebook.com/DrRCortes',
                            'thumb_height': None,
                            'thumb_url': 'https://i.ytimg.com/vi_webp/jWKe98MURcw/maxresdefault.webp',
                            'thumb_width': None,
                            'title': 'COVID-19 y VACUNAS l Variante DELTA l ¿Puedo enfermarme '
                                     'si ya me vacuné? l Q&A ft Dr. Ricardo Cortés'}
               ],
             'link': 'https://www.youtube.com/channel/UCBrGE6cmFbcwzlwAyIDMGpw',
             'publishDate': '2024-09-03 22:39:16+00:00',
             'title': 'Creadores entrevistan a expertos: COVID-19 y vacunas'}

    if ret_dict != expected:
        sys.exit(1)


def main():
    logger.configure_console()

    test_convert_to_audio()

    test_parse_playlist()


if __name__ == '__main__':
    main()
