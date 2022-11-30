#!/usr/bin/env python3


import os 
from zipfile import ZipFile 
from PyPDF2 import PdfReader, PdfFileReader
import pandas as pd
import pdfkit as pdf
import fitz
#from langdetect import detect
import py3langid as langid
import epub
import eyed3
import numpy as np 
from fpdf import FPDF
import aspose.words as aw



class Ressource():

    def __init__(self):        
        self.path = os.getcwd() + "/livres" 
        self.pdf = []
        self.epub = []
        self.other = []


    def extract(self,repo, path = None):
        if path : 
            a = path
        else:
            a = self.path
        print(a)
        b = "/" + str(repo)
        path_2 = a + b
        p = os.listdir(path_2)
        Ressource.tri(self,p,path_2)


    def dezip(self,file):
        new_file = self.path + "/" + str(file)
        os.mkdir(new_file[:-4])
        with ZipFile(new_file, 'r') as zip:      
            zip.extractall(new_file[:-4]) 
        p = os.listdir(new_file[:-4])
        Ressource.tri(self,p,new_file[:-4])


    def tri(self,p = None, path = None):
        if path:
            new_path = path
        else: 
            new_path = self.path
        print(new_path)
        if p:
            for k in p:
                if ".epub" in k:
                    self.epub.append(k)

                elif ".pdf" in k:
                    self.pdf.append(k)

                elif '.' not in k:
                    Ressource.extract(self,k,new_path)

                else: 
                    self.other.append(k) 
        else :
            list_files = os.listdir(new_path)
            for i in range(len(list_files)):
                element = list_files[i]
                print(element)
                if ".epub" in element:
                    self.epub.append(element)

                elif ".pdf" in element:
                    self.pdf.append(element)

                elif '.' not in element:
                    Ressource.extract(self,element,new_path)

                elif ".zip" in element:
                    Ressource.dezip(self,element)
                else:
                    self.other.append(element) 
                    print(f"Vous devez ouvrir ce dossier : {element}")



class Livre():

    def __init__(self,path = None):
        if path:
            self.path = path
        else:
            self.path = os.getcwd() + "/livres"
        self.filename = ""
        self.title = ""
        self.author = ""
        self.language = ""
        self.table = []


    def recup(self, filename = None):
        if filename:
            self.filename = filename
        livre = self.path + "/" + str(self.filename)

        if ".pdf" in self.filename or ".epub" in self.filename: 

            if ".epub" in self.filename:
                reader = epub.open_epub(livre)
                meta = reader.opf.metadata
                name_author = meta.creators[0][0]
                name_title = meta.titles[0][0]
               
            
            if ".pdf" in self.filename:
                reader = PdfReader(livre)
                meta = reader.metadata
                name_author = meta.author
                name_title = meta.title


            if name_author == None and name_title == None:
                self.author = self.filename
                self.title = self.filename
            elif name_author == None:
                self.author = self.filename
                self.title = name_title
            elif name_title == None:
                self.author = name_author
                self.title = self.filename
            else:
                self.author = name_author
                self.title = name_title

            d = self.path + '/' + self.filename
            doc = fitz.open(d)
            toc = doc.get_toc()
            self.table = str(toc)
            self.language = langid.classify(self.table)[0]

        elif ".mp3" in self.filename:
            audiofile = eyed3.load(livre)
            self.author = audiofile.tag.artist
            self.title = audiofile.tag.title

        return self

    
