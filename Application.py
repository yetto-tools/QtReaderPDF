from ast import Try
import sys
from tkinter import W
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter, QPrintPreviewDialog



################################################
# dependens convert pdf file  
################################################
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from io import StringIO
import re


# ---------------------------------------- 
#  dependens generate new formar report
# ---------------------------------------- 
#
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import mm, inch
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

# ---------------------------------------- 
#  Register Font Family Arial 
# ---------------------------------------- 
#
registerFont(TTFont('Arial', 'arial.ttf'))
registerFont(TTFont('Arial-Bold', 'arialbd.ttf'))
registerFont(TTFont('Arial-Italic', 'ariali.ttf'))
registerFont(TTFont('Arial-BoldItalic', 'arialbi.ttf'))
addMapping('Arial', 0, 0, 'Arial')
addMapping('Arial', 1, 0, 'Arial-Bold')
addMapping('Arial', 0, 1, 'Arial-Italic')
addMapping('Arial', 1, 1, 'Arial-BoldItalic')

################################################
####### Crear ventana principal
################################################
'''
env var  dir 
    // Temp dir    %temp%
    QStandardPaths.writableLocation(QStandardPaths.TempLocation)
    
    // Home Dir to str
    QStandardPaths.writableLocation(QStandardPaths.HomeLocation)

    // Download dir to str
    QStandardPaths.writableLocation(QStandardPaths.DownloadLocation)

'''

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.getSettingsValues()
        hboxlayout = QHBoxLayout()
        self.treeview = QTreeView()
        self.dirModel = QFileSystemModel()
        self.webView = QWebEngineView()
        self.centralwidget = QWidget()

        self.webView.page().setBackgroundColor(QColor(82, 86, 89))
        self.treeview.setHeaderHidden(False)
        self.treeview.setSortingEnabled(True)
        self.treeview.setAlternatingRowColors(True)
        self.treeview.sortByColumn(0, Qt.AscendingOrder)
        self.setWindowTitle ('Qt Reader PDF')
        self.setWindowIcon(QIcon('./Resource/icons/adobe-acrobat--v2.ico'))
        ###### data convert ########
        self.file_selected  = None
        self.pdfdata  = None
        ###### Crear interfaz ######

        hboxlayout.addWidget(self.treeview)
        hboxlayout.addWidget(self.webView,2)

        self.centralwidget.setLayout(hboxlayout)
        self.setCentralWidget(self.centralwidget)

        self.dirModel.setRootPath(QDir.homePath())
        self.dirModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs  |  QDir.Files)   
        self.dirModel.setNameFilters({'*.pdf'})
        self.dirModel.setNameFilterDisables(False)

        self.treeview.setModel(self.dirModel)
        self.treeview.setRootIndex(self.dirModel.setRootPath(QDir.homePath()))

        self.treeview.hideColumn(1)
        self.treeview.hideColumn(2)

        self.treeview.clicked.connect(self.on_clicked)
        
        self.webView.settings().setAttribute(QWebEngineSettings.SpatialNavigationEnabled, False)
        self.webView.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        self.webView.settings().setAttribute(QWebEngineSettings.PdfViewerEnabled, True)

        # Menu Bar
        self.menuBar = self.menuBar()

        ## File Menu
        self.exitAction = QAction(QIcon(QApplication.style().standardIcon(QStyle.SP_DialogCloseButton)),"&Salir...", self)

        #About Menu
        self.aboutAction = QAction("&Acerca de", self)

        # menu bar items
        FileMenu = QMenu("&Achivo", self)
        self.menuBar.addMenu(FileMenu)
        # Abrir
        self.openFileAction = QAction(QIcon('./Resource/icons/document-pdf-text.png'), "&Abrir", self)
        self.openFileAction.setShortcut('Ctrl+A')
        self.openFileAction.triggered.connect(self.open_file_dialog)

        # Abri Folder
        self.openDirAction = QAction(QIcon(QApplication.style().standardIcon(QStyle.SP_DirIcon)), "&Carpeta", self)
        self.openDirAction.setShortcut('Ctrl+Shift+A')
        self.openDirAction.triggered.connect(self.open_folder_dialog)

        # Imprimir
        self.printDirectAction = QAction(QIcon('./Resource/icons/printer--arrow.png'), "&Imprimir...", self)
        self.printDirectAction.setShortcut('Ctrl+P')
        self.printDirectAction.triggered.connect(self.printDirect)

        # Vista previa de Impresion
        self.printPreViewAction = QAction(QIcon('./Resource/icons/printer--pencil.png'), "&Vista previa de Impresión...", self)
        self.printPreViewAction.setShortcut('Ctrl+Alt+P')
        self.printPreViewAction.triggered.connect(self.printPreView)

        # Preferencias
        self.preferenceAction = QAction(QIcon('./Resource/icons/printer--pencil.png'), "Pre&ferencias...", self)
        self.preferenceAction.setShortcut('Ctrl+Alt+P')
        self.preferenceAction.triggered.connect(self.preference)

        self.exitAction.triggered.connect(self.menu_exit)


        EditMenu = QMenu("&Edición", self)
        self.menuBar.addMenu(EditMenu)

        self.convertFormatAction = QAction(QIcon('./Resource/icons/document-convert.png'), "&Convertir Formato Cheque", self)
        self.convertFormatAction.setShortcut('Ctrl+T')
        self.convertFormatAction.triggered.connect(self.convertFormat)

        EditMenu.addAction(self.convertFormatAction)


        FormatMenu = QMenu("&Configuración", self)
        self.menuBar.addMenu(FormatMenu)


        AboutMenu = QMenu("&Acerca", self)
        self.menuBar.addMenu(AboutMenu)


        FileMenu.addAction(self.openFileAction)
        FileMenu.addAction(self.openDirAction)
        FileMenu.addSeparator()
        FileMenu.addAction(self.printDirectAction)
        FileMenu.addAction(self.printPreViewAction)
        FileMenu.addSeparator()
        FileMenu.addAction(self.preferenceAction)
        FileMenu.addSeparator()
        FileMenu.addAction(self.exitAction)

        toolbar =  QToolBar("Main")
        self.addToolBar(toolbar)

        button_openFile = self.openFileAction
        toolbar.addAction(button_openFile)

        button_printDirect = self.printDirectAction
        toolbar.addAction(button_printDirect)

        button_printPreview = self.printPreViewAction
        toolbar.addAction(button_printPreview)

        button_convertFile = self.convertFormatAction
        toolbar.addAction(button_convertFile)


        try:
            h = self.setting_window.value('Height')
            w = self.setting_window.value('Width')
            x = self.setting_window.value('posX')
            y = self.setting_window.value('posY')
            self.dirwork = self.setting_variables.value('Path')
            # self.treeview.setRootIndex(self.dirModel.index(self.dirwork))
            self.treeview.setRootIndex(self.dirModel.setRootPath(self.dirwork))
            self.move(x,y)
        except:
            pass
        if h is None or w is None or self.dirwork is None or x is None or y is None:
            self.resize(800, 640)
            self.dirwork =  QStandardPaths.writableLocation(QStandardPaths.HomeLocation)
        else:
            self.resize(w, h)
            self.treeview.setRootIndex(self.dirModel.setRootPath(self.dirwork))

    def on_clicked(self, index):
        self.file_selected = self.dirModel.fileInfo(index)
        filename = self.file_selected.fileName()
        path = self.file_selected.filePath()
        if not self.file_selected.isDir():
            self.webView.setUrl(QUrl(f"file:///{self.file_selected.absoluteFilePath()}"))


    @pyqtSlot()
    def convertFormat(self):
        if self.pdfdata == None:
            print("none")
        else:
            #self.webView.page():
            with open(self.file_selected, 'rb') as file:
                rsrcmgr = PDFResourceManager()
                retstr = StringIO()
                rsrcmgr = PDFResourceManager()
                laparams = LAParams()
                device = TextConverter(rsrcmgr, retstr, laparams=laparams)
                interpreter = PDFPageInterpreter(rsrcmgr, device)

                page_no = 0
                data = []
                for pageNumber, page in enumerate(PDFPage.get_pages(file)):
                    if pageNumber == page_no:
                        interpreter.process_page(page)
                        data.append(retstr.getvalue().split('\n')[:10])
                        retstr.truncate(0)
                        retstr.seek(0)
                        lista =  [item.strip() for item in data[0] if len(item)>0]
                
                self.pdfdata = lista
        
        list_fields = {'fecha': '', 'monto':'', 'nombre' : '', 'monto_en_letras': '', 'no_negociable' : '','otros':''}
        for field in self.pdfdata:
            if re.findall(r'[Guatemala,]+.[0-3]{1}[0-9]{1}.[de].*.[de].[0-9]{4}', field):
                list_fields['fecha'] = field

            elif re.findall(r'[0-9][,0-9]*\.[0-9]{2}', field):
                list_fields['monto'] = field

            elif re.findall(r'[A-Z ]+[0-9]+\/100', field):
                list_fields['monto_en_letras'] = field
            
            # elif re.findall(r'^PANADEROS*', field) or re.findall(r'^CUDILLERO*', field):
            # continue
            elif re.findall(r'[\*]{3}.*.[\*]{3}', field):
                list_fields['no_negociable'] = field
            else:
                list_fields['otros'] == field
                if list_fields['nombre'] == '':
                    list_fields['nombre'] = field
            
            self.pdfdata = list_fields
            self.formatPDFCheck()



    def formatPDFCheck(self):
        h,l = 215.9*mm,279.4*mm
        h_checkbi = 68*mm
        l_checkbi = 168*mm
        ancho,largo = letter

        temp = QStandardPaths.writableLocation(QStandardPaths.TempLocation)
        paper = letter
        try:
            myCanvas = canvas.Canvas(temp+'/'+self.file_selected.fileName(), pagesize=paper)

            myCanvas.setFont('Arial-Bold', 10.5)

            def top():
                mt = l
                return mt
            def margin_left():
                ml = ((h/2)-(h_checkbi/2))
                return ml

            myCanvas.rotate(90)
            myCanvas.drawString(top()-135*mm, -margin_left()-24.7*mm, self.pdfdata['fecha'])
            myCanvas.drawString(top()-30*mm, -margin_left()-24.7*mm, self.pdfdata['monto'])
            myCanvas.drawString(top()-140*mm, -margin_left()-31.7*mm, self.pdfdata['nombre'])
            myCanvas.drawString(top()-145*mm, -margin_left()-38.7*mm, self.pdfdata['monto_en_letras'])
            myCanvas.drawString(top()-105*mm, -margin_left()-59.7*mm, self.pdfdata['no_negociable'])

            myCanvas.showPage()
            myCanvas.save()
            tempfile = temp+"/"+self.file_selected.fileName()
            self.webView.setUrl(QUrl(f'file:///{tempfile}'))
            self.webView.setPage(self.webView.page())
            print(tempfile)
        except TypeError:
            msgbox = QMessageBox()
            msgbox.setIcon(QMessageBox.information)
            msgbox.setText("Primero Selecciona un Archivo Valido para convertir")
            msgbox.setInformativeText("This is additional information")
            msgbox.setDetailedText("The details are as follows:")
            msgbox.setStandardButtons(QMessageBox.Ok)


    @pyqtSlot()
    def open_file_dialog(self):
        options = QFileDialog.Options()
        path, check = QFileDialog.getOpenFileName(self,"Abrir Archivo PDF para Visualizar", 
            QStandardPaths.writableLocation(QStandardPaths.DownloadLocation),
            "*.pdf;;CrystalReport*.pdf;;All Files (*)", 
            options=options)
        if check:           
            self.webView.setUrl(QUrl(f'file:///{path}'))
            self.webView.setPage(self.webView.page())
            

    @pyqtSlot()
    def open_folder_dialog(self):
        options = QFileDialog.Options()
        path = QFileDialog.getExistingDirectory(self,"Abrir Archivo PDF para Visualizar", 
            QStandardPaths.writableLocation(QStandardPaths.DownloadLocation) )
        self.treeview.setRootIndex(self.dirModel.setRootPath(path))
        self.treeview.sortByColumn(3,Qt.DescendingOrder)
        self.setting_variables.setValue('Path', path)
        self.dirwork = path

    @pyqtSlot()
    def preference(self):
        print("print")

    @pyqtSlot()
    def menu_exit(self):
        self.closeEvent(self.event)
        qApp.quit
       

    @pyqtSlot()
    def printDirect(self):
        handler = PrintHandler ()
        handler.setPage (self.webView.page())
        #handler.printPreview()
        handler.print()
    
    @pyqtSlot()
    def printPreView(self):
        handler = PrintHandler ()
        handler.setPage (self.webView.page())
        handler.printPreview()
        

    def getSettingsValues(self):
        self.setting_window = QSettings("QtReader PDF", 'Window Size')
        self.setting_variables = QSettings ("QtReader PDF", "Work Dir")

    def closeEvent(self, event):
        self.setting_window.setValue('Height', self.rect().height() )
        self.setting_window.setValue('Width', self.rect().width() )
        self.setting_window.setValue("posX", self.x())
        self.setting_window.setValue("posY", self.y())
        self.setting_variables.setValue('Path', self.dirwork)
        print(self.dirwork)

        #self.setting_variables.setValue('Path', QStandardPaths.writableLocation(QStandardPaths.HomeLocation))


