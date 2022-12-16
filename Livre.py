#!/usr/bin/env python3


import os 
import shutil
from zipfile import ZipFile 
from PyPDF2 import PdfReader, PdfFileReader
import pandas as pd
import pdfkit as pdf
import fitz
import py3langid as langid
import epub
import eyed3
import numpy as np 
from fpdf import FPDF
import aspose.words as aw
import time


class Ressource():

    def __init__(self):                              #initialisation des variables
        self.path = os.getcwd() + "/livres"          #recupération du chemin d'accès
        self.pdf = []
        self.epub = []
        self.other = []


    def extract(self,repo, path = None):            #récupération des fichiers d'un dossier contenu dans "livres"
        if path : 
            a = path
        else:
            a = self.path
        print(a)
        b = "/" + str(repo)
        path_2 = a + b
        p = os.listdir(path_2)
        Ressource.tri(self,p,path_2)


    def dezip(self,file):                           #dézipe un dossier .zip dans "livres"
        new_file = self.path + "/" + str(file)
        os.mkdir(new_file[:-4])
        with ZipFile(new_file, 'r') as zip:      
            zip.extractall(new_file[:-4]) 
        p = os.listdir(new_file[:-4])
        Ressource.tri(self,p,new_file[:-4])


    def tri(self,p = None, path = None):          #permet de lister tous les fichiers des tous les dossiers/sous-dossiers contenus dans "livres"
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

    def __init__(self,path = None):                 #initialisation d'un livre
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

            if ".epub" in self.filename:                            #récupération metadata d'un fichier .epub
                reader = epub.open_epub(livre)
                meta = reader.opf.metadata
                name_author = meta.creators[0][0]
                name_title = meta.titles[0][0]
               
            
            if ".pdf" in self.filename:                             #récupération metadata d'un fichier .pdf
                reader = PdfReader(livre)
                meta = reader.metadata
                name_author = meta.author
                name_title = meta.title


            if name_author == None and name_title == None:         #si metadata absente alors on met le nom du fichier 
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
            toc = doc.get_toc()                                 #récupération de la table des matières du livre
            self.table = str(toc)                               #transforme la table des matières en str
            self.language = langid.classify(self.table)[0]      #récupération de la langue du livre à partir de la table des matières

        elif ".mp3" in self.filename:
            audiofile = eyed3.load(livre)                       
            self.author = audiofile.tag.artist                  #récupération des tags du mp3 (ici l'artiste)
            self.title = audiofile.tag.title                    #récupération des tags du mp3 (ici le titre)

        return self

    