"""
    def recup(self,path,filename):
        path_3 = path + "/" + str(filename)
        with open(path_3, "rb") as pdf_file:
            read_pdf = PyPDF2.PdfFileReader(pdf_file, strict = False)
            #page = read_pdf.pages[0]
            #page_content = page.extract_text()
        return read_pdf  
"""
class Bibliotheque():

    def __init__(self):
        self.path = os.getcwd() + "/livres"
        self.livres = []
        self.table_auteur = []

    def sommaire(self, livre):
        t = livre.table 
        sommaire = []
        G = ""
        for i in range(1,len(t)-1):
            if t[i] == "[":
                G = ""
            elif t[i] == "]":
                sommaire.append(G)
            else :
                G += t[i]
        sommaire2 = pd.DataFrame(sommaire, columns = ["sommaire"])
        nom_sommaire = livre.filename + "_sommaire"
        sommaire2.to_html(nom_sommaire + '.html', index=False)  #create a html_file just to visualize the table
        np.savetxt(nom_sommaire + '.txt', sommaire2,fmt='%s', encoding="utf-8") #save the dataFrame as a txt file
        pdf = FPDF()    #save FPDF() class into a variable pdf 
        pdf.add_page()  #add a page
        pdf.set_font("Helvetica", size = 8)
        f = open(nom_sommaire + ".txt", "r",encoding="ISO-8859-1") #open the text file in read mode
        for x in f: #insert the test in pdf
            pdf.multi_cell(150, 5, txt = x)
        pdf.output(nom_sommaire + ".pdf") #save txt_file as  a pdf_file
        doc = aw.Document(nom_sommaire + ".txt")
        doc.save(nom_sommaire + ".epub") #save txt_file as an epub_file
        
                
    
    def recup(self,path = None,el = None):
        if path:
            new_path = path
            if el:
                new_path += '/' + el
        else:
            new_path = self.path

        bibli = os.listdir(new_path) #list all of the files/directory in the new_path created
        err = ["verne_phare_bout_monde_mv.pdf","verne_phare_bout_monde.pdf","verne_geographie_france_et_colonies_ocr.pdf","autorun.pdf","pochette_cd_conan_doyle.pdf","epinal"]
        for i in range(len(bibli)):
            element = bibli[i]
            print(element)
            if not "." in element and not element in err:
                path_2 = new_path +"/"+ element
                Bibliotheque.recup(self,path_2)
            elif not element in err:
                B = Livre(new_path)

                livre = B.recup(element)
                if not livre.author in [row.author for row in self.livres] or not livre.title in [row.title for row in self.livres]: 
                    self.livres.append(livre)
                    Bibliotheque.ajoute_auteur(self,livre)
                    Bibliotheque.sommaire(self,livre)
        return self.livres

    def DataFrame(self):
        #Construction de la data frame correspondant au liste des ouvrages
        C_aut = pd.DataFrame([row.author + " | " for row in self.livres],columns = ["auteurs"])
        C_liv = pd.DataFrame([row.title + " | "  for row in self.livres],columns = ["livres"])
        C_lang = pd.DataFrame([row.language + " | "  for row in self.livres],columns = ["langue"])
        C_nom = pd.DataFrame([" > " + row.filename + " | " for row in self.livres],columns = ["nom du fichier"])
        DataFrame_auteurs = pd.concat([C_nom,C_liv,C_aut,C_lang],axis = 1) #create a dataframe of all of the books
        DataFrame_auteurs.to_html('Ouvrages.html', index=False)  #create a html_file just to visualize the table
        np.savetxt('Ouvrages.txt', DataFrame_auteurs,fmt='%s') #save the dataFrame as a txt file
        pdf = FPDF()    #save FPDF() class into a variable pdf 
        pdf.add_page()  #add a page
        pdf.set_font("Helvetica", size = 8)
        f = open("Ouvrages.txt", "r",encoding="ISO-8859-1") #open the text file in read mode
        for x in f: #insert the test in pdf
            pdf.multi_cell(150, 5, txt = x)
        pdf.output("Ouvrages.pdf") #save txt_file as  a pdf_file
        doc = aw.Document("Ouvrages.txt")
        doc.save("Ouvrages.epub") #save txt_file as an epub_file

        #Construction de la data frame correspondant au liste des auteurs avec leurs oeuvres
        L1 = pd.DataFrame([" > " + row[0] + " : " for row in self.table_auteur],columns = ["auteurs"])
        L2 = pd.DataFrame([row[1] for row in self.table_auteur],columns = ["livres et leur nom de fichier"])
        L = pd.concat([L1,L2],axis = 1) #create a dataframe of all of the authors
        L.to_html('Auteurs.html', index=False) #create a html_file just to visualize the table
        np.savetxt('Auteurs.txt', L,  fmt='%s') #save the DataFrame as a txt_file
        pdf = FPDF() # save FPDF() class into a variable pdf    
        pdf.add_page() # Add a page
        pdf.set_font("Arial", size = 8) # set style and size of font
        f = open("Auteurs.txt", "r",encoding="ISO-8859-1") # open the text file in read mode
        for x in f: # insert the text in pdf
            pdf.multi_cell(150, 5, txt = x)
        pdf.output("Auteurs.pdf") #save txt_file as a pdf_file
        doc = aw.Document("Auteurs.txt")
        doc.save("Auteurs.epub") #save txt_file as an epub_file

    def clear(self):
        self.livres = []
        self.table_auteur = []

    def __isub__(self,element):
        if isinstance(element,Livre):
            self.livres.remove(element)



    def __iadd__(self,element):
        if isinstance(element,Livre):
            if not element.author in [row.author for row in self.livres] or not element.title in [row.title for row in self.livres]:
                self.livres.append(element)
                Bibliotheque.ajoute_auteur(element)

        elif isinstance(element,str):
            if ".conf" in element:
                Bibliotheque.recup(self.path,element)                
                A = Livre.recup(element)
                if not A.author in [row.author for row in self.livres] or not A.title in [row.title for row in self.livres]: 
                    self.livres.append(A)
                    Bibliotheque.ajoute_auteur(A)
            else :
                A = Livre.recup(element)
                if not A.author in [row.author for row in self.livres] or not A.title in [row.title for row in self.livres]: 
                    self.livres.append(A)
                    Bibliotheque.ajoute_auteur(A)

        elif isinstance(objet, Bibliotheque):
            for i in range(len(objet)):
                if not B[i].auteur in [row.author for row in self.livres] or not B[i].title in [row.title for row in self.livres]:
                    self.livres.append(B[i])
                    Bibliotheque.ajoute_auteur(B[i])
        

    def ajoute_auteur(self,element):
        j = -1
        for i in range(len(self.table_auteur)):
            if self.table_auteur[i][0] == element.author:
                j = i
        if j == -1 :
            self.table_auteur.append([element.author, "\n" + str([element.title,element.filename]) + "\n" ])
        else:
            self.table_auteur[j][1] += str([element.title,element.filename]) + "\n"


    def ajouter_dans_auteur(self,element):
        myfile = open(os.getcwd() + "/Auteurs.txt", "rt") 
        texte_auteur = myfile.read() 
        if not element.author in texte_auteur:
            texte_auteur +=  element.author +'\n' +'[' + element.title+ ', ' + element.filename +' ]'
        
        else:
            nom_auteur =""
            for i in range(len(texte_auteur)):                
                nom_auteur += texte_auteur[i]
                if texte_auteur[i] == '[' and texte_auteur[i-3] != ']':
                    if nom_auteur == element.author:
                        temp = texte_auteur.split()
                        mid_pos = i-1
                        texte_auteur = ' '.join(temp[:mid_pos] + ['[' + element.title+ ', ' + element.filename +' ]'] + temp[mid_pos:])
                        break
                    nom_auteur = ""
                if texte_auteur[i] != ']':
                    nom_auteur = ""


    def update(self):
        myfile = open(os.getcwd() + "/Ouvrages.txt", "rt") 
        texte_ouvrage = myfile.read() 
        bibli = os.listdir(os.getcwd() + "/livres2")
        print(bibli)
        for i in range(len(bibli)):
            livre = bibli[i]
            if not livre in texte_ouvrage:
                A = Livre(os.getcwd() + "/livres")
                element = A.recup(livre)
                texte_ouvrage += element.filename+' | ' + element.title+' | ' + element.author+' | ' + element.language+' | '
                Bibliotheque.ajouter_dans_auteur(self,element) 
            else:
                k = 0
                trouve_livre = False
                nom_auteur = ""
                nom_livre = ""
                nom_fichier = ""
                nom_langue = ""
                for i in range(len(texte_ouvrage)):
                    if k%4 == 0:
                        nom_fichier +=  texte_ouvrage[i]
                        if trouve_livre:
                            break

                    if texte_ouvrage[i] == '|':
                        k += 1
                        if k == 1:
                            nom_fichier = nom_fichier[:len(nom_fichier)-2]
                            if nom_fichier == livre:
                                trouve_livre = True
                            else:
                                nom_fichier =""
                        else: 
                            nom_fichier = nom_fichier[:len(nom_fichier)-2]
                            if nom_fichier == livre:
                                trouve_livre = True
                            else:
                                nom_fichier =""
                    if trouve_livre:
                        if k%4 == 1:
                            nom_livre  += texte_ouvrage[i]
                        elif k%4 == 2:
                            nom_auteur  += texte_ouvrage[i]
                        elif k%4 == 3:
                            nom_langue  += texte_ouvrage[i]                        
                nom_livre = nom_livre[:len(nom_fichier)-2]
                nom_auteur = nom_auteur[:len(nom_fichier)-2]
                nom_langue = nom_langue[:len(nom_fichier)-2] +"\n"
   
        k = 0
        nom_auteur = ""
        nom_livre = ""
        nom_fichier = ""
        nom_langue = ""
        i = 0
        element_a_enlever = False
        mot = texte_ouvrage.split()
        while ( i != len(mot) ):
            if k%4 == 0 and mot[i] != "|":
                nom_fichier += mot[i]
            if mot[i] == '|':
                k +=1
                if k%4 == 1:
                    if not nom_fichier in bibli:
                        element_a_enlever = True
                        debut = i- 2
                    else:
                        element_a_enlever = False
                    nom_fichier = ""
                elif k%4 == 0 and element_a_enlever == True:
                    fin = i
                    mot = mot[:debut] + mot[fin:]
                    i = debut

            i+=1
        texte_ouvrage = ' '.join(mot)

        print(texte_ouvrage)



    
B = Bibliotheque()
B.recup()
B.DataFrame()


