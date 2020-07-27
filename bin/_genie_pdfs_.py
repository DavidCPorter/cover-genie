

import sys
import os

from fpdf import FPDF

class PDF(FPDF):

    def generate(self, output_path):
        # Read text file
        with open(output_path, 'rb') as fh:
            txt = fh.read().decode('latin-1')
        self.set_font('Times', '', 12)
        self.multi_cell(0, 5, txt)
        self.ln()
        self.set_font('', 'I')
        self.cell(0, 5, '(end of excerpt)')

    def generate_page(self, output_path):
        self.add_page()
        self.generate(output_path)
