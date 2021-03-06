# -*- coding: utf-8 -*-

import os

import kivy
kivy.require('1.10.1')
from kivy.app import App
from kivy.core.window import Window
from kivy.config import Config
from kivy.base import EventLoop
from kivy.lang.builder import Builder
from kivy.properties import ObjectProperty, BooleanProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.settings import Settings

from kivymd.theming import ThemeManager

from data_reader import DataReader
from tab_operations import TabOperations
from graphs.cottrell_graph_kivy import CottrellGraph
from graphs.linearRegress_graph_kivy import GraphLinearRegression
from components.file_chooser import OpenDialog
from components.cox_popup import CoxPopup
from components.interval_popup import IntervalPopup
from components.errorpopup import ErrorPopup
from components.settingthemepicker import SettingThemePicker
import cottrell.cottrell_math as cm

Config.read('config.ini')
# set config
Config.write()

class MainWindow(Widget):
    """Classe représentant la fenêtre principale
    Elle a le même nom que dans app.kv.
    """
    curveBoxLayout = ObjectProperty(None)
    expCurveSwitch = ObjectProperty(None)

    smallCurveBoxLayout = ObjectProperty(None)

    #valeurs pour Dth
    buttonDth = ObjectProperty(None)    
    valDth=NumericProperty(10**(-5))
    valMinDth=NumericProperty(0)
    valMaxDth=NumericProperty(10**(-4))
    stepsDth=NumericProperty(10**(-6))
    
    #valeurs pour N
    buttonN = ObjectProperty(None)
    valN=NumericProperty(1)
    valMinN=NumericProperty(1)
    valMaxN=NumericProperty(4)
    stepsN=NumericProperty(1)

    #valeurs pour S
    buttonS = ObjectProperty(None)
    valS=NumericProperty(0.25)
    valMinS=NumericProperty(0)
    valMaxS=NumericProperty(0.5)
    stepsS=NumericProperty(0.01)
    
    #valeurs pour C
    buttonC = ObjectProperty(None)
    valC=NumericProperty(10**(-5))
    valMinC=NumericProperty(0)
    valMaxC=NumericProperty(1)
    stepsC=NumericProperty(10**(-6))
    
    thCurveSwitchActive = BooleanProperty(True)
    
    valIntervalMin=NumericProperty(0)
    valIntervalMax=NumericProperty(100)
    
    expDataLoaded=BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)
        
        #Valeurs pour le bouton Dth
        self.buttonDth.value=self.valDth
        self.buttonDth.min_value=self.valMinDth
        self.buttonDth.max_value=self.valMaxDth
        self.buttonDth.steps=self.stepsDth
        
        #Valeurs pour le bouton N
        self.buttonN.value=self.valN
        self.buttonN.min_value=self.valMinN
        self.buttonN.max_value=self.valMaxN
        self.buttonN.steps=self.stepsN
    
        #Valeurs pour le bouton S
        self.buttonS.value=self.valS
        self.buttonS.min_value=self.valMinS
        self.buttonS.max_value=self.valMaxS
        self.buttonS.steps=self.stepsS
        
        #Valeurs pour le bouton C
        self.buttonC.value=self.valC
        self.buttonC.min_value=self.valMinC
        self.buttonC.max_value=self.valMaxC
        self.buttonC.steps=self.stepsC
        
        #tableau de valeurs expérimentales non traité (gardé en mémoire)
        self.exptRaw=None
        self.expIRaw=None
        #tableau de valeurs exp traité suivant l'intervalle sélectionné
        self.expt = None
        self.expI = None
        #valeur à ajouter aux I du tableau en cas de problème 
        self.correctI = 0
        
        self.mainGraph = CottrellGraph()
        
        # Initialisation des tableaux t et I théoriques
        self.t = cm.create_t(0, 20, 1000)
        self.I = cm.cottrell_curve_gen(self.buttonN.value, self.buttonS.value, 
                        self.buttonC.value, self.buttonDth.value, self.t)
                                           
        
        self.mainGraph.set_theoric_data(self.t, self.I)
        
        self.mainGraph.set_limit_interval()
        self.mainGraph.update()
        
        self.curveBoxLayout.add_widget(self.mainGraph.get_canvas())
        
        self.bind_update_values(self.buttonDth)
        self.bind_update_values(self.buttonN)
        self.bind_update_values(self.buttonS)
        self.bind_update_values(self.buttonC)
    
    def on_expCurveSwitch_active(self, active):
        if active:
            if self.expt:
                self.mainGraph.display_experimental()
                self.mainGraph.set_limit_interval()
            else:
                self.expCurveSwitch.active = False
        else:
            self.mainGraph.display_experimental(False)
            self.mainGraph.set_limit_interval()
        self.mainGraph.update()
    
    def on_thCurveSwitch_active(self, active):
        if active:
            self.mainGraph.display_theoric()
            self.mainGraph.set_limit_interval()
        else:
            self.mainGraph.display_theoric(False)
            self.mainGraph.set_limit_interval()
        self.mainGraph.update()
    
    def on_interval_define_button_active(self,instance):  
        if self.expt :
            interval_popup=IntervalPopup() 
            interval_popup.intervalbox.val_min=self.valIntervalMin
            interval_popup.intervalbox.val_max=self.valIntervalMax
            interval_popup.intervalbox.correction_I = self.correctI
            interval_popup.intervalbox.update_display_val()
            interval_popup.bind(on_dismiss=self.on_interval_popup_closed)
            interval_popup.open()
        
    def on_interval_popup_closed(self, popup):
        maxtexp = max(self.exptRaw)
        mintexp = min(self.exptRaw)
        if (mintexp <= popup.intervalbox.val_min < popup.intervalbox.val_max <= maxtexp and 
                popup.intervalbox.val_max-popup.intervalbox.val_min > 0.2) :
            self.valIntervalMin=popup.intervalbox.val_min
            self.valIntervalMax=popup.intervalbox.val_max
            self.correctI = popup.intervalbox.correction_I
            self.set_exp_tab_interval()
            self.set_correction_I()

            self.mainGraph.set_experimental_data(self.expt, self.expI)
            
            #Recalcule les valeurs théoriques pour coller avec l'étendue des 
            #valeurs expériementales
            self.t = cm.create_t(0, max(self.expt), 1000)
            self.I = cm.cottrell_curve_gen(self.valN, self.valS, self.valC, 
                                                          self.valDth, self.t)
            self.mainGraph.set_theoric_data (self.t, self.I)
            
            self.mainGraph.set_limit_interval()
            self.mainGraph.update()
            
            if not hasattr(self, 'graphLinearRegression') and self.ids['dCurveCheckBox'].active:
                if self.expt and min(self.expI)>0:
                    self.graphLinearRegression = GraphLinearRegression(self.valN, self.valS, self.valC, 
                                                                       self.expt, self.expI)
            if hasattr(self, 'graphLinearRegression'):
                if self.expt and min(self.expI)>0:
                    if self.graphLinearRegression.get_canvas() not in self.curveBoxLayout.children:
                        self.curveBoxLayout.clear_widgets()
                        self.curveBoxLayout.add_widget(self.graphLinearRegression.get_canvas())
                    self.graphLinearRegression.t = self.expt
                    self.graphLinearRegression.I = self.expI
                    self.graphLinearRegression.update()
                else:
                    self.curveBoxLayout.clear_widgets()
                    self.curveBoxLayout.add_widget(Label(text="""[color=FF0000]Attention !
Les données expérimentales contiennent des valeurs négatives ou nulles.
Veuillez les enlever avec le bouton[/color] [color=000000]«Sélectionner l'intervalle de travail»[/color]""",
                    markup=True, halign='center', valign='center', font_size=20))
        else :
            ErrorPopup("L'intervalle doit être contenu entre {}s et {}s.\n\
Les valeurs sont inchangées.".format(mintexp, maxtexp)).open()
                                                                                                                                         
    def on_cox_button_active(self,instance):
        cox_popup=CoxPopup()
        cox_popup.CoxvalDth=self.valDth
        cox_popup.CoxvalS=self.valS
        cox_popup.CoxvalC=self.valC
        cox_popup.CoxvalN=self.valN
        cox_popup.coxGraph.update()
        cox_popup.open()
        
    def set_exp_tab_interval(self):
        """Change les tableaux `expt` et `expI` pour qu'ils correspondent à 
        l'intervalle actuel.
        """
        self.expt, self.expI = TabOperations.del_values_not_between_tmin_tmax(self.exptRaw, self.expIRaw, 
                                                                  self.valIntervalMin, self.valIntervalMax)
    def set_correction_I(self):
        self.expI = TabOperations.add_x_to_tab(self.expI,self.correctI)

    def on_dCurveCheckBox_active(self, active):
        """Affiche/Efface la courbe de régression linéaire lorsque les données 
        le permettent, ou un message d'erreur si elles ne le permettent pas.
        """
        if active:
            self.curveBoxLayout.clear_widgets()
            if self.expt and min(self.expI)>0:
                self.graphLinearRegression = GraphLinearRegression(self.valN, self.valS, self.valC, 
                                                                   self.expt, self.expI)
                self.graphLinearRegression.update()
                self.curveBoxLayout.add_widget(self.graphLinearRegression.get_canvas())
            else:
                self.curveBoxLayout.add_widget(Label(text="""[color=FF0000]Attention !
Les données expérimentales contiennent des valeurs négatives ou nulles.
Veuillez les enlever avec le bouton[/color] [color=000000]«Sélectionner l'intervalle de travail»[/color]""",
                    markup=True, halign='center', valign='center', font_size=20))
            self.mainGraph.legend = False
            self.mainGraph.ticks_labels = False
            self.smallCurveBoxLayout.clear_widgets()
            self.smallCurveBoxLayout.add_widget(self.mainGraph.get_canvas())
            self.mainGraph.set_limit_interval()
            self.mainGraph.update()
        else:
            if hasattr(self, 'graphLinearRegression'):
                del self.graphLinearRegression
            self.smallCurveBoxLayout.clear_widgets()
            self.curveBoxLayout.clear_widgets()
            self.mainGraph.legend = True
            self.mainGraph.ticks_labels = True
            self.mainGraph.set_limit_interval()
            self.mainGraph.update()
            self.curveBoxLayout.add_widget(self.mainGraph.get_canvas())
    
    def on_theme_colors(self, *args):
        """Appelé lors de la modification des couleurs du thème.
        """
        self.mainGraph.update_colors(*args)
        if hasattr(self, 'graphLinearRegression') and \
           self.graphLinearRegression is not None:
            self.graphLinearRegression.update_colors(*args)
            
        
    def on_touch_down(self, touch):
        """Gestion du zoom à la souris.
        """
        if self.mainGraph.collide_plot(*self.mainGraph.to_widget(*touch.pos, relative=True)):
            if touch.is_mouse_scrolling:
                if touch.button == 'scrolldown':
                    #Zoom out
                    self.mainGraph.zoom(0.95, 0.95, *self.mainGraph.to_widget(*touch.pos, relative=True))
                elif touch.button == 'scrollup':
                    #Zoom in
                    self.mainGraph.zoom(1.05, 1.05, *self.mainGraph.to_widget(*touch.pos, relative=True))
                return True
        return super(MainWindow, self).on_touch_down(touch)            
        
    def on_touch_move(self, touch):
        """Gestion du zoom aux doigts.
        """
        if len(EventLoop.touches)==2:
            for other_touch in EventLoop.touches:
                if touch.distance(other_touch):
                    center = ((touch.x+other_touch.x)/2, (touch.y+other_touch.y)/2)
                    if self.mainGraph.collide_plot(*self.mainGraph.to_widget(*center, relative=True)):
                        dx = abs(touch.x - other_touch.x) - abs(touch.px - other_touch.px)
                        dy = abs(touch.y - other_touch.y) - abs(touch.py - other_touch.py)
                        factor = dx if abs(dx)>=abs(dy) else dy
                        self.mainGraph.zoom(1 + 0.05*factor/20, 1 + 0.05*factor/20, *self.mainGraph.to_widget(*center, relative=True))
                        return True
        return super(MainWindow, self).on_touch_move(touch)
    
    def update_values(self,instance,text):
        '''Met à jour les courbes avec les nouvelles valeurs.
        '''
        error_text="{0} ne peut pas prendre une valeur négative {1}!\n\
La valeur de {0} utilisée pour le graphique est inchangée."
        if self.buttonDth.value >=0:
            self.valDth=self.buttonDth.value
        else :
            ErrorPopup(text=error_text.format("Dth", '')).open()
            self.buttonDth.value = self.valDth
        if self.buttonN.value>0:
            self.valN=self.buttonN.value
        else :
            ErrorPopup(text=error_text.format("n", "ou nulle ")).open()
            self.buttonN.value = self.valN
        if self.buttonC.value>0:
            self.valC=self.buttonC.value
        else :
            ErrorPopup(text=error_text.format("C",  "ou nulle ")).open()
            self.buttonC.value = self.valC
        if self.buttonS.value>0:
            self.valS=self.buttonS.value
        else :
            ErrorPopup(text=error_text.format("S", "ou nulle ")).open()
            self.buttonS.value = self.valS
            
        self.I = cm.cottrell_curve_gen(self.valN,self.valS, self.valC, self.valDth, self.t)
        
        self.mainGraph.I=self.I
        self.mainGraph.update()
        
        if hasattr(self, 'graphLinearRegression'):
            self.graphLinearRegression.n = self.valN
            self.graphLinearRegression.S = self.valS
            self.graphLinearRegression.C = self.valC
            self.graphLinearRegression.update()

    def bind_update_values(self, spinbox):
        spinbox.value_id.bind(text = self.update_values)

    def show_openDialog(self):
        """Affiche la boite de dialogue d'ouverture de fichier.
        """
        content = OpenDialog()
        self._openPopup = Popup(title="Sélectionnez le fichier de données :",
                                content=content, size_hint=(0.7, 0.7))
        content.cancel = self._openPopup.dismiss
        content.load = self.load_data_from_dialog
        self._openPopup.open()
    
    def load_data_from_dialog(self, path, filename):
        if isinstance(filename, (list, tuple)):
            if filename:
                filename = filename[0]
        if filename:
            err = self.load_exp_data(path, filename)
            if err is None:
                self._openPopup.dismiss()
            else:
                if isinstance(err, FileNotFoundError):
                    ErrorPopup(text="Le fichier spécifié est introuvable ! \
Veuillez vérifier son nom et son chemin.").open()
                else:
                    ErrorPopup(text="Une erreur est survenue lors de la lecture \
du fichier !\n\n"+str(err)).open()
                
        else:
            ErrorPopup(text="Veuillez sélectionner un fichier.").open()
    
    def load_exp_data(self, path, filename):
        """Charge les valeurs expérimentales depuis le fichier `filename` situé
        dans le dossier `path`. Si `filename` est une liste ou un tuple, seule
        la première case est considérée.
        
        Paramètres
        ----------
        path : str
            Chemin du fichier à charger.
        filename : str or list-like of str
            Nom du fichier à charger.
        
        Retour
        ------
        Retourne None si la lecture s'est bien passée, retourne l'erreur sinon.
        """
        try:
            reader = DataReader(os.path.join(path, filename))
        except FileNotFoundError as err:
            print(err)
            return err
        except ValueError as err:
            print("ValueError: ",err)
            return err
        except Exception as err:
            print(err)
            return err
        
        self.exptRaw = reader.get_t()
        self.expIRaw = reader.get_I()
        self.expt = self.exptRaw
        self.expI = self.expIRaw
            
        #Pour la modification d'intervalle
        self.valIntervalMin = (min(self.expt))
        self.valIntervalMax = (max(self.expt))
        
        self.mainGraph.set_experimental_data(self.expt, self.expI)
        
        #Recalcule les valeurs théoriques pour coller avec l'étendue des valeurs
        #expérimentales
        self.t = cm.create_t(0, max(self.expt), 1000)
        self.I = cm.cottrell_curve_gen(self.valN, self.valS, self.valC, self.valDth, self.t)
        self.mainGraph.set_theoric_data (self.t, self.I)
        
        self.mainGraph.set_limit_interval()
        self.mainGraph.update()
        
        self.expDataLoaded=True
        
        return None