class Bibliotheque():

    def __init__(self):                             #initialise une bibliothèque
        self.path = os.getcwd() + "/livres"
        self.livres = []
        self.table_auteur = []



    def sommaire(self, livre):                      #permet de créer le sommaire d'un livre au format .pdf/ .epub/ .html/ .txt
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
        if ".epub" in livre.filename:
            nom_fichier = livre.filename[:-5]
        else:
            nom_fichier = livre.filename[:-4]

        sommaire2 = pd.DataFrame(sommaire, columns = ["sommaire"])
        nom_sommaire = nom_fichier + "_sommaire"
        sommaire2.to_html(nom_sommaire + '.html', index=False)  #créé un fichier html pour mieux visualiser les données
        np.savetxt(nom_sommaire + '.txt', sommaire2,fmt='%s', encoding="utf-8") #sauvegarde la dataframe au format .txt
        pdf = FPDF()    #enregistre la class (FPDF() dans une variable)
        pdf.add_page()  #ajoute une page
        pdf.set_font("Helvetica", size = 8)
        f = open(nom_sommaire + ".txt", "r",encoding="ISO-8859-1") #ouvre le fichier en mode lecture avec le bon encodage
        for x in f: #insert le texte dans le pdf
            pdf.multi_cell(150, 5, txt = x)
        pdf.output(nom_sommaire + ".pdf") #conversion .txt en .pdf
        doc = aw.Document(nom_sommaire + ".txt")
        doc.save(nom_sommaire + ".epub") #conversion .txt en .epub
        f.close()

        sommaires = [nom_sommaire + ".pdf",nom_sommaire + ".epub",  nom_sommaire + '.html',nom_sommaire + ".txt" ]

        for sommaire in sommaires:
            shutil.move(os.getcwd() + "/" + sommaire, os.getcwd() + "/les_sommaires" + "/"+ sommaire) #déplacement sommaires dans sous-dossier "les_sommaires"




    def sup_sommaire(self,nom_fichier):                     #supprime les sommaires qui ne doivent plus être dans le sommaire
        if ".epub" in nom_fichier:
            nom_sommaire = nom_fichier[:-5] +"_sommaire"
        else:
            nom_sommaire = nom_fichier[:-4] +"_sommaire"

        os.remove(os.getcwd() + "/les_sommaires/" + nom_sommaire + ".pdf")
        os.remove(os.getcwd() + "/les_sommaires/" + nom_sommaire + ".epub")
        os.remove(os.getcwd() + "/les_sommaires/" + nom_sommaire + ".txt")
        os.remove(os.getcwd() + "/les_sommaires/" + nom_sommaire + ".html")

    
    def recup(self,path = None,el = None):                  #notre commande init
        if path:
            new_path = path
            if el:
                new_path += '/' + el
        else:
            new_path = self.path
            os.mkdir(self.path[:-7]   +'/les_sommaires')        #création des sous-dossiers où l'on aura les sommaires et les listes des livres/auteurs
            os.mkdir(self.path[:-7]  + "/liste_auteurs")
            os.mkdir(self.path[:-7]  + "/liste_ouvrages")
            file = open(os.getcwd()+"/log.txt", "w")            #création d'un fichier log vide 
            file.write("Fichier Log:" +"\n") 
            file.close()
            file = open(os.getcwd()+"/bibli2.conf", "w")        #création d'un fichier .conf 
            file.write("Fichier de Configuration :" +"\n")      
            file.close()
            file = open(os.getcwd()+"/bibli2.conf", "a")            
            dossier = os.listdir(os.getcwd())
            for i in range(len(dossier)):
                file.write(dossier[i]+"\n")                     #remplissage du .conf (qui résume ce que l'on a dans le répertoire courant)
            file.close()


        
        bibli = os.listdir(new_path) #liste tous les éléments dans le nouveau chemin 
        err = ["verne_phare_bout_monde_mv.pdf","verne_phare_bout_monde.pdf","verne_geographie_france_et_colonies_ocr.pdf","autorun.pdf","pochette_cd_conan_doyle.pdf","epinal"]
        #err désigne la liste des éléments qui nous pose problème
        for i in range(len(bibli)):
            element = bibli[i]
            print(element)
            if not "." in element and not element in err:
                path_2 = new_path +"/"+ element
                Bibliotheque.recup(self,path_2)
            elif not element in err:
                B = Livre(new_path)
                livre = B.recup(element)
                self.livres.append(livre)
                Bibliotheque.ajoute_auteur(self,livre)
                Bibliotheque.sommaire(self,livre)
        return self.livres





    def DataFrame(self,ouvrages = None, auteurs = None):
        #Construction de la data frame correspondant au liste des ouvrages
        if ouvrages:
            C_aut = pd.DataFrame([row[2] + " | " for row in ouvrages],columns = ["auteurs"])
            C_liv = pd.DataFrame([row[1] + " | "  for row in ouvrages],columns = ["livres"])
            C_lang = pd.DataFrame([row[3] + " | "  for row in ouvrages],columns = ["langue"])
            C_nom = pd.DataFrame([" > " + row[0] + " | " for row in ouvrages],columns = ["nom du fichier"])
            L1 = pd.DataFrame([" > " + row[0] + " : " for row in auteurs],columns = ["auteurs"])
            L2 = pd.DataFrame([row[1] for row in auteurs],columns = ["livres et leur nom de fichier"])

        else:
            C_aut = pd.DataFrame([row.author + " | " for row in self.livres],columns = ["auteurs"])
            C_liv = pd.DataFrame([row.title + " | "  for row in self.livres],columns = ["livres"])
            C_lang = pd.DataFrame([row.language + " | "  for row in self.livres],columns = ["langue"])
            C_nom = pd.DataFrame([" > " + row.filename + " | " for row in self.livres],columns = ["nom du fichier"])
            L1 = pd.DataFrame([" > " + row[0] + " : " for row in self.table_auteur],columns = ["auteurs"])
            L2 = pd.DataFrame([row[1] for row in self.table_auteur],columns = ["livres et leur nom de fichier"])

        
        DataFrame_auteurs = pd.concat([C_nom,C_liv,C_aut,C_lang],axis = 1) #create a dataframe of all of the books
        DataFrame_auteurs.to_html('Ouvrages.html', index=False)  #create a html_file just to visualize the table
        np.savetxt('Ouvrages.txt', DataFrame_auteurs,fmt='%s',encoding="utf-8") #save the dataFrame as a txt file
        pdf = FPDF()    #save FPDF() class into a variable pdf 
        pdf.add_page()  #add a page
        pdf.set_font("Helvetica", size = 8)
        f = open("Ouvrages.txt", "r",encoding="ISO-8859-1") #open the text file in read mode
        for x in f: #insert the test in pdf
            pdf.multi_cell(150, 5, txt = x)
        pdf.output("Ouvrages.pdf") #save txt_file as  a pdf_file
        doc = aw.Document("Ouvrages.txt")
        doc.save("Ouvrages.epub") #save txt_file as an epub_file
        f.close()

        ouvrages = [ 'Ouvrages.html', 'Ouvrages.txt' , "Ouvrages.pdf", "Ouvrages.epub"]

        for ouvrage in ouvrages:
            shutil.move(os.getcwd() + "/" + ouvrage, os.getcwd() + "/liste_ouvrages" + "/"+ ouvrage)
                

        #Construction de la data frame correspondant au liste des auteurs avec leurs oeuvres
        L = pd.concat([L1,L2],axis = 1) #create a dataframe of all of the authors
        L.to_html('Auteurs.html', index=False) #create a html_file just to visualize the table
        np.savetxt('Auteurs.txt', L,  fmt='%s',encoding="utf-8") #save the DataFrame as a txt_file
        pdf = FPDF() # save FPDF() class into a variable pdf    
        pdf.add_page() # Add a page
        pdf.set_font("Arial", size = 8) # set style and size of font
        f = open("Auteurs.txt", "r",encoding="ISO-8859-1") # open the text file in read mode
        for x in f: # insert the text in pdf
            pdf.multi_cell(150, 5, txt = x)
        pdf.output("Auteurs.pdf") #save txt_file as a pdf_file
        doc = aw.Document("Auteurs.txt")
        doc.save("Auteurs.epub") #save txt_file as an epub_file
        f.close()

        listes_auteur = [ 'Auteurs.html', 'Auteurs.txt',"Auteurs.pdf", "Auteurs.epub"]

        for liste_auteur in listes_auteur:
            shutil.move(os.getcwd() + "/" + liste_auteur, os.getcwd() + "/liste_auteurs" + "/"+ liste_auteur)
        


    def ajoute_auteur(self,element):
        j = -1
        for i in range(len(self.table_auteur)):
            if self.table_auteur[i][0] == element.author:
                j = i
        if j == -1 :
            self.table_auteur.append([element.author, "\n" + str([element.title,element.filename+ " "]) + "\n" ])
        else:
            self.table_auteur[j][1] += str([element.title,element.filename+ " "]) + "\n"





    def update(self):
        myfile1 = open(os.getcwd() + "/liste_ouvrages/Ouvrages.txt", "r",encoding = "utf-8")    #Ouverture de la liste des ouvrages
        texte_ouvrage = myfile1.read() 
        myfile2 = open(os.getcwd() + "/liste_auteurs/Auteurs.txt", "r",encoding = "utf-8")      #Ouverture de la liste des auteurs
        texte_auteur = myfile2.read()
        bibli = os.listdir(os.getcwd() + "/livres")
        date = os.path.getmtime(os.getcwd()+"/liste_auteurs/Auteurs.txt")                       #On met la date de mise à jour de la liste des auteurs
        Liste_ouvrages = []
        Liste_auteurs = []
        err = ["verne_phare_bout_monde_mv.pdf","verne_phare_bout_monde.pdf","verne_geographie_france_et_colonies_ocr.pdf","autorun.pdf","pochette_cd_conan_doyle.pdf","epinal"]
        for i in range(len(bibli)):
            livre = bibli[i]        
            print(livre)   
            if not livre in Liste_ouvrages and ".zip" not in livre and "." in livre and livre not in err: 
                A = Livre(os.getcwd() + "/livres")
                element = A.recup(livre)
                Liste_ouvrages.append([ element.filename, element.title, element.author,element.language])
                nom_auteurs = [row[0] for row in Liste_auteurs]
                if not element.author in nom_auteurs:
                    Bibliotheque.sommaire(self,element)                                                              #Nouvel élément donc nous devons mettre son sommaire
                    Liste_auteurs.append([element.author, "\n" + str([element.title,element.filename+ " "]) + "\n" ])
                else:
                    for j in range(len(Liste_auteurs)):
                        if nom_auteurs[j] == element.author:
                            Liste_auteurs[j][1] += str([element.title,element.filename+ " "]) + "\n"
                            break
                if livre not in texte_ouvrage:                                                                       #Nouvel élément donc nous devons mettre dans le log
                        file = open(os.getcwd()+"/log.txt", "a") 
                        file.write("Ajout du fichier : " + livre +"\n")                                                 
                        file.close()
                else:
                    if date < os.path.getmtime(os.getcwd()+"/livres/" + livre):                                         #mise à jour d'un élément
                        file = open(os.getcwd()+"/log.txt", "a") 
                        file.write("Mise a jour du fichier : " + livre +"\n") 
                        file.close()                        

        k = 0
        nom_fichier = ""
        i = 0
        element_a_ajouter = False
        mot = texte_ouvrage.split()
        while ( i != len(mot)):
            if k%4 == 0 and mot[i] != ">" and mot[i] != "|":                                #On a la forme : > nom_fichier | nom_titre | nom_auteur | langue
                nom_fichier += mot[i]                                                       # On essaie de lire le nom du fichier et verifier s'il est encore dans la nouvelle bibliothèque
            if mot[i] == '|':
                k +=1
                if k%4 == 1:
                    if not nom_fichier in bibli:
                        element_a_ajouter = False
                        Bibliotheque.sup_sommaire(self,nom_fichier)                         #On supprime si le fichier n'y est plus
                        file = open(os.getcwd()+"/log.txt", "a") 
                        file.write("Suppression du fichier : " +nom_fichier +"\n")          #On le précise dans le log
                        file.close()
                    else:
                        element_a_ajouter = True
                        if not livre in Liste_ouvrages: 
                            A = Livre(os.getcwd() + "/livres")
                            element = A.recup(livre)
                            Liste_ouvrages.append([ element.filename, element.title, element.author,element.language])
                            nom_auteurs = [row[0] for row in Liste_auteurs]
                            if not element.author in nom_auteurs:
                                Bibliotheque.sommaire(self,element)
                                Liste_auteurs.append([element.author, "\n" + str([element.title,element.filename+ " "]) + "\n" ])
                            else:
                                for j in range(len(Liste_auteurs)):
                                    if nom_auteurs[j] == element.author:
                                        Liste_auteurs[j][1] += str([element.title,element.filename+ " "]) + "\n"
                                        break
                    nom_fichier = ""
            i+=1
        myfile1.close()
        myfile2.close()
        Bibliotheque.DataFrame(self,Liste_ouvrages,Liste_auteurs)                       #On refait les datas-frames



    def update_bibli(self):                             #Permet de mettre à jour le .conf
        dossier = os.listdir(os.getcwd())
        print(dossier)
        file = open(os.getcwd()+"/bibli2.conf", "r")
        liste_conf = file.readlines()
        file.close()
        liste_finale = liste_conf[0]
        for i in range(len(dossier)):
            dossier[i] += "\n" 

        for i in range(1,len(liste_conf)):
            if liste_conf[i] in dossier:
                liste_finale+= liste_conf[i]
            else:
                file = open(os.getcwd()+"/log.txt", "a") 
                file.write("Suppression du fichier/dossier : " +liste_conf[i]) 
                file.close()
        

        for i in range(len(dossier)):
            if not dossier[i] in liste_conf:
                liste_finale += dossier[i]
                file = open(os.getcwd()+"/log.txt", "a") 
                file.write("Ajout du fichier/dossier : " +dossier[i]) 
                file.close()

        file = open(os.getcwd()+"/bibli2.conf", "w")
        file.write(liste_finale) 
        file.close()