class configMenu(QDialog):
    def __init__(self):
        QDialog.__init__(self)




class PrinterHandler(QObject):
    def __init__(self, partent = None):
        super().__init__(partent)
        self.m_page = None
        self.m_inPrintPreview = False


class PrintHandler(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.m_page = None
        self.m_inPrintPreview = False


    def setPage(self, page):
        assert not self.m_page
        self.m_page = page
        self.m_page.printRequested.connect(self.printPreview)


    @pyqtSlot()
    def print(self):
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self.m_page.view())
        if dialog.exec_() != QDialog.Accepted:
            return
        self.printDocument(printer)

    @pyqtSlot()
    def printPreview(self):
        if not self.m_page:
            return
        if self.m_inPrintPreview:
            return
        self.m_inPrintPreview = True
        printer = QPrinter()
        preview = QPrintPreviewDialog(printer, self.m_page.view())
        preview.paintRequested.connect(self.printDocument)
        preview.exec()
        self.m_inPrintPreview = False

    @pyqtSlot()
    def printPreviewCustom(self):
        if not self.m_page:
            return
        if self.m_inPrintPreview:
            return
        self.m_inPrintPreview = True
        printer = QPrinter()
        preview = QPrintPreviewDialog(printer, self.m_page.view())
        preview.paintRequested.connect(self.printDocument)
        preview.exec()
        self.m_inPrintPreview = False


    @pyqtSlot(QPrinter)
    def printDocument(self, printer):
        loop = QEventLoop()
        result = False

        def printPreview(success):
            nonlocal result
            result = success
            loop.quit()
        progressbar = QProgressDialog(self.m_page.view())
        progressbar.findChild(QProgressBar).setTextVisible(False)
        progressbar.setLabelText("Espere por favor Generando vista previa...")
        progressbar.setRange(0, 0)
        progressbar.show()
        progressbar.canceled.connect(loop.quit)
        self.m_page.print(printer, printPreview)
        loop.exec_()
        progressbar.close()
        if not result:
            painter = QPainter()
            if painter.begin(printer):
                font = painter.font()
                font.setPixelSize(20)
                painter.setFont(font)
                painter.drawText(QPointF(10, 25), "No podría generar una vista previa de impresión.")
                painter.end()


 
 
################################################
 #######Empezando
################################################
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()

    sys.exit(app.exec_())
 
