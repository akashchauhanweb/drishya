This API is created for the Second Assesment Test at Drishya.ai

Coded by: Akash Chauhan on 17th February 2023


Guidelines for Usage:

APIs - 

1. / - GET METHOD- It's the home directory showing all the APIs available, including the path, method used, and the parameters that can be passed.

2. /merge - POST METHOD - This API is focused on creating and merging texts and images based on the user's input.
    Parameters are as follows:

    (*Mandatory parameters)
    a. files 
        - Type: List[File] 
        - Description: User can upload any no of images in this.

    b. filename 
        - Type: String 
        - Description: This is the String of the file name and is also added as the header in the first page of the pdf.
    
    (Optional Parameters)
    a. pagesize 
        - Type: String 
        - Default: A4 
        - Description: User can provide custom page size in inches. If not provided, it'll take A4 page size as default size.
        - Sample Input: 10,10 / 12.35, 16.12

    b. collate 
        - Type: Boolean 
        - Default: False 
        - Description: Users can provide True if they want images to be combined into pages based on the image sizes. If not provided, images will be merged in different pages.
