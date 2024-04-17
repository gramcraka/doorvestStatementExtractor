import os
import unittest

from doorvestStatementExtractor.TableProcessor import TableProcessor


class TableProcessorTestCase(unittest.TestCase):
    def test_start_start(self):
        tp = TableProcessor()
        with self.assertRaises(ValueError):
            tp._start()
            tp._start()

    def test_not_started(self):  # test all state transitions that require the TableProcessor to be started
        tp = TableProcessor()
        with self.assertRaises(ValueError):
            tp._read_row()
        with self.assertRaises(ValueError):
            tp._read_header()
        with self.assertRaises(ValueError):
            tp._read_cell()
        with self.assertRaises(ValueError):
            tp._end_page()
        with self.assertRaises(ValueError):
            tp._end_table()

    def test_simple_table(self):
        tp = TableProcessor()
        self.assertEqual(tp.state, 'init')
        table = ["ablab", "Transactions", "Amount", "Date", "Balance", "Beginning Cash Balance as of 09/01/2023", "a",
                 "b", "\n", "c1", "Total"]
        states = ['init', 'readHeader', 'readHeader', 'readHeader', 'readRow', 'skipRow', 'skipRow', 'skipRow',
                  'readRow', 'readCell', 'end']

        tp._extract_text_visitor_callback(table[0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        for text, state in list(zip(table, states)):
            tp._extract_text_visitor_callback(text, [0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
            self.assertEqual(state, tp.state, text)


if __name__ == '__main__':
    unittest.main()