class AppApp(App):
    """Point d'entrée de l'application.
    """
    title = "ReDoxLab"
    use_kivy_settings = False
    
    theme = 'default'
    
    theme_cls = ThemeManager()
    theme_cls.primary_palette = "BlueGray"
    theme_cls.accent_palette = "Gray"
    theme_cls.theme_style = "Dark"
    
    def build(self):
        Window.bind(on_keyboard=self.key_input)
        self.register_event_type('on_theme_colors')
        
        #Chargement des configuration
        config = self.config
        self.theme = config.get('Apparence', 'theme') 
        self.theme_cls.theme_style, self.theme_cls.primary_palette,\
            self.theme_cls.accent_palette = config.get('Apparence', 'theme-colors') .split(', ')
        
        self.load_theme_kv("app-{}.kv")
        
        self.load_theme_kv("components/cox_popup-{}.kv")
        self.load_theme_kv("components/entrypopup-{}.kv")
        self.load_theme_kv("components/errorpopup-{}.kv")
        self.load_theme_kv("components/file_chooser-{}.kv")
        self.load_theme_kv("components/intervalbox-{}.kv")
        self.load_theme_kv("components/interval_popup-{}.kv")
        self.load_theme_kv("components/spinbox-{}.kv")
        
        self.settings_cls = Settings
        
        #print(self.theme_cls.primary_color)
        
        self.root = MainWindow()
        self.bind(on_theme_colors=self.root.on_theme_colors)
        
        if self.theme == 'material-design':
            self.dispatch('on_theme_colors', config.get('Apparence', 'theme-colors'))
        
        return self.root
    
    def load_theme_kv(self, path):
        """
        path must be similar to "/optional/mywidget{}.kv" to be parsed by format.
        """
        try:
            Builder.load_file(path.format(self.theme))
        except FileNotFoundError as err:
            print("""Erreur lors de l'ouverture du fichier {} : {}
Chargement du fichier kv par défaut.""".format(path.format(self.theme), err))
            Builder.load_file(path.format("default"))
    def build_config(self, config):
        """
        Définie les valeurs par défaut pour les sections de configuration.
        """
        config.setdefaults('Apparence', {'theme': 'material-design',})
        config.setdefaults('Apparence', {'theme-colors': '{}, {}, {}'.format(
                self.theme_cls.theme_style, self.theme_cls.primary_palette, 
                self.theme_cls.accent_palette),})

    def build_settings(self, settings):
        """
        Ajoute notre propre section à l'objet de configuration par défaut.
        """
        settings.register_type('theme-picker', SettingThemePicker)
        settings.add_json_panel('Apparence', self.config, 'settings.json')

    def on_config_change(self, config, section, key, value):
        """
        Répond aux changements dans la configuration.
        """

        if section == "Apparence":
            if key == "theme":
                pass
            if key == "theme-colors":
                if self.theme == 'material-design':
                    self.dispatch('on_theme_colors', value)
    
    def on_theme_colors(self, *args):
        pass

    def close_settings(self, settings=None):
        """
        Appelé quand le panneau des paramètres est clos.
        """
        super(AppApp, self).close_settings(settings)
        
    def on_pause(self):
        return True
    
    def on_resume(self):
        return True
    
    def key_input(self, window, key, scancode, codepoint, modifier):
        #Gestion de la touche Esc/Echap et du bouton Back sur Android.
        if key == 27:
            
            if self.theme == "default":
                content = BoxLayout(orientation = 'vertical')
                content.add_widget(Label(text = "Voulez vous vraiment fermer l'application ?"))
                
                buttons = BoxLayout(orientation = 'horizontal')
                button_close = Button(text='Fermer')
                button_cancel = Button(text='Annuler')
                buttons.add_widget(button_close)
                buttons.add_widget(button_cancel)
                
                content.add_widget(buttons)
                popup = Popup(title = "Fermer ?", content=content, auto_dismiss=True, size_hint=(0.3, 0.2))
                
                #lie l'evènement "on_press" du buton à la fonction dismiss() 
                button_cancel.bind(on_press=popup.dismiss)
                button_close.bind(on_press=popup.dismiss)
                button_close.bind(on_press = self.close)
                
                #ouvre le popup
                popup.open()
            elif self.theme == "material-design":
                from kivymd.dialog import MDDialog
                
                def callback(self, result):
                    if result == "Fermer":
                        self.close()
                    popup.dismiss()
                
                popup = MDDialog(
                        title="Fermer ?", size_hint=(0.3, 0.2),
                        text_button_ok="Fermer",
                        text="Voulez vous vraiment fermer l'application ?",
                        text_button_cancel="Annuler",
                        events_callback=lambda *args: callback(self, args[0])
                )
                popup.open()
            return True  
        else:           #la touche ne fait maintenant plus rien
            return False
    
    def close(self, *args, **kwargs):
        Window.close()
        App.get_running_app().stop()


if __name__ in ('__main__', '__android__'):
    AppApp().run()
