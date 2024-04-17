import unittest
import os
import io

from doorvestStatementExtractor.extract import extract_content


class TableProcessorTestCase(unittest.TestCase):

    def test_small_table(self):
        buffer = io.StringIO()
        file_path = os.path.join(os.path.dirname(__file__), 'data', 'small table.pdf')
        tp = extract_content(file_path)
        self.assertEqual(tp.state, 'end')

        tp.to_csv(buffer)
        contents = buffer.getvalue()
        buffer.close()
        self.assertEqual(
            contents,
            "Date,Payee / Payer,Type,Reference,Description,Cash In,Cash Out,Balance\n"
            '12/22/2023,DV COMMUNITIES LLC,Check,29,Management Fee - Management Fee for 11/2023,,34.70,"2,664.23"\n'
        )

    def test_multi_page_table(self):
        buffer = io.StringIO()
        file_path = os.path.join(os.path.dirname(__file__), 'data', 'multi page statement.pdf')
        tp = extract_content(file_path)
        self.assertEqual(tp.state, 'end')

        tp.to_csv(buffer)
        contents = buffer.getvalue()
        buffer.close()
        self.assertEqual(
            contents,
            "Date,Payee / Payer,Type,Reference,Description,Cash In,Cash Out,Balance\n"
            '11/08/2023,e n,CC receipt,6518-6500,Rent Income - November 2023 - Rent Income,"1,045.00",,"3,209.32"\n'
            '11/21/2023,DVC Maintenance,ACH payment,,Repairs & Maintenance - Work Order #2738-1 Handyman - Sewage smell in master bathroom downstairs and tub knob is not working,,625.00,"2,584.32"\n'
            '11/21/2023,DVC Maintenance,ACH payment,,Reno Guarantee by DVC - Work Order #2738-1 Handyman - Sewage smell in master bathroom downstairs and tub knob is not working,625.00,,"3,209.32"\n'
            '11/22/2023,DV COMMUNITIES LLC,Check,26,Management Fee - Management Fee for 11/2023,,104.50,"3,104.82"\n'
            '11/22/2023,DVC Maintenance,Check,27,Repairs & Maintenance - Work Order #2690-1 Handyman,,98.77,"3,006.05"\n'
            '11/22/2023,DVC Maintenance,Check,27,Repairs & Maintenance - Work Order #2546-1 Electrical,,179.45,"2,826.60"\n'
            '11/22/2023,DVC Maintenance,Check,27,Repairs & Maintenance - Work Order #2698-1 Handyman,,129.63,"2,696.97"\n'
            '11/22/2023,DVC Maintenance,Check,27,Repairs & Maintenance - Work Order #2473-1 Handyman,,345.04,"2,351.93"\n'
            '11/23/2023,,CC receipt,016B- AD40,Rent Income - November 2023 - Rent Income,347.00,,"2,698.93"\n'
            '11/29/2023,DVC Maintenance,Check,,Repairs & Maintenance - Work Order #2738-1 Residential Visual Inspection,,427.59,"2,271.34"\n'
            '11/29/2023,DVC Maintenance,Check,,Reno Guarantee by DVC - Work Order #2738-1 Residential Visual Inspection,427.59,,"2,698.93"\n'
        )

    def test_empty_table(self):
        buffer = io.StringIO()
        file_path = os.path.join(os.path.dirname(__file__), 'data', 'empty table.pdf')
        tp = extract_content(file_path)
        self.assertEqual(tp.state, 'end')

        tp.to_csv(buffer)
        contents = buffer.getvalue()
        buffer.close()
        self.assertEqual(contents, "Date,Payee / Payer,Type,Reference,Description,Cash In,Cash Out,Balance\n")


if __name__ == '__main__':
    unittest.main()
