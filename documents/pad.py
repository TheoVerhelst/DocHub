# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid
import unicodedata
import tempfile

from .models import Document
from django.shortcuts import get_object_or_404


class PadSelectionDenied(Exception):
    """Exception used when a cursor selection is not allowed.
    Handling should include resetting the client's cursor to its previous position.
    """
    pass

class PadOutOfSync(Exception):
    """Exception used when a synchronization problem is detected.
    Handling should include re-submitting the whole pad content to the client.
    """
    pass

class Cursor:
    def __init__(self):
        self.col = -1
        self.row = -1


class Pad:
    def __init__(self, document_pk):
        self.document_pk = document_pk

        document = get_object_or_404(Document, pk=document_pk)
        data = document.original.read().decode("utf-8")
        self.lines = data.splitlines(keepends=True)
        if len(self.lines) == 0:
            self.lines = [""]

        self.cursors = {}
        self.new_cursor_id = -1

        self.content_as_string = "" #Whole content concatenated into one string
        self.content_was_modified = True #Was the content modified since the last concat ?

    def _char_to_row_col(self, char_count):
        """
        Translates a character count (from file beginning) to row, col position
        """
        row, col = 0, 0
        while char_count > 0:
            line_cols = len(self.lines[row])

            if char_count < line_cols or row == len(self.lines) - 1:
                col = char_count
                char_count = 0
            else:
                row += 1
                col = 0
                char_count -= line_cols

        return row, col

    def _row_col_to_char(self, row, col):
        char = 0
        for i in range(row):
            char += len(self.lines[i])
        char += col
        return char

    def _get_cursor_from_id(self, cursor_id):
        try:
            return self.cursors[cursor_id]
        except:
            self.cursors[cursor_id] = Cursor()
            return self.cursors[cursor_id]

    def _get_all_cursors(self):
        for cursor in self.cursors.values():
            yield cursor

    def get_cursor_position(self, cursor_id):
        cursor = self._get_cursor_from_id(cursor_id)
        return self._row_col_to_char(cursor.row, cursor.col)

    def _cursor_can_select_row(self, row_number, cursor_ref):
        for cur in self._get_all_cursors():
            #If there is another cursor on 'row_number'
            if cur.row == row_number and cur != cursor_ref:
                return False
        return True


    def cursor_seek(self, cursor_id, char_position, char_context, context_position):
        """
        Positions cursor identified by cursor_id at position 'char_position'
        If char_context do not surround char_position, tries to reposition cursor by finding the closest position where they do.
        """
        text = repr(self) #Whole text as single string

        #If char position is not valid, re-sync client
        if char_position < 0 or char_position > len(text) or char_position < context_position:
            raise PadOutOfSync #CONTENT MUST BE SENT TO CLIENT

        #Find next and previous closest positions of center of char_context
        context_left_span = context_position
        context_right_span = len(char_context) - context_position

        next_closest_position = text.find(char_context, char_position - context_left_span)
        prev_closest_position = text.rfind(char_context, 0, char_position + context_right_span)

        #If context could not be found, re-sync client
        if next_closest_position == -1 and prev_closest_position == -1:
            raise PadOutOfSync #CONTENT MUST BE SENT TO CLIENT

        #Choose best position
        true_position = 0
        distance_to_next = (next_closest_position + context_left_span) - char_position
        distance_to_prev = char_position - (prev_closest_position + context_left_span)
        if prev_closest_position == -1 or distance_to_next < distance_to_prev:
            true_position = next_closest_position + context_left_span
        else:
            true_position = prev_closest_position + context_left_span

        cursor = self._get_cursor_from_id(cursor_id)
        row, col = self._char_to_row_col(true_position)

        if self._cursor_can_select_row(row, cursor):
            cursor.row, cursor.col = row, col
            return true_position
        else:
            raise PadSelectionDenied #REFUSE SELECTION BY CLIENT


    def cursor_delete(self, cursor_id):
        """
        Removes the cursor identified by cursor_id from the Pad
        """
        print("DELETE", self)
        del self.cursors[cursor_id]

    def insert(self, cursor_id, content):
        """
        Inserts 'content' from the position of the cursor identified by 'cursor_id'
        """
        print("INSERT", self)
        cursor = self._get_cursor_from_id(cursor_id)
        pad_line = self.lines[cursor.row]

        #Insert content into line
        self.content_was_modified = True
        self.lines[cursor.row] = pad_line[0:cursor.col] + content + pad_line[cursor.col:]

        #Check if line needs to be splitted (new lines)
        splitted_lines = self.lines[cursor.row].splitlines(keepends=True)

        #If no line feeds have been added, advance same-line cursors and return
        if len(splitted_lines) == 1:
            for other_cursor in self._get_all_cursors():
                if other_cursor.row == cursor.row and other_cursor.col >= cursor.col:
                    other_cursor.col += len(content)
            return

        #Modify line list
        current_row = cursor.row #Modified row
        current_col = cursor.col #Modified column
        self.lines = self.lines[0:current_row] + splitted_lines + self.lines[current_row+1:]

        #Compute offset due to insertion (for futher cursors)
        furtherCursorRowOffset = len(splitted_lines) - 1
        furtherCursorColOffset = (len(content) - content.rindex('\n') - 1) - current_col

        #Advance cursors
        for other_cursor in self._get_all_cursors():
            #Cursors on following lines: advance row
            if other_cursor.row > current_row:
                other_cursor.row += furtherCursorRowOffset
            #Cursors on same line and following columns: advance row and columns
            elif other_cursor.row == current_row and other_cursor.col >= current_col:
                other_cursor.row += furtherCursorRowOffset
                other_cursor.col += furtherCursorColOffset


    def remove(self, cursor_id, backspace_count):
        """
        Removes backspace_count characters from the cursor identified by cursor_id
        """
        print("REMOVE", self)
        self.content_was_modified = True
        cursor = self._get_cursor_from_id(cursor_id)

        current_row = cursor.row
        current_col = cursor.col
        del_start_row = cursor.row
        del_start_col = cursor.col

        backspace_remaining = backspace_count
        backspace_stop = False

        while not backspace_stop:
            #If we ran out of backspaces
            if del_start_col > backspace_remaining:
                backspace_stop = True
                del_start_col = del_start_col - backspace_remaining
                backspace_remaining = 0

            #If we ran out of characters
            elif del_start_row == 0:
                backspace_stop = True
                backspace_remaining -= del_start_col
                del_start_col = 0

            #If we must continue
            else:
                backspace_remaining -= del_start_col
                #If cursor is allowed to select previous line
                if self._cursor_can_select_row(del_start_row-1, cursor):
                    del_start_row -= 1
                    del_start_col = len(self.lines[del_start_row])
                #Otherwise stop there
                else:
                    del_start_col = 0
                    backspace_stop = True

        #Row and column offsets after the deletion
        del_rows = current_row - del_start_row
        del_cols = len(self.lines[del_start_row]) - current_col

        for cur in self._get_all_cursors():
            if cur.row > current_row:
                cur.row -= del_rows
            elif cur.row >= current_row and cur.col >= current_col:
                cur.row -= del_rows
                cur.col += del_cols

        first_line = self.lines[del_start_row]
        last_line = self.lines[current_row]
        self.lines[del_start_row] = first_line[0:del_start_col] + last_line[current_col:]

        for i in range(1, del_rows+1):
            del self.lines[del_start_row + 1]

        return backspace_count - backspace_remaining

    def __repr__(self):
        if self.content_was_modified:
            self.content_was_modified = False
            self.content_as_string = ''.join(self.lines)
        return self.content_as_string

    def file_flush(self):
        tmpfile = tempfile.NamedTemporaryFile("w+")
        tmpfile.write(repr(self))
        tmpfile.flush()

        document = get_object_or_404(Document, pk=self.document_pk)
        document.original.delete(save=False)
        with open(tmpfile, 'r') as file:
            document.original.save(str(uuid.uuid4()) + document.file_type, file)
