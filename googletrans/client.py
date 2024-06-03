# -*- coding: utf-8 -*-
"""
A Translation module.

You can translate text using this module.
"""
import random
import time
import typing
import re
import json

import httpcore
import httpx
from httpx import Timeout

from googletrans import urls, utils
from googletrans.gtoken import TokenAcquirer
from googletrans.constants import (
    DEFAULT_CLIENT_SERVICE_URLS,
    DEFAULT_FALLBACK_SERVICE_URLS,
    DEFAULT_USER_AGENT, LANGCODES, LANGUAGES, SPECIAL_CASES,
    DEFAULT_RAISE_EXCEPTION, DUMMY_DATA
)
from googletrans.models import Translated, Detected, TranslatedPart
from requests_tor import RequestsTor

EXCLUDES = ('en', 'ca', 'fr')

RPC_ID = 'MkEWBc'

rt = RequestsTor(tor_ports=(9050, 9052, 9053, 9054, 9055, 9056, 9057, 9058, 9059,
                            9060, 9061, 9062, 9063, 9064, 9065, 9066, 9067, 9068, 9069,
                            9070, 9071, 9072, 9073, 9074, 9075, 9076, 9077, 9078, 9079,
                            9080, 9081, 9082, 9083, 9084, 9085, 9086, 9087, 9088, 9089,
                            9090, 9091, 9092, 9093, 9094, 9095, 9096, 9097, 9098, 9099,
                            9103, 9104, 9105, 9106, 9107, 9108, 9099, 9100, 9101, 9102,
                            9109, 9110, 9111, 9112, 9113, 9114, 9115, 9116, 9117, 9118,
                            9119, 9120, 9121, 9122, 9123, 9124, 9125, 9126, 9127, 9128,
                            9129, 9130, 9131, 9132, 9133, 9134, 9135, 9136, 9137, 9138,
                            9139, 9140, 9141, 9142, 9143, 9144, 9145, 9146, 9147, 9148,
                            9149, 9150, 9151, 9152, 9153, 9154, 9155, 9156, 9157, 9158,
                            9159, 9160, 9161, 9162, 9163, 9164, 9165, 9166, 9167, 9168,
                            9169, 9170, 9171, 9172, 9173, 9174, 9175, 9176, 9177, 9178,
                            9179, 9180, 9181, 9182, 9183, 9184, 9185, 9186, 9187, 9188,
                            9189, 9190, 9191, 9192, 9193, 9194, 9195, 9196, 9197, 9198,
                            9199, 9200, 9201, 9202, 9203, 9204, 9205, 9206, 9207, 9208,
                            9209, 9210, 9211, 9212, 9213, 9214, 9215, 9216, 9217, 9218,
                            9219, 9220, 9221, 9222, 9223, 9224, 9225, 9226, 9227, 9228,
                            9229, 9230, 9231, 9232, 9233, 9234, 9235, 9236, 9237, 9238,
                            9239, 9240, 9241, 9242, 9243, 9244, 9245, 9246, 9247, 9248,
                            9249, 9250, 9251, 9252, 9253, 9254, 9255, 9256, 9257, 9258,
                            9259, 9260, 9261, 9262, 9263, 9264, 9265, 9266, 9267, 9268,
                            9269, 9270, 9271, 9272, 9273, 9274, 9275, 9276, 9277, 9278,
                            9279, 9280, 9281, 9282, 9283, 9284, 9285, 9286, 9287, 9288,
                            9289, 9290, 9291, 9292, 9293, 9294, 9295, 9296, 9297, 9298,
                            9299, 9300), autochange_id=3)


