from documents.pad import *

import pytest

def test_pad_creation():
    print("Testing pad creation...", end="")
    #Empty pad creation
    pad = Pad("")
    assert(repr(pad) == "\n")
    assert(len(pad.lines) == 2)

    #Pad creation
    pad = Pad("Hello\nHola\n")
    assert(str(pad) == "Hello\nHola\n")
    assert(len(pad.lines) == 3) #empty line at end
    print("done !")

def test_basic_functions():
    print("Testing basic functions...", end="")
    pad = Pad("Hello\n\nHola\n")
    
    #Cursor creation
    cur_id = pad.cursor_create()
    cur_ref = pad._get_cursor_from_id(cur_id)
    assert(cur_ref is not None)
    
    #Cursor seek
    pad.cursor_seek(cur_id, 5, "llo\n\nH", 3) #end of hello
    assert(cur_ref.row == 0 and cur_ref.col == 5)
    
    #Insertion
    pad.insert(cur_id, " to")
    pad.insert(cur_id, " you")
    assert(cur_ref.row == 0 and cur_ref.col == 12)
    assert(str(pad) == "Hello to you\n\nHola\n")
    
    #Removal
    pad.remove(cur_id, len(" you"))
    assert(cur_ref.row == 0 and cur_ref.col == 8)
    assert(str(pad) == "Hello to\n\nHola\n")
    
    print("done !")

def test_seeks():
    print("Testing seeks...", end="")
    pad = Pad("Hello\nHola\n")
    cur_id = pad.cursor_create()
    cur_ref = pad._get_cursor_from_id(cur_id)
    
    #Beginning of file seek
    pad.cursor_seek(cur_id, 0, "Hell", 0)
    assert(cur_ref.row == 0 and cur_ref.col == 0)
    
    #Beginning of file seek (too high)
    pad.cursor_seek(cur_id, 20, "Hell", 0)
    assert(cur_ref.row == 0 and cur_ref.col == 0)
    
    #Wrong position seek (too low)
    pad.cursor_seek(cur_id, 0, "Hol", 0)
    assert(cur_ref.row == 1 and cur_ref.col == 0)
    
    #Wrong position seek (too high)
    pad.cursor_seek(cur_id, 150, "lo\n", 1)
    assert(cur_ref.row == 0 and cur_ref.col == 4)
    
    #End of file seek
    pad.cursor_seek(cur_id, 11, "Hola\n", 5)
    assert(cur_ref.row == 2 and cur_ref.col == 0)
    
    #End of file seek (too high)
    pad.cursor_seek(cur_id, 23, "Hola\n", 5)
    assert(cur_ref.row == 2 and cur_ref.col == 0)
    
    #End of file seek (too low)
    pad.cursor_seek(cur_id, 7, "Hola\n", 5)
    assert(cur_ref.row == 2 and cur_ref.col == 0)
    
    print("done !")

def test_insertions():
    print("Testing insertions...", end="")
    pad = Pad("Hello\nHola\n")
    cur_id = pad.cursor_create()
    
    #Insert at end of text
    pad.cursor_seek(cur_id, 11, "la\n", 2)
    pad.insert(cur_id, "\n")
    assert(str(pad) == "Hello\nHola\n\n")
    assert(len(pad.lines) == 4)
    
    pad.insert(cur_id, "This is it")
    assert(len(pad.lines) == 4)
    assert(str(pad) == "Hello\nHola\nThis is it\n")
    
    pad.cursor_seek(cur_id, 0, "Hel", 0)
    pad.insert(cur_id, "Bonjour\n")
    assert(len(pad.lines) == 5)
    assert(str(pad) == "Bonjour\nHello\nHola\nThis is it\n")
    
    print("done !")

def test_two_cursors():
    print("Testing two cursors...", end="")
    pad = Pad("Hello\n\nHola\n")
    cur1_id = pad.cursor_create()
    cur2_id = pad.cursor_create()
    
    #Multi-seek
    pad.cursor_seek(cur1_id, 5, "llo\n\nH", 3) #end of hello
    pad.cursor_seek(cur2_id, 4, "ola", 3) #end of hola
    
    #Multi-insert
    pad.insert(cur1_id, "\nDear Fella !")
    pad.insert(cur2_id, "\nCómo estás ?")
    assert(str(pad) == "Hello\nDear Fella !\n\nHola\nCómo estás ?\n")
    
    #Multi-remove
    pad.remove(cur1_id, 15)
    assert(str(pad) == "Hel\n\nHola\nCómo estás ?\n")
    pad.remove(cur2_id, 4)
    assert(str(pad) == "Hel\n\nHola\nCómo est\n")
    
    print("done !")