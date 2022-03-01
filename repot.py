from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.platypus import Spacer
from num2words import num2words


class MyParagraph(Paragraph):
    def drawOn(self, canvas, x, y, _sW=0):
        #return super().drawOn(canvas, x, y, _sW)
        canvas.saveState()
        canvas.setStrokeColor((1,0,0))
        canvas.setLineWidth(1)
        print ('x=%s y=%s width=%s height=%s' % (x,y,self.width,self.height))
        canvas.rect(x,y,self.width,self.height,stroke=1,fill=0)
        canvas.restoreState()
        Paragraph.drawOn(self,canvas,x,y,_sW)

styleSheet = getSampleStyleSheet()
bt = styleSheet['BodyText']
p1 = MyParagraph("Este es un Concepto literarion y abstractro para imprimir por pantalla")
p2 = MyParagraph("The concept of an integrated one box solution for advanced")

story = [p1, Spacer(72,72),p2]

doc = SimpleDocTemplate('tp.pdf')
doc.build(story)