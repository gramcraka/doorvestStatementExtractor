import pandas as pd
from collections import OrderedDict
import re


def is_same_text_row(num1, num2):
    return abs(num1 - num2) <= 10


class TableProcessor:
    """
    Class to process tables in PDFs. The class is highly coupled to the "Transactions" table in Doorvest
    (www.doorvest.com) statements.
    """

    def __init__(self):
        self.currentRow = None
        self.data = None
        self.rowYPos = None
        self.state = 'init'
        self.headerPositions = OrderedDict()  # stores header data (header->xPos)
        self.step = 0  # Running state transition steps total

    def _end_page(self):
        if self.state == 'init':
            raise ValueError("TableProcessor not started")
        elif self.state == 'start':
            raise ValueError("TableProcessor has not processed any data")
        elif self.state == 'end':
            raise ValueError("TableProcessor already ended")
        elif self.state == 'readHeader':
            raise ValueError("Header not finished")
        else:
            self.state = 'endPage'
            self.rowYPos = None
        self.step += 1

    def _end_table(self):
        if self.state == 'init':
            raise ValueError("TableProcessor not started")
        if self.state == 'start':
            raise ValueError("TableProcessor has not processed any data")
        if self.state != 'end':
            self.step += 1
        self.state = 'end'

    def _read_header(self):
        if self.state == 'init':
            raise ValueError("TableProcessor not started")
        elif self.state == 'readHeader':
            raise ValueError("Already reading header")
        elif self.state == 'start':
            self.state = 'readHeader'
        else:
            raise ValueError("Cannot read header")
        self.step += 1

    def _start(self):
        if self.state == 'init':
            self.state = 'start'
        else:
            raise ValueError("TableProcessor already started")
        self.step += 1

    def _read_row(self):
        s = self.state
        if s == 'init':
            raise ValueError("TableProcessor not started")
        elif s == 'readRow':
            raise ValueError("Already reading row")
        elif s == 'start':
            raise ValueError("Cannot read row before header")
        elif s == 'readHeader' or s == 'readCell' or s == 'skipRow' or s == 'endPage':
            self.state = 'readRow'
            if self.currentRow is not None:
                self.data = pd.concat([self.data,
                                       pd.DataFrame([self.currentRow], columns=list(self.headerPositions.keys()))],
                                      ignore_index=True)
            self.currentRow = {key: None for key in self.headerPositions.keys()}
        self.step += 1

    def concat(self, other):  # Concatenate two TableProcessors
        if self.state != 'end' or other.state != 'end':
            raise ValueError("TableProcessor not finished")
        if self.headerPositions.keys() != other.headerPositions.keys():
            raise ValueError("Header mismatch")
        self.data = pd.concat([self.data, other.data], ignore_index=True)

    def to_csv(self, file_path):
        return self.data.to_csv(file_path, index=False)

    def _read_cell(self):
        if self.state == 'readRow' or self.state == 'readCell':
            self.state = 'readCell'
        else:
            raise ValueError("Not reading row")
        self.step += 1

    def _skip_row(self):
        if self.state == 'init':
            raise ValueError("TableProcessor not started")
        else:
            self.state = 'skipRow'
            self.currentRow = None
        self.step += 1

    def _is_running(self):
        s = self.state
        return (s == 'readRow' or s == 'readCell' or s == 'start' or
                s == 'readHeader' or s == 'skipRow' or s == 'endPage')

    def __str__(self):
        return f"TableProcessor(state={self.state}, step={self.step})"

    def _process_cell(self, text, x_pos):
        if self.state != 'readCell':
            raise ValueError("Not reading cell")

        text = text.strip()
        # iterate in reverse through header positions
        for header, header_x_pos in reversed(self.headerPositions.items()):
            if x_pos >= header_x_pos or abs(x_pos - header_x_pos) < 10:
                if self.currentRow[header] is None:
                    self.currentRow[header] = text
                else:
                    self.currentRow[header] += " " + text
                return

        raise ValueError('No header found for', text, 'at', x_pos)

    def extract_text_visitor_callback(self, text, _current_transformation_matrix, text_matrix, _font_dictionary,
                                      _font_size):
        """
        Callback function used by PyPDF2._page.PageObject.extract_text.
        :param text: The text content of the current text object.
        :param _current_transformation_matrix: It's a 3x3 matrix that defines translation, rotation, scaling, and \
                skewing transformations applied to the text.
        :param text_matrix: The text matrix represents the final transformation applied to the text, including the
            transformation specified by the transformation matrix. A 3x3 matrix represented as a list of 6 numbers.
        :param _font_dictionary: not used
        :param _font_size: not used
        :return:
        """
        self._extract_text_visitor_callback(text, text_matrix)

    def _extract_text_visitor_callback(self, text, text_matrix):
        if self.state == 'end':
            return
        elif self.state == 'init':
            if text == 'Transactions':
                self._start()
                self._read_header()
            return
        elif self.state == 'skipRow':
            if text == '\n':
                self._read_row()
            return
        elif self._is_running() and (text == '' or text == '\n'):
            return
        elif (self._is_running() and
              re.search(r'Page (\d+) of (\d+)', text) and
              not is_same_text_row(text_matrix[5], self.rowYPos)):  # End of page
            self._read_row()
            self._end_page()
            return
        elif self.state == 'endPage':
            self._skip_row()  # Skip the repeated header row
            return
        elif self._is_running() and text == 'Total':  # End of table
            self._end_table()
            return
        elif self._is_running() and text.startswith('Beginning Cash Balance as of') or text == 'Ending Cash Balance':
            if self.rowYPos is not None and not is_same_text_row(text_matrix[5], self.rowYPos):
                self._read_row()
            self._skip_row()
            return
        elif self.state == 'readHeader':
            header_text = self._process_header(text, text_matrix[4])
            if header_text == 'Balance':  # Last header
                self.data = pd.DataFrame(columns=list(self.headerPositions.keys()))
                self._read_row()
        elif self.state == 'readRow':
            self._read_cell()
            self.rowYPos = text_matrix[5]
            return self._extract_text_visitor_callback(text, text_matrix)
        elif self.state == 'readCell':
            if not is_same_text_row(text_matrix[5], self.rowYPos):
                self._read_row()
                return self._extract_text_visitor_callback(text, text_matrix)
            self._process_cell(text, text_matrix[4])

    def _process_header(self, text, x_pos):
        text = text.strip()
        self.headerPositions[text] = x_pos
        return text
