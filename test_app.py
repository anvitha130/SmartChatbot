# test_app.py
from main_functions import detect_language, translate_to_english, get_advice

def test_detect_language():
    assert detect_language("Hola") == "es"

def test_translate_to_english():
    result = translate_to_english("Bonjour")
    assert "Hello" in result or result == "Hello"

def test_get_advice():
    advice = get_advice("career in ai")
    assert isinstance(advice, str)
    assert len(advice) > 0
    
import pytest
from database import insert_query, get_queries, create_table

def test_database_functions():
    create_table()
    insert_query("test_user", "What is AI?", "AI is Artificial Intelligence.", "Chat")
    result = get_queries("test_user")
    assert len(result) > 0
