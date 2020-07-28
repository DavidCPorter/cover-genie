

import sys
import os
import textwrap
import pdb

from fpdf import FPDF

class PDF(FPDF):

    def generate(self, output_path):
        # Read text file
        with open(output_path, 'rb') as fh:
            for part in fh.readlines():
                part = part.decode('latin-1')
                part = part.lstrip(' ')
                if part[0] == '*':
                    part = part.replace('*', '-')
                    lines = textwrap.wrap(part, 100)
                    self.ln(1)
                    self.set_left_margin(15)
                    self.cell(0, 5, lines.pop(0), align='L',ln=1)
                    for l in lines:
                        self.set_left_margin(17)
                        self.cell(0, 5, l, align='L',ln=1)
                    self.set_left_margin(10)
                    self.ln(0)
                    continue

                self.multi_cell(0, 5, part, align='L')

    def generate_page(self, output_path):
        self.add_page()
        self.set_font('Times', '', 12)
        self.set_left_margin(10)
        self.set_right_margin(10)
        self.generate(output_path)
