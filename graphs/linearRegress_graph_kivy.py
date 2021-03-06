# -*- coding: utf-8 -*-

from kivy.app import App
from kivy.garden.graph import Graph, SmoothLinePlot
from kivy.clock import Clock
from kivy.utils import get_color_from_hex

from kivymd.color_definitions import colors

from linear_regression import LinearRegression

class GraphLinearRegression(LinearRegression):
    """Crée le graphique des courbes de régression linéaire.
    """
    
    def __init__(self, n, S, C, t, I):
        """
        Paramètres
        ----------
        n : int
            Nombre d'électrons échangés au cours de la réaction.
        S : float
            Surface d'échange.
        C : float
            Concentration de l'espèce.
        t : list
            Tableau de valeurs des temps expérimentaux.
        I : list
            Tableau de valeurs des intensités mesurées expérimentalement.
        """
        super(GraphLinearRegression, self).__init__(t, I)
        self.n=n 
        self.S=S
        self.C=C
        
        graph_theme = {
            'label_options': {
                'color': [0, 0, 0, 1],  # color of tick labels and titles
                'bold': False},
            'background_color': [1, 1, 1, 1],  # back ground color of canvas
            'tick_color': [0, 0, 0, 1],  # ticks and grid
            'border_color': [0, 0, 0, 1]}  # border drawn around each graph

        self.graph = Graph(title = 'Courbes de Regression lineaire',
           xlabel='log Temps (s)',
           ylabel='log Intensité (A)',
           x_ticks_minor=5,
           x_ticks_major=5,
           y_ticks_major=0.2,
           y_ticks_minor=4,
           y_grid_label=True,
           x_grid_label=True,
           padding=5,
           x_grid=False,
           y_grid=False,
           precision="%#.4g",
           **graph_theme)
    
        self.logexpplot = SmoothLinePlot(color=[1, 0, 0, 1])
        self.logexpplot.label = "Expérimentale"
        
        self.linlogexpplot = SmoothLinePlot(color=[1, 0, 1, 1])

        self.graph.legend = True
    
        self.graph.add_plot(self.logexpplot) 
        self.graph.add_plot(self.linlogexpplot)
        
        self._trigger = Clock.create_trigger(self.update_ticks)
        self.graph._plot_area.bind(pos=self._trigger)
    
    def update(self, *args):
        """Met à jour l'affichage des courbes de régression linéaire et le 
        calcul du coefficient de diffusion expérimental. 
        """
        self.logexp_and_linear_curves_tab(self.t, self.I)
        _, intercept= self.linregress()
        self.Dexp=self.calculate_D ( intercept, self.n, self.S, self.C)
        
        self.linlogexpplot.label = "Régression linéaire\nD="+str(self.Dexp)
        
        self.logexpplot.points = list(zip(self.logexpt, self.logexpI))
        self.linlogexpplot.points = list (zip(self.logexpt, self.linlogexpI))
        
        self.graph.xmin=float(min(self.logexpt))
        self.graph.xmax=float(max(self.logexpt))
        self.graph.ymin=float(min(self.logexpI))
        self.graph.ymax=float(max(self.logexpI))
        
        self.update_ticks()
    
    def update_ticks(self, *args):
        """Met à jour l'échelle.
        """
        width, height = self.graph.get_plot_area_size()
        self.graph.x_ticks_major = (self.graph.xmax-self.graph.xmin)/(width/100)
        self.graph.x_ticks_minor = 10
        self.graph.y_ticks_major = (self.graph.ymax-self.graph.ymin)/(height/50)
        self.graph.y_ticks_minor = 5
    
    def update_colors(self, *args):
        theme_cls = App.get_running_app().theme_cls
        self.graph.label_options['color'] = get_color_from_hex(colors[theme_cls.primary_palette][theme_cls.primary_hue])
        self.graph.background_color = get_color_from_hex(colors[theme_cls.theme_style]["Background"])
        self.graph.tick_color = get_color_from_hex(colors[theme_cls.accent_palette][theme_cls.accent_hue])
        self.graph.border_color = get_color_from_hex(colors[theme_cls.accent_palette][theme_cls.accent_hue])
        
    def get_canvas(self):
        return self.graph
