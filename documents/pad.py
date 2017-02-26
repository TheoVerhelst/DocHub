# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid
import unicodedata
import tempfile

from .models import Document
from django import get_object_or_404


class Cursor:
	def __init__(self, col=0, row=0):
		self.col = col
		self.row = row


class Pad:
	def __init__(self, document_pk):
		self.document_pk = document_pk
		
		document = get_object_or_404(Document, pk=document_pk)
		data = document.original.read().decode("utf-8")
		self.lines = data.splitlines(keepends=True)
		
		self.cursors = {}
		self.new_cursor_id = -1
		
	def _get_cursor_from_id(self, cursor_id):
		return self.cursors[cursor_id]
		
	def _get_all_cursors(self):
		for cursor in self.cursors.values():
			yield cursor
		
	def cursor_create(self):
		"""
		Creates a new cursor and returns its id
		"""
		self.new_cursor_id += 1
		self.cursors[self.new_cursor_id] = Cursor()
		return self.new_cursor_id
		
	def _find_synced_row(self, row, lines_context):
		"""
		Parses all lines before and after 'row' and returns 'true_row'.
		'true_row' is the row
		"""
		offset = 0
		for i in range(1, len(self.lines)*2):			
			offset = i//2 * (-1 if i%2==0 else 1)
			true_row = row + offset 
			
			if self._is_synced(true_row, lines_context):
				return true_row
		
		return None
		
	def _is_synced(self, row, lines_context):
		line_count = len(self.lines)
		
		if row < 0 or row >= line_count:
			return False
		
		for i in range(-1, 2):
			if (row+i >= 0 and row+i < line_count) and lines_context[i+1] != self.lines[row+i]:
				return False
		
		return True
		
		
	def cursor_seek(self, cursor_id, row, col, lines_context):
		"""
		Positions cursor identified by cursor_id at index 'col' of row 'row'
		"""
		true_row = self._find_synced_row(row, lines_context)
		
		if not (true_row is None):
			cursor = self._get_cursor_from_id(cursor_id)
			cursor.row = true_row
			if col > len(self.lines[true_row]) or col < 0:
				raise ValueError
			cursor.col = col
		else:
			raise ValueError
		
	def cursor_delete(self, cursor_id):
		"""
		Removes the cursor identified by cursor_id from the Pad
		"""
		del self.cursors[cursor_id]
		
	def insert(self, cursor_id, content):
		"""
		Inserts 'content' from the position of the cursor identified by 'cursor_id'
		"""
		cursor = self._get_cursor_from_id(cursor_id)
		pad_line = self.lines[cursor.row]
		
		#Insert content into line
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
	
	def _can_backspace(self, row_number, cursor_ref):
		for cur in self._get_all_cursors():
			#If there is another cursor on 'row_number'
			if cur.row == row_number and cur != cursor_ref:
				return False
		return True
	
	
	def remove(self, cursor_id, backspace_count):
		"""
		Removes backspace_count characters from the cursor identified by cursor_id
		"""
		cursor = self._get_cursor_from_id(cursor_id)
		
		current_row = cursor.row
		current_col = cursor.col
		del_start_row = cursor.row
		del_start_col = cursor.col
		
		backspace_remaining = backspace_count
		backspace_stop = False
		
		while not backspace_stop:
			#As long as we're allowed to deleted
			if self._can_backspace(del_start_row, cursor):
				
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
					del_start_row -= 1
					del_start_col = len(self.lines[del_start_row])
		
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
			del self.lines[del_start_row + i]
		
	def printCursors(self):
		for id, cur in self.cursors.items():
			print(id, cur.row, cur.col)

	def __repr__(self):
		return ''.join(str(l) for l in self.lines)
		
	def file_flush(self):		
		tmpfile = tempfile.NamedTemporaryFile("w+")
		tmpfile.write(repr(self))
		tmpfile.flush()
		
		document = get_object_or_404(Document, pk=self.document_pk)
		document.original.delete(save=False)
		with open(tmpfile, 'r') as file:
			document.original.save(str(uuid.uuid4()) + document.file_type, file)
