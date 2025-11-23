import sys, os
sys.path.append('w:/JARVIS 1.0')
try:
    from core import Gemini
    print('Gemini imported')
    print('format_response test:', Gemini.format_response('Hello *world*'))
except Exception as e:
    print('Error:', e)
