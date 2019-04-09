# -*- coding: utf-8 -*-

import math as m

def list_transformation_log (values): 
    """Cette fonction crée une liste du logarithme népérien de chaque valeur d'une liste.
        
    Paramètres
    ----------
    values : list
        Tableau de valeurs

    Retour
    ------
    loglist : list
        Tableau de valeurs log

    """
    loglist=list()
    for val in values[1:]:
        loglist.append(m.log(val))
    return (loglist)

def mean (liste):
    """Cette fonction calcule la moyenne d'une liste.
    """
    
    summ=m.fsum(liste)
    mean = summ/(len(liste))
    return (mean)

class LinearRegression:
    """Cette classe permet d'effectuer la régression linéaire sur les valeurs 
    expérimentales.
    """

    def __init__(self, t, I):
        """
        Paramètres
        ----------
        t : list
            Tableau de valeurs des temps expérimentaux.
        I : list
            Tableau de valeurs des Intensités mesurées expérimentalement.
        """
        self.t=t
        self.I=I
        self.Dexp=0
        
    F = 96485.3329  #Constante de Faraday
    
    def logexp_curves_tab(self, expt, expI):
        """Cette fonction calcule les listes des valeurs logarithmique des liste du temps et de l'intensité.
        
        Paramètres
        ----------
        expt : list
            Tableau de valeurs des temps expérimentaux
        expI : list
             Tableau de valeurs des Itensité expérimentales
        
        """
        self.logexpt= list_transformation_log(expt)
        self.logexpI=list_transformation_log(expI)
    
    def linregress (self):
        """Cette fonction calcule à l'aide de formules mathématiques et 
        par le modèle des moindres carrés le coefficient directeur et 
        l'ordonnée à l'origine de la droite de régression linéaire. 
        
        Retour
        ------
        linearcoefficient : float
            Coefficient directeur de la droite de régression linéaire
        intercept : float
            Ordonnée à l'origine de la droite de régression linéaire
        
        """
        meant = mean(list_transformation_log(self.t))
        meanI = mean(list_transformation_log(self.I))
        linearcoefficient = m.fsum(((t)-meant)*((I)-meanI) for t,I in zip(self.logexpt,self.logexpI))/(m.fsum(((t)-meant)**2 for t in self.logexpt)) 
        intercept = meanI-linearcoefficient*meant
        return(linearcoefficient,intercept)
        
    def logexp_and_linear_curves_tab (self, expt, expI):
        """Cette fonction calcule la liste des valeurs de la droite de régression 
        linéaire.
        
        Paramètres
        ----------
        expt : list
            Tableau de valeurs de temps expérimentales
        expI : list
            Tableau de valeurs d'intensité expérimentales
            
        Retour
        ------
        linlogexpI : list
            Tableau des valeurs d'Intensité de la droite de régression linéaire
        """
        self.logexp_curves_tab (expt, expI)
        
        linearcoefficient, intercept= self.linregress()
        self.linlogexpI=[]
        for i in range (len(self.logexpt)) :
            self.linlogexpI.append(linearcoefficient*self.logexpt[i]+intercept)

        return (self.logexpt, self.logexpI, self.linlogexpI)
        
    def calculate_D (self, intercept, n, S, C):
        """Calcule le coefficient de diffusion D à l'aide des valeurs `n`, `S`
        et `C`.
        
        Paramètres
        ----------
        intercept : float
            Ordonnée à l'origine
        n : int
            Nombre d'électrons échangés au cours de la réaction.
        S : float
            Surface d'échange.
        C : float
            Concentration de l'espèce.
        
        Retour
        ------
        D : float
            Coefficient de diffusion retrouvé expérimentalement
            
        """
        exponentialintercept = m.exp (intercept)
        D = (exponentialintercept**2*m.pi)/(n**2*self.F**2*S**2*C**2)
        self.Dexp=D
        return (D)             
       
        
