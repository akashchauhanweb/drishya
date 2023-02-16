from fastapi import FastAPI, File, UploadFile, Form, HTTPException, status
from fastapi.responses import FileResponse
from typing import List, Optional
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import inch
from PIL import Image
import os

app = FastAPI()

@app.get('/')
def home():
    """
        GET API for home showing the available codes in the project
    """
    return {'urls_available': {1: {'url': '/merge', 'method': 'post', 'parameters': 'files: File, filename: Str, pagesize(optional): Float, Float, collate(optional): Boolean'}}}

@app.post('/merge')
def merge(files: Optional[List[UploadFile]] = None, filename: Optional[str] = Form(None), pagesize: Optional[str] = Form(None), collate: Optional[bool] = Form(False)):
    """
        POST API
        This API takes care of adding headers and merging images into the pdf
    """

    #validation of the parameters passed into the API
    params = []
    if not files: params.append('files')
    if not filename: params.append('filename')
    if params: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Parameter(s) {lst} not passed!'.format(lst=' and '.join(params)))
    
    #adjusting page size if user passes a custom page size
    pageWidth, pageHeight = 8.27, 11.69
    try: 
        if pagesize: pageWidth, pageHeight = [float(x.strip()) for x in pagesize.split(',')]
    except:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='Invalid page size!')

    #validating page size
    canvas = ''
    if pageWidth < 5.0 or pageHeight < 5.0:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='Page Size too small!')
    
    #code for storing the created canvas / pdf
    if not os.path.exists('static/'):
        os.makedirs('static')
    else:
        for file in os.listdir('static/'):
            os.remove('static/'+file)

    #creating a canvas with the default / adjusted page size
    canvas = Canvas('static/'+filename+'.pdf', pagesize=(pageWidth * inch, pageHeight * inch))
    pageWidth, pageHeight = pageWidth * inch, pageHeight * inch

    #writing the header on page
    canvas.setFont("Times-Roman", 30)
    canvas.drawCentredString(pageWidth/2, pageHeight-(1 * inch), filename)
    
    #adding images to the pdf based on collate config
    discarded_files = []
    if collate:
        cur = pageHeight - (1.5 * inch)
        for file in files:
            if not file.filename.endswith(('.png', '.jpeg', '.jpg')):
                discarded_files.append(file.filename)
                continue
            image, iw, ih = get_corrected_image(file.file, pageWidth, pageHeight)
            if (cur - (1 * inch)) < ih:
                cur = pageHeight - (1 * inch)
                canvas.showPage()
            canvas.drawInlineImage(image, (pageWidth - iw)/2, (cur - ih), iw, ih, preserveAspectRatio=True)
            cur -= ih+(0.5 * inch)
    else:
        for file in files:
            if not file.filename.endswith(('.png', '.jpeg', '.jpg')):
                discarded_files.append(file.filename)
                continue
            canvas.showPage()
            image, iw, ih = get_corrected_image(file.file, pageWidth, pageHeight)
            canvas.drawInlineImage(image, (pageWidth - iw)/2, (pageHeight - ih)/2, iw, ih, preserveAspectRatio=True)
    if discarded_files:
        canvas.showPage()
        canvas.drawCentredString(pageWidth/2, pageHeight/2, 'Discarded files: {files}'.format(files=', '.join(discarded_files)))
    canvas.save()
    
    #returning the file
    return FileResponse(path='static/'+filename+'.pdf', filename=filename+'.pdf', content_disposition_type='application/pdf', status_code=status.HTTP_200_OK)


def get_corrected_image(imagedata, pageWidth, pageHeight):
    """
        Function to correct image aspect ratio in case of large images to fit in the page
    """
    image = Image.open(imagedata)
    iw, ih = image.size
    if iw > pageWidth-(1*inch):
        aspect = ih / float(iw)
        iw = pageWidth-(1*inch)
        ih = pageWidth * aspect
    if ih > pageHeight-(1*inch):
        aspect = iw / float(ih)
        ih = pageHeight-(1*inch)
        iw = pageHeight * aspect
    return image, iw, ih