class Translator:
    """Google Translate ajax API implementation class

    You have to create an instance of Translator to use this API

    :param service_urls: google translate url list. URLs will be used randomly.
                         For example ``['translate.google.com', 'translate.google.co.kr']``
                         To preferably use the non webapp api, service url should be translate.googleapis.com
    :type service_urls: a sequence of strings

    :param user_agent: the User-Agent header to send when making requests.
    :type user_agent: :class:`str`

    :param proxies: proxies configuration.
                    Dictionary mapping protocol or protocol and host to the URL of the proxy
                    For example ``{'http': 'foo.bar:3128', 'http://host.name': 'foo.bar:4012'}``
    :type proxies: dictionary

    :param timeout: Definition of timeout for httpx library.
                    Will be used for every request.
    :type timeout: number or a double of numbers
    :param proxies: proxies configuration.
                    Dictionary mapping protocol or protocol and host to the URL of the proxy
                    For example ``{'http': 'foo.bar:3128', 'http://host.name': 'foo.bar:4012'}``
    :param raise_exception: if `True` then raise exception if smth will go wrong
    :param http2: whether to use HTTP2 (default: True)
    :param use_fallback: use a fallback method
    :type raise_exception: boolean
    """

    def __init__(self, service_urls=DEFAULT_CLIENT_SERVICE_URLS, user_agent=DEFAULT_USER_AGENT,
                 raise_exception=DEFAULT_RAISE_EXCEPTION,
                 proxies: typing.Dict[str, httpcore.SyncHTTPTransport] = None,
                 timeout: Timeout = None,
                 http2=True,
                 use_fallback=False):

        self.client = httpx.Client(http2=http2)
        if proxies is not None:  # pragma: nocover
            self.client.proxies = proxies

        self.client.headers.update({
            'User-Agent': user_agent,
            'Referer': 'https://translate.google.com',
        })

        if timeout is not None:
            self.client.timeout = timeout

        if use_fallback:
            self.service_urls = DEFAULT_FALLBACK_SERVICE_URLS
            self.client_type = 'gtx'
            pass
        else:
            # default way of working: use the defined values from user app
            self.service_urls = service_urls
            self.client_type = 'tw-ob'
            self.token_acquirer = TokenAcquirer(
                client=self.client, host=self.service_urls[0])

        self.raise_exception = raise_exception

    def _build_rpc_request(self, text: str, dest: str, src: str):
        return json.dumps([[
            [
                RPC_ID,
                json.dumps([[text, src, dest, True], [None]], separators=(',', ':')),
                None,
                'generic',
            ],
        ]], separators=(',', ':'))

    def _pick_service_url(self):
        if len(self.service_urls) == 1:
            return self.service_urls[0]
        return random.choice(self.service_urls)

    def _translate(self, text: str, dest: str, src: str, reset_tor: bool):
        url = urls.TRANSLATE_RPC.format(host=self._pick_service_url())
        data = {
            'f.req': self._build_rpc_request(text, dest, src),
        }
        params = {
            'rpcids': RPC_ID,
            'bl': 'boq_translate-webserver_20201207.13_p0',
            'soc-app': 1,
            'soc-platform': 1,
            'soc-device': 1,
            'rt': 'c',
        }
        # r = self.client.post(url, params=params, data=data)

        if reset_tor:
            print('reset_tor')
            # new Tor identity. Calling this function includes time.sleep(3)
            rt.new_id()
            print('reset_tor done')
            # test automatic TOR new identity
            rt.test()
            print(rt.test())

        while True:
            check = rt.check_ip()
            print(check)

            regex2 = r'Just a moment\.\.\.'
            if re.search(regex2, text, re.DOTALL):
                print("Just a moment...")
                time.sleep(10)
                check = rt.check_ip()
                print('check2: ',check)
            else:
                break

            r = rt.post(url, params=params, data=data)

            regex1 = r"client does not have permission"
            if re.search(regex1, r.text, re.DOTALL):
                print("Access denied: 403 Forbidden detected! change ip... ")
            else:
                break

        if r.status_code != 200 and self.raise_Exception:
            raise Exception('Unexpected status code "{}" from {}'.format(
                r.status_code, self.service_urls))

        return r.text, r

    def _translate_legacy(self, text, dest, src, override):
        token = ''  # dummy default value here as it is not used by api client
        if self.client_type == 'webapp':
            token = self.token_acquirer.do(text)

        params = utils.build_params(client=self.client_type, query=text, src=src, dest=dest,
                                    token=token, override=override)

        url = urls.TRANSLATE.format(host=self._pick_service_url())
        r = self.client.get(url, params=params)

        if r.status_code == 200:
            data = utils.format_json(r.text)
            return data, r

        if self.raise_exception:
            raise Exception('Unexpected status code "{}" from {}'.format(
                r.status_code, self.service_urls))

        DUMMY_DATA[0][0][0] = text
        return DUMMY_DATA, r

    def _parse_extra_data(self, data):
        response_parts_name_mapping = {
            0: 'translation',
            1: 'all-translations',
            2: 'original-language',
            5: 'possible-translations',
            6: 'confidence',
            7: 'possible-mistakes',
            8: 'language',
            11: 'synonyms',
            12: 'definitions',
            13: 'examples',
            14: 'see-also',
        }

        extra = {}

        for index, category in response_parts_name_mapping.items():
            extra[category] = data[index] if (
                    index < len(data) and data[index]) else None

        return extra

    def translate(self, text: str, dest='en', src='auto', reset_tor=False):
        dest = dest.lower().split('_', 1)[0]
        src = src.lower().split('_', 1)[0]

        if src != 'auto' and src not in LANGUAGES:
            if src in SPECIAL_CASES:
                src = SPECIAL_CASES[src]
            elif src in LANGCODES:
                src = LANGCODES[src]
            else:
                raise ValueError('invalid source language')

        if dest not in LANGUAGES:
            if dest in SPECIAL_CASES:
                dest = SPECIAL_CASES[dest]
            elif dest in LANGCODES:
                dest = LANGCODES[dest]
            else:
                raise ValueError('invalid destination language')

        origin = text
        data, response = self._translate(text, dest, src, reset_tor)

        token_found = False
        square_bracket_counts = [0, 0]
        resp = ''
        for line in data.split('\n'):
            token_found = token_found or f'"{RPC_ID}"' in line[:30]
            if not token_found:
                continue

            is_in_string = False
            for index, char in enumerate(line):
                if char == '\"' and line[max(0, index - 1)] != '\\':
                    is_in_string = not is_in_string
                if not is_in_string:
                    if char == '[':
                        square_bracket_counts[0] += 1
                    elif char == ']':
                        square_bracket_counts[1] += 1

            resp += line
            if square_bracket_counts[0] == square_bracket_counts[1]:
                break

        data = json.loads(resp)
        parsed = json.loads(data[0][2])
        # not sure
        should_spacing = parsed[1][0][0][3]
        translated_parts = list(
            map(lambda part: TranslatedPart(part[0], part[1] if len(part) >= 2 else []), parsed[1][0][0][5]))
        translated = (' ' if should_spacing else '').join(map(lambda part: part.text, translated_parts))

        if src == 'auto':
            try:
                src = parsed[2]
            except:
                pass
        if src == 'auto':
            try:
                src = parsed[0][2]
            except:
                pass

        # currently not available
        confidence = None

        origin_pronunciation = None
        try:
            origin_pronunciation = parsed[0][0]
        except:
            pass

        pronunciation = None
        try:
            pronunciation = parsed[1][0][0][1]
        except:
            pass

        extra_data = {
            'confidence': confidence,
            'parts': translated_parts,
            'origin_pronunciation': origin_pronunciation,
            'parsed': parsed,
        }
        result = Translated(src=src, dest=dest, origin=origin,
                            text=translated, pronunciation=pronunciation,
                            parts=translated_parts,
                            extra_data=extra_data,
                            response=response)
        return result

    def translate_legacy(self, text, dest='en', src='auto', **kwargs):
        """Translate text from source language to destination language

        :param text: The source text(s) to be translated. Batch translation is supported via sequence input.
        :type text: UTF-8 :class:`str`; :class:`unicode`; string sequence (list, tuple, iterator, generator)

        :param dest: The language to translate the source text into.
                     The value should be one of the language codes listed in :const:`googletrans.LANGUAGES`
                     or one of the language names listed in :const:`googletrans.LANGCODES`.
        :param dest: :class:`str`; :class:`unicode`

        :param src: The language of the source text.
                    The value should be one of the language codes listed in :const:`googletrans.LANGUAGES`
                    or one of the language names listed in :const:`googletrans.LANGCODES`.
                    If a language is not specified,
                    the system will attempt to identify the source language automatically.
        :param src: :class:`str`; :class:`unicode`

        :rtype: Translated
        :rtype: :class:`list` (when a list is passed)

        Basic usage:
            >>> from googletrans import Translator
            >>> translator = Translator()
            >>> translator.translate('안녕하세요.')
            <Translated src=ko dest=en text=Good evening. pronunciation=Good evening.>
            >>> translator.translate('안녕하세요.', dest='ja')
            <Translated src=ko dest=ja text=こんにちは。 pronunciation=Kon'nichiwa.>
            >>> translator.translate('veritas lux mea', src='la')
            <Translated src=la dest=en text=The truth is my light pronunciation=The truth is my light>

        Advanced usage:
            >>> translations = translator.translate(['The quick brown fox', 'jumps over', 'the lazy dog'], dest='ko')
            >>> for translation in translations:
            ...    print(translation.origin, ' -> ', translation.text)
            The quick brown fox  ->  빠른 갈색 여우
            jumps over  ->  이상 점프
            the lazy dog  ->  게으른 개
        """
        dest = dest.lower().split('_', 1)[0]
        src = src.lower().split('_', 1)[0]

        if src != 'auto' and src not in LANGUAGES:
            if src in SPECIAL_CASES:
                src = SPECIAL_CASES[src]
            elif src in LANGCODES:
                src = LANGCODES[src]
            else:
                raise ValueError('invalid source language')

        if dest not in LANGUAGES:
            if dest in SPECIAL_CASES:
                dest = SPECIAL_CASES[dest]
            elif dest in LANGCODES:
                dest = LANGCODES[dest]
            else:
                raise ValueError('invalid destination language')

        if isinstance(text, list):
            result = []
            for item in text:
                translated = self.translate_legacy(item, dest=dest, src=src, **kwargs)
                result.append(translated)
            return result

        origin = text
        data, response = self.translate_legacy(text, dest, src)

        # this code will be updated when the format is changed.
        translated = ''.join([d[0] if d[0] else '' for d in data[0]])

        extra_data = self._parse_extra_data(data)

        # actual source language that will be recognized by Google Translator when the
        # src passed is equal to auto.
        try:
            src = data[2]
        except Exception:  # pragma: nocover
            pass

        pron = origin
        try:
            pron = data[0][1][-2]
        except Exception:  # pragma: nocover
            pass

        if pron is None:
            try:
                pron = data[0][1][2]
            except:  # pragma: nocover
                pass

        if dest in EXCLUDES and pron == origin:
            pron = translated

        # put final values into a new Translated object
        result = Translated(src=src, dest=dest, origin=origin,
                            text=translated, pronunciation=pron,
                            extra_data=extra_data,
                            response=response)

        return result

    def detect(self, text: str):
        translated = self.translate(text, src='auto', dest='en')
        result = Detected(lang=translated.src, confidence=translated.extra_data.get('confidence', None),
                          response=translated._response)
        return result

    def detect_legacy(self, text, **kwargs):
        """Detect language of the input text

        :param text: The source text(s) whose language you want to identify.
                     Batch detection is supported via sequence input.
        :type text: UTF-8 :class:`str`; :class:`unicode`; string sequence (list, tuple, iterator, generator)

        :rtype: Detected
        :rtype: :class:`list` (when a list is passed)

        Basic usage:
            >>> from googletrans import Translator
            >>> translator = Translator()
            >>> translator.detect('이 문장은 한글로 쓰여졌습니다.')
            <Detected lang=ko confidence=0.27041003>
            >>> translator.detect('この文章は日本語で書かれました。')
            <Detected lang=ja confidence=0.64889508>
            >>> translator.detect('This sentence is written in English.')
            <Detected lang=en confidence=0.22348526>
            >>> translator.detect('Tiu frazo estas skribita en Esperanto.')
            <Detected lang=eo confidence=0.10538048>

        Advanced usage:
            >>> langs = translator.detect(['한국어', '日本語', 'English', 'le français'])
            >>> for lang in langs:
            ...    print(lang.lang, lang.confidence)
            ko 1
            ja 0.92929292
            en 0.96954316
            fr 0.043500196
        """
        if isinstance(text, list):
            result = []
            for item in text:
                lang = self.detect(item)
                result.append(lang)
            return result

        data, response = self._translate_legacy(text, 'en', 'auto', kwargs)

        # actual source language that will be recognized by Google Translator when the
        # src passed is equal to auto.
        src = ''
        confidence = 0.0
        try:
            if len(data[8][0]) > 1:
                src = data[8][0]
                confidence = data[8][-2]
            else:
                src = ''.join(data[8][0])
                confidence = data[8][-2][0]
        except Exception:  # pragma: nocover
            pass
        result = Detected(lang=src, confidence=confidence, response=response)

        return result
