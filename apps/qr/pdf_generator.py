"""
PDF Generator for UPN QR format
Generates PDF documents according to UPN QR technical standard
"""
from fpdf import FPDF
from django.conf import settings
import os
import warnings
from datetime import datetime
import segno
from io import BytesIO
from PIL import Image


class UpnPdfGenerator:
    """Generator for UPN QR format PDF documents"""

    # Page dimensions and margins
    PAGE_WIDTH = 210  # mm (A4)
    PAGE_HEIGHT = 297  # mm (A4)
    FORM_HEIGHT = 99  # mm (UPN form height)

    def __init__(self, position='top', draw_template=True):
        """
        Initialize PDF generator with custom settings

        Args:
            position: 'top' or 'bottom' - where to place the payment slip
            draw_template: bool - whether to draw the background template
        """
        self.position = position
        self.draw_template = draw_template

        # Calculate Y_BASE based on position
        if position == 'bottom':
            self.Y_BASE = self.PAGE_HEIGHT - self.FORM_HEIGHT  # 297 - 99 = 198mm
        else:
            self.Y_BASE = 0  # Start from top

        self.pdf = FPDF(orientation='portrait', unit='mm', format="A4")
        self.pdf.set_margin(0)
        self.pdf.add_page()

        # Load fonts - use BASE_DIR/static for development, STATIC_ROOT for production
        if hasattr(settings, 'STATICFILES_DIRS') and settings.STATICFILES_DIRS:
            fonts_dir = os.path.join(settings.STATICFILES_DIRS[0], 'fonts')
        else:
            fonts_dir = os.path.join(settings.STATIC_ROOT, 'fonts')

        self.pdf.add_font("cour", style="", fname=os.path.join(fonts_dir, "Courier New.ttf"))
        self.pdf.add_font("cour", style="b", fname=os.path.join(fonts_dir, "Courier New Bold.ttf"))
        self.pdf.add_font("myriad", style="", fname=os.path.join(fonts_dir, "MyriadPro-Semibold.ttf"))

    def _draw_square(self, x, y, count):
        """Draw numbered squares for data entry"""
        self.pdf.set_draw_color(r=255, g=128, b=0)
        self.pdf.set_fill_color(255, 255, 255)
        self.pdf.set_line_width(0.2)
        self.pdf.rect(x, y, (3.75 * count), 5, style="DF")
        for c in range(count):
            self.pdf.set_line_width(0.1)
            self.pdf.line(x + 3.75, y, x + 3.75, y + 1.5)
            self.pdf.line(x + 3.75, y + 5, x + 3.75, y + 5 - 1.5)
            x = x + 3.75

    def _draw_square_cross(self, x, y):
        """Draw checkbox square with cross"""
        self.pdf.set_draw_color(r=255, g=128, b=0)
        self.pdf.set_fill_color(255, 255, 255)
        self.pdf.set_line_width(0.2)
        self.pdf.rect(x, y, 4, 4, style="DF")
        self.pdf.set_line_width(0.1)
        self.pdf.line(x, y, x + 4, y + 4)
        self.pdf.line(x, y + 4, x + 4, y)

    def _draw_template(self):
        """Draw the UPN QR form template"""
        Y_BASE = self.Y_BASE

        # Orange line at top
        self.pdf.set_draw_color(r=255, g=128, b=0)
        self.pdf.line(0, Y_BASE, 210, Y_BASE)

        # Background rectangles
        self.pdf.set_fill_color(254, 230, 226)
        self.pdf.set_draw_color(r=254, g=230, b=226)
        self.pdf.rect(60, Y_BASE, 210, 54.5, style="DF")

        self.pdf.set_fill_color(255, 242, 219)
        self.pdf.set_draw_color(r=255, g=242, b=219)
        self.pdf.rect(60, Y_BASE + 54.5, 210, 99 - 54.5, style="DF")

        self.pdf.set_draw_color(r=255, g=128, b=0)

        # Left side (Potrdilo) ====================================================

        # A1 - Title "UPN QR - potrdilo"
        self.pdf.set_xy(31.6, Y_BASE + 2)
        self.pdf.set_font('myriad', size=10)
        self.pdf.set_text_color(r=0, g=0, b=0)
        self.pdf.set_stretching(100)
        self.pdf.set_char_spacing(-0.5)
        self.pdf.write(text='UPN QR - potrdilo')

        # A2 - Label "Ime plačnika"
        self.pdf.set_xy(3, Y_BASE + 3.5)
        self.pdf.set_font('myriad', size=7)
        self.pdf.set_text_color(r=255, g=128, b=0)
        self.pdf.write(text='Ime plačnika')

        # A3 - Box for payer name
        self.pdf.rect(4, Y_BASE + 6, 52.5, 13.5, style="D")

        # A4 - Label "Namen in rok plačila"
        self.pdf.set_xy(3, Y_BASE + 20)
        self.pdf.set_font('myriad', size=7)
        self.pdf.set_text_color(r=255, g=128, b=0)
        self.pdf.write(text='Namen in rok plačila')

        # A5 - Box for purpose and deadline
        self.pdf.rect(4, Y_BASE + 22.5, 52.5, 9, style="D")

        # A6 - Label "Znesek"
        self.pdf.set_xy(15.5, Y_BASE + 32)
        self.pdf.set_font('myriad', size=7)
        self.pdf.set_text_color(r=255, g=128, b=0)
        self.pdf.write(text='Znesek')

        # A7 - EUR label
        self.pdf.set_xy(6.8, Y_BASE + 35.6)
        self.pdf.set_font('myriad', size=11)
        self.pdf.set_text_color(r=0, g=0, b=0)
        self.pdf.set_stretching(100)
        self.pdf.set_char_spacing(-0.5)
        self.pdf.write(text='EUR')

        # A8 - Amount box
        self.pdf.rect(16.5, Y_BASE + 34.5, 40, 5, style="D")

        # A9 - Label "IBAN in referenca prejemnika"
        self.pdf.set_xy(3, Y_BASE + 40)
        self.pdf.set_font('myriad', size=7)
        self.pdf.set_text_color(r=255, g=128, b=0)
        self.pdf.write(text='IBAN in referenca prejemnika')

        # A10 - Box for IBAN and reference
        self.pdf.rect(4, Y_BASE + 42.5, 52.5, 13.5, style="D")

        # A11 - Label "Ime prejemnika"
        self.pdf.set_xy(3, Y_BASE + 56.5)
        self.pdf.set_font('myriad', size=7)
        self.pdf.set_text_color(r=255, g=128, b=0)
        self.pdf.write(text='Ime prejemnika')

        # A12 - Box for recipient name
        self.pdf.rect(4, Y_BASE + 59, 52.5, 13.5, style="D")

        # A14 - Provider space label
        self.pdf.set_xy(12.8, Y_BASE + 97)
        self.pdf.set_font('myriad', size=5)
        self.pdf.set_char_spacing(0)
        self.pdf.set_text_color(r=255, g=128, b=0)
        self.pdf.write(text='Prostor za vpise ponudnika plačilnih storitev')

        # Right side (Nalog) ====================================================

        # A15, A16 - Black corner markers
        self.pdf.set_draw_color(r=0, g=0, b=0)
        self.pdf.set_fill_color(0, 0, 0)
        self.pdf.rect(61, Y_BASE + 1, 1.5, 1.5, style="DF")
        self.pdf.rect(207.5, Y_BASE + 1, 1.5, 1.5, style="DF")

        # A17 - Label "Koda QR"
        self.pdf.set_xy(62.5, Y_BASE + 3.5)
        self.pdf.set_font('myriad', size=7)
        self.pdf.set_text_color(r=255, g=128, b=0)
        self.pdf.write(text='Koda QR')

        # A18 - Label "IBAN plačnika"
        self.pdf.set_char_spacing(0)
        self.pdf.set_xy(105.5, Y_BASE + 3.5)
        self.pdf.set_font('myriad', size=7)
        self.pdf.set_text_color(r=255, g=128, b=0)
        self.pdf.write(text='IBAN plačnika')

        # A19 - Label "Polog"
        self.pdf.set_xy(183.3, Y_BASE + 3.5)
        self.pdf.set_font('myriad', size=7)
        self.pdf.set_text_color(r=255, g=128, b=0)
        self.pdf.write(text='Polog')

        # A20 - Label "Dvig"
        self.pdf.set_xy(195.1, Y_BASE + 3.5)
        self.pdf.set_font('myriad', size=7)
        self.pdf.set_text_color(r=255, g=128, b=0)
        self.pdf.write(text='Dvig')

        # A21 - QR code box with corner markers
        self.pdf.set_draw_color(r=255, g=128, b=0)
        self.pdf.set_fill_color(255, 255, 255)
        self.pdf.rect(63.5, Y_BASE + 6, 40, 39.5, style="DF")
        self.pdf.set_line_width(0.1)
        # Corner markers for QR box
        self.pdf.line(63.5, Y_BASE + 6 + 1.8, 63.5 + 0.6, Y_BASE + 6 + 1.8)
        self.pdf.line(63.5 + 1.8, Y_BASE + 6, 63.5 + 1.8, Y_BASE + 6 + 0.6)
        self.pdf.line(63.5, Y_BASE + 6 + 39.5 - 1.8, 63.5 + 0.6, Y_BASE + 6 + 39.5 - 1.8)
        self.pdf.line(63.5 + 1.8, Y_BASE + 6 + 39.5, 63.5 + 1.8, Y_BASE + 6 + 39.5 - 0.6)
        self.pdf.line(63.5 + 40 - 1.8, Y_BASE + 6 + 39.5, 63.5 + 40 - 1.8, Y_BASE + 6 + 39.5 - 0.6)
        self.pdf.line(63.5 + 40, Y_BASE + 6 + 39.5 - 1.8, 63.5 + 40 - 0.6, Y_BASE + 6 + 39.5 - 1.8)
        self.pdf.line(63.5 + 40 - 0.6, Y_BASE + 6 + 1.8, 63.5 + 40, Y_BASE + 6 + 1.8)
        self.pdf.line(63.5 + 40 - 1.8, Y_BASE + 6, 63.5 + 40 - 1.8, Y_BASE + 6 + 0.6)

        # A22 - IBAN plačnika squares
        self._draw_square(106.5, Y_BASE + 6, 4)
        self._draw_square(106.5 + (3.75 * 4), Y_BASE + 6, 4)
        self._draw_square(106.5 + (3.75 * 8), Y_BASE + 6, 4)
        self._draw_square(106.5 + (3.75 * 12), Y_BASE + 6, 4)
        self._draw_square(106.5 + (3.75 * 16), Y_BASE + 6, 3)

        # A23 - Polog checkbox
        self._draw_square_cross(185.2, Y_BASE + 6.5)

        # A24 - Dvig checkbox
        self._draw_square_cross(196.5, Y_BASE + 6.5)

        # A26 - Label "Referenca plačnika"
        self.pdf.set_xy(105.5, Y_BASE + 11.5)
        self.pdf.set_font('myriad', size=7)
        self.pdf.set_text_color(r=255, g=128, b=0)
        self.pdf.write(text='Referenca plačnika')

        # A27, A28 - Referenca plačnika squares
        self._draw_square(106.5, Y_BASE + 14, 4)
        self._draw_square(123.5, Y_BASE + 14, 22)

        # A29 - Label "Ime, ulica in kraj plačnika"
        self.pdf.set_xy(105.5, Y_BASE + 19.5)
        self.pdf.set_font('myriad', size=7)
        self.pdf.set_text_color(r=255, g=128, b=0)
        self.pdf.write(text='Ime, ulica in kraj plačnika')

        # A30 - Payer address box
        self.pdf.set_draw_color(r=255, g=128, b=0)
        self.pdf.set_fill_color(255, 255, 255)
        self.pdf.set_line_width(0.2)
        self.pdf.rect(106.5, Y_BASE + 22, 99.5, 15, style="DF")

        # A31, A32 - Dashed lines for address
        self.pdf.set_line_width(0.1)
        self.pdf.set_dash_pattern(0.2, 0.25)
        self.pdf.line(106.5, Y_BASE + 22 + 5, 106.5 + 99.5, Y_BASE + 22 + 5)
        self.pdf.line(106.5, Y_BASE + 22 + 5 + 5, 106.5 + 99.5, Y_BASE + 22 + 5 + 5)
        self.pdf.set_dash_pattern(0, 0)

        # A33 - EUR label
        self.pdf.set_xy(105.5, Y_BASE + 41.6)
        self.pdf.set_font('myriad', size=11)
        self.pdf.set_text_color(r=0, g=0, b=0)
        self.pdf.set_stretching(100)
        self.pdf.set_char_spacing(-0.5)
        self.pdf.write(text='EUR')

        # A34 - Label "Znesek"
        self.pdf.set_xy(113.2, Y_BASE + 38)
        self.pdf.set_char_spacing(0)
        self.pdf.set_font('myriad', size=7)
        self.pdf.set_text_color(r=255, g=128, b=0)
        self.pdf.write(text='Znesek')

        # A35 - Label "Datum plačila"
        self.pdf.set_xy(160.2, Y_BASE + 38)
        self.pdf.set_char_spacing(0)
        self.pdf.set_font('myriad', size=7)
        self.pdf.set_text_color(r=255, g=128, b=0)
        self.pdf.write(text='Datum plačila')

        # A36 - Label "Nujno"
        self.pdf.set_xy(194.3, Y_BASE + 38)
        self.pdf.set_char_spacing(0)
        self.pdf.set_font('myriad', size=7)
        self.pdf.set_text_color(r=255, g=128, b=0)
        self.pdf.write(text='Nujno')

        # A37 - Amount squares
        self._draw_square(114.2, Y_BASE + 40.5, 3)
        self._draw_square(114.2 + (3.75 * 3), Y_BASE + 40.5, 3)
        self._draw_square(114.2 + (3.75 * 6), Y_BASE + 40.5, 3)
        self._draw_square(114.2 + (3.75 * 9), Y_BASE + 40.5, 2)

        # A38 - Date squares
        self._draw_square(161.2, Y_BASE + 40.5, 2)
        self._draw_square(161.2 + (3.75 * 2), Y_BASE + 40.5, 2)
        self._draw_square(161.2 + (3.75 * 4), Y_BASE + 40.5, 4)

        # A39 - Nujno checkbox
        self._draw_square_cross(196.5, Y_BASE + 41)

        # A40 - Label "Koda namena"
        self.pdf.set_xy(62.5, Y_BASE + 46.5)
        self.pdf.set_char_spacing(0)
        self.pdf.set_font('myriad', size=7)
        self.pdf.set_text_color(r=255, g=128, b=0)
        self.pdf.write(text='Koda namena')

        # A41 - Label "Namen plačila"
        self.pdf.set_xy(79.5, Y_BASE + 46.5)
        self.pdf.set_char_spacing(0)
        self.pdf.set_font('myriad', size=7)
        self.pdf.set_text_color(r=255, g=128, b=0)
        self.pdf.write(text='Namen plačila')

        # A42 - Label "Rok plačila"
        self.pdf.set_xy(175.2, Y_BASE + 46.5)
        self.pdf.set_char_spacing(0)
        self.pdf.set_font('myriad', size=7)
        self.pdf.set_text_color(r=255, g=128, b=0)
        self.pdf.write(text='Rok plačila')

        # A43 - Koda namena squares
        self._draw_square(63.5, Y_BASE + 49, 4)

        # A44 - Namen plačila squares
        self._draw_square(80.5, Y_BASE + 49, 25)

        # A45 - Rok plačila squares
        self._draw_square(176.2, Y_BASE + 49, 2)
        self._draw_square(176.2 + (3.75 * 2), Y_BASE + 49, 2)
        self._draw_square(176.2 + (3.75 * 4), Y_BASE + 49, 4)

        # A46 - Label "IBAN prejemnika"
        self.pdf.set_xy(62.5, Y_BASE + 55.5)
        self.pdf.set_char_spacing(0)
        self.pdf.set_font('myriad', size=7)
        self.pdf.set_text_color(r=255, g=128, b=0)
        self.pdf.write(text='IBAN prejemnika')

        # A47 - IBAN prejemnika squares
        self._draw_square(63.5, Y_BASE + 58, 4)
        self._draw_square(63.5 + (3.75 * 4), Y_BASE + 58, 4)
        self._draw_square(63.5 + (3.75 * 8), Y_BASE + 58, 4)
        self._draw_square(63.5 + (3.75 * 12), Y_BASE + 58, 4)
        self._draw_square(63.5 + (3.75 * 16), Y_BASE + 58, 4)
        self._draw_square(63.5 + (3.75 * 20), Y_BASE + 58, 4)
        self._draw_square(63.5 + (3.75 * 24), Y_BASE + 58, 4)
        self._draw_square(63.5 + (3.75 * 28), Y_BASE + 58, 4)
        self._draw_square(63.5 + (3.75 * 32), Y_BASE + 58, 2)

        # A48 - "UPN QR" text
        self.pdf.set_xy(193.3, Y_BASE + 59.1)
        self.pdf.set_font('myriad', size=11)
        self.pdf.set_text_color(r=0, g=0, b=0)
        self.pdf.set_stretching(100)
        self.pdf.set_char_spacing(0)
        self.pdf.write(text='UPN QR')

        # A49 - Label "Referenca prejemnika"
        self.pdf.set_xy(62.5, Y_BASE + 63.5)
        self.pdf.set_char_spacing(0)
        self.pdf.set_font('myriad', size=7)
        self.pdf.set_text_color(r=255, g=128, b=0)
        self.pdf.write(text='Referenca prejemnika')

        # A50 - Referenca squares
        self._draw_square(63.5, Y_BASE + 66, 4)

        # A51 - Referenca squares continued
        self._draw_square(80.5, Y_BASE + 66, 22)

        # A52 - Reserved space for signature
        self.pdf.set_draw_color(r=255, g=128, b=0)
        self.pdf.set_fill_color(255, 255, 255)
        self.pdf.set_line_width(0.2)
        self.pdf.rect(166, Y_BASE + 66, 40, 23, style="DF")

        # A53 - Label "Ime, ulica in kraj prejemnika"
        self.pdf.set_xy(62.5, Y_BASE + 71.5)
        self.pdf.set_char_spacing(0)
        self.pdf.set_font('myriad', size=7)
        self.pdf.set_text_color(r=255, g=128, b=0)
        self.pdf.write(text='Ime, ulica in kraj prejemnika')

        # A54 - Recipient address box
        self.pdf.set_draw_color(r=255, g=128, b=0)
        self.pdf.set_fill_color(255, 255, 255)
        self.pdf.set_line_width(0.2)
        self.pdf.rect(63.5, Y_BASE + 74, 99.5, 15, style="DF")

        # A55, A56 - Dashed lines for recipient address
        self.pdf.set_line_width(0.1)
        self.pdf.set_dash_pattern(0.2, 0.25)
        self.pdf.line(63.5, Y_BASE + 74 + 5, 63.5 + 99.5, Y_BASE + 74 + 5)
        self.pdf.line(63.5, Y_BASE + 74 + 5 + 5, 63.5 + 99.5, Y_BASE + 74 + 5 + 5)
        self.pdf.set_dash_pattern(0, 0)

        # A57 - Signature line
        self.pdf.set_draw_color(r=255, g=128, b=0)
        self.pdf.set_line_width(0.2)
        self.pdf.line(168.6, Y_BASE + 85.3, 168.6 + 35, Y_BASE + 85.3)

        # A58 - Signature label
        self.pdf.set_xy(171, Y_BASE + 86)
        self.pdf.set_char_spacing(0)
        self.pdf.set_font('myriad', size=7)
        self.pdf.set_char_spacing(-0.5)
        self.pdf.set_text_color(r=255, g=128, b=0)
        self.pdf.write(text='Podpis plačnika (neobvezno žig)')

        # A60 - Provider space label
        self.pdf.set_xy(117.9, Y_BASE + 97)
        self.pdf.set_char_spacing(0)
        self.pdf.set_font('myriad', size=5)
        self.pdf.set_char_spacing(0)
        self.pdf.set_text_color(r=255, g=128, b=0)
        self.pdf.write(text='Prostor za vpise ponudnika plačilnih storitev')

        # A62 - Black corner marker
        self.pdf.set_draw_color(r=0, g=0, b=0)
        self.pdf.set_fill_color(0, 0, 0)
        self.pdf.rect(207.5, Y_BASE + 96.5, 1.5, 1.5, style="DF")

        # Bottom orange line
        self.pdf.set_draw_color(r=255, g=128, b=0)
        self.pdf.line(0, Y_BASE + 99, 210, Y_BASE + 99)

        # Website URL
        self.pdf.set_xy(188, Y_BASE + 97)
        self.pdf.set_char_spacing(0)
        self.pdf.set_font('myriad', size=4)
        self.pdf.set_char_spacing(0)
        self.pdf.set_text_color(r=255, g=128, b=0)
        self.pdf.write(text='https://upn-epc-qr.si/')

    def _fill_data(self, data):
        """Fill template with data from UpnModel"""
        Y_BASE = self.Y_BASE

        # Format amount with thousand separator and comma as decimal separator
        # Example: 1234.56 -> ***1.234,56
        amount_str = f"***{data.znesek:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')

        # Format date if available
        rok_placila_str = ""
        if data.rok_placila:
            rok_placila_str = data.rok_placila.strftime("%d.%m.%Y")

        # Format IBAN with spaces (every 4 characters)
        # Example: SI56020170014356205 -> SI56 0201 7001 4356 205
        def format_iban(iban):
            if not iban:
                return ""
            iban = iban.replace(' ', '')  # Remove existing spaces
            return ' '.join([iban[i:i+4] for i in range(0, len(iban), 4)])

        # Format reference for right side (4 spaces between first 4 chars and rest)
        # Example: SI081236-17-345679 -> SI08    1236-17-345679
        def format_reference_right(ref):
            if not ref:
                return ""
            ref = ref.replace(' ', '')  # Remove existing spaces
            if len(ref) > 4:
                return ref[:4] + '    ' + ref[4:]  # 4 spaces
            return ref

        # Right side data fields ====================================================

        # Payer address (right side - A29)
        if data.ime_placnika:
            self.pdf.set_xy(107, Y_BASE + 23)
            self.pdf.set_font('cour', style="b", size=10)
            self.pdf.set_text_color(r=0, g=0, b=0)
            self.pdf.set_char_spacing(-0.0)
            self.pdf.cell(text=data.ime_placnika[:33])

        if data.ulica_placnika:
            self.pdf.set_xy(107, Y_BASE + 28)
            self.pdf.cell(text=data.ulica_placnika[:33])

        if data.kraj_placnika:
            self.pdf.set_xy(107, Y_BASE + 33)
            self.pdf.cell(text=data.kraj_placnika[:33])

        # Amount (right side - A37)
        self.pdf.set_xy(115.2, Y_BASE + 41.5)
        self.pdf.set_font('cour', style="b", size=10)
        self.pdf.set_text_color(r=0, g=0, b=0)
        self.pdf.set_char_spacing(-0.0)
        self.pdf.cell(text=amount_str)

        # Payment code (right side - A43)
        if data.koda_namena:
            self.pdf.set_xy(64, Y_BASE + 50)
            self.pdf.set_font('cour', style="b", size=10)
            self.pdf.set_text_color(r=0, g=0, b=0)
            self.pdf.set_char_spacing(-0.0)
            self.pdf.cell(text=data.koda_namena[:4])

        # Payment purpose (right side - A44)
        if data.namen_placila:
            self.pdf.set_xy(81, Y_BASE + 50)
            self.pdf.set_font('cour', style="b", size=10)
            self.pdf.set_text_color(r=0, g=0, b=0)
            self.pdf.set_char_spacing(-0.0)
            self.pdf.cell(text=data.namen_placila[:42])

        # Payment deadline (right side - A45)
        if rok_placila_str:
            self.pdf.set_xy(176, Y_BASE + 50)
            self.pdf.set_font('cour', style="b", size=10)
            self.pdf.set_text_color(r=0, g=0, b=0)
            self.pdf.set_char_spacing(-0.0)
            self.pdf.cell(text=rok_placila_str)

        # Recipient IBAN (right side - A47) - formatted with spaces
        if data.iban_prejemnika:
            self.pdf.set_xy(64, Y_BASE + 59)
            self.pdf.set_font('cour', style="b", size=10)
            self.pdf.set_text_color(r=0, g=0, b=0)
            self.pdf.set_char_spacing(-0.0)
            self.pdf.cell(text=format_iban(data.iban_prejemnika[:34]))

        # Recipient reference (right side - A50) - formatted with 4 spaces
        if data.referenca:
            self.pdf.set_xy(64, Y_BASE + 67)
            self.pdf.set_font('cour', style="b", size=10)
            self.pdf.set_text_color(r=0, g=0, b=0)
            self.pdf.set_char_spacing(-0.0)
            self.pdf.cell(text=format_reference_right(data.referenca[:26]))

        # Recipient address (right side - A54)
        if data.ime_prejemnika:
            self.pdf.set_xy(64, Y_BASE + 75)
            self.pdf.set_font('cour', style="b", size=10)
            self.pdf.set_text_color(r=0, g=0, b=0)
            self.pdf.set_char_spacing(-0.0)
            self.pdf.cell(text=data.ime_prejemnika[:42])

        if data.ulica_prejemnika:
            self.pdf.set_xy(64, Y_BASE + 80)
            self.pdf.cell(text=data.ulica_prejemnika[:33])

        if data.kraj_prejemnika:
            self.pdf.set_xy(64, Y_BASE + 85)
            self.pdf.cell(text=data.kraj_prejemnika[:33])

        # Left side data fields ====================================================

        # Payer name (left side - A3)
        if data.ime_placnika:
            self.pdf.set_xy(4, Y_BASE + 6.5)
            self.pdf.set_font('cour', size=10)
            self.pdf.set_text_color(r=0, g=0, b=0)
            self.pdf.set_stretching(75)
            self.pdf.set_char_spacing(-0.3)
            self.pdf.cell(text=data.ime_placnika[:33])

        if data.ulica_placnika:
            self.pdf.set_xy(4, Y_BASE + 9.5)
            self.pdf.cell(text=data.ulica_placnika[:33])

        if data.kraj_placnika:
            self.pdf.set_xy(4, Y_BASE + 12.5)
            self.pdf.cell(text=data.kraj_placnika[:33])

        # Purpose and deadline (left side - A5)
        if data.namen_placila:
            self.pdf.set_xy(4, Y_BASE + 22.5)
            self.pdf.set_font('cour', size=10)
            self.pdf.set_text_color(r=0, g=0, b=0)
            self.pdf.set_stretching(75)
            self.pdf.set_char_spacing(-0.3)
            self.pdf.cell(text=data.namen_placila[:42])

        if rok_placila_str:
            self.pdf.set_xy(4, Y_BASE + 25.5)
            self.pdf.cell(text=f'Rok plačila: {rok_placila_str}')

        # Amount (left side - A8)
        self.pdf.set_xy(16.5, Y_BASE + 35.5)
        self.pdf.set_font('cour', size=10)
        self.pdf.set_text_color(r=0, g=0, b=0)
        self.pdf.set_stretching(75)
        self.pdf.set_char_spacing(-0.3)
        self.pdf.cell(text=amount_str)

        # IBAN and reference (left side - A10) - formatted with spaces
        if data.iban_prejemnika:
            self.pdf.set_xy(4, Y_BASE + 43)
            self.pdf.set_font('cour', size=10)
            self.pdf.set_text_color(r=0, g=0, b=0)
            self.pdf.set_stretching(75)
            self.pdf.set_char_spacing(-0.3)
            self.pdf.cell(text=format_iban(data.iban_prejemnika[:34]))

        if data.referenca:
            self.pdf.set_xy(4, Y_BASE + 50)
            self.pdf.cell(text=data.referenca[:26])

        # Recipient name (left side - A12)
        if data.ime_prejemnika:
            self.pdf.set_xy(4, Y_BASE + 60)
            self.pdf.set_font('cour', size=10)
            self.pdf.set_text_color(r=0, g=0, b=0)
            self.pdf.set_stretching(75)
            self.pdf.set_char_spacing(-0.3)
            self.pdf.cell(text=data.ime_prejemnika[:42])

        if data.ulica_prejemnika:
            self.pdf.set_xy(4, Y_BASE + 63)
            self.pdf.cell(text=data.ulica_prejemnika[:33])

        if data.kraj_prejemnika:
            self.pdf.set_xy(4, Y_BASE + 66)
            self.pdf.cell(text=data.kraj_prejemnika[:33])

    def _generate_upn_qr_data(self, data):
        """
        Generate UPN QR data string according to technical standard section 5.2

        Returns 20 fields separated by \n (LF)
        Character set: ISO-8859-2
        Maximum length: 411 characters (Version 15)

        Args:
            data: UpnModel instance

        Returns:
            str: UPN QR data string
        """
        # Field 1: Leading style (constant "UPNQR")
        field_1 = "UPNQR"

        # Field 2: Payer's IBAN (empty for payments)
        field_2 = ""

        # Field 3: Deposit (empty or "X")
        field_3 = ""

        # Field 4: Withdrawal (empty or "X")
        field_4 = ""

        # Field 5: Payer's reference (empty for this use case)
        field_5 = ""

        # Field 6: Payer's name
        field_6 = data.ime_placnika if data.ime_placnika else ""

        # Field 7: Payer's street
        field_7 = data.ulica_placnika if data.ulica_placnika else ""

        # Field 8: Payer's city
        field_8 = data.kraj_placnika if data.kraj_placnika else ""

        # Field 9: Amount in cents (multiply by 100, format with leading zeros)
        amount_cents = int(data.znesek * 100)
        field_9 = f"{amount_cents:011d}"  # 11 digits with leading zeros

        # Field 10: Payment date (empty)
        field_10 = ""

        # Field 11: Urgent (empty or "X")
        field_11 = ""

        # Field 12: Purpose code
        field_12 = data.koda_namena if data.koda_namena else ""

        # Field 13: Purpose of payment
        field_13 = data.namen_placila if data.namen_placila else ""

        # Field 14: Payment deadline (format DD.MM.YYYY)
        field_14 = ""
        if data.rok_placila:
            field_14 = data.rok_placila.strftime("%d.%m.%Y")

        # Field 15: Recipient's IBAN (without spaces)
        field_15 = data.iban_prejemnika.replace(' ', '') if data.iban_prejemnika else ""

        # Field 16: Recipient's reference (without spaces)
        field_16 = data.referenca.replace(' ', '') if data.referenca else ""

        # Field 17: Recipient's name
        field_17 = data.ime_prejemnika if data.ime_prejemnika else ""

        # Field 18: Recipient's street
        field_18 = data.ulica_prejemnika if data.ulica_prejemnika else ""

        # Field 19: Recipient's city
        field_19 = data.kraj_prejemnika if data.kraj_prejemnika else ""

        # Field 20: Checksum (sum of lengths of fields 1-19 including \n)
        fields_1_19 = [
            field_1, field_2, field_3, field_4, field_5,
            field_6, field_7, field_8, field_9, field_10,
            field_11, field_12, field_13, field_14, field_15,
            field_16, field_17, field_18, field_19
        ]
        checksum = sum(len(f) + 1 for f in fields_1_19)  # +1 for \n after each field
        field_20 = f"{checksum:03d}"  # 3 digits with leading zeros

        # Combine all fields with \n separator
        upn_data = '\n'.join(fields_1_19 + [field_20]) + '\n'

        return upn_data

    def _generate_upn_qr_image(self, upn_data):
        """
        Generate UPN QR code image according to technical standard section 5.1

        Specifications:
        - Version: 15 (77x77 modules)
        - Error Correction: M
        - Character Set: ISO-8859-2 (ECI 000004)
        - Size: 40mm x 39.5mm on PDF

        Args:
            upn_data: UPN QR data string (UTF-8)

        Returns:
            BytesIO: PNG image of QR code
        """
        # Create QR code with ISO-8859-2 encoding
        # According to technical standard section 5.1:
        # "The use of Extended Channel Interpretation (ECI value 000004) is required"
        # When eci=True, segno automatically inserts the correct ECI designator
        # based on the encoding parameter (ECI 000004 for iso-8859-2)
        qr = segno.make(
            upn_data,              # Pass string directly
            version=15,            # Force Version 15 (77x77 modules)
            error='m',             # Error Correction Level M
            encoding='iso-8859-2', # ISO-8859-2 character set (Latin-2)
            eci=True               # Enable ECI mode (inserts ECI 000004 header)
        )

        # Calculate scale to fit QR code into 40mm width
        # QR Version 15 = 77 modules
        # Target size: 40mm = 113.39 pixels at 72 DPI (fpdf default)
        # Scale = 113.39 / 77 ≈ 1.47 pixels per module
        # Use scale=8 for better quality (will resize in PDF)
        scale = 8  # Higher scale for better quality

        # Generate QR code as PNG in memory
        buffer = BytesIO()
        qr.save(
            buffer,
            kind='png',
            scale=scale,
            border=0,  # No border (we'll add white space in PDF)
            dark='#000000',  # Black modules
            light='#FFFFFF'  # White background
        )
        buffer.seek(0)

        return buffer

    def _add_upn_qr_to_pdf(self, upn_model):
        """
        Add UPN QR code to PDF at position A25

        According to technical standard section 5.1:
        - QR code size (without white border): 32.60mm x 32.60mm
        - QR space (with required white border): 35.98mm x 35.98mm
        - Total field A25: 40mm x 39.5mm at position (63.5mm, Y_BASE+6.0mm)

        Args:
            upn_model: UpnModel instance
        """
        Y_BASE = self.Y_BASE

        # Generate UPN QR data string
        upn_data = self._generate_upn_qr_data(upn_model)

        # Generate QR code image
        qr_buffer = self._generate_upn_qr_image(upn_data)

        # QR code dimensions according to standard
        qr_size = 32.60  # mm - actual QR code size without white border
        field_width = 40.0  # mm - total field width
        field_height = 39.5  # mm - total field height

        # Calculate margins to center QR code in field
        # This creates larger white borders as seen on printed invoices
        margin_x = (field_width - qr_size) / 2  # = 3.7mm
        margin_y = (field_height - qr_size) / 2  # = 3.45mm

        # Add QR code image centered in field A25
        self.pdf.image(
            qr_buffer,
            x=63.5 + margin_x,  # 63.5 + 3.7 = 67.2mm
            y=Y_BASE + 6.0 + margin_y,  # Y_BASE + 6.0 + 3.45 = Y_BASE + 9.45mm
            w=qr_size,  # 32.60mm
            h=qr_size   # 32.60mm
        )

    def generate(self, upn_model):
        """
        Generate PDF for UPN QR document

        Args:
            upn_model: UpnModel instance with payment data

        Returns:
            bytes: PDF document as bytes
        """
        # Draw template background (optional - for blank forms)
        if self.draw_template:
            self._draw_template()

        # Always fill data and add QR code
        self._fill_data(upn_model)
        self._add_upn_qr_to_pdf(upn_model)

        return bytes(self.pdf.output())

    @staticmethod
    def generate_filename(upn_model):
        """
        Generate meaningful filename for PDF

        Format: UPN-{recipient_name}-{reference}-{date}.pdf
        Example: UPN-T-2-SI12-2539015667766-07122025.pdf
        """
        # Clean recipient name (remove spaces, special chars)
        recipient = upn_model.ime_prejemnika.replace(' ', '-').replace('.', '')[:20]

        # Clean reference (remove spaces)
        reference = upn_model.referenca.replace(' ', '-')[:20] if upn_model.referenca else 'NO-REF'

        # Current date
        date_str = datetime.now().strftime("%d%m%Y")

        return f"UPN-{recipient}-{reference}-{date_str}.pdf"