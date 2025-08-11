# courses/utils.py

from courses.models import Lesson
from courses.models import UserProgress
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
from datetime import date

def has_completed_course(user, course):
    lessons = Lesson.objects.filter(course=course)
    completed_count = UserProgress.objects.filter(
        user=user,
        lesson__in=lessons,
        completed=True
    ).count()
    return completed_count == lessons.count()

from reportlab.lib import colors
from reportlab.lib.units import inch

def generate_certificate(student_name, course_name):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Light cream background
    c.setFillColorRGB(1, 0.98, 0.9)
    c.rect(0, 0, width, height, fill=1)

    # Border
    border_margin = 40
    c.setStrokeColor(colors.darkblue)
    c.setLineWidth(5)
    c.rect(border_margin, border_margin, width - 2 * border_margin, height - 2 * border_margin)

    # Title
    c.setFont("Helvetica-Bold", 30)
    c.setFillColor(colors.darkblue)
    c.drawCentredString(width / 2, height - 150, "Certificate of Completion")

    # Subtitle
    c.setFont("Helvetica-Oblique", 18)
    c.setFillColor(colors.darkgreen)
    c.drawCentredString(width / 2, height - 200, "This certifies that")

    # Student name
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(colors.darkred)
    c.drawCentredString(width / 2, height - 250, student_name)

    # Confirmation text
    c.setFont("Helvetica", 16)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, height - 300, "has successfully completed the course")

    # Course name
    c.setFont("Helvetica-BoldOblique", 20)
    c.setFillColor(colors.darkblue)
    c.drawCentredString(width / 2, height - 350, f"\"{course_name}\"")

    # Signature line
    c.setStrokeColor(colors.black)
    c.setLineWidth(1.5)
    sig_x = width / 2 - 100
    sig_y = border_margin + 80
    c.line(sig_x, sig_y, sig_x + 200, sig_y)
    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2, sig_y - 20, "Instructor Signature")

    # Date
    today = date.today().strftime("%B %d, %Y")
    c.setFont("Helvetica-Oblique", 14)
    c.setFillColor(colors.gray)
    c.drawString(border_margin + 20, border_margin + 30, f"Issued on {today}")

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer
